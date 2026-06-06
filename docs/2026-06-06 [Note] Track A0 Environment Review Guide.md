---
doc_type: note
status: review
note_id: track-a0-environment-review-guide
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-05-26 [Task] Track A Public Alpamayo Reproduction.md
created_at: 2026-06-06 15:40:55 KST
updated_at: 2026-06-06 21:54:07 KST
role: teacher_evaluator
---

# Track A0 Environment Review Guide

문서 목적: 사용자가 A0 환경 결과를 명령 결과로만 암기하지 않고, 현재 결론과 한계를
자기 말로 설명할 수 있는지 가르치고 평가한다.

주 독자: A1-A4 후속 작업에 들어가기 전의 사용자.

판단 질문: 사용자가 현재 README 공식 환경 성공, 과거 fallback 경로, 아직 열려 있는
A5 AlpaSim simulator/runtime blocker를 구분할 수 있는가?

제외 범위: 이 문서는 새 실험을 실행하지 않고, Root Task 상태를 수정하지 않으며, A5를
재분류하지 않는다. 현재 Manager review가 끝난 A0 evidence를 요약한다.

## 1. A0 한 문장 요약

A0는 현재 host에서 CUDA Toolkit 12.8을 설치한 뒤 README 공식 경로
`uv venv ar1_venv -> source ar1_venv/bin/activate -> uv sync --active ->
python src/alpamayo_r1/test_inference.py`가 성공하고, locked `flash-attn==2.8.3` source
build와 PAI 단일 샘플 inference가 재현되었음을 확인했다.

A0의 모델 기능 검증 관점 핵심은 README의 sample inference를 실행해 ego pose history와
multi-camera image input이 있는 상황에서 trajectory prediction과 CoC reasoning이 실제로
출력되는지 확인한 것이다. 여기서 얻은 가장 큰 가치는 성능 결론이 아니라, 후속 A1-A4가
기댈 수 있는 실행 가능한 baseline contract다.

## 2. A0에서 확인된 것

### README 공식 환경 경로

현재 A0의 기준 경로는 README inference path다.

```bash
uv venv ar1_venv
source ar1_venv/bin/activate
uv sync --active
hf auth login
python src/alpamayo_r1/test_inference.py
```

Manager review 기준으로 이 경로는 현재 host에서 성공했다. `ar1_venv`는 README가
안내하는 가상환경 방식이며, activate 이후의 `python`과 `hf`는 그 환경 안의 실행
파일을 가리킨다.

각 줄의 역할:

- `uv venv ar1_venv`: `ar1_venv/` 디렉터리에 Python virtual environment를 만든다.
  이 안에는 `bin/python`, `bin/pip`, `bin/activate`, package 설치 공간이 생긴다.
- `source ar1_venv/bin/activate`: 현재 shell의 `PATH`와 `VIRTUAL_ENV`를 바꿔 이후
  `python`, `pip`, `hf`가 `ar1_venv/bin/` 안의 실행 파일을 먼저 가리키게 한다.
- `uv sync --active`: `pyproject.toml`과 `uv.lock` 기준 dependency를 현재 active
  environment인 `ar1_venv`에 설치한다.

`source ar1_venv/bin/activate`는 Python `venv`/`virtualenv` 계열의 일반적인 방식이다.
`activate ar1_venv`는 보통 Python venv 표준 명령이 아니며, `conda activate ...`처럼
Conda 계열에서 더 익숙한 형태다. `activate`는 현재 shell의 환경변수를 바꾸는 script라서
그냥 실행하지 않고 `source`로 현재 shell에 반영해야 한다.

### CUDA Toolkit 12.8 compiler toolchain

host에 CUDA Toolkit 12.8이 설치되었고, `nvcc V12.8.93`이 확인되었다. `/home/user/.zshrc`
에는 `CUDA_HOME=/usr/local/cuda-12.8`, `CUDA_PATH=$CUDA_HOME`, `$CUDA_HOME/bin` PATH가
설정되었다.

이것은 중요한 전환점이다. A0 초기에 GPU runtime은 있었지만 CUDA compiler toolchain이
없어 `flash-attn` source build가 실패했다. 지금은 compiler toolchain이 설치되어
공식 source-build path가 가능하다.

### `flash-attn==2.8.3` source build

plain `uv sync --active`가 locked `flash-attn==2.8.3`을 source build했고 exit code 0으로
완료되었다. 이것은 과거 wheel workaround보다 강한 재현성 evidence다.

source build라고 판단하는 직접 근거는 sync log의 build 단계다.

```text
Building flash-attn==2.8.3
Built flash-attn==2.8.3
Prepared 1 package without build isolation
Installed 1 package ... flash-attn==2.8.3
```

이미 만들어진 prebuilt wheel을 단순 설치했다면 `Building`/`Built` 단계가 핵심 evidence로
남지 않는다. A0에서는 CUDA Toolkit 12.8 설치 전 이 build 단계가 `nvcc`/`CUDA_HOME` 부재로
막혔고, 설치 후 같은 공식 경로에서 통과했기 때문에 source build 성공으로 판정한다.

검증 로그:

- `docs/logs/2026-06-06-a0-cuda128-readme-uv-sync-active.log`

### PAI official inference

같은 `ar1_venv`에서 `python src/alpamayo_r1/test_inference.py`가 성공했다.

확인된 결과:

```text
Chain-of-Causation (per trajectory):
 [['Nudge to the left to increase clearance from the construction cones encroaching into the lane.']]
minADE: 2.5593724 meters
```

검증 로그:

- `docs/logs/2026-06-06-a0-cuda128-readme-test-inference.log`

### HF access

Track A에 필요한 Hugging Face 접근은 `kimdh1st` 계정으로 해결되었다. PAI `features.csv`,
NuRec metadata, AlpaSim configured USDZ scene artifact 접근이 확인되었다.

HF access는 "로그인했다"와 "필요한 gated asset에 실제 접근했다"를 모두 포함한다.

## 3. A0에서 확인되지 않은 것

### 전체 데이터셋 평가

A0는 PAI 단일 샘플 inference를 재현했을 뿐, full PAI dataset sweep이나 여러 clip의
성능 분포를 확인하지 않았다. 따라서 A0 결과만으로 model quality, 일반화 성능,
dataset-wide metric을 주장하면 안 된다.

### SFT/RL training

`uv sync --active`, `flash-attn` source build, PAI inference가 성공했더라도 장시간
SFT/RL training 가능성이 검증된 것은 아니다. training은 multi-GPU memory, dataloader
throughput, optimizer/checkpoint/export path, 장시간 안정성을 별도로 요구한다.

### AlpaSim closed-loop rollout

AlpaSim은 A0 환경 blocker가 아니라 A5 simulator/runtime blocker로 이관되었다. A0는
NuRec artifact 접근과 container start까지의 evidence를 갖고 있지만, closed-loop
metrics/video가 생성되는 valid rollout은 확인하지 못했다.

## 4. 남은 blocker와 의미

### A0에서 해결된 blocker

다음은 현재 A0 기준으로 해결되었다.

- HF access: `kimdh1st` 계정으로 Track A 필요 asset 접근 확인
- CUDA compiler toolchain: CUDA Toolkit 12.8 설치 및 `nvcc V12.8.93` 확인
- `flash-attn` source build: plain `uv sync --active`에서 locked `flash-attn==2.8.3` build 성공
- official PAI inference: `ar1_venv`에서 `minADE: 2.5593724 meters` 재현

### A5로 이관된 blocker

AlpaSim closed-loop 실패는 A0의 공식 설치 재현성 blocker가 아니다. 현재 evidence상
AlpaSim은 NuRec artifact 접근과 container start 이후, container 내부 서비스에서
`alpasim_grpc.v0.common_pb2` import 실패와 sensorsim exit 139로 막힌다.

의미:

A5는 simulator/runtime packaging, generated gRPC module, sensorsim crash, wizard exit
code 해석을 다뤄야 한다. A0를 다시 열어 HF나 `flash-attn` 문제로 되돌릴 필요는 없다.

### 계속 남는 해석 한계

A0 done은 "현재 host에서 README official environment와 single-sample PAI inference가
재현된다"는 뜻이다. 이것은 full dataset, training, closed-loop simulator, vehicle
control readiness를 뜻하지 않는다.

## 5. 핵심 개념 설명

### HF access

HF access는 두 단계다.

첫째, local CLI가 어떤 계정으로 인증되어 있는지 확인한다.

둘째, 그 계정이 필요한 gated NVIDIA asset에 실제 접근할 수 있는지 파일 또는 metadata
probe로 확인한다.

A0에서는 `kimdh1st` 계정으로 PAI `features.csv`, NuRec metadata, configured USDZ scene
artifact 접근을 확인했다. 따라서 A0의 HF blocker는 해결되었다.

### `ar1_venv` / activate / `python`

README의 공식 방식은 `uv venv ar1_venv`로 가상환경을 만들고
`source ar1_venv/bin/activate`로 shell의 `PATH`를 바꾼 뒤 `python`과 `hf`를 실행하는
것이다.

activate 이후:

- `python`은 `ar1_venv/bin/python`을 가리킨다.
- `hf`는 `ar1_venv/bin/hf`를 가리킨다.
- `uv sync --active`는 active environment에 locked dependencies를 설치한다.

과거 `.venv/bin/python` 직접 실행은 같은 원리의 명시적 호출이지만, 현재 A0의 primary
path는 README와 맞춘 `ar1_venv` activate 방식이다.

### GPU runtime vs CUDA compiler toolchain

GPU runtime 가능성은 "Torch가 GPU에서 CUDA 연산을 실행할 수 있다"는 뜻이다.

CUDA compiler toolchain은 "`flash-attn` 같은 CUDA extension을 source build할 수 있다"는
뜻이다.

A0 초기 상태:

- Torch CUDA runtime: 가능
- GPU/driver: 있음
- `nvcc`/`CUDA_HOME`: 없음
- 결과: inference 우회는 가능했지만 `flash-attn` source build 실패

현재 상태:

- CUDA Toolkit 12.8 설치
- `nvcc V12.8.93` 확인
- `CUDA_HOME=/usr/local/cuda-12.8`
- 결과: README `uv sync --active`가 `flash-attn==2.8.3` source build 성공

### `flash-attn`: wheel workaround vs source-build path

과거 wheel workaround:

- `uv sync --no-install-package flash-attn`
- Dao-AILab prebuilt wheel 설치
- `.venv/bin/python`으로 runtime import와 inference 검증

이것은 A0 초기에 환경 가능성을 분리하기 위한 historical fallback이다.

현재 source-build path:

- CUDA Toolkit 12.8 설치
- `uv venv ar1_venv`
- `source ar1_venv/bin/activate`
- `uv sync --active`
- locked `flash-attn==2.8.3` source build 성공

현재 host의 primary path는 source-build path다. wheel workaround를 현재 blocker 또는
기본 설치 방법처럼 설명하면 stale한 설명이다.

### PAI inference

PAI inference는 공개 PAI sample을 loader/processor/model path에 넣어 CoC reasoning과
future trajectory를 생성하고 minADE를 계산하는 open-loop 실행이다.

A0에서 공식 inference 성공은 다음을 확인한다.

- PAI sample 접근 가능
- checkpoint shard load 가능
- processor/model inference path 실행 가능
- CoC text 생성 가능
- `pred_xyz` 기반 minADE 계산 가능

하지만 이것은 closed-loop simulator, full dataset evaluation, SFT/RL training readiness를
보장하지 않는다.

즉 A0에서 우리가 얻은 것은 다음이다.

- 공식 실행 경로가 현재 머신에서 재현 가능하다는 증거
- HF/PAI 접근권이 실제 inference path에서 동작한다는 증거
- Alpamayo 최소 input/output contract: multi-camera image context + ego history 입력,
  CoC reasoning + 64-step future trajectory 출력
- A1이 따라갈 실제 code path 기준점
- A3/A4가 확장할 단일 sample baseline

반대로 얻지 못한 것은 다음이다.

- 전체 PAI dataset 성능
- SFT/RL 학습 가능성
- AlpaSim closed-loop 성공
- 자체 데이터 또는 실제 차량 적용 가능성

### AlpaSim smoke

AlpaSim smoke는 open-loop inference보다 넓다. scene artifact, renderer/runtime, driver
service, controller, simulator service, generated proto package가 함께 맞아야 한다.

A0에서 AlpaSim은 A0 공식 환경 재현성 blocker에서 제외되었고 A5로 이관되었다. A0 done을
AlpaSim closed-loop success로 해석하면 틀린다.

## 6. A0 결과가 A1-A4에 주는 영향

### A1 Code and Model Flow Study

A1은 이제 README source-build environment를 기준으로 PAI inference code path를 설명할
수 있다. 과거 `.venv` wheel workaround를 기준 path로 삼을 필요가 없다.

핵심 질문:

PAI sample에서 image frames, ego history, tokenized data가 어떤 함수들을 지나 CoC text와
`pred_xyz`로 바뀌는가?

### A2 PAI Dataset Literacy and Storage Strategy

A0는 gated PAI 접근 가능성을 확인했다. A2는 full download를 전제로 하지 말고 manifest,
selected component, selected chunk 기준으로 storage budget을 세워야 한다.

### A3 Inference Experiment Suite

A0는 단일 sample의 official inference를 재현했다. A3는 여러 clip, seed, sample 수,
runtime, VRAM, metric 분포를 확인해야 한다.

### A4 Visualization and Demo Lab

A0 output은 CoC text와 minADE 중심이다. A4는 image input, ego history, ground truth
future, predicted trajectory를 시각적으로 비교할 수 있게 만들어야 한다.

## 7. 이해도 테스트

### Short-Answer Questions

#### Q1. 과거 wheel workaround와 현재 README source-build path의 차이는 무엇인가?

기대 답변:

과거 workaround는 `flash-attn` source build가 안 되던 상태에서
`uv sync --no-install-package flash-attn` 후 Dao-AILab prebuilt wheel을 설치해 runtime
import와 inference를 우회 검증한 것이다. 현재 path는 CUDA Toolkit 12.8을 설치한 뒤
README 방식으로 `uv venv ar1_venv`, activate, `uv sync --active`를 실행해 locked
`flash-attn==2.8.3`을 source build한 것이다. 현재 host의 primary path는 README
source-build path다.

오답 징후:

- wheel workaround를 현재 기본 경로라고 말함
- `flash-attn` import 성공과 source build 성공을 구분하지 못함
- `ar1_venv` README path를 언급하지 못함

#### Q2. GPU runtime 가능성과 CUDA compiler toolchain 필요성은 어떻게 다른가?

기대 답변:

GPU runtime 가능성은 Torch가 GPU에서 CUDA 연산을 실행할 수 있다는 뜻이다. CUDA compiler
toolchain은 CUDA extension을 source build할 수 있도록 `nvcc`, headers, dev libraries,
`CUDA_HOME`이 준비되었다는 뜻이다. A0 초기에는 runtime은 있었지만 compiler toolchain이
없어 `flash-attn` build가 실패했고, CUDA Toolkit 12.8 설치 후 source build가 성공했다.

오답 징후:

- `torch.cuda.is_available()`이면 `flash-attn` source build도 된다고 말함
- `nvcc`와 NVIDIA driver/runtime을 같은 것으로 취급함
- `CUDA_HOME`의 역할을 설명하지 못함

#### Q3. HF login은 성공했는데 AlpaSim이 실패했다. 이 둘은 같은 문제인가?

기대 답변:

아니다. A0에서 HF access는 `kimdh1st` 계정으로 PAI `features.csv`, NuRec metadata,
configured USDZ artifact 접근까지 확인되었다. AlpaSim 실패는 이후 container 내부에서
`alpasim_grpc.v0.common_pb2`가 import되지 않고 sensorsim이 exit 139로 죽은
simulator/runtime packaging 문제이며 A5로 이관되었다.

오답 징후:

- "HF가 안 돼서 AlpaSim이 실패했다"고 말함
- NuRec artifact download 성공을 언급하지 못함
- A5 이관을 설명하지 못함

#### Q4. A0에서 가장 강한 성공 evidence는 무엇인가?

기대 답변:

현재 기준에서는 두 가지가 함께 가장 중요하다. 첫째, README path의 `uv sync --active`가
locked `flash-attn==2.8.3` source build까지 성공했다. 둘째, 같은 `ar1_venv`에서
`python src/alpamayo_r1/test_inference.py`가 PAI sample inference를 완료하고 CoC text와
`minADE: 2.5593724 meters`를 재현했다.

오답 징후:

- 과거 `.venv` wheel import만 언급함
- PAI inference만 말하고 official install reproducibility를 빼먹음
- source build와 inference가 같은 `ar1_venv`에서 이어졌다는 점을 설명하지 못함

#### Q5. PAI inference 1회 성공으로 전체 데이터셋 학습 가능성을 주장할 수 있는가?

기대 답변:

아니다. A0의 official inference 1회는 PAI sample 접근, model load, CoC generation,
trajectory prediction, minADE calculation을 확인한 open-loop smoke다. full dataset
evaluation, SFT/RL training, throughput, memory budget, learning stability는 확인하지
않았다.

오답 징후:

- "minADE가 나왔으니 학습도 가능하다"고 말함
- inference와 training을 구분하지 못함
- single sample과 dataset-wide 평가를 구분하지 못함

### Scenario Questions

#### S1. A1 Expert가 "이제 A0가 끝났으니 AlpaSim closed-loop도 된다고 보면 되나요?"라고 묻는다. 어떻게 답할 것인가?

기대 답변:

아니다. A0 done은 README environment, `flash-attn` source build, PAI single-sample
inference가 재현됐다는 뜻이다. AlpaSim은 container start 이후 generated gRPC module
import 실패와 sensorsim crash가 남아 있으며, A5 simulator/runtime blocker로 이관되었다.

오답 징후:

- "A0 done이면 closed-loop도 통과"라고 답함
- "wizard finished"만 보고 성공이라고 답함
- A5 이관 이유를 설명하지 못함

#### S2. 누군가 "예전에는 wheel workaround를 썼으니 앞으로도 `.venv` wheel 환경을 기준으로 하자"고 말한다. 어떻게 판단할 것인가?

기대 답변:

현재 host에서는 CUDA Toolkit 12.8 설치 후 README source-build path가 성공했으므로
primary path는 `ar1_venv` 공식 경로다. `.venv` wheel workaround는 historical fallback
또는 비교용으로만 남겨야 한다. 공식 경로와 괴리가 커지면 커뮤니티 문서, 이슈 검색,
재현성 판단이 어려워진다.

오답 징후:

- "둘 다 되니 아무거나 쓰면 된다"고 답함
- 공식 경로를 primary로 둬야 하는 이유를 설명하지 못함
- historical fallback과 current primary path를 구분하지 못함

#### S3. A3를 시작하려는 사람이 "A0에서 minADE가 2.5593724니까 모델 성능은 이미 검증됐다"고 말한다. 무엇이 문제인가?

기대 답변:

단일 PAI sample의 minADE는 baseline smoke evidence이지 model quality validation이
아니다. A3는 여러 clip, seed, sample 수, runtime, VRAM, metric 분포를 봐야 한다. A0
결과는 A3의 출발점이지 결론이 아니다.

오답 징후:

- single metric을 dataset-wide 성능으로 일반화함
- A3의 필요성을 설명하지 못함
- minADE가 나온 실행 범위를 말하지 못함

#### S4. `torch.cuda.is_available()`가 True인데 `uv sync --active`가 실패한다면 무엇을 먼저 의심해야 하는가?

기대 답변:

GPU runtime은 가능하지만 compiler toolchain이 없을 수 있다. `which nvcc`,
`nvcc --version`, `CUDA_HOME`, CUDA Toolkit dev package, PATH 설정을 확인해야 한다.
A0 초기 실패가 이 경우였고, CUDA Toolkit 12.8 설치 후 해결되었다.

오답 징후:

- GPU가 보이면 build도 된다고 가정함
- driver, runtime, compiler를 구분하지 못함
- `nvcc` 확인을 빼먹음

### Misconception Check

#### M1. "A0 done = Alpamayo README 환경 재현성과 PAI 단일 샘플 inference가 현재 host에서 된다."

정답:

맞음. 단, full dataset evaluation, SFT/RL training, AlpaSim closed-loop, vehicle readiness는
여전히 별도다.

오답 징후:

"A0 done"을 모든 후속 track 완료처럼 확장함.

#### M2. "A0 done = AlpaSim closed-loop smoke 성공."

정답:

틀림. AlpaSim은 A5 simulator/runtime blocker로 이관되었다.

오답 징후:

container start 또는 wizard exit code 0만 보고 closed-loop 성공이라고 판단함.

#### M3. "이제 `flash-attn`은 wheel workaround로만 되는 상태다."

정답:

틀림. 현재 host에서는 CUDA Toolkit 12.8 덕분에 `uv sync --active`가 locked
`flash-attn==2.8.3`을 source build한다. wheel workaround는 historical fallback이다.

오답 징후:

과거 실패 기록을 현재 blocker로 읽음.

#### M4. "HF access 실패와 dependency 실패는 같은 환경 문제다."

정답:

틀림. HF access는 인증/권한 문제이고, dependency/source build는 compiler/toolchain
문제다. A0에서는 둘 다 현재 기준으로 해결되었다.

오답 징후:

접근권, dependency, simulator runtime blocker를 하나의 "환경 문제"로 뭉뚱그림.

## 8. 최종 A0 시험 문제

사용자는 A1 Expert와 대화하기 전에 아래 질문에 답해야 한다.

1. 현재 A0의 official reproduction path를 명령 순서대로 설명하라.
2. 과거 `.venv` wheel workaround와 현재 `ar1_venv` README source-build path의 차이를 설명하라.
3. `torch.cuda.is_available()`와 `nvcc --version`이 각각 무엇을 검증하는지 설명하라.
4. A0에서 해결된 blocker 네 가지를 말하라.
5. AlpaSim blocker가 왜 A0가 아니라 A5로 이관되었는지 설명하라.
6. `minADE: 2.5593724 meters`가 증명하는 것과 증명하지 않는 것을 구분하라.
7. A0 done이 A1, A2, A3, A4에 각각 어떤 출발점을 제공하는지 설명하라.
8. `uv venv ar1_venv`, `source ar1_venv/bin/activate`, `uv sync --active` 각 줄의 역할을
   설명하라.
9. A0 log에서 `flash-attn==2.8.3`이 source build되었다고 판단하는 근거를 설명하라.

## 9. 채점 기준

| Grade | Criteria |
| --- | --- |
| pass | README `ar1_venv` 경로, CUDA Toolkit 12.8/source-build 성공, PAI inference 재현, AlpaSim A5 이관을 모두 구분해 설명함 |
| partial | PAI inference 성공은 설명하지만 source-build path나 A5 이관을 일부 혼동함 |
| fail | 과거 wheel workaround를 현재 primary path로 말하거나, A0 done을 full dataset/training/AlpaSim closed-loop 성공으로 과장함 |

Pass 판정에 필요한 최소 답변:

- `uv venv ar1_venv`, activate, `uv sync --active`, `python src/alpamayo_r1/test_inference.py`
  경로가 현재 기준임을 말할 수 있어야 한다.
- CUDA Toolkit 12.8과 `nvcc`가 `flash-attn` source build에 필요한 이유를 설명할 수
  있어야 한다.
- Dao-AILab wheel workaround는 historical fallback이고 현재 host의 primary path가
  아니라고 말할 수 있어야 한다.
- AlpaSim은 HF/dependency 문제가 아니라 A5 simulator/runtime 문제로 이관되었다고 말할
  수 있어야 한다.
- A0 done은 single-sample PAI inference와 official environment reproduction의 성공이지,
  full dataset, training, closed-loop 검증 완료가 아니라고 말할 수 있어야 한다.

## 10. 사용자가 틀리기 쉬운 지점

### 과거 실패를 현재 blocker로 읽는 것

2026-05-27의 `uv sync --active` 실패는 당시 host에 `nvcc`/`CUDA_HOME`이 없던 historical
failure다. 2026-06-06 CUDA Toolkit 12.8 설치 후 current blocker가 아니다.

### GPU runtime과 compiler toolchain을 같은 것으로 보는 것

GPU에서 실행되는 것과 CUDA extension을 컴파일하는 것은 다르다. A0는 이 차이를 실제로
겪었고, Toolkit 설치로 해결했다.

### 공식 경로와 fallback 경로를 같은 무게로 보는 것

`.venv` wheel workaround는 유용한 smoke fallback이었지만, 현재 host에서는 README
`ar1_venv` source-build path가 우선이다.

### open-loop inference와 closed-loop simulator를 혼동하는 것

PAI inference는 sample 기반 open-loop path다. AlpaSim은 renderer/runtime/services가
맞물리는 closed-loop path이고 A5에서 다룬다.

### single metric을 과장하는 것

`minADE: 2.5593724 meters`는 A0 sample에서 inference와 metric path가 작동했다는
evidence다. model quality validation이나 dataset-wide result가 아니다.

## 11. A0에 대해 과장하면 안 되는 주장

다음 문장은 A0 evidence보다 강하다.

- "A0로 전체 PAI 성능이 검증됐다."
- "SFT/RL training도 가능하다고 검증됐다."
- "AlpaSim closed-loop smoke가 성공했다."
- "vehicle shadow-mode readiness가 확보됐다."
- "single-sample minADE가 dataset-wide 성능이다."
- "HF login만 하면 모든 future asset 접근도 보장된다."
- "GPU runtime이 보이면 CUDA extension source build도 자동으로 된다."
- "과거 wheel workaround가 현재 공식 primary path다."

## Teacher Follow-Up Rule

사용자가 위 시험 문제 중 두 개 이상에서 historical fallback/current primary path,
runtime/compiler, A0/A5 blocker를 혼동하면 A1로 넘어가기 전에 다음 세 문장을 다시
작성해야 한다.

1. 현재 A0가 실제로 증명한 것.
2. 과거 wheel workaround가 현재 어떤 지위를 갖는지.
3. A5로 이관된 AlpaSim blocker가 무엇인지.
