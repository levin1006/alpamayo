---
doc_type: task
task_role: subtask
status: not_started
task_id: alpamayo-track-a-public-reproduction
parent_plan: docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md
parent_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
created_at: 2026-05-26 18:24:55 KST
updated_at: 2026-05-26 18:24:55 KST
---

# Track A Public Alpamayo/PAI Reproduction Task

## Objective

공개 Alpamayo 1/PAI/AlpaSim 경로가 현재 환경에서 실제로 재현 가능한지 확인한다.
이 Subtask는 후속 Track B-F가 의존하는 baseline contract와 환경 리스크를
검증하는 첫 gate다.

## Parent Plan

- Canonical Plan: `docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md`
- Root Task: `docs/2026-05-26 [Task] Alpamayo R&D Root Task.md`
- Source draft: `docs/2026-05-26 [Plan] Track A Public Alpamayo Reproduction.md`

## Scope

Included:

- Hugging Face access 상태 확인
- Alpamayo 1 inference smoke path 확인
- PAI subset 로딩 경로 확인
- AlpaSim `alpamayo1` 또는 `alpamayo1_5` driver 실행 가능성 확인
- 실행 결과와 실패 원인 기록

Excluded:

- 장시간 SFT/RL training
- custom dataset adapter 구현
- 실제 차량 데이터 사용
- 실제 차량 제어 통합

## Checklist

| Item | Status | Evidence path or command | Result | Next action |
| --- | --- | --- | --- | --- |
| HF access 확인 | not_started | `hf auth whoami`, gated repo access | Pending | Access/token 확인 |
| Python/uv 환경 확인 | not_started | `uv sync --active` | Pending | dependency install |
| Alpamayo inference | not_started | `python src/alpamayo_r1/test_inference.py` | Pending | run and log |
| PAI subset 확인 | not_started | `scripts/download_pai.py`, `PAIDataset` load | Pending | 최소 chunk 결정 |
| AlpaSim driver smoke | not_started | `uv run alpasim_wizard ... driver=alpamayo1` | Pending | GPU/scene 확인 |
| Reproduction report | not_started | docs/log artifact | Pending | 결과 정리 |

## Execution Steps

1. 환경과 접근권 확인
   - Verify: HF login, gated model/dataset access, CUDA visible, Python 3.12 environment.

2. Alpamayo inference smoke 실행
   - Verify: CoC text 출력, `pred_xyz` 생성, minADE 계산.

3. PAI subset 다운로드 또는 로딩 확인
   - Verify: `features.csv`, `clip_index.parquet`, metadata, camera zip, egomotion zip 존재.

4. AlpaSim Alpamayo driver smoke 검토
   - Verify: rollout directory, metrics, optional reasoning overlay 생성.

5. 결과 보고서 작성
   - Verify: 성공/실패 분기, 로그 위치, 다음 트랙으로 넘길 contract 기록.

## Acceptance Criteria

- inference 또는 AlpaSim smoke 중 최소 하나가 실행 가능한 상태로 확인될 것
- 실패 시 원인이 HF access, GPU memory, dependency, dataset, simulator 중 어디인지 분류될 것
- Track B/C가 사용할 Alpamayo input/output contract가 문서화될 것
- 사용자가 결과의 의미와 한계를 설명할 수 있을 것

## Vehicle Relevance Check

- 줄일 리스크: compute risk, dependency risk, public model usability risk, baseline trajectory contract risk
- 아직 남는 리스크: self dataset compatibility, closed-loop safety, sim-to-real, vehicle control interface
- 다음 gate: public reproduction이 실패하면 Track B/C/E는 adapter 설계 위주로 축소하고, 실행형 학습 계획은 보류한다.

## User Understanding Check

Track A 완료 전 사용자는 다음을 설명할 수 있어야 한다.

- Alpamayo 공개 inference가 어떤 입력과 출력을 갖는가
- PAI dataset contract가 후속 자체 데이터 adapter에 왜 중요한가
- AlpaSim smoke가 open-loop 평가와 어떻게 다른가
- 실패 시 어떤 원인이 후속 Track B/C/E를 막는가

## Replan Conditions

- 24GB 이상 GPU 접근이 불가능한 경우
- HF gated access가 확보되지 않는 경우
- 공개 모델 license가 목표 사용 범위와 충돌하는 경우

## Execution Log

아직 실행 전이다.

## Validation

아직 실행 전이다.

## Open Issues

- HF access/token 상태 미확인
- GPU/VRAM 상태 미확인
- AlpaSim scene/model cache 상태 미확인

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-05-26 18:24:55 KST | created | Track A legacy Plan의 Progress Tracker를 Subtask 실행 문서로 이관 |
