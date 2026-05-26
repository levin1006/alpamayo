---
doc_type: plan
status: superseded
plan_id: alpamayo-track-c-self-dataset-open-loop
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

# Track C: Self Dataset Open-Loop Evaluation

- Created: 2026-05-26 15:27:39 KST
- Status: planned
- Parent roadmap: `docs/2026-05-19 [Plan] Alpamayo Research and Development.md`
- Migration note: this document is a legacy source draft. Create a Subtask from the Root Task before execution.

## Goal

자체 구축 데이터셋을 Alpamayo input/output contract에 맞게 변환하고, 실제 차량 제어 전에 open-loop trajectory/reasoning evaluation을 수행할 수 있는지 확인한다.

## Scope

Included:

- 자체 데이터셋 포맷, sensor rig, calibration, timestamp, localization/egomotion 조사
- Alpamayo sample dict 또는 PAI-like local dataset 변환 설계
- 최소 sample converter prototype 계획
- open-loop metric smoke 계획

Excluded:

- 대규모 학습
- closed-loop simulation
- 차량 actuation

## Progress Tracker

| Item | Status | Evidence path or command | Result | Next action |
| --- | --- | --- | --- | --- |
| 자체 데이터 inventory | Not started | user-provided dataset manifest | Pending | schema 수집 |
| sensor/calibration 확인 | Not started | intrinsics/extrinsics/time sync | Pending | validation checklist |
| egomotion/future label 확인 | Not started | localization/trajectory logs | Pending | frame transform 설계 |
| converter contract | Not started | sample dict spec | Pending | prototype 범위 확정 |
| open-loop metric smoke | Not started | ADE/minADE script | Pending | held-out split 설계 |

## Execution Steps

1. 데이터 inventory 작성
   - Verify: camera list, frame rate, FOV, resolution, timestamp source, pose source, storage format.

2. Alpamayo contract gap 분석
   - Verify: 공개 `load_physical_aiavdataset()` 출력 key와 자체 데이터 field 간 매핑표.

3. 최소 converter 설계
   - Verify: one clip -> Alpamayo sample dict 변환 가능성.

4. open-loop metric 정의
   - Verify: ground truth future trajectory 기준 ADE/minADE 산출 가능성.

5. held-out/evaluation split 원칙 정의
   - Verify: ODD, location/time leakage 방지 기준.

## Acceptance Criteria

- 자체 데이터셋이 open-loop evaluation에 필요한 최소 정보를 제공하는지 판정될 것
- 최소 1개 sample 변환에 필요한 field와 transform이 정의될 것
- 불가능한 항목은 데이터 수집/로그 구조 변경 요구사항으로 기록될 것

## Vehicle Relevance Check

- 줄일 리스크: self data format risk, sensor calibration risk, trajectory label risk
- 아직 남는 리스크: simulation realism, learning effectiveness, safety gate
- 다음 gate: 자체 데이터 sample contract가 검증되기 전까지 Track E의 자체 데이터 학습은 시작하지 않는다.

## Replan Conditions

- future ego trajectory ground truth가 없는 경우
- camera synchronization 또는 calibration 품질이 학습/평가 기준에 미달하는 경우
- localization frame 정의가 불명확해 ego-frame trajectory를 신뢰할 수 없는 경우
