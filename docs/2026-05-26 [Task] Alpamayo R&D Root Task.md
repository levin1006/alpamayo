---
doc_type: task
task_role: root
status: in_progress
task_id: alpamayo-rnd-root
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task:
created_at: 2026-05-26 18:24:55 KST
updated_at: 2026-06-07 00:57:10 KST
---

# Alpamayo R&D Root Task

이 문서는 Alpamayo R&D canonical Plan v3의 실행 상태를 관리하는 Root Task다.
세부 실행 내용은 Subtask에 기록하고, 이 문서는 registry, 상태 roll-up, blocker,
다음 의사결정만 관리한다.

## Objective

`docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md`의 실행 상태를
한 곳에서 추적한다. Root Task는 Plan의 전체 실행 상태를 대표하지만, 세부 로그를
직접 누적하지 않는다.

## Subtask Registry

이 표는 Root Task의 compact index다. 긴 실행 로그와 해석은 각 Subtask에 기록한다.

| Subtask | Status | Required | Owner | First action |
| --- | --- | --- | --- | --- |
| A0 Environment and Access Baseline | done | yes | Manager | Review existing Track A Task |
| A1 Code and Model Flow Study | done | yes | Manager + VLA Expert + Teacher | Closed; use A1 contract for A2-A4 |
| A2 PAI Dataset Literacy and Storage Strategy | not_started | yes | Manager + VLA Expert + Teacher | Build manifest and subset budget |
| A3 Inference Experiment Suite | not_started | yes | Manager + VLA Expert + Teacher | Run 5-clip pilot matrix |
| A4 Visualization and Demo Lab | not_started | yes | Manager + VLA Expert + Teacher | Export first notebook visuals |
| A5 AlpaSim Closed-Loop Baseline | not_started | yes | Manager + VLA Expert + Reviewer | Diagnose container runtime blocker |
| A6 Scene/3D Reconstruction Exploration | not_started | yes | Manager + VLA Expert + Teacher | Inventory geometry assets |
| A7 SFT Micro-Learning Baseline | not_started | yes | Manager + VLA Expert + Reviewer | Run dataloader sanity |
| A8 RL Pipeline Literacy and Tiny Smoke | not_started | yes | Manager + VLA Expert + Reviewer | Run reward/prefetch smoke |
| B Public Dataset Mapping | not_started | yes | Manager | Start after A1-A4 review |
| C Self Dataset Mapping | not_started | yes | Manager | Start after A1-A4 review |

## Subtask Detail Blocks

### A0 Environment and Access Baseline

Status: `done`

Result:

- HF login and PAI/NuRec access work as `kimdh1st`.
- CUDA Toolkit 12.8 is installed on the host and provides `nvcc V12.8.93`.
- README environment path succeeds with `uv venv ar1_venv`, `source ar1_venv/bin/activate`,
  and `uv sync --active`.
- Locked `flash-attn==2.8.3` source-builds successfully through plain `uv sync --active`.
- Official PAI `test_inference.py` completes from `ar1_venv` with CoC text and
  `minADE: 2.5593724`.
- AlpaSim reaches container runtime but services fail internally.

Blockers and caveats:

- The earlier Dao-AILab prebuilt wheel workaround is historical fallback, not the current
  primary host path.
- AlpaSim closed-loop is not validated because generated gRPC modules are missing in services
  and sensorsim exits 139.

Reference:

- `docs/2026-05-26 [Task] Track A Public Alpamayo Reproduction.md`
- `docs/2026-06-06 [Report] Track A0 Official Environment Reproduction.md`
- `docs/logs/2026-06-06-a0-cuda128-readme-uv-sync-active.log`
- `docs/logs/2026-06-06-a0-cuda128-readme-test-inference.log`

### A1 Code and Model Flow Study

Status: `done`

Purpose:

- Establish an explainable code path from PAI clip input to CoC text and `pred_xyz`.
- Split work between VLA Expert evidence gathering and Teacher user-facing review material.

Outputs:

- `docs/2026-06-06 [Task] Track A1 Alpamayo Code and Model Flow Study.md`
- `docs/2026-06-06 [Report] Track A1 Expert Code Path Analysis.md`
- `docs/2026-06-06 [Review] Track A1 Expert Code Path Review.md`
- `docs/2026-06-06 [Note] Track A1 Code Flow Review Guide.md`

Manager decision:

- User understanding gate is satisfied for the minimum A1 scope.
- A2 should start before A3/A4 so dataset/storage profiles are explicit before broader runtime
  experiments and visualization outputs.

### A2-A8 Phase A Baseline Lab

Status: `not_started`

Next order:

- Start A2 first: PAI manifest, component/chunk profile, storage budget, and approved pilot subset.
- Then run A3 and A4 together or back-to-back on the A2-approved subset.
- A5-A8 remain queued until their first-gate blocker or smoke scope is explicitly opened.

### B/C Dataset Mapping

Status: `not_started`

Next condition:

- Defer broad public/self dataset mapping until A1-A4 are reviewable, unless the user explicitly
  opens a parallel low-priority mapping task.

## Status Roll-Up

- Root status: `in_progress`
- Required blocker summary:
  - Track A acceptance is satisfied by official PAI inference: CoC text and `minADE: 2.5593724`.
  - HF access for Track A is resolved as `kimdh1st`; PAI `features.csv` and the AlpaSim NuRec
    scene artifact are accessible.
  - Required `flash-attn` install reproducibility is resolved on the current host. CUDA Toolkit
    12.8 provides `nvcc`, and plain README `uv sync --active` source-builds locked
    `flash-attn==2.8.3`.
  - AlpaSim is not validated as a closed-loop smoke yet. It reaches container start, then fails on
    missing `alpasim_grpc.v0.common_pb2` in services plus sensorsim exit 139.
  - The AlpaSim failure is now classified under A5 simulator/runtime work, not A0 environment
    reproduction.
  - v3 is now the canonical Plan and reframes Phase A as Alpamayo Baseline Lab.
  - A1 code/model flow study is closed. The user understanding gate is satisfied for the
    official `test_inference.py` path and its limits.
  - A2 is the next entry point. It should define PAI data/storage profiles before A3 inference
    sweeps or A4 visualization demos.
  - A3/A4 should record runtime-loaded config, `num_traj_samples`, seed, clip selection, and
    output schema as fresh evidence.
  - B/C are deferred until A1-A4 become reviewable, unless explicitly opened as low-priority
    parallel tasks.
- Current canonical Plan: `docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md`
- Superseded Plan: `docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md`

## Multi-Session Operating Rule

- Manager session updates this Root Task and controls status roll-up.
- VLA Expert sessions write evidence reports for assigned Subtasks.
- Teacher sessions write user-facing learning/review notes based on Expert reports.
- Reviewer sessions are used only for important milestones, plan changes, or high-risk claims.
- Agent sessions coordinate through repository documents, not unstated cross-session context.

## Decision Log

| Time (KST) | Decision | Reason |
| --- | --- | --- |
| 2026-05-26 18:24:55 KST | Use Plan -> Root Task -> Subtask structure | Prevent Plan body drift and missing task roll-up |
| 2026-05-26 18:24:55 KST | Start with Track A Subtask | Track A validates the public baseline and contract needed by later tracks |
| 2026-05-26 18:45:22 KST | Track A execution approved | User approved running Track A until acceptance criteria or blocker |
| 2026-05-26 18:50:58 KST | Track A blocked on external access | PAI and NuRec gated HF artifacts return 401 without login/access |
| 2026-05-26 19:03:19 KST | Synthetic model smoke classified | Weights download/load path checked separately from gated PAI data |
| 2026-05-26 19:03:34 KST | Synthetic model inference succeeded | Direct single-GPU placement with dummy inputs produced 64-step trajectory tensors |
| 2026-05-27 08:14:41 KST | Track A access blocker rechecked | HF is still not logged in, and PAI/NuRec gated downloads still return 401 |
| 2026-05-27 08:17:40 KST | Official-like synthetic inference succeeded | Dummy 16-image processor path produced CoC text and 64-step trajectory tensors |
| 2026-05-27 09:01:33 KST | HF login succeeded but gated datasets remain blocked | `kimdh1st` login works; PAI/NuRec direct downloads return 403 |
| 2026-05-27 09:18:15 KST | Track A acceptance satisfied by official inference | HF access corrected, official PAI inference completes with `minADE: 2.5593724`; AlpaSim remains a simulator runtime blocker |
| 2026-05-27 12:39:31 KST | v3 review Plan drafted | User requested Phase A become a deep Alpamayo baseline lab before nuScenes/a2z expansion |
| 2026-06-06 13:51:36 KST | v3 canonical Plan approved | User approved v3 and requested a multi-session Manager/VLA Expert/Teacher operating model |
| 2026-06-06 13:51:36 KST | A1 Subtask opened | First v3 step is to make the Alpamayo code/model flow explainable before larger data and experiment work |
| 2026-06-06 20:35:48 KST | A0 official environment reproduction closed | CUDA Toolkit 12.8 enables README `uv sync --active`, locked `flash-attn` source build, and PAI inference in `ar1_venv`; AlpaSim remains A5 runtime blocker |
| 2026-06-07 00:57:10 KST | A1 closed and A2 selected next | Teacher/Evaluator report and user confirmation satisfy A1 understanding gate; A2 should precede A3/A4 to control dataset/storage scope |

## User Understanding Check

Before marking any required Subtask `done`, the user should be able to answer:

- What risk did this Subtask reduce?
- Which code path or data contract did it inspect or change?
- Which command or evidence produced the result?
- What does the result prove, and what does it not prove?
- What decision does this result enable or block?

## Next Step

Start A2 with separate Expert and Teacher outputs:

- Create `docs/2026-06-07 [Task] Track A2 PAI Dataset Literacy and Storage Strategy.md`.
- Expert output: PAI manifest/component/chunk/storage evidence report.
- Teacher output: user review note and storage/download decision test.
- Manager output: approve or reject the first pilot subset before A3/A4.

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-05-26 18:24:55 KST | created | canonical Plan v2 execution registry 생성 |
| 2026-05-26 18:45:22 KST | status, Track A row, roll-up, decision log | Track A 실행 승인 반영 |
| 2026-05-26 18:50:58 KST | status, Track A row, roll-up, decision log, next step | Track A HF 접근권 blocker 반영 |
| 2026-05-26 18:50:58 KST | Track B/C rows | Track A contract draft 작성 및 미검증 상태 반영 |
| 2026-05-26 19:03:19 KST | updated_at, Track A row, roll-up, decision log | synthetic 모델 로드/추론 blocker 반영 |
| 2026-05-26 19:03:34 KST | updated_at, Track A row, roll-up, decision log | synthetic Alpamayo 10B inference smoke 성공 반영 |
| 2026-05-27 08:14:41 KST | updated_at, decision log | Track A HF 접근권 blocker 재확인 결과 반영 |
| 2026-05-27 08:17:40 KST | updated_at, Track A row, roll-up, decision log | official-like synthetic inference smoke 성공 반영 |
| 2026-05-27 09:01:33 KST | updated_at, Track A row, roll-up, decision log | HF 로그인 성공 및 gated dataset 403 상태 반영 |
| 2026-05-27 09:18:15 KST | status, updated_at, Track A/B/D/E rows, roll-up, decision log, next step | Track A 공식 inference 성공 및 AlpaSim runtime blocker 반영 |
| 2026-05-27 12:39:31 KST | updated_at, roll-up, decision log, next step | v3 검토 계획 생성 및 다음 의사결정 반영 |
| 2026-06-06 13:51:36 KST | parent_plan, updated_at, registry, roll-up, operating rule, decision log, next step | v3 canonical 승인 및 multi-session Manager/Expert/Teacher 운영 모델 반영 |
| 2026-06-06 20:35:48 KST | updated_at, A0 detail block, roll-up, decision log | CUDA Toolkit 12.8 기반 README 경로 성공으로 A0 blocker 해소 및 AlpaSim blocker를 A5로 이관 |
| 2026-06-07 00:57:10 KST | updated_at, A1 row, A1 block, A2-A8 block, roll-up, decision log, next step | A1 Teacher/Evaluator 확인 및 사용자 이해 gate 통과 보고에 따라 A1 done 처리와 A2 우선 진입 결정 반영 |
