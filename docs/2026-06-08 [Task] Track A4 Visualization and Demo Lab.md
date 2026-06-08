---
doc_type: task
task_role: subtask
status: in_progress
task_id: alpamayo-rnd-a4-visualization-demo-lab
parent_plan: docs/2026-06-08 [Plan] Track A4 Visualization and Demo Lab.md
parent_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
created_at: 2026-06-08 17:25:54 KST
updated_at: 2026-06-08 19:36:53 KST
---

# Track A4 Visualization and Demo Lab

## Objective

Turn A3-compatible Alpamayo inference outputs into human-reviewable visualization and demo video
artifacts, then scale from a 1-clip smoke to target-clip full-window processing only after runtime,
storage, and GPU utilization are reviewed.

## Current Roll-Up

Status: `in_progress`

The 1-clip smoke has completed successfully and the rendered video is acceptable for review. The
first full-target attempt was invalidated because the manifest used egomotion timestamps alone and
created windows beyond the available camera frame timestamp range. The partial outputs and logs were
removed per Manager instruction, the manifest generator now intersects egomotion and camera
timestamp bounds, and the corrected 2-GPU run is in progress.

## Completed Evidence

Smoke target:

- `clip_id`: `c23d0ac1-fe93-4f25-bf71-198ccec5c190`
- `chunk_id`: `3119`
- `t0_us`: `[3_100_000, 4_100_000, 5_100_000, 6_100_000, 7_100_000]`
- stride: `1_000_000us`
- seed: `42`
- `num_traj_samples`: `1`
- result: `5/5` windows succeeded
- total runtime: `30.975s`
- mean runtime/window after model load: `2.148s`
- peak CUDA allocated memory: `22_026 MiB`
- output video: `experiments/a4_visualization/2026-06-08-a4-demo/smoke-c23d0ac1/smoke_demo.mp4`
- output JSONL: `experiments/a4_visualization/2026-06-08-a4-demo/smoke-c23d0ac1/results.jsonl`
- output NPZ: `experiments/a4_visualization/2026-06-08-a4-demo/smoke-c23d0ac1/predictions.npz`
- summary JSON: `docs/artifacts/a4_visualization/2026-06-08-summary/2026-06-08-a4-smoke-c23d0ac1.json`
- summary Markdown: `docs/artifacts/a4_visualization/2026-06-08-summary/2026-06-08-a4-smoke-c23d0ac1.md`

Visualization update:

- front-wide `t0` camera panel now overlays projected ground-truth and predicted future waypoints;
- BEV panel shows ego history, ground-truth future, predicted future, and `t0`;
- 4-camera context panel remains visible;
- metric/CoC panel shows ADE/minADE, seed, `num_traj_samples`, and validation-scope caveat.

## Performance Review Gate

Question: before running all target clip frames, is the current implementation efficient enough, or
does A4 need a sharded multi-GPU runner?

Current evidence:

- The smoke runner loads `AlpamayoR1` once per process, then loops through all approved `t0_us`
  windows in that process.
- The smoke runner does not reload the model for every window.
- Peak CUDA allocation is about `22.0 GiB` on a 24 GiB RTX 4090, so one model replica can fit per
  GPU but leaves little headroom.
- The current shell wrapper defaults to `CUDA_VISIBLE_DEVICES=0`, so it does not use GPU 1.
- `nvidia-smi` shows two RTX 4090 GPUs available.
- The current script accepts one `clip_id` and one `t0_us` list, so full target processing would
  require either manual sharding or a new batch/shard wrapper.

Preliminary judgment:

- Same-clip full-window processing can run with the current script if the `t0_us` list is generated
  externally and passed to one process.
- Five target clips should not be run as one long single-GPU serial job if faster feedback is
  needed.
- The practical acceleration path is two independent processes, one pinned to each GPU, with
  disjoint clip/window shards and separate output directories.
- In-process multi-GPU model parallelism is not the first choice here because the model already
  fits on one GPU, and the workload is embarrassingly parallel across `(clip_id, t0_us)` windows.

Recommended next implementation before full target processing:

1. Add or prepare a fixed A4 full-target runner that reads the canonical 100ms manifest. Done.
2. Keep only the GPU id as user input; all experiment parameters remain fixed in the script. Done.
3. Launch one worker per GPU with fixed clip ownership and separate `CUDA_VISIBLE_DEVICES`. Done.
4. Write each clip's JSONL/NPZ/video under its own output directory. Done in the prepared worker.
5. Avoid merge for the primary A4 full-target run because each clip is owned by exactly one worker.

## Prepared Full-Target Tooling

Fixed GPU-specific launcher:

```bash
cd /home/user/Workspace/alpamayo
scripts/run_a4_window_manifest_2gpu.sh 0
scripts/run_a4_window_manifest_2gpu.sh 1
```

Run the two commands in separate tmux sessions. The only accepted input is the GPU id, `0` or `1`.
All other experiment parameters are fixed inside the script so the A4 run remains a stable
experiment record.

The launcher internally defines:

- manifest path:
  `docs/artifacts/a4_visualization/2026-06-08-summary/a4-target-windows-100ms.jsonl`
- stride: `100_000us` (`0.1s`)
- output root: `experiments/a4_visualization/2026-06-08-a4-demo/target-full-100ms/`
- GPU 0 worker clips:
  - `ac321da3-3848-4736-a9c2-053be0bea770`
  - `b8fa0288-f799-4443-ba62-4601c45fe133`
  - `cb656c5d-7520-4cc2-9e87-889f061fc6cb`
- GPU 1 worker clips:
  - `ac7ac12e-7371-47ec-987d-61e0b3c7693f`
  - `c23d0ac1-fe93-4f25-bf71-198ccec5c190`

Concurrent launch behavior:

- Both GPU sessions may start independently.
- Manifest generation is guarded by a file lock, so concurrent starts do not corrupt the manifest.
- Each GPU process owns complete clips and writes clip-local outputs.

Invalidated full-target attempt:

- run root removed: `experiments/a4_visualization/2026-06-08-a4-demo/target-full-100ms/`
- removed logs:
  - `docs/logs/2026-06-08-a4-target-full-100ms-gpu0.log`
  - `docs/logs/2026-06-08-a4-target-full-100ms-gpu1.log`
  - `docs/logs/2026-06-08-a4-target-full-100ms-monitor.log`
- failure mode: timestamp range overflow at approximately `t0_us=20_000_000` to
  `20_100_000`;
- root cause: manifest generation used egomotion timestamp range but inference also requires camera
  frames at `[t0-0.3s, t0-0.2s, t0-0.1s, t0]`;
- worker visibility fix: clip summaries now record `expected_windows`, `processed_windows`, and
  `completion_status` so partial clips are not mistaken for complete full-target outputs.

Corrected `0.1s` manifest:

- path: `docs/artifacts/a4_visualization/2026-06-08-summary/a4-target-windows-100ms.jsonl`
- total windows: `917`
- GPU 0 assigned windows: `550`
- GPU 1 assigned windows: `367`
- per-clip windows:
  - `ac321da3-3848-4736-a9c2-053be0bea770`: `184`, `t0_us=1_700_000..20_000_000`
  - `ac7ac12e-7371-47ec-987d-61e0b3c7693f`: `183`, `t0_us=1_700_000..19_900_000`
  - `b8fa0288-f799-4443-ba62-4601c45fe133`: `183`, `t0_us=1_700_000..19_900_000`
  - `c23d0ac1-fe93-4f25-bf71-198ccec5c190`: `184`, `t0_us=1_700_000..20_000_000`
  - `cb656c5d-7520-4cc2-9e87-889f061fc6cb`: `183`, `t0_us=1_700_000..19_900_000`

Merge status:

- No merge is required for the primary A4 full-target run.
- Each clip is assigned to exactly one GPU worker.
- Each clip writes its own `results.jsonl`, `predictions.npz`, `demo.mp4`,
  `video_manifest.json`, and `run_summary.json`.
- The older generic shard/merge scripts may remain as utilities, but they are not the primary A4
  execution path because they split windows across shards and make clip-level review harder.

Runtime estimate:

- smoke mean per-window runtime: `2.148s`;
- 917 corrected windows on one GPU: roughly `33m` window runtime, plus model load and IO/render
  overhead;
- fixed clip-owned 2-GPU run: GPU 0 has `550` windows and GPU 1 has `367` windows;
- practical expected wall time is bounded by GPU 0: roughly `20m` inference plus IO/render
  overhead;
- the clip-owned split is intentionally less balanced than window-level modulo sharding because it
  avoids merge and preserves one output directory per clip.

Current corrected run:

- launch time: `2026-06-08 18:25 KST`;
- tmux sessions:
  - `alpamayo-a4-gpu0`
  - `alpamayo-a4-gpu1`
  - `alpamayo-a4-monitor`
- initial status at `2026-06-08 18:26 KST`: both workers loaded the model and started processing
  windows with no failed windows observed yet.

Full-target completion:

- GPU 0 completed `550/550` windows with `0` failed windows.
- GPU 1 completed `367/367` windows with `0` failed windows.
- All five clip-level outputs are marked `completion_status=complete`.

BEV render update:

- First clip only rerendered for review:
  `experiments/a4_visualization/2026-06-08-a4-demo/target-full-100ms/ac321da3-3848-4736-a9c2-053be0bea770/demo_bev_scale3.mp4`
- Rerender source: existing `results.jsonl` and `predictions.npz`; inference was not rerun.
- BEV view uses three fixed presets: `short`, `medium`, `long`.
- First clip selected `medium`: lateral `[-3.5m, 3.5m]`, longitudinal `[-16m, 85m]`.
- BEV panel now uses independent fixed x/y axes for A4 demo readability, so lateral variation is
  easier to inspect but the plot is not metric-equal aspect.
- The previous first-clip `demo.mp4` became unreadable because the MP4 container was not finalized
  (`moov atom not found`). The renderer now writes to a temporary MP4 and atomically replaces the
  target only after `VideoWriter.release()`.

All-local run:

- Scope: all locally downloaded PAI chunks with `egomotion` and the four A4 cameras available.
- Chunks: `156`, `297`, `727`, `1843`, `1864`, `1875`, `2129`, `2281`, `3119`, `3135`.
- Clips: `772`.
- Windows at `100_000us` stride: `139_534`.
- Manifest:
  `docs/artifacts/a4_visualization/2026-06-08-summary/a4-all-local-windows-100ms.jsonl`.
- Output root:
  `experiments/a4_visualization/2026-06-08-a4-demo/all-local-100ms/`.
- GPU 0 chunks: `727`, `1875`, `156`, `3135`, `297`; assigned windows: `70_159`.
- GPU 1 chunks: `3119`, `1864`, `1843`, `2129`, `2281`; assigned windows: `69_375`.
- Inference workers run with `--skip-video` and `--continue-on-failure`; clip videos are rendered
  by a separate CPU watcher after each clip output is complete.
- Estimated wall time:
  - inference JSONL/NPZ: roughly `41-45h` on two RTX 4090 GPUs;
  - render watcher will trail inference and may extend total wall time depending on IO/decode load.
- Started at `2026-06-08 19:35 KST` in tmux sessions:
  - `alpamayo-a4-all-gpu0`
  - `alpamayo-a4-all-gpu1`
  - `alpamayo-a4-all-render`
  - `alpamayo-a4-all-monitor`
- Initial status at `2026-06-08 19:36 KST`: GPU 0 `22/70_159`, GPU 1 `22/69_375`, failed windows
  `0`.

## Next Decision

Choose the full target processing mode:

- Option A: one target clip full-window, single GPU, lowest coordination risk.
- Option B: five target clips limited-window, two GPU shards, fastest next feedback.
- Option C: five target clips full-window, two GPU shards, highest cost but closest to target demo.

A4 should not start Option B or C until the sharded execution approach is accepted or implemented.

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-06-08 17:25:54 KST | created | A4 smoke accepted visually; full target processing requires performance and GPU utilization review |
| 2026-06-08 17:25:54 KST | prepared tooling | Added fixed 100ms manifest and clip-owned 2-GPU execution path without merge |
| 2026-06-08 17:25:54 KST | launcher input | Changed full-target launcher to accept only GPU id for tmux-per-GPU execution |
| 2026-06-08 18:26:20 KST | corrected manifest | Removed invalid partial full-target outputs, fixed manifest camera timestamp bounds, and restarted the 2-GPU run |
| 2026-06-08 19:22:48 KST | BEV rerender | Added three-level fixed BEV scale, rerendered first clip only, and recorded MP4 finalization issue |
| 2026-06-08 19:36:53 KST | all-local execution | Added all-local manifest/worker/render watcher path and started 772-clip execution |
