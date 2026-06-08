---
doc_type: report
status: done
track: A3
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-06-08 [Task] Track A3 Inference Experiment Suite.md
created_at: 2026-06-08 12:24:00 KST
updated_at: 2026-06-08 16:41:36 KST
---

# Track A3 Inference Experiment Suite

## Document Frame

Purpose: record the first local PAI subset Alpamayo inference pilot with enough evidence for the
Manager to decide whether A4 visualization can start from the produced outputs.

Primary reader: Alpamayo R&D Manager, A4 visualization session, and the user reviewing A3 limits.

Decision question: did the local PAI subset run produce CoC text, trajectory tensors,
ADE/minADE, runtime, VRAM, failure classification, and an A4-usable output schema?

Exclusion scope: no model-quality claim, no training, no large download, no Root Task update, no
A4 visualization polish.

## Current Conclusion

A3 first gate is satisfied for a 5-clip pilot on local `chunk 3119`.

All five selected clips loaded from the canonical local root and completed Alpamayo inference with
CoC text, `pred_xyz`, `pred_rot`, single-sample ADE/minADE, runtime, peak VRAM, and structured
artifacts. No failure occurred in the pilot. The produced JSONL plus NPZ schema is sufficient for
A4 to reconstruct image inputs from `(dataset_root, clip_id, t0_us)` and plot ego history, ground
truth future, and predicted future.

This is not a model-quality validation. The pilot uses `num_traj_samples=1`, so each reported
`minADE` is effectively the ADE of a single sampled trajectory, not best-of-K minADE.

Scope decision, 2026-06-08 16:41:36 KST:

- A3 is accepted as a contract-validation pilot and should be closed at the current scope.
- No separate A4-prep track is needed.
- Full-clip or sliding-window inference for demo video should be handled inside A4 visualization,
  where each clip can be inferred across many valid `t0_us` windows and rendered together.
- A3 therefore records only single-`t0_us` evidence per selected clip. It does not claim temporal
  rollout stability or continuous per-frame prediction coverage.

Correction note, 2026-06-08 13:54:50 KST:

- The original A3 pilot evidence was generated with an inline Python runner executed from the
  terminal, not with a committed repo script.
- That was insufficient for the "reproducible command/script path" acceptance criterion.
- The reproducible runner paths are now `scripts/run_a3_inference_pilot.sh` and
  `scripts/run_a3_inference_pilot.py`.
- The new runner has not yet been executed after this correction. Manager/user approval is required
  before re-running it because it loads the model and writes inference artifacts.

## Execution Path

Canonical shell runner:

```bash
cd /home/user/Workspace/alpamayo
scripts/run_a3_inference_pilot.sh
```

The shell runner sets `CUDA_VISIBLE_DEVICES=0` and
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` when they are not already set, then delegates to
`scripts/run_a3_inference_pilot.py`.

The Python runner defaults to offline/cache-only model loading. It sets
`TRANSFORMERS_OFFLINE=1` and `HF_HUB_OFFLINE=1` internally unless `--allow-download` is provided.

Canonical Python runner, equivalent to the shell default:

```bash
cd /home/user/Workspace/alpamayo
CUDA_VISIBLE_DEVICES=0 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
ar1_venv/bin/python scripts/run_a3_inference_pilot.py \
  --pilot-name 2026-06-08-pilot-canonical \
  --seed-check-name 2026-06-08-seed-check-canonical
```

Default run configuration:

- dataset root: `/data/datasets/physical_ai_av`
- output root: `docs/artifacts/a3_inference`
- log directory: `docs/logs`
- chunk IDs: `[3119]`
- clip IDs:
  - `ac321da3-3848-4736-a9c2-053be0bea770`
  - `ac7ac12e-7371-47ec-987d-61e0b3c7693f`
  - `b8fa0288-f799-4443-ba62-4601c45fe133`
  - `c23d0ac1-fe93-4f25-bf71-198ccec5c190`
  - `cb656c5d-7520-4cc2-9e87-889f061fc6cb`
- `t0_us`: `5_100_000`
- pilot seed: `42`
- seed-check seeds: `[42, 43, 44]`
- `num_traj_samples`: `1`
- `num_traj_sets`: `1`
- `top_p`: `0.98`
- `temperature`: `0.6`
- `max_generation_length`: `256`
- CUDA device: `0`
- max memory: `23GiB`

Expected output paths from the canonical runner:

- `docs/artifacts/a3_inference/2026-06-08-pilot/results.jsonl`
- `docs/artifacts/a3_inference/2026-06-08-pilot/predictions.npz`
- `docs/artifacts/a3_inference/2026-06-08-pilot/run_summary.json`
- `docs/artifacts/a3_inference/2026-06-08-seed-check/results.jsonl`
- `docs/artifacts/a3_inference/2026-06-08-seed-check/run_summary.json`
- `docs/logs/2026-06-08-pilot.log`
- `docs/logs/2026-06-08-seed-check.log`

Historical execution caveat:

The currently committed artifacts below were generated before this canonical runner existed. They
match the same model path, dataset root, clip list, seed, `num_traj_samples`, and output schema, but
the exact inline runner code was not preserved as a script. Treat them as valid historical evidence
with a reproducibility caveat until the canonical runner is executed and compared.

## Evidence Summary

Local data evidence:

- Actual canonical dataset root: `/data/datasets/physical_ai_av`
- Requested historical subset paths were not present as separate directories during this session.
- The canonical root size is `271G`.
- Available selected chunks on disk: `0156`, `0297`, `0727`, `1843`, `1864`, `1875`, `2129`,
  `2281`, `3119`, `3135`.
- Selected 10 chunks contain `772` clips with the A3/A4 required features.
- `chunk 3119` contains `100` required-feature clips.
- One data-contract smoke loaded:
  - `image_frames`: `(4, 4, 3, 1080, 1920)`
  - `ego_history_xyz`: `(1, 1, 16, 3)`
  - `ego_future_xyz`: `(1, 1, 64, 3)`
  - `absolute_timestamps`: `(4, 4)`

Runtime environment:

- Python environment: `ar1_venv`
- GPU: `NVIDIA GeForce RTX 4090`, 24564 MiB total on GPU 0
- Package versions:
  - `torch==2.8.0`
  - `transformers==4.57.1`
  - `physical_ai_av==0.2.0`
  - `alpamayo-r1==0.1.0`
  - `pandas==3.0.1`
  - `pyarrow==23.0.1`
- Offline guard:
  - `TRANSFORMERS_OFFLINE=1`
  - `HF_HUB_OFFLINE=1`
  - `local_files_only=True`
- No large additional download was performed.

Runtime-loaded config:

| Field | Value |
| --- | --- |
| `model_id` | `nvidia/Alpamayo-R1-10B` |
| `processor_id` | `Qwen/Qwen3-VL-2B-Instruct` |
| `model_class` | `AlpamayoR1` |
| `dtype` | `torch.bfloat16` |
| `device_map` | `{"": 0}` |
| `max_memory` | `{0: "23GiB"}` |
| `vlm_name_or_path` | `Qwen/Qwen3-VL-8B-Instruct` |
| `tokens_per_history_traj` | `48` |
| `tokens_per_future_traj` | `128` |
| `traj_vocab_size` | `4000` |
| `top_p` | `0.98` |
| `temperature` | `0.6` |
| `max_generation_length` | `256` |
| `num_traj_samples` | `1` |
| `num_traj_sets` | `1` |
| `seed` | `42` |
| `t0_us` | `5_100_000` |

Evidence artifacts:

- Pilot log: `docs/logs/2026-06-08-a3-5clip-pilot.log`
- Pilot summary: `docs/artifacts/a3_inference/2026-06-08-pilot/run_summary.json`
- Pilot result table: `docs/artifacts/a3_inference/2026-06-08-pilot/results.jsonl`
- Pilot tensors: `docs/artifacts/a3_inference/2026-06-08-pilot/predictions.npz`
- Seed check log: `docs/logs/2026-06-08-a3-seed-check.log`
- Seed check result table: `docs/artifacts/a3_inference/2026-06-08-seed-check/results.jsonl`

## What Was Executed in the Historical Inline Run

The inline runner performed the following control flow:

1. Set offline/cache-only guards:
   - `TRANSFORMERS_OFFLINE=1`
   - `HF_HUB_OFFLINE=1`
2. Load local PAI data through
   `PhysicalAIAVDatasetLocalInterface("/data/datasets/physical_ai_av", chunk_ids=[3119])`.
3. For each selected clip, call:
   `load_physical_aiavdataset(clip_id, t0_us=5_100_000, avdi=avdi, maybe_stream=False)`.
4. Build model messages from `data["image_frames"].flatten(0, 1)` with
   `helper.create_message()`.
5. Load `AlpamayoR1.from_pretrained("nvidia/Alpamayo-R1-10B", dtype=torch.bfloat16,
   device_map={"": 0}, max_memory={0: "23GiB"}, local_files_only=True)`.
6. Load `Qwen/Qwen3-VL-2B-Instruct` processor with the model tokenizer.
7. Run `model.sample_trajectories_from_data_with_vlm_rollout(...)` with:
   - `top_p=0.98`
   - `temperature=0.6`
   - `num_traj_samples=1`
   - `num_traj_sets=1`
   - `max_generation_length=256`
   - `return_extra=True`
8. Compute ADE/minADE by comparing predicted XY future trajectory with
   `ego_future_xyz` XY over 64 future steps.
9. Write per-clip JSONL rows and compressed NPZ trajectory tensors.
10. Run the first clip again with seeds `42`, `43`, and `44` for seed-variance evidence.

## 5-Clip Pilot Result

All rows use `chunk_id=3119`, `t0_us=5_100_000`, `seed=42`, `num_traj_samples=1`,
`num_traj_sets=1`.

| Clip ID | CoC summary | ADE | minADE | Runtime sec | Peak VRAM MiB | Failure |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `ac321da3-3848-4736-a9c2-053be0bea770` | Keep distance to the lead vehicle because it is directly ahead in the same lane | 0.8285 | 0.8285 | 2.470 | 22026.0 | none |
| `ac7ac12e-7371-47ec-987d-61e0b3c7693f` | Adjust speed to keep safe distance from the vehicle ahead | 0.6219 | 0.6219 | 2.307 | 22026.0 | none |
| `b8fa0288-f799-4443-ba62-4601c45fe133` | Keep distance to the lead vehicle because it is ahead in the same lane | 0.9802 | 0.9802 | 1.960 | 22026.0 | none |
| `c23d0ac1-fe93-4f25-bf71-198ccec5c190` | Change lanes right due to slower traffic ahead and an available right-lane gap | 1.1155 | 1.1155 | 2.206 | 22026.0 | none |
| `cb656c5d-7520-4cc2-9e87-889f061fc6cb` | Keep speed through the intersection since the traffic light is green | 0.7419 | 0.7419 | 2.792 | 22026.0 | none |

Aggregate pilot numbers:

- Success count: `5 / 5`
- minADE range: `0.6219` to `1.1155` meters
- mean single-sample ADE/minADE: `0.8576` meters
- mean per-clip runtime after model load: `2.347` seconds
- max measured per-clip peak VRAM: `22026.0` MiB

## Result Analysis

Execution result:

- The pilot is primarily a runtime/data-contract success: all five local `chunk 3119` clips loaded
  and produced CoC text, `pred_xyz`, `pred_rot`, ADE/minADE, runtime, and VRAM evidence.
- There were no failed clips, so no concrete `data contract`, `model/runtime`, `GPU memory`,
  `dependency`, or `output schema` failure was observed.
- Peak CUDA allocation was about `22.0 GiB`, which is close to the usable capacity of a 24 GiB
  RTX 4090. This makes larger `num_traj_samples` a memory-risk item, not a free next step.

Metric interpretation:

- Because `num_traj_samples=1`, the reported `minADE` is numerically the same as the one sampled
  trajectory's ADE.
- The 5-clip mean of `0.8576m` is useful as an open-loop pilot signal for these exact clips, but it
  must not be compared to paper-level dataset metrics or used as a model-quality claim.
- The highest pilot ADE/minADE was clip `c23d0ac1-fe93-4f25-bf71-198ccec5c190` at `1.1155m`.
  Its CoC summary says the model chose a right lane change due to slower traffic and an available
  right-lane gap. A4 should visualize this clip first because lane-change intent is more
  semantically loaded than simple keep-distance behavior.
- The lowest pilot ADE/minADE was clip `ac7ac12e-7371-47ec-987d-61e0b3c7693f` at `0.6219m`.
  Its CoC summary is a simple keep-distance/speed-adjustment statement. This is a good baseline
  visualization clip, but low ADE alone does not prove CoC correctness.

CoC pattern:

- Four of five clips generated conservative longitudinal behavior summaries such as keeping
  distance, adjusting speed, or keeping speed through a green signal.
- One clip generated a lateral action summary, the right-lane-change case. This is the most useful
  clip for A4 to inspect for reasoning-action consistency.
- The report does not grade whether each CoC is visually true. That remains an A4 visual review
  task because it requires inspecting images, trajectory shape, and scene context together.

Seed variance:

- The first clip produced `0.8285m`, `0.8084m`, and `0.5626m` under seeds `42`, `43`, and `44`.
- This spread is enough to show that the stochastic inference path can change the sampled
  trajectory under the same clip and config.
- Future A3 expansion must report seed and `num_traj_samples` with every row. A result table that
  omits either field is not comparable.

A4 handoff implication:

- A4 can start with the existing schema because it has `clip_id`, `chunk_id`, `t0_us`, CoC text,
  `pred_xyz`, `pred_rot`, `ego_history_xyz`, `ego_future_xyz`, and timestamps.
- A4 should treat the existing A3 artifacts as a schema and contract reference, not as the final
  demo input. For demo video, A4 should run its own sliding-window inference over each target clip
  and visualize the resulting rolling 6.4s forecasts.
- A4 should prioritize:
  1. the right-lane-change clip for reasoning-action visual inspection;
  2. one low-ADE keep-distance clip for baseline sanity;
  3. the seed-check clip if A4 wants to show stochastic variation.
- A4 should not request additional PAI download before testing these five clips because the local
  root and tensor artifacts are already sufficient for first visualization.

## Seed Check

The seed check used the first pilot clip only:
`ac321da3-3848-4736-a9c2-053be0bea770`.

| Seed | ADE | minADE | Runtime sec | Peak VRAM MiB | Failure |
| ---: | ---: | ---: | ---: | ---: | --- |
| 42 | 0.8285 | 0.8285 | 1.439 | 22026.0 | none |
| 43 | 0.8084 | 0.8084 | 1.128 | 22026.0 | none |
| 44 | 0.5626 | 0.5626 | 1.063 | 22026.0 | none |

Interpretation: the same clip can produce different sampled trajectories across seeds. This is a
sampling-variance signal, not proof that one seed is better in deployment. Because
`num_traj_samples=1`, the reported `minADE` remains single-sample ADE for each seed.

## Output Schema for A4

Schema version: `a3_pilot_v1`

Primary result table: JSONL, one row per inference run.

Required JSONL fields:

- `run_id`: stable run identifier.
- `clip_id`: PAI clip ID.
- `chunk_id`: source PAI chunk.
- `t0_us`: inference timestamp in microseconds.
- `seed`: sampling seed.
- `num_traj_samples`: trajectory samples per set.
- `num_traj_sets`: trajectory set count.
- `status`: `success` or `failed`.
- `failure_reason`: one of `data contract`, `model/runtime`, `GPU memory`, `dependency`,
  `output schema`, or `null`.
- `runtime_sec`: total per-clip runtime after model load.
- `data_load_sec`: local data loading time when successful.
- `inference_sec`: model inference time when successful.
- `peak_vram_mib`: peak CUDA allocation during the run.
- `image_frames_shape`, `ego_history_xyz_shape`, `ego_future_xyz_shape`, `pred_xyz_shape`,
  `pred_rot_shape`: tensor shape evidence.
- `ade`: XY average displacement error for the single sample when `num_traj_samples=1`.
- `minade`: minimum ADE over samples; same as `ade` when `num_traj_samples=1`.
- `minade_interpretation`: explicit metric caveat.
- `coc_text`: generated Chain-of-Causation text.
- `output_npz_keys`: mapping from semantic tensor names to keys in `predictions.npz`.

Tensor store: compressed NPZ, keyed by `<clip_id>__<tensor_name>`.

Current NPZ tensor names and shapes:

- `<clip_id>__pred_xyz`: `(1, 1, 1, 64, 3)`, `float32`
- `<clip_id>__pred_rot`: `(1, 1, 1, 64, 3, 3)`, `float32`
- `<clip_id>__ego_history_xyz`: `(1, 1, 16, 3)`, `float32`
- `<clip_id>__ego_future_xyz`: `(1, 1, 64, 3)`, `float32`
- `<clip_id>__absolute_timestamps`: `(4, 4)`, `int64`

A4 image reconstruction:

- Images are not duplicated into the artifact.
- A4 should reload image frames from `/data/datasets/physical_ai_av` using `clip_id`, `chunk_id`,
  `t0_us`, the four official camera features, and `maybe_stream=False`.
- This keeps A3 artifacts small and avoids copying large image tensors into docs.

## Failure Classification

No pilot or seed-check run failed.

The runner used these failure classes for future expansion:

- `data contract`: missing feature, invalid timestamp, unexpected tensor shape.
- `model/runtime`: model load, processor, generation, or non-memory runtime failure.
- `GPU memory`: CUDA OOM or memory allocation failure.
- `dependency`: missing import or incompatible package failure.
- `output schema`: JSON/NPZ serialization or schema write failure.

Observed warning:

- `torchao` emitted a warning about incompatible torch version for optional C++ extensions.
- The warning did not block inference and is not classified as a current A3 blocker.

## Limits

- Five clips from one chunk do not establish dataset-wide quality.
- `num_traj_samples=1` means `minADE` is not best-of-K minADE.
- CoC text was recorded but not semantically graded for truthfulness or action consistency.
- Runtime excludes cold environment setup but includes local data load and inference after model
  load for each clip.
- Peak VRAM is CUDA allocated memory, not full process RSS or total reserved system memory.
- A3 did not run continuous per-clip prediction. Each selected clip has one `t0_us` pilot row.
- The A4 schema is sufficient for first visualization, but A4 still must verify rendered image
  alignment and trajectory frame interpretation.

## Next Manager Decision

Recommended immediate decision: close A3 as a contract-validation pilot with the reproducibility
caveat recorded above.

Do not create a separate A4-prep track. A4 should own demo-oriented full-clip or bounded
sliding-window inference and visualization together, using A3's JSONL/NPZ schema and loader contract
as the reference.

Expansion to 20 clips, higher `num_traj_samples`, or dense per-clip `t0_us` sweeps should be treated
as A4 visualization inputs or a later Manager-approved inference pass, not as required A3 closure
work.
