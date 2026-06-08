# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

"""Create a Track A4 clip/window manifest for sharded inference."""

from __future__ import annotations

import argparse
import io
import json
import os
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from alpamayo_r1.data.pai_utils import PhysicalAIAVDatasetLocalInterface


DEFAULT_DATASET_ROOT = Path("/data/datasets/physical_ai_av")
DEFAULT_OUTPUT_PATH = Path(
    "docs/artifacts/a4_visualization/2026-06-08-summary/a4-target-windows-100ms.jsonl"
)
DEFAULT_CLIP_IDS = [
    "ac321da3-3848-4736-a9c2-053be0bea770",
    "ac7ac12e-7371-47ec-987d-61e0b3c7693f",
    "b8fa0288-f799-4443-ba62-4601c45fe133",
    "c23d0ac1-fe93-4f25-bf71-198ccec5c190",
    "cb656c5d-7520-4cc2-9e87-889f061fc6cb",
]
DEFAULT_ALL_LOCAL_CHUNK_IDS = [156, 297, 727, 1843, 1864, 1875, 2129, 2281, 3119, 3135]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--chunk-ids", type=int, nargs="+", default=[3119])
    parser.add_argument("--clip-ids", nargs="+", default=DEFAULT_CLIP_IDS)
    parser.add_argument("--all-local", action="store_true")
    parser.add_argument("--stride-us", type=int, default=100_000)
    parser.add_argument("--align-offset-us", type=int, default=100_000)
    parser.add_argument("--start-t0-us", type=int)
    parser.add_argument("--end-t0-us", type=int)
    parser.add_argument("--max-windows-per-clip", type=int, default=0)
    parser.add_argument("--history-us", type=int, default=1_600_000)
    parser.add_argument("--future-us", type=int, default=6_400_000)
    parser.add_argument("--image-frame-us", type=int, default=100_000)
    parser.add_argument("--num-image-frames", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-traj-samples", type=int, default=1)
    parser.add_argument("--num-traj-sets", type=int, default=1)
    return parser.parse_args()


def read_egomotion_timestamps(
    avdi: PhysicalAIAVDatasetLocalInterface,
    dataset_root: Path,
    clip_id: str,
) -> np.ndarray:
    feature = "egomotion"
    chunk = avdi.get_clip_chunk(clip_id)
    chunk_filename = avdi.features.get_chunk_feature_filename(chunk, feature)
    clip_files = avdi.features.get_clip_files_in_zip(clip_id, feature)
    with zipfile.ZipFile(os.path.join(dataset_root, chunk_filename), "r") as zf:
        egomotion_bytes = io.BytesIO(zf.read(clip_files["egomotion"]))
        egomotion_df = pd.read_parquet(egomotion_bytes)
    return egomotion_df["timestamp"].to_numpy(dtype=np.int64)


def camera_features(avdi: PhysicalAIAVDatasetLocalInterface) -> list[str]:
    return [
        avdi.features.CAMERA.CAMERA_CROSS_LEFT_120FOV,
        avdi.features.CAMERA.CAMERA_FRONT_WIDE_120FOV,
        avdi.features.CAMERA.CAMERA_CROSS_RIGHT_120FOV,
        avdi.features.CAMERA.CAMERA_FRONT_TELE_30FOV,
    ]


def read_camera_timestamps(
    avdi: PhysicalAIAVDatasetLocalInterface,
    dataset_root: Path,
    clip_id: str,
    feature: str,
) -> np.ndarray:
    chunk = avdi.get_clip_chunk(clip_id)
    chunk_filename = avdi.features.get_chunk_feature_filename(chunk, feature)
    clip_files = avdi.features.get_clip_files_in_zip(clip_id, feature)
    with zipfile.ZipFile(os.path.join(dataset_root, chunk_filename), "r") as zf:
        frame_timestamp_bytes = io.BytesIO(zf.read(clip_files["frame_timestamps"]))
        frame_timestamps = pd.read_parquet(frame_timestamp_bytes)["timestamp"]
    return frame_timestamps.to_numpy(dtype=np.int64)


def align_up(value: int, stride: int, offset: int) -> int:
    if value <= offset:
        return offset
    steps = int(np.ceil((value - offset) / stride))
    return offset + steps * stride


def build_t0_list(
    *,
    egomotion_timestamps: np.ndarray,
    camera_timestamp_sets: list[np.ndarray],
    stride_us: int,
    align_offset_us: int,
    history_us: int,
    future_us: int,
    image_frame_us: int,
    num_image_frames: int,
    start_t0_us: int | None,
    end_t0_us: int | None,
    max_windows: int,
) -> list[int]:
    egomotion_start = int(egomotion_timestamps.min())
    egomotion_end = int(egomotion_timestamps.max())
    camera_start = max(int(timestamps.min()) for timestamps in camera_timestamp_sets)
    camera_end = min(int(timestamps.max()) for timestamps in camera_timestamp_sets)
    image_history_us = (num_image_frames - 1) * image_frame_us

    lower_bound = max(
        history_us + 1,
        egomotion_start + history_us,
        camera_start + image_history_us,
    )
    upper_bound = min(
        egomotion_end - future_us,
        camera_end,
    )
    if start_t0_us is not None:
        lower_bound = max(lower_bound, start_t0_us)
    if end_t0_us is not None:
        upper_bound = min(upper_bound, end_t0_us)

    first = align_up(lower_bound, stride_us, align_offset_us)
    if first > upper_bound:
        return []
    values = list(range(first, upper_bound + 1, stride_us))
    if max_windows > 0:
        values = values[:max_windows]
    return values


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    args = parse_args()
    if args.all_local and args.chunk_ids == [3119]:
        args.chunk_ids = DEFAULT_ALL_LOCAL_CHUNK_IDS
    avdi = PhysicalAIAVDatasetLocalInterface(args.dataset_root, chunk_ids=args.chunk_ids)
    clip_ids = avdi.get_all_clip_ids() if args.all_local else args.clip_ids
    rows: list[dict[str, Any]] = []
    global_index = 0
    skipped: list[dict[str, Any]] = []
    for clip_id in clip_ids:
        try:
            egomotion_timestamps = read_egomotion_timestamps(avdi, args.dataset_root, clip_id)
            camera_timestamp_sets = [
                read_camera_timestamps(avdi, args.dataset_root, clip_id, feature)
                for feature in camera_features(avdi)
            ]
            chunk_id = int(avdi.get_clip_chunk(clip_id))
            t0_us_list = build_t0_list(
                egomotion_timestamps=egomotion_timestamps,
                camera_timestamp_sets=camera_timestamp_sets,
                stride_us=args.stride_us,
                align_offset_us=args.align_offset_us,
                history_us=args.history_us,
                future_us=args.future_us,
                image_frame_us=args.image_frame_us,
                num_image_frames=args.num_image_frames,
                start_t0_us=args.start_t0_us,
                end_t0_us=args.end_t0_us,
                max_windows=args.max_windows_per_clip,
            )
        except Exception as exc:
            skipped.append(
                {
                    "clip_id": clip_id,
                    "failure_type": type(exc).__name__,
                    "failure_message": str(exc),
                }
            )
            continue
        for clip_window_index, t0_us in enumerate(t0_us_list):
            rows.append(
                {
                    "global_window_index": global_index,
                    "clip_id": clip_id,
                    "chunk_id": chunk_id,
                    "clip_window_index": clip_window_index,
                    "t0_us": t0_us,
                    "stride_us": args.stride_us,
                    "seed": args.seed,
                    "num_traj_samples": args.num_traj_samples,
                    "num_traj_sets": args.num_traj_sets,
                }
            )
            global_index += 1

    write_jsonl(args.output_path, rows)
    print(
        json.dumps(
            {
                "output_path": str(args.output_path),
                "total_windows": len(rows),
                "clips": len(clip_ids),
                "clips_with_windows": len({row["clip_id"] for row in rows}),
                "chunks": args.chunk_ids,
                "stride_us": args.stride_us,
                "max_windows_per_clip": args.max_windows_per_clip or None,
                "skipped_clips": len(skipped),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
