---
doc_type: note
status: done
track: A3
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-06-08 [Task] Track A3 Inference Experiment Suite.md
created_at: 2026-06-08 12:24:00 KST
updated_at: 2026-06-08 16:41:36 KST
---

# Track A3 Inference Review Guide

## Document Frame

Purpose: help the user review the A3 inference pilot design, outputs, and limits well enough to
challenge the next A4 decision.

Primary reader: the user and Manager before accepting A3 evidence or starting A4.

Decision question: can the user explain what the 5-clip pilot proves, what it does not prove, and
how A4 should consume the output schema?

Exclusion scope: no visualization tutorial, no model architecture deep dive beyond A3 runtime
needs, no claim about driving quality.

## What Happened

A3 ran Alpamayo inference on five local PAI clips from `chunk 3119`.

Each run used:

- local root: `/data/datasets/physical_ai_av`
- clip selection: five required-feature clips from `chunk 3119`
- `t0_us=5_100_000`
- `seed=42`
- `num_traj_samples=1`
- offline model/cache mode
- GPU 0 on an RTX 4090

Each successful run produced:

- CoC text
- `pred_xyz`
- `pred_rot`
- ground-truth future trajectory
- ADE and minADE
- runtime
- peak VRAM
- a failure field, which stayed `null`

The artifacts are:

- `docs/artifacts/a3_inference/2026-06-08-pilot/results.jsonl`
- `docs/artifacts/a3_inference/2026-06-08-pilot/predictions.npz`
- `docs/artifacts/a3_inference/2026-06-08-seed-check/results.jsonl`

## How to Read the Result

The important result is not that the model is good. The important result is that the local PAI
subset can drive the full A3 inference path and produce structured evidence.

The current chain is:

```text
local PAI root + chunk_ids
  -> local dataset interface
  -> 4 cameras x 4 frames
  -> 16-step ego history
  -> Alpamayo processor and model
  -> CoC text
  -> pred_xyz and pred_rot
  -> compare pred_xyz XY against ego_future_xyz XY
  -> single-sample ADE/minADE
  -> JSONL and NPZ artifacts for A4
```

The output table answers: "Can we run, log, compare, and hand off the result?" It does not answer:
"Is Alpamayo safe?", "Does the CoC explanation match the scene?", or "How well does the model
generalize across PAI?"

It also does not answer: "Can we show continuous prediction over a whole clip?" A3 used one
`t0_us` per selected clip. Continuous demo output requires A4 to run sliding-window inference over
many valid `t0_us` values for each target clip, then render those rolling forecasts.

## The minADE Trap

`minADE` can sound like a best-of-many metric. In this A3 pilot it is not.

The run used `num_traj_samples=1`. That means there is only one candidate trajectory. Taking the
minimum over one candidate gives the same value as that candidate's ADE.

Correct reading:

- "For this run, minADE is single-sample ADE."
- "A lower number on one clip is not a dataset-quality claim."
- "Changing seed can change the sampled trajectory."

Incorrect reading:

- "This is best-of-K minADE."
- "The model is validated because five minADE values look reasonable."
- "The CoC text is correct because ADE is low."

## Why Seed Check Matters

The same clip was run with seeds 42, 43, and 44.

The single-sample ADE/minADE values were:

- seed 42: `0.8285`
- seed 43: `0.8084`
- seed 44: `0.5626`

This shows sampling variance. It does not mean seed 44 is generally better. It means A3/A4 should
record seed and `num_traj_samples` with every result, otherwise later comparisons become ambiguous.

## A4 Handoff

A4 should use the JSONL as the run index and the NPZ as the tensor store.

For each successful row:

- read `clip_id`, `chunk_id`, and `t0_us`;
- reload image frames from `/data/datasets/physical_ai_av` with `maybe_stream=False`;
- read `pred_xyz`, `ego_history_xyz`, and `ego_future_xyz` from `predictions.npz`;
- plot ego history, ground truth future, and predicted future in the same local ego frame;
- show CoC text next to the plot;
- label the metric as single-sample ADE/minADE when `num_traj_samples=1`.

A4 should not assume image arrays are stored in the NPZ. A3 intentionally stores references and
trajectory tensors, not duplicated image payload.

For demo video, A4 should not be limited to the five single-`t0_us` A3 rows. It should use A3's
contract as the reference schema, then run full-clip or bounded sliding-window inference at the
visualization stage so every rendered forecast has matching input frames, ego history, ground truth
future, prediction, CoC text, and timing metadata.

## Review Questions

1. Why did A3 use `/data/datasets/physical_ai_av` instead of the historical
   `selected_chunks_10_multisensor` path?

Expected answer: the current local state is a single canonical root with selected chunk files
inside it. The run target is expressed with `chunk_ids` and clip selection, not a separate copied
dataset directory.

2. What does the 5-clip pilot prove?

Expected answer: local loading, processor/model inference, CoC generation, trajectory output,
ADE/minADE calculation, runtime/VRAM logging, and A4 handoff schema work for five selected clips.

3. What does it not prove?

Expected answer: it does not prove dataset-wide model quality, closed-loop safety, CoC
truthfulness, generalization, route following, or training readiness.

4. Why is `num_traj_samples=1` important?

Expected answer: with one sample, minADE is effectively the ADE of that single trajectory. It is
not a best-of-K metric.

5. Why must seed be recorded?

Expected answer: the trajectory sampling is stochastic. The same clip produced different ADE values
under seeds 42, 43, and 44, so comparisons without seed are not reproducible enough.

6. What should A4 do with `pred_xyz` and `ego_future_xyz`?

Expected answer: plot predicted and ground-truth future trajectories in the same local ego frame,
then inspect whether the plot and CoC text are coherent enough for visual sanity review.

7. Why is A3 not a continuous clip demo yet?

Expected answer: A3 intentionally uses one `t0_us` per selected clip to validate the data/model/output
contract. A continuous demo needs A4 to run sliding-window inference over many `t0_us` values and
render rolling 6.4s forecasts.

8. If a future clip fails, how should the failure be classified?

Expected answer: use one of `data contract`, `model/runtime`, `GPU memory`, `dependency`, or
`output schema`, then cite the failing code path or artifact.

## Pass Criteria

Pass:

- User can describe the local root plus `chunk_ids` selection model.
- User can explain PAI clip to CoC and `pred_xyz` flow at a high level.
- User explicitly states that `num_traj_samples=1` makes minADE single-sample ADE.
- User can identify the JSONL and NPZ artifacts A4 should read.
- User can distinguish A3 single-`t0_us` contract validation from A4 full-clip sliding-window demo
  inference.
- User does not turn five clips into a model-quality claim.

Partial:

- User understands the run succeeded but confuses ADE/minADE or omits seed/runtime/VRAM evidence.
- User can name artifacts but cannot describe how A4 reconstructs images.

Fail:

- User claims the five clips validate Alpamayo driving quality.
- User treats CoC text as automatically correct.
- User says A4 needs a new large PAI download before trying the produced schema.
- User cannot explain why seed and `num_traj_samples` are part of the result.

## Closure Review Gate

For A3 closure, Manager should confirm the user can answer:

- "What exactly did A3 prove?"
- "Why is this not model-quality validation?"
- "How should A4 use the output schema?"
- "What changes if `num_traj_samples` becomes 2 or 3?"
- "Why does continuous demo output belong in A4 rather than a separate A4-prep track?"

Those answers are now accepted as the intended closure direction: A3 stops at contract validation,
and A4 owns demo-oriented sliding-window inference plus visualization. If a future review conflates
single-sample minADE with best-of-K or quality validation, pause before expanding inference scope.
