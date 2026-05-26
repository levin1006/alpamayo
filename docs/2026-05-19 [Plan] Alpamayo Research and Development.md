---
doc_type: plan
status: superseded
plan_id: alpamayo-rnd
version: 1
canonical: false
created_at: 2026-05-19 17:09:08 KST
approved_at: 2026-05-26 15:27:39 KST
root_plan:
supersedes:
superseded_by: docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md
root_task:
revision_type: initial_baseline
revision_reason: initial research and roadmap plan, superseded by canonical v2 harness
---

# Alpamayo Research and Development Plan

- Created: 2026-05-19 17:09:08 KST
- Status: program roadmap plus initial research draft
- Source command: `docs/2026-05-19 [AI Command] Alpamayo Research and Development.md`
- Roadmap update: 2026-05-26 16:29:04 KST

## 0. North Star and Program Roadmap

### North Star

이 프로그램의 최종 목표는 Alpamayo 논문, 공개 구현, 공개 데이터셋, AlpaSim, Physical AI AV, nuScenes, 자체 구축 데이터셋, 자체 구축 자율주행 차량 데이터를 하나의 검증 가능한 연구개발 흐름으로 연결하여, 최종적으로 자체 차량에서 안전 제약이 있는 VLA closed-loop 평가까지 도달하는 것이다.

이 목표는 매 실행 계획의 범위가 아니라, 매 실행 계획을 평가하는 기준이다. 즉 개별 트랙은 작게 실행하되, 각 결과가 최종 차량 VLA closed-loop 목표의 어떤 리스크를 줄였는지 반드시 확인한다.

### Non-Negotiable Principles

1. 공개 재현은 최종 성과가 아니라 전제 검증이다. Alpamayo/PAI/AlpaSim 재현은 이후 public dataset, 자체 데이터, 차량 적용으로 이어질 수 있어야 한다.
2. open-loop 결과는 필요하지만 충분하지 않다. minADE/ADE는 trajectory 품질의 중요한 신호지만, closed-loop simulation, shadow-mode, safety gate 없이는 실제 차량 적용 판단으로 승격하지 않는다.
3. 데이터 contract가 모델보다 먼저다. Alpamayo input/output contract, camera order, egomotion frame, timestamp alignment, calibration 품질이 검증되지 않으면 SFT/RL 결과는 신뢰하지 않는다.
4. 실제 차량 제어는 마지막 단계다. 공개 모델은 certified AV stack이 아니므로, offline evaluation, closed-loop simulation, shadow-mode, safety monitor를 통과하기 전까지 actuation 통합을 목표로 두지 않는다.
5. top-down roadmap과 bottom-up evidence를 함께 사용한다. 상위 목표는 방향을 고정하고, 세부 트랙은 실행 결과에 따라 다음 단계의 현실성을 갱신한다.
6. 사용자 이해도는 완료 기준의 일부다. 계획, 구현, 실험, 결과 해석은 AI가 이해하고 넘어가는 산출물이 아니라 사용자가 핵심 코드 흐름과 실험 의미를 설명하고 리뷰할 수 있는 수준으로 문서화되어야 한다.

### Planning Hierarchy

| Layer | Purpose | Update cadence | Artifact |
| --- | --- | --- | --- |
| North Star | 흔들리지 않는 최종 목표와 안전 경계 고정 | 목표 변경 시에만 | 이 문서의 Section 0 |
| Program Roadmap | 전체 트랙, 의존성, gate, 리스크 연결 | 주요 실험 결과 이후 | 이 문서의 Section 0 및 Section 7/9 |
| Track Execution Plans | 각 트랙의 1-4주 단위 실행 계획, 진행 상태, 결과 추적 | 실행 중 지속 갱신 | `docs/2026-05-26 [Plan] Track *.md` |
| Experiment Logs | 명령어, 환경, 결과, 실패 원인 기록 | 실험마다 | 후속 log 문서 또는 실험 산출물 |
| Learning/Review Notes | 사용자가 구현·실험·해석을 직접 설명할 수 있도록 개념, 코드 경로, 확인 질문 정리 | 의미 있는 계획/구현/실험 결과마다 | Track 문서의 review section 또는 별도 note |

### Program Tracks

| Track | Name | Primary question | First gate | Output used by |
| --- | --- | --- | --- | --- |
| A | Public Alpamayo/PAI Reproduction | 공개 Alpamayo를 로컬에서 재현할 수 있는가? | inference, PAI load, AlpaSim smoke 중 최소 하나 이상 완료 | 모든 후속 트랙 |
| B | Public Dataset Open-Loop Evaluation | nuScenes 등 공개 데이터셋을 Alpamayo 평가 contract로 매핑할 수 있는가? | nuScenes-to-Alpamayo sample feasibility report | Track C/E |
| C | Self Dataset Open-Loop Evaluation | 자체 데이터셋을 Alpamayo input/output contract로 변환해 open-loop 평가할 수 있는가? | sample converter prototype와 metric smoke | Track D/E/F |
| D | Self-Data Simulation and Replay | 자체 데이터 기반 replay/simulation 환경으로 closed-loop 또는 pseudo-closed-loop 평가가 가능한가? | replay/simulation design proof 및 log schema | Track F |
| E | Learning and Adaptation | 공개/자체 데이터로 SFT, adapter tuning, RL reward 실험을 의미 있게 수행할 수 있는가? | small-set overfit 또는 short-run metric | Track F |
| F | Vehicle Shadow and VLA Closed-Loop | 실제 차량에서 안전 제약 하에 VLA를 평가할 수 있는가? | offline/shadow safety gate 통과 | 최종 목표 |

### Dependency Map

```text
Track A public reproduction
  -> Track B public dataset mapping
  -> Track C self dataset open-loop
  -> Track D self-data simulation/replay
  -> Track E learning/adaptation
  -> Track F shadow-mode and vehicle closed-loop
```

Track B와 Track C는 병렬로 일부 진행할 수 있다. 다만 Track E는 데이터 contract 검증 없이 시작하지 않는다. Track F는 Track C/D/E의 산출물이 safety gate를 만족하기 전까지 설계만 수행하고 실제 제어 실험은 보류한다.

### Track Plan Index

- Track A: `docs/2026-05-26 [Plan] Track A Public Alpamayo Reproduction.md`
- Track B: `docs/2026-05-26 [Plan] Track B Public Dataset Open Loop Evaluation.md`
- Track C: `docs/2026-05-26 [Plan] Track C Self Dataset Open Loop Evaluation.md`
- Track D: `docs/2026-05-26 [Plan] Track D Self Data Simulation and Replay.md`
- Track E: `docs/2026-05-26 [Plan] Track E Learning and Adaptation.md`
- Track F: `docs/2026-05-26 [Plan] Track F Vehicle Shadow and VLA Closed Loop.md`

### Vehicle Relevance Check Template

각 트랙 문서는 아래 질문에 답해야 한다.

- 이번 작업이 자체 차량 VLA closed-loop 목표에 주는 정보는 무엇인가?
- 줄어든 리스크는 무엇인가? 예: sensor format, trajectory contract, compute, data quality, simulation, safety.
- 아직 줄지 않은 리스크는 무엇인가?
- 어떤 결과가 나오면 다음 트랙으로 진행하고, 어떤 결과가 나오면 재계획해야 하는가?
- 사용자가 이 결과를 리뷰하기 위해 이해해야 할 핵심 개념과 코드 경로는 무엇인가?
- 사용자가 직접 설명할 수 있어야 다음 단계로 넘어갈 수 있는 질문은 무엇인가?

### Top-Down and Bottom-Up Review Rule

상위 roadmap은 먼저 top-down으로 정의한다. 그러나 각 트랙의 세부 계획과 실험 결과가 쌓인 뒤에는 bottom-up review를 수행한다. 이 review의 목적은 전체 계획에 논리적 비약이 있는지, 리소스와 데이터 조건상 현실적으로 달성 가능한지, 특정 트랙이 최종 목표와 무관한 방향으로 비대해지고 있지 않은지 점검하는 것이다.

이 review에는 사용자 이해도 점검을 포함한다. 사용자가 핵심 구현 경로, 실험 설정, 결과의 의미와 한계를 설명하지 못하는 상태라면 해당 트랙은 기술 산출물이 있어도 완료로 보지 않는다. 이 경우 다음 구현으로 진행하지 않고 learning/review note를 먼저 작성하거나 보강한다.

## 1. Executive Summary

Alpamayo 1은 multi-camera image와 egomotion history를 입력으로 받아 Chain-of-Causation(CoC) reasoning trace와 6.4초 미래 trajectory를 생성하는 reasoning VLA다. 논문은 reasoning을 단순 설명이 아니라 action prediction을 개선하는 기능적 구성요소로 다루며, CoC reasoning, action prediction, trajectory generation, long-tail generalization을 한 학습 경로 안에 묶는다.

현재 공개 구현으로 가능한 것:

- Alpamayo 1 inference 재현: `python src/alpamayo_r1/test_inference.py`
- Physical AI AV subset 다운로드 및 local dataset 구성
- SFT Stage 1/2 fine-tuning
- Cosmos-RL 기반 RL local pipeline 검증
- RL checkpoint를 Hugging Face checkpoint 형태로 export
- AlpaSim에서 Alpamayo 1/1.5 closed-loop driver 실행

현재 공개 구현과 논문 사이의 주요 차이:

- Alpamayo 1 README는 공개 10B 모델이 RL post-training을 거치지 않았고, RL-trained weights는 릴리스에 포함되지 않는다고 명시한다.
- Alpamayo 1 공개 모델은 explicit route/navigation input과 meta-action/general VQA를 포함하지 않는다.
- 논문은 route conditioning, meta-actions, RL reasoning reward까지 다루지만 공개 코드의 기본 RL reward는 trajectory ADE와 comfort 중심 demo reward다.

가장 큰 실제 차량 적용 리스크:

- 공개 모델/가중치 license와 제품 적용 가능성
- 사용자 차량 sensor rig가 Alpamayo/PAI의 4-camera 또는 7-camera 가정과 다를 가능성
- open-loop minADE와 closed-loop driving safety 간 불일치
- CoC reasoning 품질이 실제 planning 안정성을 보장하지 않는 문제
- 시뮬레이션/공개 데이터에서 실제 차량 ODD로 전이할 때의 sim-to-real gap

## 2. Alpamayo 방법론 해설

### 입력 데이터 구조

근거:

- `src/alpamayo_r1/load_physical_aiavdataset.py:27`의 `load_physical_aiavdataset()`는 기본 16 history step, 64 future step, 0.1초 간격, 4개 camera, 4 temporal frames를 사용한다.
- 같은 파일은 기본 camera를 `camera_cross_left_120fov`, `camera_front_wide_120fov`, `camera_cross_right_120fov`, `camera_front_tele_30fov`로 둔다.
- 출력 sample key는 `image_frames`, `camera_indices`, `ego_history_xyz`, `ego_history_rot`, `ego_future_xyz`, `ego_future_rot`, `relative_timestamps`, `absolute_timestamps`, `t0_us`, `clip_id`다.
- `src/alpamayo_r1/data/pai.py:26`의 `PAIDataset`은 local PAI directory와 `clip_index.parquet`를 기반으로 `load_physical_aiavdataset()`를 호출하고, 필요 시 VLA preprocessor를 붙인다.

해석:

- Alpamayo 공개 경로의 최소 입력은 multi-camera image tensor와 t0 기준 ego-frame history pose다.
- calibration은 PAI 다운로드 및 dataset에는 포함 가능하지만, 공개 inference의 model input dict에는 직접 들어가지 않는다.
- 실제 차량 적용 시 calibration은 image rectification, camera naming/order, ego-frame transform 검증에 필요하다.

### 출력 구조

근거:

- `src/alpamayo_r1/test_inference.py:56`은 `sample_trajectories_from_data_with_vlm_rollout()`를 호출해 `pred_xyz`, `pred_rot`, `extra`를 받는다.
- `src/alpamayo_r1/models/alpamayo_r1.py:321`은 `return_extra=True`일 때 VLM이 생성한 text token을 `extra`로 추출한다.
- `src/alpamayo_r1/test_inference.py:66`은 `extra["cot"]`를 Chain-of-Causation으로 출력한다.
- `src/alpamayo_r1/test_inference.py:68` 이후는 `ego_future_xyz`와 예측 XY trajectory의 minADE를 계산한다.

해석:

- 공개 inference의 실질 출력은 CoC text와 continuous trajectory다.
- discrete trajectory token은 VLM training/RL 경로에서 쓰이며, inference의 최종 제어 후보는 action expert와 diffusion decoder가 만든 continuous waypoints다.

### 모델 구조

근거:

- `src/alpamayo_r1/models/base_model.py:200`의 `ReasoningVLAConfig` 기본 backbone은 `Qwen/Qwen3-VL-8B-Instruct`, trajectory vocab size는 768, history token은 16, future token은 64다.
- `src/alpamayo_r1/models/base_model.py:285`의 `ReasoningVLA`는 Qwen3-VL backbone과 trajectory tokenizer를 초기화한다.
- `src/alpamayo_r1/models/alpamayo_r1.py:75`의 `AlpamayoR1`은 `ReasoningVLA`를 상속하고, expert transformer, action space, diffusion, action projection을 추가한다.
- `src/alpamayo_r1/models/alpamayo_r1.py:124` 이후 inference는 먼저 VLM rollout으로 reasoning을 생성하고, 그 KV-cache를 action expert가 사용해 diffusion sampling을 수행한다.

해석:

- 공개 Alpamayo 1 구현은 "VLM backbone + action expert + diffusion/action-space" 구조다.
- 논문은 Cosmos-Reason backbone을 설명하지만, local config/code는 Qwen3-VL 계열 processor/backbone 설정과 공개 checkpoint config를 함께 사용한다. 공개 HF 모델 card와 checkpoint config 확인이 추가로 필요하다.

### SFT와 RL의 역할 차이

근거:

- `docs/FINETUNE_SFT.md:54`는 학습을 2단계로 설명한다. Stage 1은 VLM이 discrete trajectory token을 내도록 fine-tune하고, Stage 2는 Stage 1 VLM을 freeze한 채 action expert trajectory diffusion을 학습한다.
- `finetune/sft/models/sft_base_model.py:43`은 future trajectory를 discrete token으로 바꾸는 `tokenize_future_trajectory()`를 제공한다.
- `finetune/sft/models/sft_alpamayo_r1.py:52`는 `cotrain_vlm`이 false이면 VLM parameter를 freeze한다.
- `finetune/rl/README.md:358`은 RL 코드가 VLM backbone을 post-train하며 action expert는 학습하지 않는다고 설명한다.
- `finetune/rl/README.md:415`는 reasoning text가 `<|cot_end|>` 이전, trajectory token이 `<|traj_future_start|>` 이후의 rollout completion string에 들어간다고 설명한다.

해석:

- SFT Stage 1은 language/action token generation 능력 조정, Stage 2는 continuous trajectory expert 학습이다.
- 공개 RL pipeline은 text/discrete-token VLM backbone alignment에 가까우며, action expert continuous decoder의 RL 학습은 future release로 남아 있다.

## 3. Source Code Map

### `/home/user/Workspace/alpamayo`

| Path | Role | Alpamayo 개발 흐름에서의 사용 위치 | 수정 또는 확장 가능성 |
| --- | --- | --- | --- |
| `README.md` | 공개 릴리스 개요, 설치, inference, 공개 범위 | 전체 재현 계획의 기준 | license/제약 확인 근거로 유지 |
| `docs/FINETUNE_SFT.md` | SFT Stage 1/2 절차와 metric 예시 | fine-tuning 재현 | 사용자 dataset override 절차 보강 가능 |
| `finetune/rl/README.md` | Cosmos-RL local/multi-node 절차 | RL post-training 검증 | custom reward, user data 경로 설계 근거 |
| `src/alpamayo_r1/test_inference.py` | 최소 inference smoke path | 모델/데이터 접근 검증 | 사용자 clip 입력 CLI화 가능 |
| `src/alpamayo_r1/load_physical_aiavdataset.py` | PAI clip을 model input으로 변환 | PAI와 사용자 데이터 adapter 기준 | 사용자 데이터 loader 구현 기준 |
| `src/alpamayo_r1/data/pai.py` | SFT/RL용 PAI Dataset | training/eval dataset path | alpasim/user data dataset class 추가 기준 |
| `src/alpamayo_r1/processor/qwen_processor.py` | chat template, image preprocessing, collate | SFT/RL tokenized_data 생성 | camera id, frame count, prompt component 조정 지점 |
| `src/alpamayo_r1/models/base_model.py` | VLM backbone, special tokens, trajectory token fusion | Stage 1, inference 공통 | token/action contract 변경 시 핵심 위험 지점 |
| `src/alpamayo_r1/models/alpamayo_r1.py` | action expert/diffusion inference | continuous trajectory sampling | inference sampling, decoder, action space 확장 |
| `finetune/sft/train_hf.py` | Hydra 기반 SFT entry | Stage 1/2 training | dataset/config override 실험 |
| `finetune/sft/configs/sft_base.yaml` | PAI train/val dataset, trainer 기본값 | SFT 실행 | local_dir, chunk_ids, W&B, eval metric 조정 |
| `scripts/download_pai.py` | HF PAI subset downloader | 데이터 준비 | required components 추가 |
| `scripts/convert_release_config_to_training.py` | release checkpoint를 RL training format으로 변환 | RL local test 전처리 | Alpamayo 1/1.5 모델 선택, local VLM path |
| `finetune/rl/rewards/aggregated_reward.py` | demo reward: ADE + comfort | RL local test | reasoning, safety, closed-loop reward 추가 |

### `/home/user/Workspace/alpasim`

| Path | Role | Alpamayo 개발 흐름에서의 사용 위치 | 수정 또는 확장 가능성 |
| --- | --- | --- | --- |
| `README.md` | AlpaSim 목적, driver support, docs index | closed-loop simulation 진입점 | Alpamayo evaluation workflow 문서화 |
| `docs/TUTORIAL.md` | Docker compose/wizard 실행, 결과 구조, Alpamayo 실행 | simulation smoke/reasoning overlay | Alpamayo-specific validation preset 추가 |
| `docs/DESIGN.md` | microservice architecture, runtime-driver-controller loop | closed-loop 설계 이해 | 사용자 차량 stack 대응도 분석 |
| `docs/DATA_PIPELINE.md` | `.asl` log 구조 | sim output을 training/eval data로 변환 | ASL to PAI-like sample converter 후보 |
| `src/driver/src/alpasim_driver/models/alpamayo_base.py` | Alpamayo driver 공통 adapter | live simulated frame/pose -> Alpamayo input | 사용자 차량 runtime adapter의 직접 참고 대상 |
| `src/driver/src/alpasim_driver/models/alpamayo1_model.py` | Alpamayo 1 checkpoint 로딩 | AlpaSim Alpamayo 1 실행 | local checkpoint path 및 sampling params |
| `src/driver/src/alpasim_driver/models/alpamayo1_5_model.py` | Alpamayo 1.5 및 optional CFG nav | Alpamayo 1.5 closed-loop 실험 | route/nav 전략 비교 |
| `src/wizard/configs/driver/alpamayo1.yaml` | Alpamayo 1 driver config | 4cam/4frame/batch1 실행 기준 | user ODD config preset |
| `src/wizard/configs/driver/alpamayo1_5.yaml` | Alpamayo 1.5 config | 1.5/CFG nav 실험 | navigation experiment path |
| `src/wizard/configs/driver/alpamayo_configs.yaml` | 4-camera 1080p 10 Hz runtime config | sensor simulation alignment | sensor rig mismatch 실험 |
| `src/eval/src/eval/scorers/minADE.py` | closed-loop predicted trajectory minADE scorer | simulation regression metric | GT/self target 선택 정책 검토 |
| `src/eval/src/eval/scorers/collision.py` | collision metric | safety regression | vehicle bbox/at-fault 기준 보강 |
| `src/eval/src/eval/scorers/offroad.py` | offroad metric | safety regression | map/road edge 품질 영향 분석 |

### `/home/user/Workspace/physical_ai_av`

| Path | Role | Alpamayo 개발 흐름에서의 사용 위치 | 수정 또는 확장 가능성 |
| --- | --- | --- | --- |
| `README.md` | dataset devkit 개요와 HF 접근 조건 | PAI data access 시작점 | 사용자 데이터 변환 가이드 보강 |
| `src/physical_ai_av/dataset.py` | HF dataset interface, features, clip index, feature loaders | Alpamayo loader의 upstream API | local mirror, chunk download, feature presence 검증 |
| `src/physical_ai_av/calibration.py` | intrinsics/extrinsics/vehicle dimensions 구조 | camera/ego-frame 정합 | 사용자 calibration adapter |
| `src/physical_ai_av/egomotion.py` | egomotion state/interpolator | ego history/future sampling | localization/IMU/odometry bridge |
| `src/physical_ai_av/video.py` | timestamp 기반 video frame reader | multi-camera frame sampling | 사용자 camera log reader bridge |
| `src/physical_ai_av/utils/hf_interface.py` | HF download/cache abstraction | gated dataset 접근 | local/offline mode와 download size 관리 |
| `tests/smoke_test.py` | package smoke check | 환경 검증 최소 기준 | dataset API smoke test 확장 |

## 4. 실험 환경 구축 계획

### 공통 환경

근거:

- `README.md`는 Python 3.12, Linux, 24GB 이상 VRAM GPU를 inference 최소 요구로 둔다.
- `pyproject.toml`은 Python `==3.12.*`, `torch==2.8.0`, `transformers==4.57.1`, `flash-attn>=2.8.3`, `deepspeed==0.18.2`, `vllm==0.11.0`, `cosmos-rl` git dependency를 명시한다.
- `docs/FINETUNE_SFT.md`의 SFT 예시는 8 x H100 80GB에서 검증되었다.
- `finetune/rl/README.md`의 local RL test는 5개 이상 GPU, 각 80GB VRAM을 요구한다.

```bash
uv venv ar1_venv
source ar1_venv/bin/activate
uv sync --active
```

RL 검증 환경:

```bash
export YOUR_HOME="/path/to/workspace"
export UV_CACHE_DIR="$YOUR_HOME/.cache/uv"
cd "$YOUR_HOME/alpamayo"
uv venv alpamayo_env
source alpamayo_env/bin/activate
uv sync --active --no-install-package flash-attn
uv sync --active
```

### Hugging Face 인증 및 접근

공식 확인:

- `nvidia/Alpamayo-R1-10B`: HF model, updated 2026-03-27, license `other`, datasets `PhysicalAI-Autonomous-Vehicles`, `PhysicalAI-Autonomous-Vehicles-NuRec`
- `nvidia/Alpamayo-1.5-10B`: HF model, updated 2026-03-27, base model `nvidia/Cosmos-Reason2-8B`
- `nvidia/PhysicalAI-Autonomous-Vehicles`: gated HF dataset, updated 2026-05-06
- `nvidia/PhysicalAI-Autonomous-Vehicles-NuRec`: gated HF dataset, updated 2026-03-13
- `nvidia/Cosmos-Reason2-8B`: gated HF model, updated 2026-04-30

공식 URL:

- https://hf.co/nvidia/Alpamayo-R1-10B
- https://hf.co/nvidia/Alpamayo-1.5-10B
- https://hf.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles
- https://hf.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles-NuRec
- https://hf.co/nvidia/Cosmos-Reason2-8B

```bash
pip install -U huggingface_hub
hf auth login
export HF_TOKEN="<HF_TOKEN>"
export HF_HOME="<PATH_TO_HF_CACHE>"
```

### 모델 가중치 다운로드

```bash
huggingface-cli download nvidia/Alpamayo-R1-10B --local-dir "<PATH_TO_MODEL>/Alpamayo-R1-10B"
```

Alpamayo 1.5/AlpaSim 비교 실험:

```bash
huggingface-cli download nvidia/Alpamayo-1.5-10B --local-dir "<PATH_TO_MODEL>/Alpamayo-1.5-10B"
huggingface-cli download nvidia/Cosmos-Reason2-8B --local-dir "<PATH_TO_MODEL>/Cosmos-Reason2-8B"
```

### Physical AI AV subset 다운로드

SFT representative slice:

```bash
python scripts/download_pai.py \
  --chunk-ids 0-10 \
  --camera camera_front_wide_120fov camera_cross_left_120fov camera_cross_right_120fov camera_front_tele_30fov \
  --calibration camera_intrinsics sensor_extrinsics \
  --labels egomotion \
  --output-dir "<PATH_TO_PAI_DATASET>"
```

RL local mini subset:

```bash
python scripts/download_pai.py \
  --chunk-ids 3116 \
  --camera camera_front_wide_120fov camera_cross_left_120fov camera_cross_right_120fov camera_front_tele_30fov \
  --calibration camera_intrinsics sensor_extrinsics vehicle_dimensions \
  --labels egomotion \
  --output-dir "$ALPAMAYO_PAI_LOCAL_DIR"

python scripts/curate_pai_samples.py \
  --clip-index-path "$ALPAMAYO_PAI_LOCAL_DIR/clip_index.parquet" \
  --chunk 3116 \
  --num-samples 16 \
  --output-path "$ALPAMAYO_PAI_LOCAL_DIR/clip_index_mini.parquet"
```

### 최소 inference 테스트

```bash
python src/alpamayo_r1/test_inference.py
```

예상 산출물:

- CoC reasoning text
- `minADE: <value> meters`
- 모델 weight 약 22GB 다운로드 또는 local cache 사용

검증 기준:

- CUDA OOM 없이 model load
- PAI example clip load 성공
- `extra["cot"]` 출력
- `pred_xyz`와 GT future trajectory 기반 minADE 계산 완료

### SFT Stage 1

```bash
torchrun --nproc_per_node 8 \
  -m finetune.sft.train_hf \
  --config-path pkg://finetune/sft/configs \
  --config-name sft_stage1 \
  model.checkpoint_path="<PATH_TO_MODEL>/Alpamayo-R1-10B" \
  data.train_dataset.local_dir="<PATH_TO_PAI_DATASET>" \
  data.val_dataset.local_dir="<PATH_TO_PAI_DATASET>" \
  data.train_dataset.chunk_ids="0-10" \
  data.val_dataset.chunk_ids="10-11"
```

검증 기준:

- `output_stage1/checkpoint-<N>` 생성
- loss/grad_norm/lr 로그 출력
- config snapshot 저장

### SFT Stage 2

```bash
torchrun --nproc_per_node 8 \
  -m finetune.sft.train_hf \
  --config-path pkg://finetune/sft/configs \
  --config-name sft_stage2 \
  model.pretrained_model_name_or_path="<PATH_TO_MODEL>/Alpamayo-R1-10B" \
  model.stage1_vlm_checkpoint_path="<PATH_TO_STAGE1>/checkpoint-<N>" \
  data.train_dataset.local_dir="<PATH_TO_PAI_DATASET>" \
  data.val_dataset.local_dir="<PATH_TO_PAI_DATASET>"
```

### SFT evaluation

```bash
torchrun --nproc_per_node 8 \
  -m finetune.sft.evaluate_hf \
  --config-path pkg://finetune/sft/configs \
  --config-name sft_stage2 \
  evaluate.eval_ckpt="<PATH_TO_STAGE2>/checkpoint-<N>" \
  data.val_dataset.local_dir="<PATH_TO_PAI_DATASET>"
```

검증 기준:

- `val/metric/min_ade < 1`을 reference sanity target으로 사용
- `ade`, `corner_distance`, `min_ade/by_t=*` 로그 확인

### RL local test

```bash
export ALPAMAYO_WORKSPACE="$YOUR_HOME/alpamayo"
export ALPAMAYO_MODEL_DIR="$YOUR_HOME/alpamayo_model_converted_from_hf"
export ALPAMAYO_PAI_LOCAL_DIR="$YOUR_HOME/PAI_mini"
export ALPAMAYO_LOG_DIR="$YOUR_HOME/alpamayo_cosmos_rl_job/logs"
export WANDB_API_KEY="<WANDB_API_KEY>"

python scripts/convert_release_config_to_training.py \
  --alpamayo-model nvidia/Alpamayo-R1-10B \
  --output-dir "$ALPAMAYO_MODEL_DIR"

cosmos-rl \
  --config finetune/rl/toml/alpamayo_rvla_rl_local_test.toml \
  --policy 1 \
  --rollout 1 \
  --log-dir "$ALPAMAYO_LOG_DIR" \
  finetune/rl/models/reasoning_vla/alpamayo_cosmos_rl_post_training_entry.py
```

예상 산출물:

- `$ALPAMAYO_LOG_DIR/logs_<YYYYMMDD-HHMMSS>/controller.log`
- `policy_<i>.log`, `rollout_<i>.log`
- `<output_dir>/checkpoints/step_<N>/policy/model_rank_<r>.pth`

검증 기준:

- rollout generation, reward computation, GRPO training loop 완료
- reward 증가 및 trajectory L2 감소 추세

### RL checkpoint export

```bash
python scripts/convert_cosmos_rl_checkpoint.py \
  --cosmos-policy-ckpt "$YOUR_HOME/alpamayo_cosmos_rl_job/outputs/checkpoints/step_<N>/policy" \
  --base-hf-ckpt "$ALPAMAYO_MODEL_DIR" \
  --output-dir "$YOUR_HOME/alpamayo_cosmos_rl_job/exported_model"
```

## 5. 재현 실험 체크리스트

- 설치 성공: `python -c "import torch, transformers, alpamayo_r1"` 통과, CUDA visible, flash-attn import 확인
- 데이터셋 로딩 성공: `features.csv`, `clip_index.parquet`, `metadata/feature_presence.parquet`, camera zip, egomotion zip 존재
- 모델 로딩 성공: `AlpamayoR1.from_pretrained()` 완료, tokenizer special trajectory tokens 포함
- inference 성공: CoC 출력, `pred_xyz` shape 확인, minADE 계산 완료
- SFT Stage 1 성공: VLM loss 감소/안정, checkpoint shard 생성
- SFT Stage 2 성공: diffusion expert loss curve 기록, VLM freeze 여부 확인
- SFT evaluation 성공: `val/metric/min_ade` reference 범위 진입
- RL rollout 성공: vLLM rollout process 생성, completion string에 CoC와 trajectory token 포함
- RL reward 성공: `traj_L2`, `comfort_reward`, `reward` 로그 확인
- RL training 성공: controller buffer, policy checkpoint, weight sync 로그 정상
- 논문 비교 metric: minADE6@3s, minADE6@6s, ADE, offroad rate, close encounter rate, AlpaSim score
- 실패 시 우선 확인: HF auth/license, dataset chunk completeness, camera order, egomotion timestamp margin, GPU memory, `controller.log`, `policy_*.log`, `rollout_*.log`

## 6. alpasim 및 physical_ai_av 활용 전략

### PAI format bridge

`physical_ai_av`는 HF dataset interface가 `features.csv`, `clip_index.parquet`, `metadata/*`를 내려받고, clip id와 feature name으로 camera/egomotion/calibration을 반환하는 구조다. Alpamayo의 `load_physical_aiavdataset()`는 이 interface를 직접 호출하므로, 사용자 데이터나 alpasim 로그를 Alpamayo 학습으로 연결하려면 다음 둘 중 하나가 필요하다.

1. 사용자/시뮬레이션 데이터를 PAI-like local directory로 변환
2. `PAIDataset`과 같은 contract를 만족하는 별도 dataset class 구현

권장 1차 전략:

- 공개 PAI subset으로 baseline을 먼저 재현
- alpasim `.asl` log에서 camera frames, ego pose history, simulated ego future trajectory, driver prediction을 추출
- PAI sample key와 동일한 dict를 생성하는 converter를 별도 script로 작성
- 초기에는 SFT/RL 학습보다 evaluation dataset과 regression set 구축에 사용

### AlpaSim closed-loop strategy

근거:

- `docs/TUTORIAL.md`는 driver group으로 `alpamayo1`, `alpamayo1_5`를 지원하고, reasoning overlay video를 생성할 수 있음을 설명한다.
- `src/driver/src/alpasim_driver/models/alpamayo_base.py`는 camera image와 ego pose history를 받아 Alpamayo input을 구성하고, output trajectory와 reasoning text를 `ModelPrediction`으로 반환한다.
- `src/wizard/configs/driver/alpamayo1.yaml`은 4 camera, context length 4, max batch size 1을 기본으로 둔다.
- `src/wizard/configs/driver/alpamayo_configs.yaml`은 1080p camera 4개를 10 Hz로 설정한다.

실행 예:

```bash
cd /home/user/Workspace/alpasim
source setup_local_env.sh
export HF_TOKEN="<HF_TOKEN>"
uv run alpasim_wizard deploy=local topology=1gpu driver=alpamayo1 wizard.log_dir="$PWD/tutorial_alpamayo"
```

Reasoning overlay:

```bash
uv run alpasim_wizard \
  deploy=local \
  topology=1gpu \
  driver=alpamayo1 \
  wizard.log_dir="$PWD/tutorial_alpamayo" \
  eval.video.video_layouts=[REASONING_OVERLAY]
```

### Long-tail scenario generation/selection

초기 target:

- stop sign/all-way intersection
- construction cones/barriers
- pedestrian crossing/clearing
- lead vehicle following
- parked vehicle avoidance
- narrow lane/offroad-prone road edge

선별 기준:

- CoC가 행동 결정을 바꿀 수 있는 명확한 causal factor 보유
- open-loop minADE만으로 충분하지 않은 interaction 포함
- AlpaSim collision/offroad/plan deviation metric과 연결 가능

## 7. 실제 차량 적용 로드맵

### Phase 0: 공개 재현

- 목표: Alpamayo 1 inference, SFT mini, RL local test 가능성 확인
- 입력: HF access, 24GB+ inference GPU, SFT/RL용 H100급 자원 여부
- 산출물: reproducibility log, model/data cache manifest
- 검증: inference minADE 출력, SFT eval metric, RL local reward log
- 리스크: gated access, VRAM 부족, flash-attn build 실패

### Phase 1: 공개 데이터 subset fine-tuning

- 목표: PAI subset으로 Stage 1/2 overfit 또는 short fine-tune 재현
- 입력: selected chunks, 4-camera egomotion calibration
- 산출물: Stage 1/2 checkpoints, eval report
- 검증: `val/metric/min_ade < 1` sanity target
- 리스크: release model이 이미 해당 데이터에 학습되어 loss 개선 폭이 작음

### Phase 2: AlpaSim closed-loop baseline

- 목표: Alpamayo 1/1.5의 closed-loop score와 failure cases 확보
- 입력: NuRec scenes, AlpaSim driver config, HF model cache
- 산출물: `.asl`, `metrics.parquet`, reasoning overlay videos
- 검증: offroad, collision, minADE, plan deviation metric
- 리스크: renderer/scene access, model VRAM, runtime latency

### Phase 3: alpasim synthetic/eval data bridge

- 목표: `.asl` log를 Alpamayo sample dict 또는 PAI-like local dataset으로 변환
- 입력: ASL camera images, ego poses, future trajectory, calibration
- 산출물: converter script design, regression dataset
- 검증: `PAIDataset` equivalent sample keys와 tensor shapes 일치
- 리스크: timestamp alignment, camera order, coordinate frame mismatch

### Phase 4: 사용자 차량 data mapping

- 목표: 사용자 차량 sensor/calibration/localization을 Alpamayo input contract에 맞춤
- 입력: camera count/FOV/resolution/fps, extrinsics/intrinsics, egomotion source, timestamp sync
- 산출물: user dataset adapter, calibration validation report
- 검증: static/dynamic calibration sanity, ego-frame transform, frame order tests
- 리스크: sensor rig mismatch, rolling shutter, dropped frames

### Phase 5: 사용자 데이터 SFT 또는 adapter fine-tuning

- 목표: 공개 checkpoint를 사용자 ODD에 맞게 보정
- 입력: curated user logs, safety labels, scenario taxonomy
- 산출물: fine-tuned checkpoint, eval report
- 검증: held-out user set minADE/ADE, CoC review sample, AlpaSim/user sim regression
- 리스크: 데이터 규모 부족, label noise, license/commercial limitation

### Phase 6: safety-gated shadow-mode

- 목표: 실제 제어 통합 전 offline/shadow validation
- 입력: read-only vehicle telemetry, model inference output, safety monitor
- 산출물: latency/safety report, intervention/failure taxonomy
- 검증: latency budget, trajectory bounds, disagreement with baseline stack
- 리스크: 공개 모델은 certified AV stack이 아니며 제어권 부여 금지

## 8. 사용자에게 물어볼 질문

1. 차량 플랫폼과 제어 인터페이스는 무엇인가?
   - 필요한 이유: Alpamayo output은 trajectory이고, 실제 차량에는 controller/MPC/actuation layer가 필요하다.
   - 답변 영향: trajectory prediction 연구로 둘지, closed-loop planning/control integration까지 갈지 결정된다.

2. 카메라 구성은 어떻게 되는가? camera count, FOV, resolution, frame rate, synchronization, exposure timing을 포함해 답변 필요.
   - 필요한 이유: 공개 Alpamayo/AlpaSim 경로는 4-camera, 4-frame, 10 Hz 구성을 강하게 가정한다.
   - 답변 영향: 기존 adapter 사용 가능성 또는 camera remap/rectification 필요성이 결정된다.

3. intrinsics/extrinsics와 vehicle dimensions, rear axle 기준 pose 정의를 보유하고 있는가?
   - 필요한 이유: ego-frame trajectory와 camera geometry 검증에 필요하다.
   - 답변 영향: PAI-like converter 구현 난이도와 calibration validation 단계가 달라진다.

4. localization/egomotion source는 무엇인가? RTK, visual odometry, wheel odometry, IMU fusion 여부를 포함한다.
   - 필요한 이유: Alpamayo는 16 step history pose와 64 step future label을 10 Hz로 샘플링한다.
   - 답변 영향: timestamp interpolation, noise filtering, coordinate transform 설계가 달라진다.

5. 기존 주행 데이터의 규모와 포맷은 무엇인가?
   - 필요한 이유: SFT/RL 이전에 PAI-like sample 생성 가능성을 판단해야 한다.
   - 답변 영향: 공개 PAI fine-tune 중심인지, 사용자 데이터 adapter 개발 중심인지 결정된다.

6. 목표 기능은 trajectory prediction, reasoning/logging, planning, end-to-end control 중 무엇인가?
   - 필요한 이유: 공개 모델은 research tool이며 fully fledged driving stack이 아니다.
   - 답변 영향: safety gate와 integration boundary가 달라진다.

7. 목표 ODD는 무엇인가? 국가, 도로 유형, 속도 범위, 날씨/야간, 비보호 좌회전, 보행자 밀도 등.
   - 필요한 이유: long-tail scenario curation과 validation set 설계가 ODD에 의존한다.
   - 답변 영향: AlpaSim scene selection과 사용자 데이터 수집 우선순위가 달라진다.

8. 사용 가능한 GPU/스토리지/네트워크 자원은 어느 정도인가?
   - 필요한 이유: inference, SFT, RL local test 요구 자원이 크게 다르다.
   - 답변 영향: 2주 계획이 inference-only인지, SFT/RL까지 포함 가능한지 결정된다.

9. 공개 가중치와 데이터셋을 상업/제품 개발에 사용할 계획인가?
   - 필요한 이유: model weights는 non-commercial/other license로 표시되며, dataset license 검토가 필요하다.
   - 답변 영향: 연구 검증과 제품 적용 경로를 분리해야 할 수 있다.

## 9. 권장 개발 계획

### 2주 계획

- 주요 목표: 공개 inference와 AlpaSim closed-loop baseline 확보
- 작업 목록:
  - HF access 승인 및 model/data cache 구성
  - Alpamayo 1 inference smoke test
  - PAI chunk 0-10 또는 작은 subset 다운로드
  - SFT config dry run 및 dataset loading 확인
  - AlpaSim `driver=alpamayo1` 실행과 reasoning overlay 생성
  - 사용자 차량 sensor/data 현황 질문 답변 수집
- 산출물:
  - reproducibility report
  - source/data/model cache manifest
  - first failure taxonomy
- 검증:
  - `python src/alpamayo_r1/test_inference.py`
  - AlpaSim `rollouts`, `aggregate`, `metrics.parquet`, reasoning overlay video 생성
- 중단/재계획 조건:
  - HF access 거절
  - inference 가능한 24GB+ GPU 부재
  - AlpaSim scene/model download 실패

### 1개월 계획

- 주요 목표: PAI subset SFT와 AlpaSim regression suite 구성
- 작업 목록:
  - Stage 1/2 SFT short run
  - SFT evaluation metric 수집
  - AlpaSim long-tail scene subset 선정
  - `.asl` log 분석 및 converter 설계
  - RL local test 자원 가능성 판단
  - custom reward 후보 정의: trajectory, comfort, offroad/collision proxy, reasoning consistency
- 산출물:
  - fine-tuned checkpoint 또는 failed-run diagnosis
  - AlpaSim baseline table
  - data bridge design note
- 검증:
  - `val/metric/min_ade` reference sanity
  - collision/offroad/minADE/plan deviation regression
- 중단/재계획 조건:
  - 8 x H100급 SFT 자원 부재
  - dataset completeness 불충분
  - 사용자 sensor rig가 Alpamayo input과 크게 불일치

### 3개월 계획

- 주요 목표: 사용자 데이터 adapter, synthetic scenario loop, safety-gated offline validation
- 작업 목록:
  - user dataset to Alpamayo sample converter
  - alpasim synthetic/closed-loop scenario curation
  - user held-out validation split
  - SFT/adaptation experiment
  - shadow-mode interface design
  - safety monitor와 trajectory bounds 정의
- 산출물:
  - user-data fine-tuned/adapted model 후보
  - offline + simulation validation report
  - safety gate checklist
- 검증:
  - held-out minADE/ADE
  - AlpaSim offroad/collision/close encounter regression
  - latency/throughput report
  - CoC reasoning sample audit
- 중단/재계획 조건:
  - license가 목표 사용을 허용하지 않음
  - 데이터/센서 품질이 최소 기준 미달
  - closed-loop regression에서 safety metric 악화

## 10. 리스크 및 의사결정 포인트

| Risk | Assessment | Mitigation | Decision question |
| --- | --- | --- | --- |
| 하드웨어 부족 | inference는 24GB+, AlpaSim은 약 40GB, RL local은 5 x 80GB 이상 요구 | 단계별 축소, inference-only baseline, cloud/HPC 검토 | 이번 분기 사용할 수 있는 GPU는 무엇인가? |
| 데이터셋 접근권 | PAI와 NuRec 모두 gated | HF license 승인 선행 | dataset license 사용 범위가 연구/상업 중 어디까지인가? |
| 모델 가중치 license | README는 model weights non-commercial이라고 명시 | 연구 검증과 제품 적용 분리 | 공개 weight를 제품 개발에 쓸 계획인가? |
| 센서 구성 불일치 | 공개 코드/AlpaSim은 4cam 10Hz 중심 | camera remap/rectification, missing camera ablation | 사용자 차량이 동일/유사 FOV camera를 보유하는가? |
| open-loop vs closed-loop gap | 논문도 closed-loop 별도 평가 필요성을 명시 | AlpaSim regression mandatory | 개발 성공 metric을 무엇으로 둘 것인가? |
| reasoning trace 품질 | plausible reasoning이 action과 불일치 가능 | reasoning-action consistency audit/reward | reasoning을 안전 monitor에 사용할 것인가, 설명 로그로만 둘 것인가? |
| sim-to-real gap | NuRec/AlpaSim은 강력하지만 실제 sensor noise/ODD와 다름 | shadow-mode, user-data held-out, conservative safety gate | 실제 차량 테스트 제한 조건은 무엇인가? |
| 안전 검증 부담 | 공개 모델은 certified AV stack이 아님 | 제어권 없는 offline/shadow부터 시작 | 언제까지 실제 actuation을 금지할 것인가? |

## Current Unknowns

- 사용자의 실제 차량 sensor rig와 calibration 상태
- 사용자 데이터 포맷과 규모
- 목표 ODD와 기능 범위
- 사용 가능한 GPU/스토리지/네트워크 자원
- license 검토 범위: research-only인지 commercial/product까지인지
- Alpamayo 1.5 레포를 별도로 함께 분석할지 여부

## Next Investigation Steps

1. HF model card full README와 license text를 별도로 보존해 license/usage matrix 작성
2. Alpamayo PDF의 table/metric 값을 plan appendix로 정리
3. AlpaSim `alpamayo1` smoke run 가능 여부 확인
4. `PAIDataset` sample contract를 기준으로 user/alpasim converter acceptance test 설계
5. 사용자 질문 답변을 받아 2주 계획의 실행 범위 확정

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-05-26 18:24:55 KST | frontmatter | canonical v2 생성에 따라 이 문서를 superseded baseline으로 표시 |
