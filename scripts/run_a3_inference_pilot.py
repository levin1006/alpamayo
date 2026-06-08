# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

"""Run the Track A3 local PAI inference pilot.

This is the reproducible script form of the 2026-06-08 A3 pilot. It loads a
small local PAI clip set, runs Alpamayo-R1 inference, writes JSONL metrics, and
stores trajectory tensors for later A4 visualization.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import random
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import AutoProcessor

from alpamayo_r1 import helper
from alpamayo_r1.data.pai_utils import PhysicalAIAVDatasetLocalInterface
from alpamayo_r1.load_physical_aiavdataset import load_physical_aiavdataset
from alpamayo_r1.models.alpamayo_r1 import AlpamayoR1


KST = timezone(timedelta(hours=9))
DEFAULT_DATASET_ROOT = Path("/data/datasets/physical_ai_av")
DEFAULT_OUTPUT_ROOT = Path("docs/artifacts/a3_inference")
DEFAULT_LOG_DIR = Path("docs/logs")
DEFAULT_CHUNK_IDS = [3119]
DEFAULT_CLIPS = [
    "ac321da3-3848-4736-a9c2-053be0bea770",
    "ac7ac12e-7371-47ec-987d-61e0b3c7693f",
    "b8fa0288-f799-4443-ba62-4601c45fe133",
    "c23d0ac1-fe93-4f25-bf71-198ccec5c190",
    "cb656c5d-7520-4cc2-9e87-889f061fc6cb",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--pilot-name", default="2026-06-08-pilot")
    parser.add_argument("--seed-check-name", default="2026-06-08-seed-check")
    parser.add_argument("--chunk-ids", type=int, nargs="+", default=DEFAULT_CHUNK_IDS)
    parser.add_argument("--clip-ids", nargs="+", default=DEFAULT_CLIPS)
    parser.add_argument("--t0-us", type=int, default=5_100_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--seed-check-seeds", type=int, nargs="+", default=[42, 43, 44])
    parser.add_argument("--num-traj-samples", type=int, default=1)
    parser.add_argument("--num-traj-sets", type=int, default=1)
    parser.add_argument("--top-p", type=float, default=0.98)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--max-generation-length", type=int, default=256)
    parser.add_argument("--cuda-device", type=int, default=0)
    parser.add_argument("--max-memory", default="23GiB")
    parser.add_argument("--model-id", default="nvidia/Alpamayo-R1-10B")
    parser.add_argument("--processor-id", default=helper.BASE_PROCESSOR_NAME)
    parser.add_argument("--skip-seed-check", action="store_true")
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow Hugging Face network access. Default is offline/cache-only.",
    )
    return parser.parse_args()


class EventLogger:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._file = path.open("w", encoding="utf-8")

    def write(self, event: dict[str, Any]) -> None:
        line = json.dumps(event, ensure_ascii=False)
        print(line, flush=True)
        self._file.write(line + "\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()


def now_kst() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def classify_failure(exc: BaseException) -> str:
    msg = str(exc).lower()
    name = type(exc).__name__.lower()
    if "out of memory" in msg or ("cuda" in msg and "memory" in msg):
        return "GPU memory"
    if "no module named" in msg or "importerror" in name or "modulenotfounderror" in name:
        return "dependency"
    if "shape" in msg or "unexpected" in msg or "t0_us" in msg or "not in features_df" in msg:
        return "data contract"
    if "json" in msg or "npz" in msg or "serializ" in msg:
        return "output schema"
    return "model/runtime"


def prepare_offline_env(allow_download: bool) -> dict[str, str | None]:
    if not allow_download:
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
    return {
        "TRANSFORMERS_OFFLINE": os.environ.get("TRANSFORMERS_OFFLINE"),
        "HF_HUB_OFFLINE": os.environ.get("HF_HUB_OFFLINE"),
    }


def load_model_and_processor(args: argparse.Namespace) -> tuple[AlpamayoR1, Any, dict[str, Any]]:
    local_files_only = not args.allow_download
    model_load_start = time.perf_counter()
    model = AlpamayoR1.from_pretrained(
        args.model_id,
        dtype=torch.bfloat16,
        device_map={"": args.cuda_device},
        max_memory={args.cuda_device: args.max_memory},
        local_files_only=local_files_only,
    )
    model.eval()
    processor = AutoProcessor.from_pretrained(
        args.processor_id,
        min_pixels=helper.MIN_PIXELS,
        max_pixels=helper.MAX_PIXELS,
        local_files_only=local_files_only,
    )
    processor.tokenizer = model.tokenizer
    runtime_config = {
        "model_id": args.model_id,
        "processor_id": args.processor_id,
        "model_class": type(model).__name__,
        "dtype": str(next(model.parameters()).dtype),
        "device_map": {"": args.cuda_device},
        "max_memory": {args.cuda_device: args.max_memory},
        "attn_implementation": getattr(model.config, "attn_implementation", None),
        "tokens_per_history_traj": getattr(model.config, "tokens_per_history_traj", None),
        "tokens_per_future_traj": getattr(model.config, "tokens_per_future_traj", None),
        "traj_vocab_size": getattr(model.config, "traj_vocab_size", None),
        "vlm_name_or_path": getattr(model.config, "vlm_name_or_path", None),
        "model_load_sec": round(time.perf_counter() - model_load_start, 3),
    }
    return model, processor, runtime_config


def build_model_inputs(processor: Any, data: dict[str, Any]) -> dict[str, Any]:
    messages = helper.create_message(data["image_frames"].flatten(0, 1))
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=False,
        continue_final_message=True,
        return_dict=True,
        return_tensors="pt",
    )
    return {
        "tokenized_data": inputs,
        "ego_history_xyz": data["ego_history_xyz"],
        "ego_history_rot": data["ego_history_rot"],
    }


def compute_single_sample_metrics(
    pred_xyz: torch.Tensor,
    gt_future_xyz: torch.Tensor,
) -> tuple[float | None, float, np.ndarray]:
    pred_xyz_cpu = pred_xyz.detach().float().cpu()
    gt_xy = gt_future_xyz.detach().float().cpu()[0, 0, :, :2].numpy().T
    pred_xy = pred_xyz_cpu.numpy()[0, 0, :, :, :2].transpose(0, 2, 1)
    per_sample_ade = np.linalg.norm(pred_xy - gt_xy[None, ...], axis=1).mean(-1)
    minade = float(per_sample_ade.min())
    ade = float(per_sample_ade[0]) if len(per_sample_ade) == 1 else None
    return ade, minade, per_sample_ade


def run_one_clip(
    *,
    args: argparse.Namespace,
    avdi: PhysicalAIAVDatasetLocalInterface,
    model: AlpamayoR1,
    processor: Any,
    clip_id: str,
    seed: int,
    run_id: str,
    write_arrays: bool,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    row: dict[str, Any] = {
        "run_id": run_id,
        "clip_id": clip_id,
        "chunk_id": int(avdi.get_clip_chunk(clip_id)),
        "t0_us": args.t0_us,
        "seed": seed,
        "num_traj_samples": args.num_traj_samples,
        "num_traj_sets": args.num_traj_sets,
        "status": "started",
        "failure_reason": None,
    }
    arrays: dict[str, np.ndarray] = {}
    clip_start = time.perf_counter()
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    try:
        data_load_start = time.perf_counter()
        data = load_physical_aiavdataset(
            clip_id,
            t0_us=args.t0_us,
            avdi=avdi,
            maybe_stream=False,
        )
        data_load_sec = time.perf_counter() - data_load_start
        model_inputs = build_model_inputs(processor, data)
        model_inputs = helper.to_device(copy.deepcopy(model_inputs), "cuda")

        set_seed(seed)
        inference_start = time.perf_counter()
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
            pred_xyz, pred_rot, extra = model.sample_trajectories_from_data_with_vlm_rollout(
                data=model_inputs,
                top_p=args.top_p,
                temperature=args.temperature,
                num_traj_samples=args.num_traj_samples,
                num_traj_sets=args.num_traj_sets,
                max_generation_length=args.max_generation_length,
                return_extra=True,
            )
        inference_sec = time.perf_counter() - inference_start
        pred_xyz_cpu = pred_xyz.detach().float().cpu()
        pred_rot_cpu = pred_rot.detach().float().cpu()
        gt_future_cpu = data["ego_future_xyz"].detach().float().cpu()
        ade, minade, _ = compute_single_sample_metrics(pred_xyz, data["ego_future_xyz"])
        peak_vram_mib = None
        if torch.cuda.is_available():
            peak_vram_mib = round(torch.cuda.max_memory_allocated() / (1024**2), 1)

        row.update(
            {
                "status": "success",
                "data_load_sec": round(data_load_sec, 3),
                "inference_sec": round(inference_sec, 3),
                "runtime_sec": round(time.perf_counter() - clip_start, 3),
                "peak_vram_mib": peak_vram_mib,
                "image_frames_shape": list(data["image_frames"].shape),
                "ego_history_xyz_shape": list(data["ego_history_xyz"].shape),
                "ego_future_xyz_shape": list(data["ego_future_xyz"].shape),
                "pred_xyz_shape": list(pred_xyz_cpu.shape),
                "pred_rot_shape": list(pred_rot_cpu.shape),
                "ade": ade,
                "minade": minade,
                "minade_interpretation": (
                    "num_traj_samples=1; minADE is equivalent to single-sample ADE "
                    "for this run"
                ),
                "coc_text": str(extra["cot"][0, 0, 0]) if "cot" in extra else None,
            }
        )
        if write_arrays:
            row["output_npz_keys"] = {
                "pred_xyz": f"{clip_id}__pred_xyz",
                "pred_rot": f"{clip_id}__pred_rot",
                "ego_history_xyz": f"{clip_id}__ego_history_xyz",
                "ego_future_xyz": f"{clip_id}__ego_future_xyz",
                "absolute_timestamps": f"{clip_id}__absolute_timestamps",
            }
            arrays[f"{clip_id}__pred_xyz"] = pred_xyz_cpu.numpy()
            arrays[f"{clip_id}__pred_rot"] = pred_rot_cpu.numpy()
            arrays[f"{clip_id}__ego_history_xyz"] = data["ego_history_xyz"].float().cpu().numpy()
            arrays[f"{clip_id}__ego_future_xyz"] = gt_future_cpu.numpy()
            arrays[f"{clip_id}__absolute_timestamps"] = data["absolute_timestamps"].cpu().numpy()
    except BaseException as exc:
        row.update(
            {
                "status": "failed",
                "failure_reason": classify_failure(exc),
                "failure_type": type(exc).__name__,
                "failure_message": str(exc),
                "runtime_sec": round(time.perf_counter() - clip_start, 3),
            }
        )
    return row, arrays


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_pilot(
    args: argparse.Namespace,
    avdi: PhysicalAIAVDatasetLocalInterface,
    model: AlpamayoR1,
    processor: Any,
    runtime_config: dict[str, Any],
    offline_env: dict[str, str | None],
) -> None:
    run_id = f"a3-{args.pilot_name}"
    output_dir = args.output_root / args.pilot_name
    logger = EventLogger(args.log_dir / f"{args.pilot_name}.log")
    logger.write(
        {
            "event": "run_start",
            "run_started": now_kst(),
            "root": str(args.dataset_root),
            "chunk_ids": args.chunk_ids,
            "clips": args.clip_ids,
            "seed": args.seed,
            "num_traj_samples": args.num_traj_samples,
            "t0_us": args.t0_us,
            "offline": offline_env,
        }
    )
    logger.write({"event": "model_loaded", "runtime_config": runtime_config})

    rows: list[dict[str, Any]] = []
    arrays: dict[str, np.ndarray] = {}
    for clip_id in args.clip_ids:
        row, clip_arrays = run_one_clip(
            args=args,
            avdi=avdi,
            model=model,
            processor=processor,
            clip_id=clip_id,
            seed=args.seed,
            run_id=run_id,
            write_arrays=True,
        )
        rows.append(row)
        arrays.update(clip_arrays)
        logger.write(
            {
                "event": "clip_done",
                "clip_id": clip_id,
                "status": row["status"],
                "runtime_sec": row.get("runtime_sec"),
                "minade": row.get("minade"),
                "peak_vram_mib": row.get("peak_vram_mib"),
                "failure_reason": row.get("failure_reason"),
            }
        )

    write_jsonl(output_dir / "results.jsonl", rows)
    if arrays:
        np.savez_compressed(output_dir / "predictions.npz", **arrays)
    summary = {
        "run_id": run_id,
        "run_finished": now_kst(),
        "dataset_root": str(args.dataset_root),
        "chunk_ids": args.chunk_ids,
        "clip_selection": args.clip_ids,
        "t0_us": args.t0_us,
        "seed": args.seed,
        "num_traj_samples": args.num_traj_samples,
        "num_traj_sets": args.num_traj_sets,
        "runtime_config": runtime_config,
        "result_counts": {
            "total": len(rows),
            "success": sum(row["status"] == "success" for row in rows),
            "failed": sum(row["status"] == "failed" for row in rows),
        },
        "outputs": {
            "jsonl": str(output_dir / "results.jsonl"),
            "npz": str(output_dir / "predictions.npz") if arrays else None,
            "log": str(args.log_dir / f"{args.pilot_name}.log"),
        },
        "output_schema_version": "a3_pilot_v1",
    }
    (output_dir / "run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.write({"event": "run_finished", "summary": summary})
    logger.close()


def run_seed_check(
    args: argparse.Namespace,
    avdi: PhysicalAIAVDatasetLocalInterface,
    model: AlpamayoR1,
    processor: Any,
) -> None:
    run_id = f"a3-{args.seed_check_name}"
    output_dir = args.output_root / args.seed_check_name
    logger = EventLogger(args.log_dir / f"{args.seed_check_name}.log")
    clip_id = args.clip_ids[0]
    logger.write(
        {
            "event": "seed_check_start",
            "clip_id": clip_id,
            "seeds": args.seed_check_seeds,
            "num_traj_samples": args.num_traj_samples,
        }
    )
    rows: list[dict[str, Any]] = []
    for seed in args.seed_check_seeds:
        row, _ = run_one_clip(
            args=args,
            avdi=avdi,
            model=model,
            processor=processor,
            clip_id=clip_id,
            seed=seed,
            run_id=run_id,
            write_arrays=False,
        )
        rows.append(row)
        logger.write(
            {
                "event": "seed_done",
                "seed": seed,
                "status": row["status"],
                "minade": row.get("minade"),
                "runtime_sec": row.get("runtime_sec"),
                "peak_vram_mib": row.get("peak_vram_mib"),
                "failure_reason": row.get("failure_reason"),
            }
        )

    write_jsonl(output_dir / "results.jsonl", rows)
    summary = {
        "run_id": run_id,
        "run_finished": now_kst(),
        "dataset_root": str(args.dataset_root),
        "clip_id": clip_id,
        "chunk_ids": args.chunk_ids,
        "t0_us": args.t0_us,
        "seeds": args.seed_check_seeds,
        "num_traj_samples": args.num_traj_samples,
        "result_counts": {
            "total": len(rows),
            "success": sum(row["status"] == "success" for row in rows),
            "failed": sum(row["status"] == "failed" for row in rows),
        },
        "outputs": {
            "jsonl": str(output_dir / "results.jsonl"),
            "log": str(args.log_dir / f"{args.seed_check_name}.log"),
        },
    }
    (output_dir / "run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.write({"event": "seed_check_finished", "summary": summary})
    logger.close()


def main() -> None:
    args = parse_args()
    offline_env = prepare_offline_env(args.allow_download)
    set_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    avdi = PhysicalAIAVDatasetLocalInterface(args.dataset_root, chunk_ids=args.chunk_ids)
    model, processor, runtime_config = load_model_and_processor(args)
    run_pilot(args, avdi, model, processor, runtime_config, offline_env)
    if not args.skip_seed_check:
        run_seed_check(args, avdi, model, processor)


if __name__ == "__main__":
    main()
