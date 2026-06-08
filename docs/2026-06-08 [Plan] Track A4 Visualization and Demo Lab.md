---
doc_type: plan
status: review
plan_id: alpamayo-rnd-a4-visualization-demo-lab
version: 1
canonical: false
created_at: 2026-06-08 17:03:01 KST
approved_at:
root_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
supersedes:
superseded_by:
root_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
revision_type: initial_track_execution_plan
revision_reason: Define Track A4 visualization and sliding-window demo gates before compute-heavy inference
---

# Track A4 Visualization and Demo Lab Plan

## Document Frame

Purpose: define the A4 execution baseline before running any compute-heavy sliding-window
inference.

Primary reader: Alpamayo R&D Manager, A4 Expert-led session, and the user reviewing whether the
first A4 smoke is small enough to approve.

Decision question: can A4 safely move from A3 single-`t0_us` artifacts to a 1-clip
sliding-window smoke, while preserving A3's schema and avoiding premature full-demo claims?

Exclusion scope: no model-quality validation, no AlpaSim/A5 work, no training, no additional PAI
download, no Root Task update by this Expert-led session.

## Current Status

This Plan is in `review` state. It is not yet an approved execution baseline. The immediate
approval request is only for the small 1-clip sliding-window smoke described below.

No full-clip or multi-clip full-window inference should run until the smoke result is reported and
the Manager/user approves a later full inference option.

## Assumptions

- A4 starts from the A3 schema and artifacts, not from a new data download.
- The local PAI root remains `/data/datasets/physical_ai_av`.
- A3's default runtime configuration remains the A4 smoke baseline:
  - model: `nvidia/Alpamayo-R1-10B`
  - processor: `Qwen/Qwen3-VL-2B-Instruct`
  - dtype: `torch.bfloat16`
  - CUDA device: `0`
  - max memory: `23GiB`
  - offline/cache-only model loading
  - `num_traj_samples=1`
  - `num_traj_sets=1`
  - `top_p=0.98`
  - `temperature=0.6`
  - `max_generation_length=256`
- The user/Manager will approve each compute expansion gate explicitly.

## Success Criteria

A4 planning is sufficient when:

- A3 artifact compatibility is checked against JSONL/NPZ fields and local image reload behavior.
- Existing provisional visualization output is classified as reusable, modifiable, or obsolete.
- A 1-clip smoke plan records `clip_id`, `chunk_id`, `t0_us` list, stride, seed,
  `num_traj_samples`, expected runtime, expected VRAM, expected output size, and output directory.
- Full inference options are estimated but not executed.
- This Plan exists for review before smoke execution.

A4 smoke is sufficient when:

- The approved 1-clip window list completes or each failure is classified.
- JSONL/NPZ/video outputs are written outside `docs/` when they are large.
- A small docs summary records actual runtime, average runtime per window, peak VRAM, output paths,
  failure status, and full inference expansion risk.
- The Report and Teacher/Evaluator Note are created after smoke execution, or earlier only if the
  Manager/user explicitly requests a pre-smoke review artifact.

## Artifact Boundary

The current stage is planning review. A4 should not produce a full Report or Teacher/Evaluator Note
before smoke execution unless the Manager/user asks for an explicit pre-smoke review artifact.

The expected document sequence is:

1. Plan in `review` state for smoke approval.
2. Smoke execution only after approval.
3. A4 Report with actual runtime, peak VRAM, output paths, failure status, and expansion judgment.
4. Teacher/Evaluator Note that explains the produced smoke/demo artifact and tests whether the
   user understands what it does and does not prove.

## A3 Artifact Compatibility Check

A4 should use the A3 JSONL as the run index and the NPZ as the small tensor store.

Required A3 fields for A4:

- `clip_id`
- `chunk_id`
- `t0_us`
- `seed`
- `num_traj_samples`
- `num_traj_sets`
- `status`
- `failure_reason`
- `data_load_sec`
- `inference_sec`
- `runtime_sec`
- `peak_vram_mib`
- `ade`
- `minade`
- `minade_interpretation`
- `coc_text`
- `output_npz_keys`

Required A3 tensors:

- `<clip_id>__pred_xyz`
- `<clip_id>__pred_rot`
- `<clip_id>__ego_history_xyz`
- `<clip_id>__ego_future_xyz`
- `<clip_id>__absolute_timestamps`

A4 must reload image frames from local PAI using `(dataset_root, chunk_id, clip_id, t0_us)`.
Images are not copied into A3 artifacts and should not be copied into docs artifacts.

## Existing Provisional Visualization Decision

Decision: `modify`.

The existing `scripts/visualize_a3_pilot.py` is useful for the single-`t0_us` pilot because it
already reconstructs local images and renders:

- camera image grid;
- ego history;
- ground-truth future;
- predicted future;
- CoC text;
- ADE/minADE;
- `num_traj_samples=1` metric caveat.

It is not sufficient as-is for sliding-window demo because it keys NPZ tensors by `clip_id` only
and writes one animation per single A3 row. Sliding-window A4 needs keys that include
`clip_id`, `t0_us`, and window index, plus a video schema that displays ordered windows.

The existing outputs under `experiments/a4_visualization/2026-06-08-a3-pilot/` should be retained
as provisional A3-pilot visualization evidence. A4 smoke/full-demo outputs should be regenerated
under `experiments/a4_visualization/2026-06-08-a4-demo/`.

## 1-Clip Sliding-Window Smoke Plan

Smoke target:

- `clip_id`: `c23d0ac1-fe93-4f25-bf71-198ccec5c190`
- `chunk_id`: `3119`
- selection reason: A3 reports this as the right-lane-change CoC clip, making it the best first
  case for reasoning-action visual sanity review.
- `t0_us` list: `[3_100_000, 4_100_000, 5_100_000, 6_100_000, 7_100_000]`
- stride/window interval: `1.0s`
- number of windows: `5`
- seed: `42`
- `num_traj_samples`: `1`
- output directory:
  `experiments/a4_visualization/2026-06-08-a4-demo/smoke-c23d0ac1/`
- small summary directory:
  `docs/artifacts/a4_visualization/2026-06-08-summary/`

Smoke execution script:

```bash
cd /home/user/Workspace/alpamayo
scripts/run_a4_sliding_window_smoke.sh
```

The script is prepared for smoke execution but should only be run after Manager/user approval.

Smoke video layout:

- front-wide `t0` camera panel with projected ground-truth and predicted future waypoints;
- 4-camera context panel for cross-left, front-wide, cross-right, and front-tele;
- BEV trajectory panel with ego history, ground-truth future, predicted future, and `t0`;
- metric and CoC panel with ADE/minADE, seed, `num_traj_samples`, `t0_us`, and validation-scope
  caveat.

Pre-smoke read-only evidence:

- A3 pilot loaded the same clip at `t0_us=5_100_000`.
- Data-only probes loaded all five proposed `t0_us` values without running model inference.
- The same clip has egomotion coverage of roughly `140s`, but the smoke intentionally covers only
  five windows.

Expected compute and storage:

- expected model load: about `4s`;
- expected per-window runtime after model load: about `2-3s`, based on A3 pilot rows;
- expected total inference runtime: about `15-25s`;
- expected visualization runtime: under `1min`;
- expected peak CUDA allocation: about `22GiB`;
- expected docs summary size: under `1MB`;
- expected experiment output size: about `2-10MB`;
- expected smoke video length: about `5s` when rendered as one ordered window per second.

Stop conditions:

- any CUDA OOM;
- any unexpected dataset contract failure for an approved `t0_us`;
- any output growth that would put large media under `docs/`;
- any script change that would require broad A3 runner refactoring instead of a narrow A4 wrapper.

## Full Inference Options After Smoke Gate

Full inference must wait for smoke result reporting and user/Manager approval.

Option A: same clip full sliding-window demo.

- target: `c23d0ac1-fe93-4f25-bf71-198ccec5c190`
- rough window count at `1.0s` stride: about `130`
- expected runtime: about `5-8min` inference plus visualization
- expected output size: tens of MB depending on video encoding
- advantage: best continuity check for one semantic lane-change case
- risk: still not closed-loop validation; CoC may remain visually plausible but unverified

Option B: 5-clip limited-window demo.

- target: A3's five pilot clips
- rough window count: `5 clips x 5 windows = 25`
- expected runtime: about `2-4min` inference plus visualization
- expected output size: tens of MB
- advantage: broader scene variety with bounded cost
- risk: sparse windows may not read like a continuous full-clip demo

Option C: 5-clip full-window demo.

- target: A3's five pilot clips
- rough window count at `1.0s` stride: about `650`
- expected runtime: about `25-45min` inference plus visualization
- expected output size: tens to hundreds of MB
- advantage: strongest demo coverage within A3's five selected clips
- risk: expensive, easy to overinterpret, and still not closed-loop or model-quality validation

## Output Schema Target

Sliding-window JSONL should contain one row per `(clip_id, t0_us, seed, num_traj_samples)`.

Required fields:

- `run_id`
- `clip_id`
- `chunk_id`
- `window_index`
- `t0_us`
- `stride_us`
- `seed`
- `num_traj_samples`
- `num_traj_sets`
- `status`
- `failure_reason`
- `data_load_sec`
- `inference_sec`
- `runtime_sec`
- `peak_vram_mib`
- `ade`
- `minade`
- `minade_interpretation`
- `coc_text`
- `output_npz_keys`
- `preview_png`
- `video_frame_index`

Large media should go under `experiments/a4_visualization/...`. Small Markdown or JSON summaries
may go under `docs/artifacts/a4_visualization/2026-06-08-summary/`.

## A5/A6 Handoff Implications

- A4 output can help A5 choose replay or simulator smoke scenes, but it does not prove closed-loop
  behavior.
- A4 output can help A6 reason about BEV/3D visualization feasibility, but it does not create new
  3D labels or reconstruction evidence.
- A4 must preserve the distinction between visual sanity checking and model quality validation.

## Review Questions

1. Can the reviewer explain why A4 starts with the right-lane-change clip?
2. Can the reviewer distinguish A3's single-`t0_us` pilot from A4's sliding-window smoke?
3. Can the reviewer explain why `num_traj_samples=1` makes minADE a single-sample ADE?
4. Can the reviewer identify which outputs belong in `docs/` and which belong in `experiments/`?

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-06-08 17:03:01 KST | created | A4 planning artifact created before smoke approval |
| 2026-06-08 17:03:01 KST | success criteria, artifact boundary | Report/Note creation moved to post-smoke stage unless explicitly requested |
| 2026-06-08 17:10:00 KST | smoke execution script | Added prepared smoke command path without executing inference |
| 2026-06-08 17:18:00 KST | smoke video layout | Added front-wide waypoint projection and richer trajectory panels to planned smoke output |
