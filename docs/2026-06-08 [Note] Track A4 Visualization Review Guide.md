---
doc_type: note
status: review
track: A4
created_at: 2026-06-08 19:46:59 KST
updated_at: 2026-06-08 19:50:21 KST
parent_report: docs/2026-06-08 [Report] Track A4 Visualization and Demo Lab.md
parent_task: docs/2026-06-08 [Task] Track A4 Visualization and Demo Lab.md
---

# Track A4 Visualization Review Guide

## Purpose

This note is the Teacher/Evaluator companion for A4. It helps the reviewer explain what the A4 demo
shows, what it does not prove, and how to inspect the outputs without confusing visual plausibility
with model validation.

## What A4 Built

A3 produced inference results for selected clips at a single `t0_us`. A4 turns that same schema into
sliding-window visual artifacts. Instead of asking "what did the model predict at one timestamp?",
A4 asks "how do predictions change as we move through the clip at repeated timestamps?"

A4 output combines four kinds of evidence:

- camera context at each timestamp;
- ego history and ground-truth future from the local dataset;
- model predicted future trajectory;
- text/metrics from the A3 inference row, including CoC text and ADE/minADE.

The completed five-clip target run uses `0.1s` windows. That makes the output feel like a clip-level
demo rather than five isolated screenshots.

## Completed Target vs In-Progress All-Local

The completed A4 evidence is the five-clip target run: `917/917` windows succeeded and each target
clip has a complete video and summary.

The all-local run is different. It covers `772` local clips and `139,534` windows, but it is still
running. Treat all-local counts as progress telemetry until the run finishes and failures, render
coverage, runtime, and storage are reviewed.

Correct phrasing:

- "The five target clips are complete."
- "The all-local run is in progress and not yet final evidence."

## A3 Single-`t0_us` vs A4 Sliding Window

A3 single-`t0_us` pilot:

- one selected timestamp per clip;
- one inference row per clip;
- useful for schema validation and first-pass sanity checks;
- not enough to inspect temporal stability.

A4 sliding-window demo:

- many timestamps per clip;
- one inference row per `(clip_id, t0_us)`;
- predictions can be watched over time;
- useful for spotting jitter, delayed turns, inconsistent stopping, or visual/metric mismatch.

The important difference is not just "more frames." A4 creates an ordered review object. The user
can ask whether the model's predicted future evolves coherently as the observed scene changes.

## How to Read the Demo

When reviewing a video, inspect these panels separately.

Front camera overlay:

- predicted future trajectory projected onto the image;
- ground-truth future trajectory projected onto the image;
- useful for seeing whether the planned path visually aligns with the lane or road geometry.

BEV panel:

- ego history shows where the vehicle came from;
- ground-truth future shows the dataset future;
- predicted future shows the model's output;
- fixed axes help compare speed/trajectory length across windows.

For first-clip BEV review, prefer `demo_bev_metric_scale3.mp4` over the older `demo.mp4` or
`demo_bev_scale3.mp4` because it uses metric-equal BEV scaling. For the other four target clips,
use the available `demo.mp4` unless they are rerendered with the metric BEV option.

Text and metrics:

- CoC text is the model's generated explanation;
- ADE/minADE summarize trajectory error for the displayed future;
- seed and `num_traj_samples` identify the run configuration.

The CoC text should be treated as a hypothesis or model explanation, not as ground truth.

## What A4 Shows

A4 can show:

- whether the renderer can reconstruct local images and trajectories from A3-compatible artifacts;
- whether predicted and ground-truth trajectories are visibly aligned or divergent;
- whether prediction length changes with apparent speed;
- whether predictions jitter laterally or temporally;
- whether CoC text and trajectory output appear mutually consistent;
- whether generated outputs are complete enough for human review.

A4 can also reveal engineering bugs, such as invalid timestamp windows, missing camera coverage, or
corrupt MP4 finalization.

## What A4 Does Not Prove

A4 does not prove:

- the model is good at driving;
- the model is safe;
- the model would behave correctly in closed loop;
- the CoC text is causally faithful;
- the model understands user intention;
- the model would obey arbitrary route or command prompts;
- low ADE on a displayed clip generalizes to other data.

The demo is a visual sanity artifact. It can motivate deeper evaluation, but it is not itself a
validation benchmark.

## Intention and Prompt Caveat

For the discussed right-turn or lane-change cases, the model input is primarily visual context,
ego trajectory, and the default prompt. If a clip is in a turn lane or the scene strongly implies a
turn, the model can predict a turn from context without receiving an explicit high-level intention.

That is different from intention-conditioned driving. To claim intention following, the system
would need a clear contract such as:

- route or maneuver labels in the dataset;
- prompts that explicitly encode the desired intention;
- training or evaluation evidence that changing the intention changes the prediction while keeping
  the scene fixed;
- tests for conflicting or ambiguous instructions.

Without that contract, it is risky to expect arbitrary future intention prompts to be obeyed simply
because some default-prompt predictions match ground truth in intention-like situations.

## Metric Caveat

The A4 runs use `num_traj_samples=1`. In this configuration, minADE is not a best-of-many sampling
metric. It is effectively single-sample ADE.

Correct phrasing:

- "minADE is single-sample ADE for this run."

Incorrect phrasing:

- "The model selected the best of multiple generated trajectories."

## Review Checklist

Use this checklist when looking at a rendered clip:

- Are all windows rendered in time order?
- Does the front camera overlay show both predicted and ground-truth future?
- Does the BEV panel show ego history, ground-truth future, prediction, and `t0`?
- Are BEV axes fixed enough to compare trajectory length across windows?
- Does the trajectory become unstable, jittery, or discontinuous?
- Does CoC text align with the visible scene and the predicted trajectory?
- Are ADE/minADE values displayed with the `num_traj_samples=1` caveat?
- Is the clip complete, partial, or complete with failures?

## Exam Questions

1. Explain the difference between A3's single-`t0_us` pilot and A4's sliding-window demo.
2. Why does a visually plausible video not prove the model is validated?
3. In the current A4 run, why should minADE be read as single-sample ADE?
4. Why was the manifest generator changed to consider camera timestamp bounds, not just egomotion?
5. Why does A4 use clip-owned GPU workers instead of splitting one clip's windows across GPUs?
6. What evidence would be required before claiming the model follows explicit driving intentions?
7. If predicted trajectory matches a right turn in a right-turn lane, what are two possible
   explanations other than explicit intention understanding?
8. What should A5/AlpaSim do with A4 videos, and what should it not infer from them?

## Pass / Partial / Fail Rubric

Pass:

- The reviewer can describe A4 as an open-loop visualization/demo stage.
- The reviewer can distinguish A3 single-timestamp inference from A4 sliding-window review.
- The reviewer can explain why `num_traj_samples=1` changes the interpretation of minADE.
- The reviewer can identify that visual plausibility is not model validation.
- The reviewer can state what additional evidence is needed for intention-conditioned claims.

Partial:

- The reviewer understands that A4 creates videos, but mixes visual review with model validation.
- The reviewer can read the panels but cannot explain the metric caveat.
- The reviewer knows A4 is not closed-loop but still overstates CoC text as reasoning evidence.
- The reviewer can describe the five-clip result but confuses it with the in-progress all-local run.

Fail:

- The reviewer claims the demo proves safe driving or closed-loop performance.
- The reviewer treats CoC text as ground truth.
- The reviewer says minADE is a best-of-many metric despite `num_traj_samples=1`.
- The reviewer cannot explain why an explicit intention interface would require separate dataset,
  prompt, and evaluation evidence.

## Expected Reviewer Answer

A concise correct answer should sound like this:

"A4 takes A3-compatible inference outputs and turns them into ordered visual review artifacts. The
five target clips completed all `917` windows at `0.1s` stride with no failed windows, so the demo
pipeline is usable for visual sanity checks. The all-local run is a separate in-progress expansion,
not final evidence yet. This remains open-loop visualization: a plausible trajectory and plausible
CoC text do not prove reasoning, intention-following, or closed-loop safety. Because
`num_traj_samples=1`, minADE should be read as single-sample ADE."
