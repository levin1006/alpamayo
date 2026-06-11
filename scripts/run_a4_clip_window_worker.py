# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

"""Run fixed A4 full-window inference for an assigned clip set."""

from __future__ import annotations

import argparse
import copy
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from alpamayo_r1.data.pai_utils import PhysicalAIAVDatasetLocalInterface
from run_a3_inference_pilot import (
    EventLogger,
    load_model_and_processor,
    now_kst,
    prepare_offline_env,
    run_one_clip,
    set_seed,
    write_jsonl,
)
from run_a4_sliding_window_smoke import (
    write_smoke_video,
    window_key_prefix,
)


DATASET_ROOT = Path("/data/datasets/physical_ai_av")
MANIFEST_PATH = Path(
    "docs/artifacts/a4_visualization/2026-06-08-summary/a4-target-windows-100ms.jsonl"
)
OUTPUT_ROOT = Path("experiments/a4_visualization/2026-06-08-a4-demo/target-full-100ms")
LOG_DIR = Path("docs/logs")
RUN_NAME = "2026-06-08-a4-target-full-100ms"
MODEL_ID = "nvidia/Alpamayo-R1-10B"
PROCESSOR_ID = "Qwen/Qwen3-VL-2B-Instruct"
MAX_MEMORY = "23GiB"
TOP_P = 0.98
TEMPERATURE = 0.6
MAX_GENERATION_LENGTH = 256
VIDEO_FPS = 10
COMPLETED_INFERENCE_STATUSES = {"complete", "complete_with_failures"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker-name", required=True)
    parser.add_argument("--clip-ids", nargs="+")
    parser.add_argument("--chunk-ids", type=int, nargs="+")
    parser.add_argument("--manifest-path", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--log-dir", type=Path, default=LOG_DIR)
    parser.add_argument("--run-name", default=RUN_NAME)
    parser.add_argument("--video-fps", type=int, default=VIDEO_FPS)
    parser.add_argument("--cuda-device", type=int, default=0)
    parser.add_argument("--skip-video", action="store_true")
    parser.add_argument("--continue-on-failure", action="store_true")
    return parser.parse_args()


def read_manifest(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def select_manifest_rows(
    manifest_rows: list[dict[str, Any]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    if args.clip_ids:
        clip_ids = set(args.clip_ids)
        return [row for row in manifest_rows if row["clip_id"] in clip_ids]
    if args.chunk_ids:
        chunk_ids = set(args.chunk_ids)
        return [row for row in manifest_rows if int(row["chunk_id"]) in chunk_ids]
    raise ValueError("Either --clip-ids or --chunk-ids must be provided.")


def make_row_args(
    base_args: argparse.Namespace,
    manifest_row: dict[str, Any],
) -> argparse.Namespace:
    row_args = copy.copy(base_args)
    row_args.t0_us = int(manifest_row["t0_us"])
    row_args.chunk_ids = [int(manifest_row["chunk_id"])]
    row_args.clip_ids = [manifest_row["clip_id"]]
    row_args.seed = int(manifest_row["seed"])
    row_args.num_traj_samples = int(manifest_row["num_traj_samples"])
    row_args.num_traj_sets = int(manifest_row["num_traj_sets"])
    row_args.top_p = TOP_P
    row_args.temperature = TEMPERATURE
    row_args.max_generation_length = MAX_GENERATION_LENGTH
    row_args.max_memory = MAX_MEMORY
    row_args.model_id = MODEL_ID
    row_args.processor_id = PROCESSOR_ID
    row_args.allow_download = False
    return row_args


def remap_arrays(
    *,
    row: dict[str, Any],
    arrays: dict[str, np.ndarray],
    manifest_row: dict[str, Any],
) -> dict[str, np.ndarray]:
    if row.get("status") != "success":
        return {}
    old_keys = row.get("output_npz_keys", {})
    key_prefix = window_key_prefix(
        row["clip_id"],
        int(manifest_row["clip_window_index"]),
        int(row["t0_us"]),
    )
    remapped: dict[str, np.ndarray] = {}
    new_keys: dict[str, str] = {}
    for semantic_name, old_key in old_keys.items():
        new_key = f"{key_prefix}__{semantic_name}"
        new_keys[semantic_name] = new_key
        remapped[new_key] = arrays[old_key]
    row["output_npz_keys"] = new_keys
    return remapped


def normalize_failure_reason(row: dict[str, Any]) -> None:
    if row.get("status") != "failed":
        return
    failure_message = str(row.get("failure_message") or "").lower()
    if "requested timestamps must be within the range of timestamps" in failure_message:
        row["failure_reason"] = "invalid_window_timestamp"


def read_json_if_valid(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def existing_inference_output_state(clip_output_dir: Path) -> dict[str, Any]:
    summary_path = clip_output_dir / "run_summary.json"
    summary = read_json_if_valid(summary_path)
    if summary is None:
        return {
            "complete": False,
            "reason": "missing_or_invalid_run_summary",
            "run_summary": str(summary_path),
        }

    completion_status = summary.get("completion_status")
    if completion_status not in COMPLETED_INFERENCE_STATUSES:
        return {
            "complete": False,
            "reason": "incomplete_summary_status",
            "completion_status": completion_status,
            "run_summary": str(summary_path),
        }

    outputs = summary.get("outputs") or {}
    results_path = Path(outputs.get("jsonl") or clip_output_dir / "results.jsonl")
    predictions_output = outputs.get("npz")
    predictions_path = Path(predictions_output) if predictions_output else clip_output_dir / "predictions.npz"
    success_count = int(summary.get("success") or 0)
    predictions_required = success_count > 0
    if not results_path.exists():
        return {
            "complete": False,
            "reason": "missing_results_jsonl",
            "completion_status": completion_status,
            "run_summary": str(summary_path),
            "results_jsonl": str(results_path),
        }
    if predictions_required and not predictions_path.exists():
        return {
            "complete": False,
            "reason": "missing_predictions_npz",
            "completion_status": completion_status,
            "run_summary": str(summary_path),
            "predictions_npz": str(predictions_path),
        }

    return {
        "complete": True,
        "reason": "existing_complete_inference_output",
        "completion_status": completion_status,
        "run_summary": str(summary_path),
        "results_jsonl": str(results_path),
        "predictions_npz": str(predictions_path) if predictions_required else None,
        "expected_windows": summary.get("expected_windows"),
        "processed_windows": summary.get("processed_windows"),
        "success": summary.get("success"),
        "failed": summary.get("failed"),
        "outputs": outputs,
    }


def write_clip_outputs(
    *,
    clip_output_dir: Path,
    rows: list[dict[str, Any]],
    arrays: dict[str, np.ndarray],
    avdi: PhysicalAIAVDatasetLocalInterface,
    skip_video: bool,
    video_fps: int,
) -> dict[str, str | None]:
    clip_output_dir.mkdir(parents=True, exist_ok=True)
    results_jsonl = clip_output_dir / "results.jsonl"
    predictions_npz = clip_output_dir / "predictions.npz"
    video_mp4 = clip_output_dir / "demo.mp4"
    manifest_json = clip_output_dir / "video_manifest.json"

    write_jsonl(results_jsonl, rows)
    if arrays:
        np.savez_compressed(predictions_npz, **arrays)

    video_path: str | None = None
    manifest_path: str | None = None
    if arrays and not skip_video:
        video_manifest = write_smoke_video(
            output_path=video_mp4,
            rows=rows,
            avdi=avdi,
            predictions=arrays,
            fps=video_fps,
        )
        manifest_json.write_text(
            json.dumps(video_manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        write_jsonl(results_jsonl, rows)
        video_path = str(video_mp4)
        manifest_path = str(manifest_json)

    return {
        "jsonl": str(results_jsonl),
        "npz": str(predictions_npz) if arrays else None,
        "video": video_path,
        "video_manifest": manifest_path,
    }


def write_clip_summary(
    *,
    clip_output_dir: Path,
    clip_id: str,
    rows: list[dict[str, Any]],
    expected_windows: int,
    outputs: dict[str, str | None],
    runtime_sec: float,
    run_name: str,
) -> None:
    success_rows = [row for row in rows if row.get("status") == "success"]
    failed_rows = [row for row in rows if row.get("status") == "failed"]
    runtimes = [row["runtime_sec"] for row in success_rows if row.get("runtime_sec") is not None]
    peak_vram = [
        row["peak_vram_mib"] for row in success_rows if row.get("peak_vram_mib") is not None
    ]
    completion_status = "complete"
    if len(rows) < expected_windows:
        completion_status = "partial"
    elif failed_rows:
        completion_status = "complete_with_failures"
    summary = {
        "run_id": run_name,
        "clip_id": clip_id,
        "expected_windows": expected_windows,
        "processed_windows": len(rows),
        "completion_status": completion_status,
        "windows": len(rows),
        "success": len(success_rows),
        "failed": len(failed_rows),
        "runtime_sec": round(runtime_sec, 3),
        "runtime_sec_per_window": {
            "mean": round(float(np.mean(runtimes)), 3) if runtimes else None,
            "max": round(float(np.max(runtimes)), 3) if runtimes else None,
        },
        "peak_vram_mib": max(peak_vram) if peak_vram else None,
        "outputs": outputs,
        "metric_caveat": "num_traj_samples=1; minADE is single-sample ADE.",
        "validation_scope": "open-loop visualization/demo only.",
    }
    (clip_output_dir / "run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.output_root.mkdir(parents=True, exist_ok=True)
    offline_env = prepare_offline_env(False)
    set_seed(42)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    manifest_rows = select_manifest_rows(read_manifest(args.manifest_path), args)
    if not manifest_rows:
        raise ValueError(
            f"No manifest rows selected for worker={args.worker_name}, "
            f"clip_ids={args.clip_ids}, chunk_ids={args.chunk_ids}"
        )
    logger = EventLogger(args.log_dir / f"{args.run_name}-{args.worker_name}.log")
    selected_clip_ids = list(dict.fromkeys(row["clip_id"] for row in manifest_rows))
    selected_chunk_ids = sorted({int(row["chunk_id"]) for row in manifest_rows})
    pending_manifest_rows: list[dict[str, Any]] = []
    pending_clip_ids: list[str] = []
    skipped_outputs: list[dict[str, Any]] = []
    for clip_id in selected_clip_ids:
        clip_rows = [row for row in manifest_rows if row["clip_id"] == clip_id]
        output_state = existing_inference_output_state(args.output_root / clip_id)
        if output_state["complete"]:
            skipped = {
                "clip_id": clip_id,
                "expected_windows": len(clip_rows),
                "skip_reason": output_state["reason"],
                "completion_status": output_state.get("completion_status"),
                "processed_windows": output_state.get("processed_windows"),
                "success": output_state.get("success"),
                "failed": output_state.get("failed"),
                "outputs": output_state.get("outputs"),
            }
            skipped_outputs.append(skipped)
            logger.write({"event": "clip_skipped_existing_output", **skipped})
            continue
        pending_clip_ids.append(clip_id)
        pending_manifest_rows.extend(clip_rows)

    logger.write(
        {
            "event": "a4_clip_worker_start",
            "run_started": now_kst(),
            "worker_name": args.worker_name,
            "selected_clip_ids": selected_clip_ids,
            "selected_chunk_ids": selected_chunk_ids,
            "pending_clip_ids": pending_clip_ids,
            "pending_chunk_ids": sorted({int(row["chunk_id"]) for row in pending_manifest_rows}),
            "skipped_existing_output_clips": len(skipped_outputs),
            "manifest_path": str(args.manifest_path),
            "output_root": str(args.output_root),
            "windows": len(manifest_rows),
            "pending_windows": len(pending_manifest_rows),
            "offline": offline_env,
        }
    )

    worker_start = time.perf_counter()
    if not pending_manifest_rows:
        worker_summary = {
            "run_id": args.run_name,
            "worker_name": args.worker_name,
            "selected_clip_ids": selected_clip_ids,
            "clip_ids": [],
            "chunk_ids": [],
            "runtime_sec": round(time.perf_counter() - worker_start, 3),
            "outputs": [],
            "skipped_outputs": skipped_outputs,
        }
        (args.output_root / f"{args.worker_name}_summary.json").write_text(
            json.dumps(worker_summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.write({"event": "a4_clip_worker_finished", **worker_summary})
        logger.close()
        return

    manifest_rows = pending_manifest_rows
    clip_ids = pending_clip_ids
    chunk_ids = sorted({int(row["chunk_id"]) for row in manifest_rows})
    avdi = PhysicalAIAVDatasetLocalInterface(DATASET_ROOT, chunk_ids=chunk_ids)

    model_args = make_row_args(args, manifest_rows[0])
    model, processor, runtime_config = load_model_and_processor(model_args)
    logger.write({"event": "model_loaded", "runtime_config": runtime_config})

    worker_outputs: list[dict[str, Any]] = []
    for clip_id in clip_ids:
        clip_rows = [row for row in manifest_rows if row["clip_id"] == clip_id]
        clip_start = time.perf_counter()
        output_rows: list[dict[str, Any]] = []
        output_arrays: dict[str, np.ndarray] = {}

        for manifest_row in clip_rows:
            row_args = make_row_args(args, manifest_row)
            set_seed(row_args.seed)
            row, arrays = run_one_clip(
                args=row_args,
                avdi=avdi,
                model=model,
                processor=processor,
                clip_id=clip_id,
                seed=row_args.seed,
                run_id=args.run_name,
                write_arrays=True,
            )
            normalize_failure_reason(row)
            row.update(
                {
                    "global_window_index": manifest_row["global_window_index"],
                    "clip_window_index": manifest_row["clip_window_index"],
                    "window_index": manifest_row["clip_window_index"],
                    "stride_us": manifest_row["stride_us"],
                    "worker_name": args.worker_name,
                }
            )
            output_arrays.update(remap_arrays(row=row, arrays=arrays, manifest_row=manifest_row))
            output_rows.append(row)
            logger.write(
                {
                    "event": "window_done",
                    "clip_id": clip_id,
                    "clip_window_index": row["clip_window_index"],
                    "t0_us": row["t0_us"],
                    "status": row["status"],
                    "runtime_sec": row.get("runtime_sec"),
                    "minade": row.get("minade"),
                    "failure_reason": row.get("failure_reason"),
                }
            )
            if row["status"] == "failed" and not args.continue_on_failure:
                break

        clip_output_dir = args.output_root / clip_id
        outputs = write_clip_outputs(
            clip_output_dir=clip_output_dir,
            rows=output_rows,
            arrays=output_arrays,
            avdi=avdi,
            skip_video=args.skip_video,
            video_fps=args.video_fps,
        )
        clip_runtime_sec = time.perf_counter() - clip_start
        write_clip_summary(
            clip_output_dir=clip_output_dir,
            clip_id=clip_id,
            rows=output_rows,
            expected_windows=len(clip_rows),
            outputs=outputs,
            runtime_sec=clip_runtime_sec,
            run_name=args.run_name,
        )
        failed_count = sum(row.get("status") == "failed" for row in output_rows)
        if len(output_rows) < len(clip_rows):
            completion_status = "partial"
        elif failed_count:
            completion_status = "complete_with_failures"
        else:
            completion_status = "complete"
        worker_outputs.append(
            {
                "clip_id": clip_id,
                "expected_windows": len(clip_rows),
                "processed_windows": len(output_rows),
                "completion_status": completion_status,
                "windows": len(output_rows),
                "success": sum(row.get("status") == "success" for row in output_rows),
                "failed": failed_count,
                "runtime_sec": round(clip_runtime_sec, 3),
                "outputs": outputs,
            }
        )
        logger.write({"event": "clip_done", **worker_outputs[-1]})

    worker_summary = {
        "run_id": args.run_name,
        "worker_name": args.worker_name,
        "selected_clip_ids": selected_clip_ids,
        "clip_ids": clip_ids,
        "chunk_ids": chunk_ids,
        "runtime_sec": round(time.perf_counter() - worker_start, 3),
        "outputs": worker_outputs,
        "skipped_outputs": skipped_outputs,
    }
    (args.output_root / f"{args.worker_name}_summary.json").write_text(
        json.dumps(worker_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.write({"event": "a4_clip_worker_finished", **worker_summary})
    logger.close()


if __name__ == "__main__":
    main()
