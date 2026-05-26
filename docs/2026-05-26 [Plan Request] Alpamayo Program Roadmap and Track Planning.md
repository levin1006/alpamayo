# Alpamayo Program Roadmap and Track Planning Request

- Created: 2026-05-26 15:27:39 KST
- Request status: accepted for planning
- Source plan: `docs/2026-05-19 [Plan] Alpamayo Research and Development.md`
- Source command: `docs/2026-05-19 [AI Command] Alpamayo Research and Development.md`

## 1. Request Summary

기존 Alpamayo 연구 개발 계획서는 유지하되, 최종 목표와 그 목표에 도달하기 위한 흔들리지 않는 roadmap을 명확히 정의한다. 기존 문서의 분석량과 근거 밀도는 보존하며, 상위 roadmap에는 지나치게 상세한 구현 절차를 넣지 않는다. 구현/실험 수준의 세부 계획은 트랙별 별도 문서로 분리한다.

## 2. User Intent

사용자의 우려는 두 가지다.

1. 최종 목표를 인지하지 못한 채 공개 모델 재현이나 논문 검토에 머무르면 실제 차량 적용으로 이어지지 않는 작업이 될 수 있다.
2. 반대로 최종 목표를 너무 앞세우면 당장 필요한 분석과 개발의 목표가 흐려지고, 아직 검증되지 않은 가정을 바탕으로 과도한 실행 계획이 만들어질 수 있다.

따라서 계획 체계는 최종 목표를 방향과 검증 기준으로 고정하되, 실제 실행은 독립된 트랙별 계획으로 작게 나누어 진행해야 한다.

## 3. Planning Objective

다음 산출물을 작성한다.

1. 기존 연구 개발 계획서 업데이트
   - North Star, non-negotiable principles, program roadmap, track structure, dependency map, top-down/bottom-up review rule 추가
   - 기존 방법론/코드맵/환경구축/체크리스트/리스크의 볼륨 보존

2. 트랙별 실행 계획 문서
   - 각 트랙마다 목표, 범위, 전제조건, 진행 상태, 실행 단계, 산출물, 검증 기준, 중단/재계획 조건, vehicle relevance check 포함
   - 진행 상황과 결과를 추적 가능한 형식으로 작성

3. 계획 검증 구조
   - top-down roadmap이 실제 실험 결과와 충돌하지 않는지 bottom-up으로 점검하는 절차 정의
   - 실험 결과가 전체 roadmap을 어떻게 갱신해야 하는지 명시

## 4. Required References

반드시 다음 문서를 기준으로 한다.

- `docs/2026-05-19 [AI Command] Alpamayo Research and Development.md`
- `docs/2026-05-19 [Plan] Alpamayo Research and Development.md`
- Alpamayo README, SFT guide, RL guide
- `/home/user/Workspace/alpasim`
- `/home/user/Workspace/physical_ai_av`
- 공식 Hugging Face 모델/데이터셋 페이지

## 5. Scope Boundary

이번 계획 수립 작업의 범위:

- 문서 체계 정비
- 상위 roadmap 정의
- Track A-F의 실행 계획 초안 작성
- 각 track의 gate와 progress tracking 형식 정의

이번 계획 수립 작업에서 제외:

- 실제 모델 다운로드
- 실제 dataset 다운로드
- inference/SFT/RL/AlpaSim 실행
- 코드 구현
- license 법무 판단의 결론 확정
- 실제 차량 제어 통합 결정

## 6. Planning Principles

1. 최종 목표는 모든 트랙의 relevance filter로 사용한다.
2. 각 실행 계획은 1-4주 안에 검증 가능한 단위로 유지한다.
3. 모든 트랙은 진행 상태와 결과를 추적할 수 있어야 한다.
4. public reproduction, public dataset, self dataset, simulation, learning, vehicle closed-loop를 하나의 문서에 뭉개지 않는다.
5. top-down 방향과 bottom-up 실험 결과가 충돌하면 bottom-up 결과를 우선해 roadmap을 갱신한다.

## 7. Acceptance Criteria

- 기존 계획서에 North Star와 roadmap이 추가되어도 기존 분석 섹션이 삭제되지 않을 것
- 트랙별 별도 문서가 존재할 것
- 각 트랙 문서가 진행 상태, gate, verification, replan condition을 포함할 것
- nuScenes와 자체 데이터셋 open-loop 평가가 roadmap에 포함될 것
- 자체 데이터 기반 simulation/replay와 최종 vehicle VLA closed-loop가 roadmap에 포함될 것
- 실제 차량 적용과 공개 모델 재현의 경계가 명확할 것

## 8. Resulting Plan Artifacts

- `docs/2026-05-19 [Plan] Alpamayo Research and Development.md`
- `docs/2026-05-26 [Plan] Track A Public Alpamayo Reproduction.md`
- `docs/2026-05-26 [Plan] Track B Public Dataset Open Loop Evaluation.md`
- `docs/2026-05-26 [Plan] Track C Self Dataset Open Loop Evaluation.md`
- `docs/2026-05-26 [Plan] Track D Self Data Simulation and Replay.md`
- `docs/2026-05-26 [Plan] Track E Learning and Adaptation.md`
- `docs/2026-05-26 [Plan] Track F Vehicle Shadow and VLA Closed Loop.md`

