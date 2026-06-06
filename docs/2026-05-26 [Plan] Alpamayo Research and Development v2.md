---
doc_type: plan
status: superseded
plan_id: alpamayo-rnd
version: 2
canonical: false
created_at: 2026-05-26 18:24:55 KST
approved_at: 2026-05-26 18:24:55 KST
root_plan: docs/2026-05-19 [Plan] Alpamayo Research and Development.md
supersedes: docs/2026-05-19 [Plan] Alpamayo Research and Development.md
superseded_by: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
root_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
revision_type: full_replacement
revision_reason: Plan baseline, Root Task, Subtask 문서 하네스 적용
---

# Alpamayo Research and Development Plan v2

이 문서는 Alpamayo/VLA 연구개발의 현재 canonical Plan이다. 실행자는 이 문서와
연결된 Root Task만으로 현재 실행 기준과 상태를 파악할 수 있어야 한다.

이전 문서인 `docs/2026-05-19 [Plan] Alpamayo Research and Development.md`는
상세 조사와 초기 roadmap을 보존하는 superseded baseline으로 남긴다. 이전
문서의 논문/소스/환경 분석은 근거 자료로 계속 사용할 수 있지만, 실행 기준은
이 v2 문서와 Root Task다.

## North Star

최종 목표는 Alpamayo 논문, 공개 구현, 공개 데이터셋, AlpaSim, Physical AI AV,
nuScenes, 자체 구축 데이터셋, 자체 구축 자율주행 차량 데이터를 하나의 검증
가능한 연구개발 흐름으로 연결하여, 최종적으로 자체 차량에서 안전 제약이 있는
VLA closed-loop 평가까지 도달하는 것이다.

이 목표는 매 실행 항목의 범위가 아니라 판단 기준이다. 각 Subtask는 작게
실행하되, 결과가 최종 차량 VLA closed-loop 목표의 어떤 리스크를 줄였는지
Root Task에 남겨야 한다.

## Non-Negotiable Principles

1. 공개 재현은 최종 성과가 아니라 전제 검증이다.
2. open-loop 결과는 필요하지만 충분하지 않다. closed-loop simulation,
   shadow-mode, safety gate 없이는 실제 차량 적용 판단으로 승격하지 않는다.
3. 데이터 contract가 모델보다 먼저다. input/output contract, camera order,
   egomotion frame, timestamp alignment, calibration 품질이 검증되지 않으면
   학습 결과를 신뢰하지 않는다.
4. 실제 차량 제어는 마지막 단계다. offline evaluation, closed-loop simulation,
   shadow-mode, safety monitor를 통과하기 전까지 actuation 통합을 목표로 두지
   않는다.
5. top-down roadmap과 bottom-up evidence를 함께 사용한다. 상위 목표는 방향을
   고정하고, 세부 실행은 결과에 따라 현실성을 갱신한다.
6. 사용자 이해도는 완료 기준의 일부다. 사용자가 핵심 구현 경로, 실험 설정,
   결과의 의미와 한계를 설명하고 리뷰할 수 있어야 다음 단계로 진행한다.

## Execution Harness

- 이 Plan의 실행 상태는 `docs/2026-05-26 [Task] Alpamayo R&D Root Task.md`에서
  관리한다.
- Root Task는 Subtask registry, 전체 상태 roll-up, blocker, 다음 의사결정을
  관리한다.
- 세부 실행 로그, 검증 결과, 사용자 이해도 확인은 Subtask에 기록한다.
- 기존 Track A-F 문서는 실행 기준 Plan이 아니라 Subtask 설계의 source draft로
  사용한다.
- Progress Tracker는 Plan 본문에 누적하지 않고 Root Task/Subtask로 이동한다.

## Program Tracks

| Track | Name | Primary question | First gate | Execution status source |
| --- | --- | --- | --- | --- |
| A | Public Alpamayo/PAI Reproduction | 공개 Alpamayo를 로컬에서 재현할 수 있는가? | inference, PAI load, AlpaSim smoke 중 최소 하나 이상 완료 | Root Task registry, Track A Subtask |
| B | Public Dataset Open-Loop Evaluation | nuScenes 등 공개 데이터셋을 Alpamayo 평가 contract로 매핑할 수 있는가? | nuScenes-to-Alpamayo sample feasibility report | Root Task registry |
| C | Self Dataset Open-Loop Evaluation | 자체 데이터셋을 Alpamayo input/output contract로 변환해 open-loop 평가할 수 있는가? | sample converter prototype와 metric smoke | Root Task registry |
| D | Self-Data Simulation and Replay | 자체 데이터 기반 replay/simulation 평가가 가능한가? | replay/simulation design proof 및 log schema | Root Task registry |
| E | Learning and Adaptation | 공개/자체 데이터로 SFT, adapter tuning, RL reward 실험을 의미 있게 수행할 수 있는가? | small-set overfit 또는 short-run metric | Root Task registry |
| F | Vehicle Shadow and VLA Closed-Loop | 실제 차량에서 안전 제약 하에 VLA를 평가할 수 있는가? | offline/shadow safety gate 통과 | Root Task registry |

## Dependency Rule

```text
Track A public reproduction
  -> Track B public dataset mapping
  -> Track C self dataset open-loop
  -> Track D self-data simulation/replay
  -> Track E learning/adaptation
  -> Track F shadow-mode and vehicle closed-loop
```

Track B와 Track C는 일부 병렬 진행할 수 있다. 다만 Track E는 데이터 contract
검증 없이 시작하지 않는다. Track F는 Track C/D/E의 산출물이 safety gate를
만족하기 전까지 설계만 수행하고 실제 제어 실험은 보류한다.

## Current Execution Priority

1. Root Task 생성 및 Subtask registry 확정
2. Track A Subtask 실행: HF access, 환경, Alpamayo inference, PAI, AlpaSim smoke
3. Track A 결과를 바탕으로 Track B/C 실행 순서와 범위 재확정
4. Track B/C의 데이터 contract 결과가 확보된 뒤 Track D/E 실행 여부 결정
5. Track F는 shadow-mode/safety gate 설계만 유지하고 actuation 관련 실행은 보류

## Completion Gates

이 Plan은 다음 조건을 충족해야 완료로 볼 수 있다.

- Root Task의 필수 Subtask가 모두 `done`
- Track A-C에서 데이터/모델 contract의 핵심 리스크가 문서화됨
- Track D에서 replay/simulation 또는 pseudo-closed-loop 대안이 판정됨
- Track E에서 학습 가능성과 학습 보류 조건이 evidence 기반으로 정리됨
- Track F에서 shadow-mode 전 안전 gate와 금지 조건이 명확히 유지됨
- 사용자가 각 단계의 코드 경로, 실험 목적, 결과 해석을 리뷰할 수 있음

## Evidence Sources

- `docs/2026-05-19 [AI Command] Alpamayo Research and Development.md`
- `docs/2026-05-19 [Plan] Alpamayo Research and Development.md`
- `docs/2026-05-26 [Plan Request] Alpamayo Program Roadmap and Track Planning.md`
- legacy Track A-F source drafts under `docs/2026-05-26 [Plan] Track *.md`
- Alpamayo source under `src/alpamayo_r1/`
- `/home/user/Workspace/alpasim`
- `/home/user/Workspace/physical_ai_av`

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-05-26 18:24:55 KST | created | 기존 roadmap을 새 Plan/Root Task/Subtask 하네스에 맞춰 canonical v2로 재구성 |
| 2026-06-06 13:51:36 KST | status, canonical, superseded_by | 사용자 승인으로 v3가 canonical Plan이 되어 v2를 superseded 처리 |
