---
doc_type: report
status: review
track: A4
created_at: 2026-06-08 19:46:59 KST
updated_at: 2026-06-08 19:50:21 KST
parent_plan: docs/2026-06-08 [Plan] Track A4 Visualization and Demo Lab.md
parent_task: docs/2026-06-08 [Task] Track A4 Visualization and Demo Lab.md
---

# Track A4 Visualization and Demo Lab Report

## Document Frame

Purpose: record the current A4 decision state after smoke, 5-clip full-window demo, BEV render
iterations, and the start of all-local processing.

Primary reader: Alpamayo R&D Manager, the A4 reviewer, and the user deciding whether the current A4
tooling is sufficient for broader visual sanity review.

Decision question: did A4 produce A3-compatible human-reviewable visualization/demo artifacts, and
what does the current demo prove or not prove?

Exclusion scope: this report does not validate model quality, closed-loop safety, AlpaSim/A5
behavior, or training/intention-following capability.

## Executive Summary

A4 reached the intended visualization/demo milestone for the five A3 target clips. The pipeline now
generates sliding-window A3-compatible inference outputs at `0.1s` stride, renders per-clip demo
videos, overlays projected trajectory information on the front camera, and shows BEV ego history,
ground-truth future, predicted future, CoC text, ADE/minADE, seed, sampling count, and window index.

The completed five-clip run processed `917/917` windows successfully with `0` failed windows. Each
clip has clip-local `results.jsonl`, `predictions.npz`, `demo.mp4`, `video_manifest.json`, and
`run_summary.json` under
`experiments/a4_visualization/2026-06-08-a4-demo/target-full-100ms/`.

Audit path: the `917` windows come from
`docs/artifacts/a4_visualization/2026-06-08-summary/a4-target-windows-100ms.jsonl`; per-clip runtime
and completion status come from each clip's `run_summary.json`.

The first all-local run has also started for all locally available PAI chunks with the required A4
features. That run is intentionally treated as in progress, not as final A4 evidence. It covers
`772` clips and `139,534` windows at `0.1s` stride, split across two GPUs, with CPU video rendering
watching for completed clips.

The key limitation remains unchanged: A4 is an open-loop visual sanity and demo artifact stage.
Videos that look plausible do not prove model quality, causal reasoning, intention-following, or
closed-loop driving safety.

## Compatibility and Schema Decision

A4 reuses the A3 runner and output schema rather than defining a new inference contract. Each
window writes one JSONL row and NPZ tensor keys that include the clip/window identity so multiple
timestamps in the same clip can coexist.

Required A3 fields used by A4:

- `clip_id`, `chunk_id`, `t0_us`
- `seed`, `num_traj_samples`, `num_traj_sets`
- `status`, `failure_reason`
- `runtime_sec`, `peak_vram_mib`
- `ade`, `minade`, `minade_interpretation`
- `coc_text`
- `output_npz_keys`

Required tensor content used by A4:

- predicted future trajectory
- ego history trajectory
- ground-truth future trajectory
- timestamps needed to align the window

Image frames are not copied into docs artifacts. The renderer reloads local PAI camera frames from
`/data/datasets/physical_ai_av` using `chunk_id`, `clip_id`, and `t0_us`.

## Provisional Visualization Review

The earlier provisional script, `scripts/visualize_a3_pilot.py`, was not discarded. It was modified
because it already handled A3 pilot visualization and local image reload, but it did not support
multi-window clip videos or richer trajectory overlays.

Final decision: `modify`.

The retained value was:

- camera grid rendering;
- BEV trajectory panel;
- CoC and metric text rendering;
- A3 JSONL/NPZ compatibility.

The required A4 additions were:

- window-keyed tensor lookup;
- ordered sliding-window video rendering;
- front-camera trajectory projection;
- fixed BEV scale support;
- clip-level summaries that distinguish complete, partial, and complete-with-failures output;
- temporary MP4 write and atomic replacement after `VideoWriter.release()` to avoid corrupt videos.

## A3 Pilot and Smoke Result

The one-clip smoke used:

- `clip_id`: `c23d0ac1-fe93-4f25-bf71-198ccec5c190`
- `chunk_id`: `3119`
- `t0_us`: `[3_100_000, 4_100_000, 5_100_000, 6_100_000, 7_100_000]`
- stride: `1_000_000us`
- seed: `42`
- `num_traj_samples`: `1`
- result: `5/5` windows succeeded
- total runtime: `30.975s`
- mean runtime per window after model load: `2.148s`
- peak VRAM: `22,026 MiB`
- video:
  `experiments/a4_visualization/2026-06-08-a4-demo/smoke-c23d0ac1/smoke_demo.mp4`

Audit path: smoke summary values come from
`experiments/a4_visualization/2026-06-08-a4-demo/smoke-c23d0ac1/run_summary.json` and the small docs
summary under `docs/artifacts/a4_visualization/2026-06-08-summary/`.

This smoke validated the basic A4 path: A3-compatible inference rows, NPZ tensor storage,
multi-window video rendering, trajectory overlays, metric display, and CoC text display.

## Five-Clip Full-Window Result

The corrected five-clip target run used `0.1s` stride and processed all valid windows after
intersecting egomotion and camera timestamp bounds.

| Clip | Windows | Success | Failed | Mean sec/window | Runtime sec |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ac321da3-3848-4736-a9c2-053be0bea770` | 184 | 184 | 0 | 1.992 | 533.191 |
| `ac7ac12e-7371-47ec-987d-61e0b3c7693f` | 183 | 183 | 0 | 2.267 | 620.680 |
| `b8fa0288-f799-4443-ba62-4601c45fe133` | 183 | 183 | 0 | 1.872 | 483.837 |
| `c23d0ac1-fe93-4f25-bf71-198ccec5c190` | 184 | 184 | 0 | 2.032 | 526.086 |
| `cb656c5d-7520-4cc2-9e87-889f061fc6cb` | 183 | 183 | 0 | 2.476 | 693.266 |

Aggregate:

- clips: `5`
- windows: `917`
- successful windows: `917`
- failed windows: `0`
- status set: `complete`
- max peak VRAM: `22,026 MiB`
- mean of per-clip mean window runtimes: `2.128s`

Output root:

```text
experiments/a4_visualization/2026-06-08-a4-demo/target-full-100ms/
```

Each clip directory contains:

- `results.jsonl`
- `predictions.npz`
- `demo.mp4`
- `video_manifest.json`
- `run_summary.json`

Audit path: the manifest source is
`docs/artifacts/a4_visualization/2026-06-08-summary/a4-target-windows-100ms.jsonl`; the table above
is derived from the five per-clip `run_summary.json` files under the output root.

## BEV and Video Rendering Decisions

The user review surfaced two important visualization issues.

First, the BEV axes had to be fixed. Dynamic axes made speed and trajectory length difficult to
compare across windows because the plot scaled itself to the trajectory. A4 now supports fixed
three-level BEV scale selection so short, medium, and long trajectory cases can be rendered with
stable viewing ranges.

Second, x/y scaling had to be interpreted carefully. A narrow lateral range made lateral jitter look
too dramatic. The preferred direction is metric-equal rendering, where one meter lateral has the
same visual scale as one meter longitudinal, and the displayed x range is derived from the graph
aspect ratio.

The first target clip was rerendered from existing inference outputs without rerunning inference:

```text
experiments/a4_visualization/2026-06-08-a4-demo/target-full-100ms/ac321da3-3848-4736-a9c2-053be0bea770/demo_bev_metric_scale3.mp4
```

The earlier unreadable MP4 issue was diagnosed as an interrupted or unfinalized MP4 container:
`moov atom not found`. The renderer now writes to a temporary MP4 and replaces the final path only
after OpenCV releases the writer.

## Full-Clip and Sliding-Window Execution Design

The five-clip target run uses complete clip ownership per GPU process, not modulo window sharding.
This intentionally avoids a merge step and gives each clip one output directory.

The current full-window design records:

- `clip_id`
- `chunk_id`
- ordered `t0_us` list from the manifest
- stride/window interval
- number of windows
- seed
- `num_traj_samples`
- model/runtime config
- runtime per window
- peak VRAM
- success/failure per window
- output JSONL/NPZ path
- output video path

Two-GPU execution is handled by:

```bash
scripts/run_a4_window_manifest_2gpu.sh 0
scripts/run_a4_window_manifest_2gpu.sh 1
```

All-local execution uses the same principle but separates inference and video rendering:

```bash
scripts/run_a4_all_local_2gpu.sh 0
scripts/run_a4_all_local_2gpu.sh 1
scripts/run_a4_all_local_render_watcher.sh
```

The all-local renderer does not use GPU. It polls completed clip summaries and renders videos in a
separate CPU process after inference writes clip-local JSONL/NPZ outputs.

## All-Local Run Status

All-local processing is in progress and should not yet be interpreted as a completed result.

Scope:

- chunks: `156`, `297`, `727`, `1843`, `1864`, `1875`, `2129`, `2281`, `3119`, `3135`
- clips: `772`
- windows: `139,534`
- stride: `100,000us`
- output root:
  `experiments/a4_visualization/2026-06-08-a4-demo/all-local-100ms/`

GPU split:

- GPU 0 chunks: `727`, `1875`, `156`, `3135`, `297`; assigned windows: `70,159`
- GPU 1 chunks: `3119`, `1864`, `1843`, `2129`, `2281`; assigned windows: `69,375`

Status snapshot at `2026-06-08 19:46:59 KST`:

- GPU 0 windows done: `301`
- GPU 1 windows done: `300`
- failed windows observed in logs: `0`
- completed clips observed per GPU logs: `1` on GPU 0 and `1` on GPU 1
- rendered videos observed by CPU watcher: `1`

Audit path: all-local scope comes from
`docs/artifacts/a4_visualization/2026-06-08-summary/a4-all-local-windows-100ms.jsonl`; progress
comes from `docs/logs/2026-06-08-a4-all-local-100ms-gpu0.log`,
`docs/logs/2026-06-08-a4-all-local-100ms-gpu1.log`, and
`docs/logs/2026-06-08-a4-all-local-100ms-render.log`. These logs are local run evidence and are not
intended for git.

Estimated runtime remains roughly `41-45h` for inference JSONL/NPZ on two RTX 4090 GPUs, with CPU
video rendering trailing inference and potentially extending total wall time.

## Demo Video Output Schema

For each clip video, `video_manifest.json` records frame/window-level render metadata. The standard
manifest fields are:

- `window_index`: clip-local sliding-window index;
- `t0_us`: timestamp used for the A3-compatible inference call;
- `video_frame_index`: frame index in the rendered demo video;
- `status`: inference status for that window;
- `ade`: single-window ADE value when available;
- `minade`: minADE value, interpreted as single-sample ADE when `num_traj_samples=1`.

Metric BEV rerenders add:

- `bev_xlim`: displayed lateral BEV range;
- `bev_ylim`: displayed longitudinal BEV range;
- `bev_scale`: selected scale preset such as `short`, `medium`, or `long`.

The video itself is intended to show:

- timestamp/window index;
- front camera frame at `t0`;
- projected predicted future trajectory;
- projected ground-truth future trajectory;
- BEV ego history;
- BEV ground-truth future;
- BEV predicted future;
- CoC text;
- ADE/minADE;
- seed;
- `num_traj_samples`;
- caveat that `num_traj_samples=1` makes minADE a single-sample ADE.

The video is a review artifact, not a benchmark artifact. It is suitable for visual inspection,
debugging, and selecting cases for deeper analysis.

## Known Limitations

- A4 does not prove model quality.
- A4 does not prove closed-loop driving safety.
- A4 does not prove the CoC text is causally correct.
- `num_traj_samples=1` means minADE is equivalent to single-sample ADE.
- The model may infer turn or stop behavior from visual context and ego history, but the current A4
  run does not isolate whether that behavior comes from true intention understanding.
- The PAI dataset artifacts inspected here do not establish an explicit high-level driver
  intention label available to the model.
- All-local processing is still running, so any all-local status is a snapshot.
- Large experiment outputs are intentionally kept under `experiments/` and are not intended for git.

## A5/A6 Handoff Implications

A5/AlpaSim should treat A4 videos as case-selection and visualization evidence only. A4 can identify
interesting clips where predictions appear plausible, unstable, delayed, or inconsistent with
ground truth. It cannot establish closed-loop behavior.

A6 or later evaluation work should add explicit metrics and scenario grouping if the goal is to
compare model behavior across intention-like situations such as lane following, lane change, stop,
or turn. If future work requires command-conditioned driving, the dataset and prompt interface need
an explicit intention/route/goal contract rather than assuming default prompts will generalize to
arbitrary user intentions.

## Teacher/Evaluator Questions

The reviewer should be able to answer:

1. What is the difference between A3 single-`t0_us` pilot output and A4 sliding-window demo output?
2. Why is a visually plausible video not evidence that the model is validated?
3. Why does `num_traj_samples=1` make minADE a single-sample ADE?
4. Why did A4 choose per-clip GPU ownership instead of window-level merge?
5. What is the difference between completed five-clip target evidence and in-progress all-local
   evidence?
6. What information would be needed before claiming intention-following capability?

## Current Decision

A4 has enough completed evidence to serve as a visualization/demo lab result for the five A3 target
clips. The all-local run can continue as an expanded visual review dataset, but it should remain
clearly separated from the completed A4 target result until it finishes and its failures, runtime,
storage, and rendered videos are reviewed.
