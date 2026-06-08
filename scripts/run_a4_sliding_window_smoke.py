# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

"""Run the Track A4 1-clip sliding-window smoke.

This script reuses the A3 inference path, runs a small ordered list of `t0_us`
windows on one clip, and writes A4-friendly JSONL/NPZ/video artifacts.
"""

from __future__ import annotations

import argparse
import copy
import json
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch

from alpamayo_r1.data.pai_utils import PhysicalAIAVDatasetLocalInterface
from alpamayo_r1.load_physical_aiavdataset import load_physical_aiavdataset
from alpamayo_r1.visualization.viz import viz_waypoints_pai
from run_a3_inference_pilot import (
    EventLogger,
    load_model_and_processor,
    now_kst,
    prepare_offline_env,
    run_one_clip,
    set_seed,
    write_jsonl,
)
from visualize_a3_pilot import make_camera_panel, plot_bev_frame, put_wrapped_text, resize_rgb


DEFAULT_DATASET_ROOT = Path("/data/datasets/physical_ai_av")
DEFAULT_OUTPUT_DIR = Path(
    "experiments/a4_visualization/2026-06-08-a4-demo/smoke-c23d0ac1"
)
DEFAULT_SUMMARY_DIR = Path("docs/artifacts/a4_visualization/2026-06-08-summary")
DEFAULT_LOG_DIR = Path("docs/logs")
DEFAULT_CLIP_ID = "c23d0ac1-fe93-4f25-bf71-198ccec5c190"
DEFAULT_CHUNK_ID = 3119
DEFAULT_T0_US = [3_100_000, 4_100_000, 5_100_000, 6_100_000, 7_100_000]
BEV_PANEL_SIZE = (880, 620)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--summary-dir", type=Path, default=DEFAULT_SUMMARY_DIR)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--run-name", default="2026-06-08-a4-smoke-c23d0ac1")
    parser.add_argument("--results-jsonl", type=Path)
    parser.add_argument("--predictions-npz", type=Path)
    parser.add_argument("--clip-id", default=DEFAULT_CLIP_ID)
    parser.add_argument("--chunk-id", type=int, default=DEFAULT_CHUNK_ID)
    parser.add_argument("--t0-us-list", type=int, nargs="+", default=DEFAULT_T0_US)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-traj-samples", type=int, default=1)
    parser.add_argument("--num-traj-sets", type=int, default=1)
    parser.add_argument("--top-p", type=float, default=0.98)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--max-generation-length", type=int, default=256)
    parser.add_argument("--cuda-device", type=int, default=0)
    parser.add_argument("--max-memory", default="23GiB")
    parser.add_argument("--model-id", default="nvidia/Alpamayo-R1-10B")
    parser.add_argument("--processor-id", default="Qwen/Qwen3-VL-2B-Instruct")
    parser.add_argument("--fps", type=int, default=1)
    parser.add_argument("--skip-video", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--render-video-name", default="smoke_demo.mp4")
    parser.add_argument("--render-manifest-name", default="manifest.json")
    parser.add_argument("--continue-on-failure", action="store_true")
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow Hugging Face network access. Default is offline/cache-only.",
    )
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def load_npz_arrays(path: Path) -> dict[str, np.ndarray]:
    with np.load(path) as data:
        return {key: data[key] for key in data.files}


def infer_stride_us(t0_us_list: list[int]) -> int | None:
    if len(t0_us_list) < 2:
        return None
    strides = [right - left for left, right in zip(t0_us_list, t0_us_list[1:])]
    if len(set(strides)) == 1:
        return strides[0]
    return None


def make_window_args(args: argparse.Namespace, t0_us: int) -> argparse.Namespace:
    window_args = copy.copy(args)
    window_args.t0_us = t0_us
    window_args.chunk_ids = [args.chunk_id]
    window_args.clip_ids = [args.clip_id]
    return window_args


def window_key_prefix(clip_id: str, window_index: int, t0_us: int) -> str:
    return f"{clip_id}__w{window_index:02d}__t0_{t0_us}"


def remap_window_arrays(
    *,
    row: dict[str, Any],
    arrays: dict[str, np.ndarray],
    window_index: int,
) -> dict[str, np.ndarray]:
    if row.get("status") != "success":
        return {}
    old_keys = row.get("output_npz_keys", {})
    key_prefix = window_key_prefix(row["clip_id"], window_index, int(row["t0_us"]))
    new_keys: dict[str, str] = {}
    remapped: dict[str, np.ndarray] = {}
    for semantic_name, old_key in old_keys.items():
        new_key = f"{key_prefix}__{semantic_name}"
        new_keys[semantic_name] = new_key
        remapped[new_key] = arrays[old_key]
    row["output_npz_keys"] = new_keys
    return remapped


def rgb_frame_to_numpy(frame: torch.Tensor) -> np.ndarray:
    return frame.permute(1, 2, 0).cpu().numpy().astype(np.uint8)


def make_front_wide_trajectory_panel(
    *,
    image_frames: torch.Tensor,
    avdi: PhysicalAIAVDatasetLocalInterface,
    clip_id: str,
    gt_xyz: np.ndarray,
    pred_xyz: np.ndarray,
) -> np.ndarray:
    front_wide_t0 = rgb_frame_to_numpy(image_frames[1, 3]).copy()
    extr = avdi.get_clip_feature(clip_id, "sensor_extrinsics", maybe_stream=False)
    intr = avdi.get_clip_feature(clip_id, "camera_intrinsics", maybe_stream=False)
    overlay = viz_waypoints_pai(
        intr,
        extr,
        front_wide_t0,
        torch.from_numpy(gt_xyz).unsqueeze(0).unsqueeze(0),
        torch.from_numpy(pred_xyz).unsqueeze(0).unsqueeze(0).unsqueeze(0),
    )
    panel = resize_rgb(overlay, (936, 526))
    cv2.putText(
        panel,
        "front_wide t0: projected waypoints",
        (12, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        panel,
        "GT future red dots | predicted future blue dots",
        (12, 58),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return panel


def rotated_bev_xy(xyz: np.ndarray) -> np.ndarray:
    xy = xyz[:, :2].T
    return np.stack([-xy[1], xy[0]], axis=0)


def compute_bev_view(
    *,
    rows: list[dict[str, Any]],
    predictions: dict[str, np.ndarray],
) -> tuple[tuple[float, float], tuple[float, float], str]:
    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    for row in rows:
        if row.get("status") != "success":
            continue
        keys = row["output_npz_keys"]
        for semantic_name in ("ego_history_xyz", "ego_future_xyz"):
            points = predictions[keys[semantic_name]][0, 0]
            bev_xy = rotated_bev_xy(points)
            xs.append(bev_xy[0])
            ys.append(bev_xy[1])
        pred_xy = rotated_bev_xy(predictions[keys["pred_xyz"]][0, 0, 0])
        xs.append(pred_xy[0])
        ys.append(pred_xy[1])

    def metric_x_limits(ylim: tuple[float, float]) -> tuple[float, float]:
        y_span = ylim[1] - ylim[0]
        x_span = y_span * BEV_PANEL_SIZE[0] / BEV_PANEL_SIZE[1]
        return (-x_span / 2, x_span / 2)

    if not xs or not ys:
        ylim = (-16.0, 85.0)
        return metric_x_limits(ylim), ylim, "medium"

    all_x = np.concatenate(xs)
    all_y = np.concatenate(ys)
    y_min = float(all_y.min())
    y_max = float(all_y.max())
    if y_max <= 35.0 and y_min >= -8.0:
        ylim = (-8.0, 40.0)
        return metric_x_limits(ylim), ylim, "short"
    if y_max <= 80.0 and y_min >= -16.0:
        ylim = (-16.0, 85.0)
        return metric_x_limits(ylim), ylim, "medium"
    ylim = (-20.0, 125.0)
    return metric_x_limits(ylim), ylim, "long"


def future_path_stats(
    *,
    history_xyz: np.ndarray,
    gt_xyz: np.ndarray,
    pred_xyz: np.ndarray,
    bev_scale: str,
) -> list[str]:
    origin = np.zeros((1, 3), dtype=np.float32)
    gt_path = np.concatenate([origin, gt_xyz[:, :3]], axis=0)
    pred_path = np.concatenate([origin, pred_xyz[:, :3]], axis=0)
    gt_length = float(np.linalg.norm(np.diff(gt_path[:, :2], axis=0), axis=1).sum())
    pred_length = float(np.linalg.norm(np.diff(pred_path[:, :2], axis=0), axis=1).sum())
    fde = float(np.linalg.norm(pred_xyz[-1, :2] - gt_xyz[-1, :2]))
    current_speed = 0.0
    if len(history_xyz) >= 2:
        current_speed = float(np.linalg.norm(history_xyz[-1, :2] - history_xyz[-2, :2]) / 0.1)
    return [
        f"BEV scale {bev_scale}",
        f"v0 {current_speed:.1f} m/s",
        f"GT len {gt_length:.1f}m | Pred len {pred_length:.1f}m",
        f"GT avg {gt_length / 6.4:.1f} m/s | Pred avg {pred_length / 6.4:.1f} m/s",
        f"FDE {fde:.2f}m",
    ]


def build_video_frame(
    *,
    row: dict[str, Any],
    frame_index: int,
    total_frames: int,
    avdi: PhysicalAIAVDatasetLocalInterface,
    predictions: dict[str, np.ndarray],
    bev_view: tuple[tuple[float, float], tuple[float, float], str],
) -> np.ndarray:
    data = load_physical_aiavdataset(
        row["clip_id"],
        t0_us=int(row["t0_us"]),
        avdi=avdi,
        maybe_stream=False,
    )
    keys = row["output_npz_keys"]
    history_xyz = predictions[keys["ego_history_xyz"]][0, 0]
    gt_xyz = predictions[keys["ego_future_xyz"]][0, 0]
    pred_xyz = predictions[keys["pred_xyz"]][0, 0, 0]

    width, height = 1920, 1080
    canvas = np.full((height, width, 3), 245, dtype=np.uint8)
    projected_panel = make_front_wide_trajectory_panel(
        image_frames=data["image_frames"],
        avdi=avdi,
        clip_id=row["clip_id"],
        gt_xyz=gt_xyz,
        pred_xyz=pred_xyz,
    )
    camera_panel = make_camera_panel(data["image_frames"], history_frame_idx=3)
    camera_panel = resize_rgb(camera_panel, (936, 420))
    bev_panel = plot_bev_frame(
        history_xyz,
        gt_xyz,
        pred_xyz,
        step=gt_xyz.shape[0] - 1,
        width=880,
        height=620,
        xlim=bev_view[0],
        ylim=bev_view[1],
        stats_text=future_path_stats(
            history_xyz=history_xyz,
            gt_xyz=gt_xyz,
            pred_xyz=pred_xyz,
            bev_scale=bev_view[2],
        ),
        equal_aspect=True,
    )

    canvas[74 : 74 + projected_panel.shape[0], 24 : 24 + projected_panel.shape[1]] = projected_panel
    canvas[74 : 74 + bev_panel.shape[0], 1000 : 1000 + bev_panel.shape[1]] = bev_panel
    canvas[636 : 636 + camera_panel.shape[0], 24 : 24 + camera_panel.shape[1]] = camera_panel

    title = (
        f"clip={row['clip_id']} | window={frame_index + 1}/{total_frames} | "
        f"t0_us={row['t0_us']} | seed={row['seed']} | "
        f"samples={row['num_traj_samples']}"
    )
    cv2.putText(
        canvas,
        title,
        (24, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        (20, 20, 20),
        2,
        cv2.LINE_AA,
    )
    metric = (
        f"ADE={row['ade']:.4f}m | minADE={row['minade']:.4f}m "
        "(single-sample; num_traj_samples=1)"
    )
    cv2.putText(
        canvas,
        metric,
        (1000, 728),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.66,
        (70, 45, 20),
        2,
        cv2.LINE_AA,
    )
    put_wrapped_text(canvas, f"CoC: {row.get('coc_text', '')}", (1000, 776), 92)
    put_wrapped_text(
        canvas,
        "Visual scope: open-loop sanity/demo only; not closed-loop or model-quality validation.",
        (1000, 982),
        92,
        color=(80, 45, 20),
    )
    return canvas


def write_smoke_video(
    *,
    output_path: Path,
    rows: list[dict[str, Any]],
    avdi: PhysicalAIAVDatasetLocalInterface,
    predictions: dict[str, np.ndarray],
    fps: int,
) -> list[dict[str, Any]]:
    success_rows = [row for row in rows if row.get("status") == "success"]
    manifest: list[dict[str, Any]] = []
    if not success_rows:
        return manifest
    bev_view = compute_bev_view(rows=success_rows, predictions=predictions)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_output_path = output_path.with_name(f"{output_path.stem}.tmp{output_path.suffix}")
    tmp_output_path.unlink(missing_ok=True)
    writer = cv2.VideoWriter(
        str(tmp_output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (1920, 1080),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Failed to open video writer for {tmp_output_path}")

    preview_path = output_path.with_name("preview_window_00.png")
    try:
        for frame_index, row in enumerate(success_rows):
            frame = build_video_frame(
                row=row,
                frame_index=frame_index,
                total_frames=len(success_rows),
                avdi=avdi,
                predictions=predictions,
                bev_view=bev_view,
            )
            if frame_index == 0:
                cv2.imwrite(str(preview_path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            row["video_frame_index"] = frame_index
            row["preview_png"] = str(preview_path) if frame_index == 0 else None
            manifest.append(
                {
                    "window_index": row["window_index"],
                    "t0_us": row["t0_us"],
                    "video_frame_index": frame_index,
                    "status": row["status"],
                    "ade": row.get("ade"),
                    "minade": row.get("minade"),
                    "bev_xlim": list(bev_view[0]),
                    "bev_ylim": list(bev_view[1]),
                    "bev_scale": bev_view[2],
                }
            )
    finally:
        writer.release()
    tmp_output_path.replace(output_path)
    output_path.chmod(0o664)
    return manifest


def write_summary_files(
    *,
    args: argparse.Namespace,
    rows: list[dict[str, Any]],
    runtime_config: dict[str, Any],
    run_started: str,
    run_finished: str,
    run_runtime_sec: float,
    outputs: dict[str, str | None],
) -> None:
    success_rows = [row for row in rows if row.get("status") == "success"]
    runtimes = [row["runtime_sec"] for row in success_rows if row.get("runtime_sec") is not None]
    peak_vram = [
        row["peak_vram_mib"] for row in success_rows if row.get("peak_vram_mib") is not None
    ]
    summary = {
        "run_id": args.run_name,
        "run_started": run_started,
        "run_finished": run_finished,
        "run_runtime_sec": round(run_runtime_sec, 3),
        "dataset_root": str(args.dataset_root),
        "clip_id": args.clip_id,
        "chunk_id": args.chunk_id,
        "t0_us_list": args.t0_us_list,
        "stride_us": infer_stride_us(args.t0_us_list),
        "seed": args.seed,
        "num_traj_samples": args.num_traj_samples,
        "num_traj_sets": args.num_traj_sets,
        "runtime_config": runtime_config,
        "result_counts": {
            "total": len(rows),
            "success": len(success_rows),
            "failed": sum(row.get("status") == "failed" for row in rows),
        },
        "runtime_sec_per_window": {
            "mean": round(float(np.mean(runtimes)), 3) if runtimes else None,
            "max": round(float(np.max(runtimes)), 3) if runtimes else None,
        },
        "peak_vram_mib": max(peak_vram) if peak_vram else None,
        "outputs": outputs,
        "metric_caveat": "num_traj_samples=1; minADE is single-sample ADE for this smoke.",
        "validation_scope": (
            "visual sanity/demo artifact only; not model quality or closed-loop validation."
        ),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.summary_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (args.summary_dir / f"{args.run_name}.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (args.summary_dir / f"{args.run_name}.md").write_text(
        format_markdown_summary(summary, rows),
        encoding="utf-8",
    )


def format_markdown_summary(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        f"# {summary['run_id']}",
        "",
        "## Scope",
        "",
        "- Track: A4 Visualization and Demo Lab",
        f"- Clip: `{summary['clip_id']}`",
        f"- Chunk: `{summary['chunk_id']}`",
        f"- `t0_us` list: `{summary['t0_us_list']}`",
        f"- Seed: `{summary['seed']}`",
        f"- `num_traj_samples`: `{summary['num_traj_samples']}`",
        "- Claim boundary: visual sanity/demo artifact only; not model quality validation.",
        "",
        "## Runtime",
        "",
        f"- Run started: `{summary['run_started']}`",
        f"- Run finished: `{summary['run_finished']}`",
        f"- Total runtime sec: `{summary['run_runtime_sec']}`",
        f"- Mean runtime/window sec: `{summary['runtime_sec_per_window']['mean']}`",
        f"- Peak VRAM MiB: `{summary['peak_vram_mib']}`",
        "",
        "## Outputs",
        "",
    ]
    for name, path in summary["outputs"].items():
        lines.append(f"- {name}: `{path}`")
    lines.extend(
        [
            "",
            "## Windows",
            "",
            "| window | t0_us | status | runtime_sec | ADE | minADE | failure |",
            "| ---: | ---: | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            f"{row.get('window_index')} | "
            f"{row.get('t0_us')} | "
            f"{row.get('status')} | "
            f"{row.get('runtime_sec')} | "
            f"{row.get('ade')} | "
            f"{row.get('minade')} | "
            f"{row.get('failure_reason')} |"
        )
    lines.extend(
        [
            "",
            "## Metric Caveat",
            "",
            summary["metric_caveat"],
            "",
        ]
    )
    return "\n".join(lines)


def run_render_only(args: argparse.Namespace) -> None:
    results_jsonl = args.results_jsonl or args.output_dir / "results.jsonl"
    predictions_npz = args.predictions_npz or args.output_dir / "predictions.npz"
    if not results_jsonl.exists():
        raise FileNotFoundError(f"Missing render-only JSONL: {results_jsonl}")
    if not predictions_npz.exists():
        raise FileNotFoundError(f"Missing render-only NPZ: {predictions_npz}")

    rows = read_jsonl(results_jsonl)
    predictions = load_npz_arrays(predictions_npz)
    chunk_ids = sorted({int(row["chunk_id"]) for row in rows if row.get("status") == "success"})
    avdi = PhysicalAIAVDatasetLocalInterface(args.dataset_root, chunk_ids=chunk_ids)
    video_mp4 = args.output_dir / args.render_video_name
    manifest_json = args.output_dir / args.render_manifest_name
    video_manifest = write_smoke_video(
        output_path=video_mp4,
        rows=rows,
        avdi=avdi,
        predictions=predictions,
        fps=args.fps,
    )
    manifest_json.write_text(
        json.dumps(video_manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_jsonl(results_jsonl, rows)
    print(
        json.dumps(
            {
                "event": "render_only_finished",
                "jsonl": str(results_jsonl),
                "npz": str(predictions_npz),
                "video": str(video_mp4),
                "manifest": str(manifest_json),
                "frames": len(video_manifest),
            },
            ensure_ascii=False,
        )
    )


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.summary_dir.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)

    if args.render_only:
        run_render_only(args)
        return

    offline_env = prepare_offline_env(args.allow_download)
    set_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    run_started = now_kst()
    run_start = time.perf_counter()
    logger = EventLogger(args.log_dir / f"{args.run_name}.log")
    logger.write(
        {
            "event": "a4_smoke_start",
            "run_started": run_started,
            "dataset_root": str(args.dataset_root),
            "clip_id": args.clip_id,
            "chunk_id": args.chunk_id,
            "t0_us_list": args.t0_us_list,
            "seed": args.seed,
            "num_traj_samples": args.num_traj_samples,
            "offline": offline_env,
        }
    )

    avdi = PhysicalAIAVDatasetLocalInterface(args.dataset_root, chunk_ids=[args.chunk_id])
    model, processor, runtime_config = load_model_and_processor(args)
    logger.write({"event": "model_loaded", "runtime_config": runtime_config})

    rows: list[dict[str, Any]] = []
    all_arrays: dict[str, np.ndarray] = {}
    stride_us = infer_stride_us(args.t0_us_list)
    for window_index, t0_us in enumerate(args.t0_us_list):
        row, arrays = run_one_clip(
            args=make_window_args(args, t0_us),
            avdi=avdi,
            model=model,
            processor=processor,
            clip_id=args.clip_id,
            seed=args.seed,
            run_id=args.run_name,
            write_arrays=True,
        )
        row["window_index"] = window_index
        row["stride_us"] = stride_us
        all_arrays.update(remap_window_arrays(row=row, arrays=arrays, window_index=window_index))
        rows.append(row)
        logger.write(
            {
                "event": "window_done",
                "window_index": window_index,
                "t0_us": t0_us,
                "status": row["status"],
                "runtime_sec": row.get("runtime_sec"),
                "minade": row.get("minade"),
                "peak_vram_mib": row.get("peak_vram_mib"),
                "failure_reason": row.get("failure_reason"),
            }
        )
        if row["status"] == "failed" and not args.continue_on_failure:
            break

    results_jsonl = args.results_jsonl or args.output_dir / "results.jsonl"
    predictions_npz = args.predictions_npz or args.output_dir / "predictions.npz"
    video_mp4 = args.output_dir / "smoke_demo.mp4"
    manifest_json = args.output_dir / "manifest.json"

    if all_arrays:
        np.savez_compressed(predictions_npz, **all_arrays)

    video_manifest: list[dict[str, Any]] = []
    if all_arrays and not args.skip_video:
        video_manifest = write_smoke_video(
            output_path=video_mp4,
            rows=rows,
            avdi=avdi,
            predictions=all_arrays,
            fps=args.fps,
        )
        manifest_json.write_text(
            json.dumps(video_manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    write_jsonl(results_jsonl, rows)

    run_finished = now_kst()
    outputs = {
        "jsonl": str(results_jsonl),
        "npz": str(predictions_npz) if all_arrays else None,
        "video": str(video_mp4) if video_manifest else None,
        "manifest": str(manifest_json) if video_manifest else None,
        "log": str(args.log_dir / f"{args.run_name}.log"),
        "docs_summary_json": str(args.summary_dir / f"{args.run_name}.json"),
        "docs_summary_md": str(args.summary_dir / f"{args.run_name}.md"),
    }
    write_summary_files(
        args=args,
        rows=rows,
        runtime_config=runtime_config,
        run_started=run_started,
        run_finished=run_finished,
        run_runtime_sec=time.perf_counter() - run_start,
        outputs=outputs,
    )
    logger.write({"event": "a4_smoke_finished", "run_finished": run_finished, "outputs": outputs})
    logger.close()


if __name__ == "__main__":
    main()
