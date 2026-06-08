# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

"""Generate A4 visual artifacts from the A3 pilot outputs.

This script consumes the A3 JSONL/NPZ artifacts, reloads local PAI camera inputs,
and writes one composite PNG plus one trajectory animation MP4 per successful clip.
"""

from __future__ import annotations

import argparse
import html
import json
import textwrap
from pathlib import Path
from typing import Any

import cv2
import matplotlib
import numpy as np
import torch

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from alpamayo_r1.data.pai_utils import PhysicalAIAVDatasetLocalInterface
from alpamayo_r1.load_physical_aiavdataset import load_physical_aiavdataset
from alpamayo_r1.visualization.viz import visualize_data


DEFAULT_RESULTS_JSONL = Path("docs/artifacts/a3_inference/2026-06-08-pilot/results.jsonl")
DEFAULT_PREDICTIONS_NPZ = Path("docs/artifacts/a3_inference/2026-06-08-pilot/predictions.npz")
DEFAULT_OUTPUT_DIR = Path("docs/artifacts/a4_visualization/2026-06-08-a3-pilot")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-jsonl", type=Path, default=DEFAULT_RESULTS_JSONL)
    parser.add_argument("--predictions-npz", type=Path, default=DEFAULT_PREDICTIONS_NPZ)
    parser.add_argument("--dataset-root", type=Path, default=Path("/data/datasets/physical_ai_av"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--fps", type=int, default=10)
    return parser.parse_args()


def read_success_rows(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    return [row for row in rows if row.get("status") == "success"]


def rotate_90cc(xy: np.ndarray) -> np.ndarray:
    return np.stack([-xy[1], xy[0]], axis=0)


def rgb_tensor_to_numpy(frame: torch.Tensor) -> np.ndarray:
    return frame.permute(1, 2, 0).cpu().numpy().astype(np.uint8)


def resize_rgb(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def make_camera_panel(image_frames: torch.Tensor, history_frame_idx: int) -> np.ndarray:
    frames = [rgb_tensor_to_numpy(image_frames[cam_idx, history_frame_idx]) for cam_idx in range(4)]
    tiles = [resize_rgb(frame, (460, 258)) for frame in frames]
    top = np.concatenate([tiles[0], tiles[1]], axis=1)
    bottom = np.concatenate([tiles[2], tiles[3]], axis=1)
    panel = np.concatenate([top, bottom], axis=0)
    labels = ["cross_left", "front_wide", "cross_right", "front_tele"]
    positions = [(8, 24), (468, 24), (8, 282), (468, 282)]
    for label, pos in zip(labels, positions, strict=True):
        cv2.putText(panel, label, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    return panel


def plot_bev_frame(
    history_xyz: np.ndarray,
    gt_xyz: np.ndarray,
    pred_xyz: np.ndarray,
    step: int,
    width: int = 580,
    height: int = 516,
) -> np.ndarray:
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    hist_xy = rotate_90cc(history_xyz[:, :2].T)
    gt_xy = rotate_90cc(gt_xyz[: step + 1, :2].T)
    pred_xy = rotate_90cc(pred_xyz[: step + 1, :2].T)
    full_gt = rotate_90cc(gt_xyz[:, :2].T)
    full_pred = rotate_90cc(pred_xyz[:, :2].T)

    ax.plot(hist_xy[0], hist_xy[1], "-", color="#595959", linewidth=1.5, label="history")
    ax.plot(full_gt[0], full_gt[1], "-", color="#f2a6a6", linewidth=1.0, alpha=0.5)
    ax.plot(full_pred[0], full_pred[1], "-", color="#9bbcff", linewidth=1.0, alpha=0.5)
    ax.plot(gt_xy[0], gt_xy[1], "-", color="#d62728", linewidth=2.2, label="gt future")
    ax.plot(pred_xy[0], pred_xy[1], "-", color="#1f77b4", linewidth=2.2, label="prediction")
    ax.scatter([hist_xy[0, -1]], [hist_xy[1, -1]], c="black", marker="x", s=35, label="t0")
    ax.scatter([gt_xy[0, -1]], [gt_xy[1, -1]], c="#d62728", s=30)
    ax.scatter([pred_xy[0, -1]], [pred_xy[1, -1]], c="#1f77b4", s=30)

    xs = np.concatenate([hist_xy[0], full_gt[0], full_pred[0]])
    ys = np.concatenate([hist_xy[1], full_gt[1], full_pred[1]])
    x_center = 0.5 * (xs.min() + xs.max())
    y_center = 0.5 * (ys.min() + ys.max())
    span = max(xs.max() - xs.min(), ys.max() - ys.min(), 4.0) * 1.25
    ax.set_xlim(x_center - span / 2, x_center + span / 2)
    ax.set_ylim(y_center - span / 2, y_center + span / 2)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.4, alpha=0.35)
    ax.set_title(f"BEV trajectory progress: {step + 1}/64")
    ax.set_xlabel("rotated x (m)")
    ax.set_ylabel("rotated y (m)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    rgb = rgba[:, :, :3].copy()
    plt.close(fig)
    return rgb


def put_wrapped_text(
    canvas: np.ndarray,
    text: str,
    origin: tuple[int, int],
    width_chars: int,
    font_scale: float = 0.55,
    color: tuple[int, int, int] = (30, 30, 30),
    line_height: int = 24,
) -> None:
    x, y = origin
    for line in textwrap.wrap(text, width=width_chars)[:5]:
        cv2.putText(canvas, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 1, cv2.LINE_AA)
        y += line_height


def write_clip_video(
    output_path: Path,
    row: dict[str, Any],
    image_frames: torch.Tensor,
    history_xyz: np.ndarray,
    gt_xyz: np.ndarray,
    pred_xyz: np.ndarray,
    fps: int,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1600, 900
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Failed to open video writer for {output_path}")

    try:
        for step in range(gt_xyz.shape[0]):
            canvas = np.full((height, width, 3), 245, dtype=np.uint8)
            hist_frame_idx = min(3, int(step / max(1, gt_xyz.shape[0] / 4)))
            camera_panel = make_camera_panel(image_frames, hist_frame_idx)
            bev_panel = plot_bev_frame(history_xyz, gt_xyz, pred_xyz, step)

            canvas[72 : 72 + camera_panel.shape[0], 24 : 24 + camera_panel.shape[1]] = camera_panel
            canvas[72 : 72 + bev_panel.shape[0], 992 : 992 + bev_panel.shape[1]] = bev_panel

            title = (
                f"clip={row['clip_id']} | seed={row['seed']} | "
                f"num_traj_samples={row['num_traj_samples']} | "
                f"ADE/minADE={row['ade']:.4f}m"
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
            cv2.putText(
                canvas,
                "Input cameras: cross-left, front-wide, cross-right, front-tele",
                (24, 622),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (40, 40, 40),
                1,
                cv2.LINE_AA,
            )
            put_wrapped_text(canvas, f"CoC: {row.get('coc_text', '')}", (24, 670), 140)
            put_wrapped_text(
                canvas,
                "Metric caveat: num_traj_samples=1, so minADE is single-sample ADE.",
                (24, 820),
                140,
                color=(80, 45, 20),
            )
            writer.write(cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR))
    finally:
        writer.release()


def write_index(output_dir: Path, rows: list[dict[str, Any]], manifest: list[dict[str, Any]]) -> None:
    table_rows = []
    for row, item in zip(rows, manifest, strict=True):
        table_rows.append(
            "<tr>"
            f"<td>{html.escape(row['clip_id'])}</td>"
            f"<td>{row['ade']:.4f}</td>"
            f"<td>{row['minade']:.4f}</td>"
            f"<td>{row['runtime_sec']:.3f}</td>"
            f"<td>{row['peak_vram_mib']:.1f}</td>"
            f"<td><a href=\"{html.escape(item['composite_png'])}\">PNG</a></td>"
            f"<td><a href=\"{html.escape(item['video_mp4'])}\">MP4</a></td>"
            "</tr>"
        )
    html_text = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>A4 Visualization from A3 Pilot</title>
  <style>
    body {{ font-family: sans-serif; margin: 24px; line-height: 1.45; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; }}
    th {{ background: #f2f2f2; }}
  </style>
</head>
<body>
  <h1>A4 Visualization from A3 Pilot</h1>
  <p>Each clip has a composite PNG based on the repository visualization utility and an MP4
  animation showing input cameras with GT/prediction BEV progression.</p>
  <p><strong>Metric caveat:</strong> num_traj_samples=1, so minADE is single-sample ADE.</p>
  <table>
    <thead>
      <tr><th>clip_id</th><th>ADE</th><th>minADE</th><th>runtime_sec</th><th>peak_vram_mib</th><th>PNG</th><th>MP4</th></tr>
    </thead>
    <tbody>
      {''.join(table_rows)}
    </tbody>
  </table>
</body>
</html>
"""
    (output_dir / "index.html").write_text(html_text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_success_rows(args.results_jsonl)
    predictions = np.load(args.predictions_npz)
    chunk_ids = sorted({int(row["chunk_id"]) for row in rows})
    avdi = PhysicalAIAVDatasetLocalInterface(args.dataset_root, chunk_ids=chunk_ids)

    manifest = []
    for idx, row in enumerate(rows, start=1):
        clip_id = row["clip_id"]
        clip_prefix = f"{idx:02d}_{clip_id}"
        data = load_physical_aiavdataset(
            clip_id,
            t0_us=int(row["t0_us"]),
            avdi=avdi,
            maybe_stream=False,
        )
        pred_xyz = torch.from_numpy(predictions[f"{clip_id}__pred_xyz"])
        gt_future = torch.from_numpy(predictions[f"{clip_id}__ego_future_xyz"])
        history = torch.from_numpy(predictions[f"{clip_id}__ego_history_xyz"])
        extr = avdi.get_clip_feature(clip_id, "sensor_extrinsics", maybe_stream=False)
        intr = avdi.get_clip_feature(clip_id, "camera_intrinsics", maybe_stream=False)

        composite_png = args.output_dir / f"{clip_prefix}_composite.png"
        visualize_data(
            data["image_frames"],
            ego_future_xyz_gt=gt_future,
            ego_future_xyz_pred=pred_xyz,
            cot_text=(
                f"{row.get('coc_text', '')} | ADE/minADE={row['ade']:.4f}m | "
                "num_traj_samples=1"
            ),
            show_waypoint_pai=True,
            extr=extr,
            intr=intr,
            save_path=str(composite_png),
        )

        video_mp4 = args.output_dir / f"{clip_prefix}_animation.mp4"
        write_clip_video(
            video_mp4,
            row,
            data["image_frames"],
            history.numpy()[0, 0],
            gt_future.numpy()[0, 0],
            pred_xyz.numpy()[0, 0, 0],
            args.fps,
        )

        manifest.append(
            {
                "clip_id": clip_id,
                "composite_png": composite_png.name,
                "video_mp4": video_mp4.name,
                "ade": row["ade"],
                "minade": row["minade"],
            }
        )
        print(json.dumps(manifest[-1]))

    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_index(args.output_dir, rows, manifest)
    print(f"Wrote {len(manifest)} clip visualizations to {args.output_dir}")


if __name__ == "__main__":
    main()
