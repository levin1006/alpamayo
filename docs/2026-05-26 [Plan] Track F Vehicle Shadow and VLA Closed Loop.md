---
doc_type: plan
status: superseded
plan_id: alpamayo-track-f-vehicle-shadow-vla-closed-loop
version: 1
canonical: false
created_at: 2026-05-26 15:27:39 KST
approved_at:
root_plan: docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md
supersedes:
superseded_by: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
root_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
revision_type: legacy_track_source_draft
revision_reason: migrated from Track Plan to Root Task/Subtask execution harness
---

# Track F: Vehicle Shadow and VLA Closed-Loop

- Created: 2026-05-26 15:27:39 KST
- Status: planned, gated
- Parent roadmap: `docs/2026-05-19 [Plan] Alpamayo Research and Development.md`
- Migration note: this document is a legacy source draft. Create a Subtask from the Root Task before execution; actuation remains prohibited until gates pass.

## Goal

자체 구축 자율주행 차량에서 VLA를 안전 제약 하에 평가하고, 최종적으로 제한된 closed-loop VLA 실험까지 도달한다. 이 트랙은 최종 목표에 해당하지만, 가장 늦게 실행되어야 하는 트랙이다.

## Scope

Included:

- offline inference validation
- shadow-mode logging
- safety monitor와 trajectory bounds 정의
- controller/MPC interface contract 정의
- 제한된 closed-loop test gate 정의

Excluded until gates pass:

- public model direct actuation
- safety monitor 없는 closed-loop
- ODD 밖 실제 주행 실험
- license 미확정 상태의 제품 적용

## Progress Tracker

| Item | Status | Evidence path or command | Result | Next action |
| --- | --- | --- | --- | --- |
| vehicle interface inventory | Not started | platform/control docs | Pending | user input 필요 |
| onboard compute inventory | Not started | GPU/edge compute specs | Pending | latency budget |
| offline inference | Blocked | Track C/E outputs | Pending | dataset adapter 필요 |
| shadow-mode design | Blocked | Track C/D/F interface | Pending | logging schema |
| safety gate definition | Not started | hazard/risk checklist | Pending | conservative limits |
| limited closed-loop | Blocked | all previous gates | Pending | do not execute yet |

## Execution Steps

1. 차량 platform/control interface 조사
   - Verify: trajectory command format, controller/MPC boundary, emergency stop/safety driver policy.

2. offline inference 평가
   - Verify: 자체 주행 log에서 VLA trajectory/reasoning 생성, latency 측정.

3. shadow-mode 설계
   - Verify: 차량이 기존 stack으로 주행하는 동안 VLA output을 read-only로 기록.

4. safety monitor 정의
   - Verify: trajectory envelope, speed/accel/yaw-rate bounds, obstacle/road-edge checks, disagreement checks.

5. 제한된 closed-loop gate 정의
   - Verify: ODD, speed, location, fallback, human supervision, stop criteria.

## Acceptance Criteria

- Track C 자체 데이터 contract와 Track D replay/simulation evidence가 확보될 것
- Track E 학습/검증 결과가 open-loop뿐 아니라 safety-related regression으로도 설명될 것
- shadow-mode에서 latency, trajectory bounds, disagreement metrics가 기록될 것
- closed-loop test는 명시된 safety gate를 통과하기 전에는 실행하지 않을 것

## Vehicle Relevance Check

- 줄일 리스크: final integration risk, latency risk, control contract risk, operational safety risk
- 아직 남는 리스크: certification, real-world rare events, model brittleness outside ODD
- 다음 gate: shadow-mode evidence가 충분하지 않으면 closed-loop는 보류하고 데이터/시뮬레이션/학습 트랙으로 되돌린다.

## Replan Conditions

- 차량 제어 인터페이스가 trajectory command를 안정적으로 받을 수 없는 경우
- onboard compute가 latency/VRAM 기준에 미달하는 경우
- safety monitor가 VLA output을 제약할 수 없는 경우
- 법무/라이선스 검토가 목표 사용을 허용하지 않는 경우
