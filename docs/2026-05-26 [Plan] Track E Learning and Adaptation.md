---
doc_type: plan
status: superseded
plan_id: alpamayo-track-e-learning-adaptation
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

# Track E: Learning and Adaptation

- Created: 2026-05-26 15:27:39 KST
- Status: planned
- Parent roadmap: `docs/2026-05-19 [Plan] Alpamayo Research and Development.md`
- Migration note: this document is a legacy source draft. Create a Subtask from the Root Task before execution.

## Goal

공개 PAI, 공개 데이터셋, 자체 데이터셋을 사용해 Alpamayo 계열 모델을 SFT, adapter tuning, 또는 RL post-training으로 개선할 수 있는지 검증한다. 이 트랙은 데이터 contract와 평가 체계가 검증된 뒤에 본격 실행한다.

## Scope

Included:

- PAI subset SFT Stage 1/2 short run 계획
- 자체 데이터 small-set overfit 계획
- RL reward 확장 후보 정의
- checkpoint export와 inference 검증 계획

Excluded:

- 데이터 contract 검증 전 대규모 학습
- 안전 reward 없이 실제 차량 적용 주장
- license 검토 없는 제품 적용 판단

## Progress Tracker

| Item | Status | Evidence path or command | Result | Next action |
| --- | --- | --- | --- | --- |
| PAI SFT readiness | Not started | Track A result | Pending | Stage 1/2 scope |
| 자체 데이터 readiness | Not started | Track C result | Pending | overfit sample 선정 |
| compute readiness | Not started | GPU/VRAM inventory | Pending | run scale 결정 |
| reward candidates | Not started | ADE/comfort/reasoning/safety | Pending | reward design note |
| checkpoint validation | Not started | inference/eval commands | Pending | export test |

## Execution Steps

1. 학습 후보를 readiness 기준으로 분류
   - Verify: PAI, public dataset, self dataset 각각 ready/blocked/needs adapter 판정.

2. PAI short SFT 계획 실행 여부 결정
   - Verify: 8 x H100급 자원 또는 축소 실험 가능성.

3. 자체 데이터 small-set overfit 계획 수립
   - Verify: 1 sample, 16-32 samples, held-out split 단계화.

4. RL reward 후보 정의
   - Verify: trajectory ADE, comfort, safety proxy, reasoning grading, reasoning-action consistency 구분.

5. checkpoint export/inference validation 설계
   - Verify: fine-tuned or RL checkpoint가 inference/eval 경로로 돌아오는지 확인.

## Acceptance Criteria

- 학습을 시작하기 전 데이터 contract, metric, compute, license gate가 확인될 것
- small-set overfit 또는 short-run의 성공/실패 기준이 명확할 것
- RL reward는 최적화 대상과 safety side effect를 함께 명시할 것

## Vehicle Relevance Check

- 줄일 리스크: adaptation feasibility, reward design risk, compute scale risk
- 아직 남는 리스크: closed-loop safety, sim-to-real, onboard inference
- 다음 gate: open-loop 개선이 closed-loop/safety metric과 연결되지 않으면 차량 적용 근거로 사용하지 않는다.

## Replan Conditions

- 데이터 규모나 품질이 학습보다 평가/수집 개선을 먼저 요구하는 경우
- GPU 자원이 SFT/RL 요구사항에 미달하는 경우
- 공개 가중치 license가 목표 사용 범위와 충돌하는 경우
