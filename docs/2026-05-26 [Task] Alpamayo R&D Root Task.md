---
doc_type: task
task_role: root
status: not_started
task_id: alpamayo-rnd-root
parent_plan: docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md
parent_task:
created_at: 2026-05-26 18:24:55 KST
updated_at: 2026-05-26 18:24:55 KST
---

# Alpamayo R&D Root Task

이 문서는 Alpamayo R&D canonical Plan v2의 실행 상태를 관리하는 Root Task다.
세부 실행 내용은 Subtask에 기록하고, 이 문서는 registry, 상태 roll-up, blocker,
다음 의사결정만 관리한다.

## Objective

`docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md`의 실행 상태를
한 곳에서 추적한다. Root Task는 Plan의 전체 실행 상태를 대표하지만, 세부 로그를
직접 누적하지 않는다.

## Subtask Registry

| Subtask | Status | Required | Source draft | Current result | Blocking issue | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| Track A Public Alpamayo/PAI Reproduction | not_started | yes | `docs/2026-05-26 [Plan] Track A Public Alpamayo Reproduction.md` | Pending | HF/GPU/environment unknown | Start Track A Subtask |
| Track B Public Dataset Open-Loop Evaluation | not_started | yes | `docs/2026-05-26 [Plan] Track B Public Dataset Open Loop Evaluation.md` | Pending | Track A contract summary pending | Create Subtask after Track A contract note |
| Track C Self Dataset Open-Loop Evaluation | not_started | yes | `docs/2026-05-26 [Plan] Track C Self Dataset Open Loop Evaluation.md` | Pending | user dataset inventory pending | Create Subtask after user data inventory |
| Track D Self-Data Simulation and Replay | not_started | yes | `docs/2026-05-26 [Plan] Track D Self Data Simulation and Replay.md` | Pending | Track C and AlpaSim log mapping pending | Hold |
| Track E Learning and Adaptation | not_started | yes | `docs/2026-05-26 [Plan] Track E Learning and Adaptation.md` | Pending | Track A/C contract and compute/license gates pending | Hold |
| Track F Vehicle Shadow and VLA Closed-Loop | not_started | yes | `docs/2026-05-26 [Plan] Track F Vehicle Shadow and VLA Closed Loop.md` | Pending | Gated by Track C/D/E safety evidence | Design only, no actuation |

## Status Roll-Up

- Root status: `not_started`
- Required blocker summary:
  - Track A has not started.
  - Track F is intentionally gated until data, simulation, learning, and safety gates exist.
- Current canonical Plan: `docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md`

## Decision Log

| Time (KST) | Decision | Reason |
| --- | --- | --- |
| 2026-05-26 18:24:55 KST | Use Plan -> Root Task -> Subtask structure | Prevent Plan body drift and missing task roll-up |
| 2026-05-26 18:24:55 KST | Start with Track A Subtask | Track A validates the public baseline and contract needed by later tracks |

## User Understanding Check

Before marking any required Subtask `done`, the user should be able to answer:

- What risk did this Subtask reduce?
- Which code path or data contract did it inspect or change?
- Which command or evidence produced the result?
- What does the result prove, and what does it not prove?
- What decision does this result enable or block?

## Next Step

Create and execute the Track A Subtask:

- `docs/2026-05-26 [Task] Track A Public Alpamayo Reproduction.md`

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-05-26 18:24:55 KST | created | canonical Plan v2 execution registry 생성 |
