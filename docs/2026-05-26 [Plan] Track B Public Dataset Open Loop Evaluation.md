---
doc_type: plan
status: superseded
plan_id: alpamayo-track-b-public-dataset-open-loop
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

# Track B: Public Dataset Open-Loop Evaluation

- Created: 2026-05-26 15:27:39 KST
- Status: planned
- Parent roadmap: `docs/2026-05-19 [Plan] Alpamayo Research and Development.md`
- Migration note: this document is a legacy source draft. Create a Subtask from the Root Task before execution.

## Goal

nuScenes 같은 공개 데이터셋을 Alpamayo 평가 contract에 맞게 변환할 수 있는지 검증한다. 목표는 곧바로 학습을 시작하는 것이 아니라, 공개 데이터셋이 Alpamayo-style open-loop evaluation에 충분한 sensor, egomotion, future trajectory, calibration 정보를 제공하는지 확인하는 것이다.

## Scope

Included:

- nuScenes data structure와 Alpamayo input/output contract 비교
- camera temporal frames, ego pose, future trajectory horizon, calibration availability 확인
- nuScenes-to-Alpamayo sample feasibility report 작성
- 필요 시 NAVSIM/Waymo 등 후보 데이터셋 비교 항목 정의

Excluded:

- 대규모 dataset conversion
- model fine-tuning
- closed-loop simulation

## Progress Tracker

| Item | Status | Evidence path or command | Result | Next action |
| --- | --- | --- | --- | --- |
| nuScenes schema 조사 | Not started | dataset docs/devkit | Pending | required fields mapping |
| Alpamayo contract 비교 | Not started | `load_physical_aiavdataset()` sample keys | Pending | gap table 작성 |
| horizon/frequency gap 확인 | Not started | 6.4s, 10 Hz 기준 비교 | Pending | resampling 가능성 판단 |
| calibration/egomotion gap 확인 | Not started | camera intrinsics/extrinsics, pose | Pending | transform 설계 |
| feasibility report | Not started | docs artifact | Pending | Track C/E 반영 |

## Execution Steps

1. 공개 데이터셋 후보 목록 확정
   - Verify: nuScenes를 1차 대상으로 두고, 필요한 경우 NAVSIM/Waymo 후보를 appendix로 둔다.

2. Alpamayo sample contract와 field-by-field 비교
   - Verify: `image_frames`, `camera_indices`, `ego_history_xyz`, `ego_history_rot`, `ego_future_xyz`, `ego_future_rot`, timestamp fields 매핑표.

3. open-loop metric 가능성 확인
   - Verify: 6.4초 10 Hz future trajectory 또는 합리적 resampling 가능성 판단.

4. 최소 변환 설계 작성
   - Verify: converter input, output sample dict, known loss of information 명시.

## Acceptance Criteria

- nuScenes가 Alpamayo open-loop 평가에 "사용 가능", "조건부 사용 가능", "부적합" 중 하나로 판정될 것
- 부적합 또는 조건부 항목은 missing field와 보완 방법이 명시될 것
- Track C의 자체 데이터 contract 설계에 재사용 가능한 mapping checklist가 만들어질 것

## Vehicle Relevance Check

- 줄일 리스크: public dataset generalization risk, format mapping risk, metric definition risk
- 아직 남는 리스크: self vehicle sensor mismatch, closed-loop transfer, safety validation
- 다음 gate: nuScenes mapping이 가능하면 자체 데이터 converter의 reference implementation으로 사용한다.

## Replan Conditions

- required future ego trajectory horizon이 부족한 경우
- camera/frame timing이 Alpamayo temporal input과 크게 다르고 보정 비용이 큰 경우
- license가 계획된 연구/검증 사용과 충돌하는 경우
