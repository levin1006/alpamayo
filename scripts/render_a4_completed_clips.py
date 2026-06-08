# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

"""Render completed A4 clip outputs without running model inference."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from alpamayo_r1.data.pai_utils import PhysicalAIAVDatasetLocalInterface
from run_a3_inference_pilot import EventLogger, now_kst, write_jsonl
from run_a4_sliding_window_smoke import load_npz_arrays, read_jsonl, write_smoke_video


DATASET_ROOT = Path("/data/datasets/physical_ai_av")
MANIFEST_PATH = Path(
    "docs/artifacts/a4_visualization/2026-06-08-summary/a4-all-local-windows-100ms.jsonl"
)
OUTPUT_ROOT = Path("experiments/a4_visualization/2026-06-08-a4-demo/all-local-100ms")
LOG_DIR = Path("docs/logs")
RUN_NAME = "2026-06-08-a4-all-local-100ms"
VIDEO_FPS = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DATASET_ROOT)
    parser.add_argument("--manifest-path", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--log-dir", type=Path, default=LOG_DIR)
    parser.add_argument("--run-name", default=RUN_NAME)
    parser.add_argument("--fps", type=int, default=VIDEO_FPS)
    parser.add_argument("--poll-sec", type=int, default=60)
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def read_manifest_clips(path: Path) -> list[str]:
    if not path.exists():
        return []
    clip_ids: list[str] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        clip_id = row["clip_id"]
        if clip_id not in seen:
            seen.add(clip_id)
            clip_ids.append(clip_id)
    return clip_ids


def read_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    tmp_path = path.with_suffix(".tmp.json")
    tmp_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp_path.replace(path)


def should_render(summary: dict[str, Any], clip_dir: Path) -> bool:
    if summary.get("completion_status") != "complete":
        return False
    outputs = summary.get("outputs") or {}
    results_path = Path(outputs.get("jsonl") or clip_dir / "results.jsonl")
    predictions_path = Path(outputs.get("npz") or clip_dir / "predictions.npz")
    video_path = clip_dir / "demo.mp4"
    manifest_path = clip_dir / "video_manifest.json"
    return results_path.exists() and predictions_path.exists() and not (
        video_path.exists() and manifest_path.exists()
    )


def render_clip(
    *,
    args: argparse.Namespace,
    clip_dir: Path,
    summary: dict[str, Any],
) -> dict[str, Any]:
    outputs = summary.get("outputs") or {}
    results_path = Path(outputs.get("jsonl") or clip_dir / "results.jsonl")
    predictions_path = Path(outputs.get("npz") or clip_dir / "predictions.npz")
    video_path = clip_dir / "demo.mp4"
    manifest_path = clip_dir / "video_manifest.json"

    rows = read_jsonl(results_path)
    predictions = load_npz_arrays(predictions_path)
    chunk_ids = sorted({int(row["chunk_id"]) for row in rows if row.get("status") == "success"})
    avdi = PhysicalAIAVDatasetLocalInterface(args.dataset_root, chunk_ids=chunk_ids)

    video_manifest = write_smoke_video(
        output_path=video_path,
        rows=rows,
        avdi=avdi,
        predictions=predictions,
        fps=args.fps,
    )
    manifest_path.write_text(
        json.dumps(video_manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_jsonl(results_path, rows)

    outputs.update(
        {
            "jsonl": str(results_path),
            "npz": str(predictions_path),
            "video": str(video_path),
            "video_manifest": str(manifest_path),
        }
    )
    summary["outputs"] = outputs
    summary["render_status"] = "complete"
    summary["rendered_frames"] = len(video_manifest)
    write_summary(clip_dir / "run_summary.json", summary)
    return {
        "clip_id": summary.get("clip_id", clip_dir.name),
        "frames": len(video_manifest),
        "video": str(video_path),
        "manifest": str(manifest_path),
    }


def main() -> None:
    args = parse_args()
    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.output_root.mkdir(parents=True, exist_ok=True)
    logger = EventLogger(args.log_dir / f"{args.run_name}-render.log")
    logger.write(
        {
            "event": "a4_render_watcher_start",
            "run_started": now_kst(),
            "manifest_path": str(args.manifest_path),
            "output_root": str(args.output_root),
            "fps": args.fps,
        }
    )

    try:
        while True:
            clip_ids = read_manifest_clips(args.manifest_path)
            rendered = 0
            complete = 0
            pending = 0
            for clip_id in clip_ids:
                clip_dir = args.output_root / clip_id
                summary_path = clip_dir / "run_summary.json"
                summary = read_summary(summary_path)
                if summary is None:
                    pending += 1
                    continue
                if summary.get("completion_status") == "complete":
                    complete += 1
                if should_render(summary, clip_dir):
                    start = time.perf_counter()
                    try:
                        result = render_clip(args=args, clip_dir=clip_dir, summary=summary)
                        result["runtime_sec"] = round(time.perf_counter() - start, 3)
                        logger.write({"event": "clip_render_done", **result})
                        rendered += 1
                    except Exception as exc:
                        logger.write(
                            {
                                "event": "clip_render_failed",
                                "clip_id": clip_id,
                                "failure_type": type(exc).__name__,
                                "failure_message": str(exc),
                            }
                        )
            logger.write(
                {
                    "event": "render_poll",
                    "clips_total": len(clip_ids),
                    "clips_complete": complete,
                    "clips_pending": pending,
                    "clips_rendered_this_poll": rendered,
                }
            )
            if args.once or (clip_ids and complete == len(clip_ids)):
                break
            time.sleep(args.poll_sec)
    finally:
        logger.write({"event": "a4_render_watcher_finished", "run_finished": now_kst()})
        logger.close()


if __name__ == "__main__":
    main()
