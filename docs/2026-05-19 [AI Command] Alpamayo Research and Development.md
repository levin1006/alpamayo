# AI Command: Alpamayo Research and Development Plan

## 목적

너는 자율주행 연구 및 개발을 지원하는 AI 리서치/엔지니어링 에이전트다. 이 작업의 최종 목표는 Alpamayo 논문과 공개 소스, 오픈 데이터셋, 오픈 시뮬레이션 프레임워크를 기반으로 사용자가 개발 중인 자율주행 차량에 적용 가능한 개발 계획을 수립하는 것이다.
/
다음 네 가지 목표를 동시에 만족하도록 조사하고 정리하라.

1. Alpamayo의 자율주행 방법론을 논문, 소스 코드, 가이드 문서 기준으로 정확히 이해한다.
2. 공개 데이터셋, 모델 가중치, 학습/추론 스크립트를 내려받아 저자가 공개한 수준의 실험 결과를 재현할 수 있는 환경 구축 절차를 도출한다.
3. `/home/user/Workspace/alpasim` 및 `/home/user/Workspace/physical_ai_av` 레포지토리를 함께 분석하여 Alpamayo 방법론으로 모델을 학습·개발·평가하는 방법에 대한 실질적 인사이트를 만든다.
4. 최종적으로 사용자가 개발 중인 실제 자율주행 차량에 이 방법론을 적용하기 위한 단계별 개발 계획과 추가 질문 목록을 제시한다.

## 반드시 참고할 자료

우선 로컬 자료를 확인하고, 최신 정보나 다운로드 링크가 필요한 경우 공식 출처를 웹에서 확인하라.

- 논문 PDF: `/home/user/Workspace/alpamayo/docs/Alpamayo-R1 Bridging Reasoning and Action Prediction for Generalizable Autonomous Driving in the Long Tail, NVIDIA Research.pdf`
- Alpamayo 소스 레포: `/home/user/Workspace/alpamayo`
- Alpamayo README: `/home/user/Workspace/alpamayo/README.md`
- SFT 가이드: `/home/user/Workspace/alpamayo/docs/FINETUNE_SFT.md`
- RL 가이드: `/home/user/Workspace/alpamayo/finetune/rl/README.md`
- 오픈 시뮬레이션 프레임워크: `/home/user/Workspace/alpasim`
- Physical AI AV 데이터셋 관련 레포: `/home/user/Workspace/physical_ai_av`
- 공개 모델 및 데이터셋: Hugging Face의 NVIDIA Alpamayo/Physical AI AV 관련 공식 페이지
- 논문/모델 카드/라이선스/데이터셋 카드/릴리즈 노트

## 조사 원칙

- 사실과 추론을 구분하라. 출처가 있는 내용은 파일 경로, 문서명, URL, 섹션명을 함께 표기하라.
- 최신 가중치, 데이터셋, 설치 명령, 라이선스, 하드웨어 요구사항은 반드시 공식 출처로 재확인하라.
- 코드 분석 시 실제 파일 경로와 주요 클래스/함수/설정 파일을 인용하라.
- 실험 재현 절차는 “명령어”, “필요 리소스”, “예상 산출물”, “검증 기준”으로 나누어 작성하라.
- 사용자의 실제 차량 적용과 관련된 불확실성은 숨기지 말고 질문으로 정리하라.
- 과도한 일반론보다 이 레포지토리와 연결되는 구체적 개발 경로를 우선하라.

## 산출물 형식

최종 답변은 다음 구조로 작성하라.

### 1. Executive Summary

- Alpamayo가 해결하려는 자율주행 문제
- 핵심 아이디어: reasoning, action prediction, trajectory generation, long-tail generalization
- 공개 구현으로 가능한 것과 불가능한 것
- 실제 차량 적용까지의 가장 큰 기술 리스크

### 2. Alpamayo 방법론 해설

논문과 코드 기준으로 다음을 설명하라.

- 입력 데이터 구조: 카메라, egomotion, calibration, clip/chunk 구성
- 출력 구조: reasoning trace, trajectory, action token 또는 continuous trajectory
- 모델 구조: VLM backbone, action expert, diffusion/trajectory module, tokenizer/action space
- Chain-of-Causation 또는 reasoning 데이터가 학습에 쓰이는 방식
- SFT와 RL post-training의 역할 차이
- inference, evaluation, fine-tuning 경로가 코드에서 어떻게 연결되는지

### 3. 소스 코드 맵

다음 레포지토리를 각각 분석하고, 중요한 파일을 표로 정리하라.

- `/home/user/Workspace/alpamayo`
- `/home/user/Workspace/alpasim`
- `/home/user/Workspace/physical_ai_av`

각 표에는 다음 열을 포함하라.

- 경로
- 역할
- Alpamayo 개발 흐름에서의 사용 위치
- 수정 또는 확장 가능성

### 4. 실험 환경 구축 계획

저자가 공개한 수준의 실험 결과 재현을 목표로 다음을 작성하라.

- Python, CUDA, PyTorch, uv, flash-attn, vLLM, Cosmos-RL 요구사항
- GPU/VRAM/디스크/네트워크 요구사항
- Hugging Face 인증 및 접근 권한 요청 절차
- 모델 가중치 다운로드 절차
- Physical AI AV 데이터셋 다운로드 절차
- 최소 추론 테스트 절차
- SFT stage 1, SFT stage 2 실행 절차
- RL local test 실행 절차
- checkpoint export 및 inference 검증 절차
- 로그, metric, artifact 저장 위치

각 절차는 실행 가능한 명령어 블록과 함께 작성하라. 단, 실제 토큰, 개인 경로, 비밀값은 placeholder로 표기하라.

### 5. 재현 실험 체크리스트

다음 항목별로 체크리스트를 작성하라.

- 설치 성공 기준
- 데이터셋 로딩 성공 기준
- 모델 로딩 성공 기준
- inference 성공 기준
- SFT 학습 진행 성공 기준
- SFT evaluation 성공 기준
- RL rollout/reward/training 성공 기준
- 논문 또는 공개 문서와 비교할 metric
- 실패 시 우선 확인할 로그와 설정

### 6. alpasim 및 physical_ai_av 활용 전략

두 레포지토리를 분석한 뒤 다음을 제안하라.

- Alpamayo 입력 포맷과 `physical_ai_av` 데이터 구조의 연결 방식
- `alpasim` 시뮬레이션 출력 데이터를 Alpamayo 학습/평가 데이터로 변환하는 방법
- 시뮬레이션에서 생성해야 할 scene, camera, ego state, trajectory, annotation 구성
- long-tail scenario를 생성하거나 선별하는 방법
- sim-to-real 또는 dataset-to-vehicle 전이에서 예상되는 문제
- validation set, regression test, closed-loop simulation 평가 설계

### 7. 실제 차량 적용 로드맵

사용자 차량에 적용하기 위한 단계별 계획을 작성하라.

단계 예시:

1. 공개 inference 재현
2. 공개 데이터셋 subset 기반 fine-tuning
3. alpasim 기반 synthetic scenario 생성
4. physical_ai_av 형식과 사용자 데이터 형식 매핑
5. 사용자 차량 센서 캘리브레이션 및 시간 동기화 정리
6. 사용자 데이터로 SFT 또는 adapter fine-tuning
7. closed-loop simulation 검증
8. 제한된 오프라인 평가
9. 안전 제약이 있는 shadow-mode 테스트
10. 실제 제어계 통합 전 safety gate 정의

각 단계마다 목표, 입력, 산출물, 검증 기준, 리스크를 작성하라.

### 8. 사용자에게 물어볼 질문

개발 계획을 구체화하기 위해 반드시 필요한 질문을 우선순위별로 작성하라.

질문 범주는 다음을 포함하라.

- 차량 플랫폼 및 제어 인터페이스
- 센서 구성: camera count, FOV, resolution, frame rate, synchronization
- calibration 보유 여부
- localization/egomotion source
- 기존 데이터셋 크기와 포맷
- 주행 환경: 도로 유형, 국가, 속도 범위, ODD
- 목표 기능: trajectory prediction, planning, end-to-end control, reasoning/logging
- 실시간 요구사항: latency, throughput, onboard compute
- 안전 요구사항과 테스트 제한
- 사용할 수 있는 GPU/스토리지/클러스터 자원
- 공개 가중치 사용 라이선스와 상업적 사용 가능성 검토 필요 여부

질문은 “왜 필요한지”와 “답변에 따라 계획이 어떻게 달라지는지”를 함께 적어라.

### 9. 권장 개발 계획

조사 결과를 바탕으로 2주, 1개월, 3개월 단위의 실행 계획을 작성하라.

각 기간마다 다음을 포함하라.

- 주요 목표
- 작업 목록
- 필요한 입력 자료
- 예상 산출물
- 검증 방법
- 중단 조건 또는 재계획 조건

### 10. 리스크 및 의사결정 포인트

다음 리스크를 구체적으로 평가하라.

- 하드웨어 부족
- 데이터셋 접근권 또는 라이선스 제한
- 모델 가중치의 상업/제품 적용 제한
- 센서 구성이 논문/공개 모델과 다른 문제
- open-loop metric과 closed-loop driving 성능의 차이
- reasoning trace 품질과 실제 planning 안정성의 관계
- sim-to-real gap
- 실제 차량 안전 검증 부담

각 리스크마다 완화 전략과 다음 의사결정 질문을 제시하라.

## 작업 방식

1. 먼저 각 레포지토리와 문서를 읽고 파일/문서 지도를 만든다.
2. 논문 PDF에서 방법론, 실험 설정, metric, 한계점을 추출한다.
3. README, SFT, RL 문서에서 재현 절차와 하드웨어 요구사항을 정리한다.
4. `src/alpamayo_r1`, `finetune/sft`, `finetune/rl` 코드 흐름을 분석한다.
5. `alpasim`, `physical_ai_av`와 Alpamayo 입력/학습 경로의 연결점을 찾는다.
6. 공식 Hugging Face 문서에서 모델/데이터셋 접근, 라이선스, 최신 다운로드 절차를 확인한다.
7. 최종적으로 사용자가 바로 답변할 수 있는 질문 목록과 개발 계획을 제시한다.

## 품질 기준

- 단순 요약이 아니라, 사용자가 실제로 실험 환경을 만들고 다음 개발 결정을 내릴 수 있는 수준이어야 한다.
- 모든 핵심 주장에는 근거 파일, 문서, 코드 경로, 공식 URL 중 하나 이상을 붙여라.
- 명령어는 복사해 실행할 수 있게 작성하되, 환경별 값은 `<PLACEHOLDER>`로 표시하라.
- 확인하지 못한 내용은 “미확인”으로 표시하고, 확인 방법을 제안하라.
- 실제 차량 적용과 안전 검증은 보수적으로 다루고, 공개 모델 재현과 실제 제어 적용을 명확히 구분하라.
