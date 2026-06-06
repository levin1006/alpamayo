---
doc_type: task
task_role: subtask
status: in_progress
task_id: alpamayo-rnd-a1-code-model-flow
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
created_at: 2026-06-06 13:51:36 KST
updated_at: 2026-06-06 13:51:36 KST
---

# Track A1 Alpamayo Code and Model Flow Study

이 Subtask는 v3 Phase A의 첫 실행 단위다. 목표는 Alpamayo의 공식 inference path를
사용자가 설명하고 리뷰할 수 있을 정도로 코드, 데이터, 모델 흐름을 분해하는 것이다.

## Objective

PAI sample이 Alpamayo inference에서 어떻게 CoC text와 `pred_xyz` trajectory로
변환되는지 evidence 기반으로 설명한다. 이 작업은 더 큰 PAI subset download,
multi-clip inference, visualization, AlpaSim, SFT, RL 작업의 공통 이해 기반이다.

## Operating Roles

### Manager

Responsibilities:

- 이 Subtask와 Root Task 상태 관리
- Expert/Teacher 산출물 위치 지정
- scope creep 차단
- 사용자 이해 gate 확인
- A2/A3/A4 진입 여부 결정

Manager-owned files:

- `docs/2026-05-26 [Task] Alpamayo R&D Root Task.md`
- `docs/2026-06-06 [Task] Track A1 Alpamayo Code and Model Flow Study.md`

### VLA Expert

Responsibilities:

- 코드 경로와 tensor/data contract를 실제 파일 기준으로 조사
- 실행 가능한 read-only 확인 명령과 low-risk probes 제안
- inference flow의 evidence, unknown, blocker를 분리
- Teacher가 설명에 사용할 수 있는 정확한 근거 제공

Expected output:

- `docs/2026-06-06 [Report] Track A1 Expert Code Path Analysis.md`

### Teacher

Responsibilities:

- Expert report를 바탕으로 사용자 학습 자료 작성
- 핵심 개념, 코드 흐름, 결과 의미, 한계 설명
- 사용자가 답해야 할 review questions 작성
- 이해 부족 지점을 Manager가 판단할 수 있게 표시

Expected output:

- `docs/2026-06-06 [Note] Track A1 Teacher Review Guide.md`

### Reviewer

Use only if needed:

- Expert/Teacher 결과가 서로 충돌할 때
- A1 결론이 A2-A4 실행 순서나 데이터 다운로드 판단을 바꿀 때
- inference path의 핵심 동작을 증명하지 못했는데 다음 단계로 넘어가려 할 때

## Scope

In scope:

- `src/alpamayo_r1/test_inference.py`
- `src/alpamayo_r1/load_physical_aiavdataset.py`
- processor/helper path used by official inference
- `src/alpamayo_r1/models/alpamayo_r1.py`
- metrics used by official inference, especially ADE and minADE
- data fields required by one PAI sample
- output fields: CoC text, `pred_xyz`, `pred_rot`, ground-truth trajectory if available

Out of scope:

- large PAI download
- model training or finetuning
- AlpaSim runtime fix
- nuScenes/a2z mapping
- code changes unless a read-only analysis proves a small correction is required and the user
  separately approves it

## Expert Questions

The VLA Expert should answer these from local code evidence:

- What exact command and file path implements the official single-sample inference?
- Which loader fields are required before processor/model execution?
- Why does the path use 4 cameras, 4 image frames, 16 history steps, and 64 future steps?
- Where are ego-frame transforms and timestamps handled?
- How does the prompt/chat template carry trajectory placeholder tokens?
- Where does CoC text generation stop and trajectory sampling begin?
- Which module produces `pred_xyz` and `pred_rot`?
- How are ADE and minADE computed in the official path?
- Which assumptions are release-specific and should not be generalized to nuScenes/a2z yet?

## Teacher Questions

The Teacher should produce a note that helps the user answer:

- What is the simplest end-to-end story from camera frames to trajectory prediction?
- What is the difference between language reasoning output and trajectory output?
- What does minADE prove, and what does it not prove?
- Which parts of the path are data contract, model logic, metric logic, and visualization logic?
- Which concepts must be understood before A2 storage planning and A3 inference experiments?

## Acceptance Criteria

This Subtask is done only when:

- Expert report exists and cites concrete files/functions/commands.
- Teacher note exists and is based on Expert evidence rather than unstated assumptions.
- The user can explain the high-level flow from PAI clip to CoC text and `pred_xyz`.
- The Manager records whether A2 and A3 can start or whether A1 needs another pass.

## Initial Manager Notes

- A0 is already complete enough to provide runtime evidence for A1.
- No large dataset transfer is needed for A1.
- A1 should prefer read-only code inspection and, if needed, low-risk local probes.
- The first useful handoff is from Manager to a separate VLA Expert Codex session.

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-06-06 13:51:36 KST | created | v3 canonical 승인 후 첫 Phase A Subtask 생성 |
