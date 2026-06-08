---
doc_type: task
task_role: subtask
status: done
task_id: alpamayo-rnd-a2-pai-dataset-literacy
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
created_at: 2026-06-07 01:03:01 KST
updated_at: 2026-06-08 12:04:42 KST
---

# Track A2 PAI Dataset Literacy and Storage Strategy

이 Subtask는 PAI 전체 133 TB를 다운로드하지 않고 Phase A에서 필요한 local subset과
storage decision을 evidence 기반으로 정리하기 위한 작업이다.

## Objective

PAI metadata, chunk/component 구조, A3/A4 minimum profile, A6 add-on 범위를 이해하고,
현재 local dataset root가 A3/A4 시작에 충분한지 판단한다.

## Outputs

- `docs/2026-06-07 [Report] Track A2 PAI Dataset Literacy and Storage Strategy.md`
- `docs/2026-06-08 [Note] Track A2 Dataset Literacy Review Guide.md`

## Manager Closure Decision

Verdict: `done`

Closure time: `2026-06-08 12:04:42 KST`

Evidence:

- A2 Expert report documents PAI metadata files, chunk/component storage model, selected chunks,
  and current local subset state.
- A2 Teacher/Evaluator note is `done`.
- User reported that A2 learning is complete.
- Read-only Manager checks confirmed the main local subset exists:
  `/data/datasets/physical_ai_av/selected_chunks_10_multisensor`
- Read-only Manager checks confirmed the selected subset size is `271G` and the single-chunk
  smoke subset is `6.2G`.

Current local data state:

- Primary A3/A4 path:
  `/data/datasets/physical_ai_av/selected_chunks_10_multisensor`
- Fast smoke path:
  `/data/datasets/physical_ai_av/chunk_3119_a3a4_min`
- Primary subset includes 10 selected chunks and 772 clips according to the Expert report.

Manager interpretation:

- A2 satisfies the minimum understanding and storage decision gate.
- A3 can start on the selected 10-chunk subset.
- A4 should follow A3 or run in tight coordination after A3 records runtime-loaded config, clip
  selection, output schema, and result files.
- A6 has useful lidar/radar/obstacle inventory material in the subset, but A6 readiness is not
  proven by A2.

## Next Track Handoff

A3 must produce fresh runtime evidence:

- selected clip list;
- seed and `num_traj_samples`;
- runtime-loaded model/config values;
- CoC text, `pred_xyz`, ADE/minADE, runtime, and peak VRAM;
- failure reason for any failed clip;
- output schema suitable for A4 visualization.

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-06-08 12:04:42 KST | created | A2 Expert-led report와 Teacher/Evaluator 학습 완료를 Subtask closure로 정리 |
