---
doc_type: task
task_role: subtask
status: in_progress
task_id: alpamayo-rnd-a3-inference-experiment-suite
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
created_at: 2026-06-08 12:04:42 KST
updated_at: 2026-06-08 12:04:42 KST
---

# Track A3 Inference Experiment Suite

이 Subtask는 A2에서 승인된 local PAI subset을 사용해 Alpamayo baseline inference를 여러 clip,
seed, sample 설정에서 실행하고 결과의 안정성과 한계를 기록하기 위한 작업이다.

## Objective

단일 official PAI sample 성공을 넘어서, selected local subset에서 CoC text, `pred_xyz`,
ADE/minADE, runtime, VRAM, failure reason을 체계적으로 기록한다.

## Operating Model

Default role: Expert-led session.

The A3 Expert-led session should produce both:

- an evidence report with commands, output files, metrics, and blocker classification;
- a Teacher/Evaluator note that checks whether the user can explain the experiment design and
  result limits.

Use independent Reviewer only if the experiment result changes A4/A5/A6 sequencing, exposes a
major data contract issue, or makes a broad model-quality claim.

## Scope

In scope:

- local subset inference on `/data/datasets/physical_ai_av/selected_chunks_10_multisensor`;
- optional fast smoke on `/data/datasets/physical_ai_av/chunk_3119_a3a4_min`;
- 5-clip pilot first, then expansion only if runtime and storage are manageable;
- at least one seed-variance check for a selected clip;
- `num_traj_samples=1` baseline, with higher sample count only if VRAM permits;
- result table with CoC text, ADE/minADE, runtime, peak VRAM, and failure reason.

Out of scope:

- large additional PAI downloads;
- training/SFT/RL;
- AlpaSim runtime fix;
- visualization polish beyond output schema needed by A4.

## Acceptance Criteria

This Subtask is done only when:

- a reproducible A3 command/script path exists;
- at least a 5-clip pilot result table exists or a blocker is classified;
- runtime-loaded config, seed, `num_traj_samples`, clip selection, and output schema are recorded;
- outputs are structured enough for A4 visualization;
- user understanding is checked through a Teacher/Evaluator note.

## Initial Manager Notes

- A3 should not claim model quality from a small pilot.
- A3 should distinguish single-sample ADE from minADE over multiple samples.
- A3 should preserve A4 handoff fields: images or image references, ego history, ground truth
  future, predictions, CoC text, ADE/minADE, clip ID, and timestamps where available.

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-06-08 12:04:42 KST | created | A2 closure 후 selected PAI subset 기반 inference experiment suite 시작 |
