---
doc_type: plan
status: superseded
plan_id: alpamayo-track-d-self-data-simulation-replay
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

# Track D: Self-Data Simulation and Replay

- Created: 2026-05-26 15:27:39 KST
- Status: planned
- Parent roadmap: `docs/2026-05-19 [Plan] Alpamayo Research and Development.md`
- Migration note: this document is a legacy source draft. Create a Subtask from the Root Task before execution.

## Goal

자체 구축 데이터셋을 기반으로 open-loop를 넘어 replay, pseudo-closed-loop, 또는 closed-loop simulation 평가 환경을 구축할 수 있는지 검증한다. 이 트랙은 실제 차량 VLA closed-loop로 가기 전 안전한 중간 검증층이다.

## Scope

Included:

- AlpaSim `.asl` log와 자체 log schema 비교
- 자체 데이터 기반 camera replay/ego pose replay 가능성 검토
- closed-loop 또는 pseudo-closed-loop metric 설계
- scenario reconstruction 요구사항 정의

Excluded:

- 실제 차량 제어
- production simulator 완성
- 대규모 synthetic generation

## Progress Tracker

| Item | Status | Evidence path or command | Result | Next action |
| --- | --- | --- | --- | --- |
| AlpaSim log contract 조사 | Not started | `docs/DATA_PIPELINE.md`, `.asl` schema | Pending | mapping table |
| 자체 log 비교 | Not started | user data manifest | Pending | missing fields |
| replay architecture draft | Not started | design note | Pending | feasibility review |
| metric set 정의 | Not started | collision/offroad/minADE/plan deviation | Pending | evaluator mapping |
| scenario selection | Not started | long-tail taxonomy | Pending | candidate list |

## Execution Steps

1. AlpaSim output/log contract 정리
   - Verify: camera image, actor poses, driver request/response, metrics artifact 흐름.

2. 자체 데이터 replay 가능성 판단
   - Verify: raw sensor replay, ego trajectory replay, environment reconstruction 가능/불가능 구분.

3. simulation mode 선택
   - Verify: offline replay, pseudo-closed-loop, AlpaSim/NuRec closed-loop, custom simulator 중 현실적 path 선택.

4. metric과 scenario taxonomy 정의
   - Verify: offroad, collision/close encounter, plan deviation, minADE, latency, reasoning audit.

## Acceptance Criteria

- 자체 데이터 기반 simulation/replay의 1차 architecture가 정의될 것
- closed-loop이 바로 불가능하면 pseudo-closed-loop 또는 replay evaluation 대안을 명시할 것
- Track F로 넘길 safety evidence 형식이 정의될 것

## Vehicle Relevance Check

- 줄일 리스크: closed-loop evaluation gap, replay/simulation feasibility risk, scenario coverage risk
- 아직 남는 리스크: real-world dynamics, sensor rendering fidelity, controller integration
- 다음 gate: replay/simulation evidence 없이 vehicle closed-loop를 진행하지 않는다.

## Replan Conditions

- 자체 데이터가 scene reconstruction에 필요한 environment/agent 정보를 제공하지 않는 경우
- AlpaSim과 자체 데이터의 sensor/log schema 차이가 너무 큰 경우
- closed-loop metric이 실제 차량 risk를 설명하지 못하는 경우
