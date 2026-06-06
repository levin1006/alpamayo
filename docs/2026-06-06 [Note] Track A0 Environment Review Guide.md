---
doc_type: note
status: review
note_id: track-a0-environment-review-guide
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-05-26 [Task] Track A Public Alpamayo Reproduction.md
created_at: 2026-06-06 15:40:55 KST
role: teacher_evaluator
---

# Track A0 Environment Review Guide

이 문서는 A0의 기존 evidence만 사용해 사용자가 환경/접근권/실행 가능성의 성공,
실패, 한계를 직접 설명할 수 있게 만드는 Teacher/Evaluator 노트다. 새 실험, 코드
수정, Root Task 수정은 포함하지 않는다.

## 1. A0 한 문장 요약

A0는 현재 머신에서 공개 Alpamayo 10B와 PAI 단일 샘플 inference가 실행 가능하다는
것을 확인했지만, plain `uv sync --active` 재현성과 AlpaSim closed-loop smoke는 아직
검증하지 못했다.

## 2. A0에서 확인된 것

### HF access

Track A에 필요한 Hugging Face 접근은 `kimdh1st` 계정으로 확인되었다.

확인된 범위는 세 가지다.

- `.venv/bin/hf auth whoami`가 `kimdh1st` 로그인을 보고했다.
- PAI `features.csv` 직접 다운로드가 성공했다.
- NuRec repo metadata 접근과 AlpaSim wizard의 configured USDZ scene artifact 다운로드가
  성공했다.

이 결과는 A0 초반의 401/403 실패가 영구적인 데이터 불가 상태가 아니라, 로그인 또는
gated dataset 승인 상태와 잘못된 stale file probe의 문제였음을 보여준다.

### `.venv` 기반 Alpamayo runtime

Track A는 repo-local `.venv`를 사용해 Python 3.12.3, Torch CUDA, Hugging Face CLI,
Alpamayo 관련 dependency를 같은 환경에서 확인했다. `.venv/bin/python`과
`.venv/bin/hf`를 직접 사용한 이유는 global Python 또는 system `hf`와 섞이지 않게
하기 위해서다.

### `flash-attn` runtime import

`flash-attn 2.8.3`은 official Dao-AILab prebuilt wheel로 설치했을 때 import가
성공했다. 이로써 Track A runtime에서 필요한 FlashAttention 모듈을 사용할 수 있음은
확인되었다.

### PAI official inference

공식 `src/alpamayo_r1/test_inference.py`가 PAI sample을 로드하고, checkpoint shard를
로드하고, CoC reasoning을 생성하고, trajectory metric인 `minADE: 2.5593724 meters`를
출력했다.

이것은 A0의 가장 강한 성공 evidence다. 단순히 모델 import가 된 것이 아니라, 공개
PAI sample에서 모델 입력 생성, 추론, reasoning 출력, metric 계산까지 이어졌다.

### synthetic model/processor smoke

PAI 접근이 막혔던 중간 단계에서도 synthetic dummy input으로 모델 가중치와 processor
경로가 실행 가능함을 확인했다. 특히 direct single-GPU placement와 official-like
processor path가 64-step trajectory tensor와 CoC text를 만들었다.

이 evidence는 모델 자체와 processor path가 완전히 막혀 있지 않다는 보조 근거지만,
PAI 실제 데이터 성공 evidence보다 약하다.

## 3. A0에서 확인되지 않은 것

### 전체 데이터셋 평가

A0는 PAI 단일 샘플 inference를 확인했을 뿐, 전체 PAI dataset sweep이나 여러 clip의
성능 분포를 확인하지 않았다. 따라서 A0 결과만으로 모델 품질, 일반화 성능, 학습
가능성, dataset-wide metric을 주장하면 안 된다.

### plain `uv sync --active` 재현성

official wheel을 통한 `flash-attn` runtime import는 성공했지만, plain
`uv sync --active`는 locked `flash-attn==2.8.3` source distribution을 build하려고 하며
host `nvcc` 또는 `CUDA_HOME`이 없어서 실패한다.

즉, "현재 runtime은 쓸 수 있다"와 "누구나 lock sync만 실행하면 완전히 재현된다"는
서로 다른 주장이다. A0는 앞의 주장을 확인했고, 뒤의 주장은 확인하지 못했다.

### AlpaSim closed-loop smoke

AlpaSim은 container start까지 도달했지만, 내부 서비스가
`alpasim_grpc.v0.common_pb2` import 실패와 sensorsim exit 139로 종료되었다. Wizard가
exit code 0과 `Alpasim finished`를 반환했더라도, metrics/video가 만들어진 valid
closed-loop smoke로 볼 수 없다.

### SFT/RL training 가능성

A0는 장시간 SFT/RL training을 수행하지 않았다. `flash-attn` import와 PAI inference
성공은 training dependency, multi-GPU strategy, memory budget, dataloader throughput,
checkpoint/export path가 모두 검증되었다는 뜻이 아니다.

## 4. 남은 blocker와 의미

### `flash-attn` lock-sync blocker

남은 문제는 GPU가 없다는 뜻이 아니다. Torch CUDA는 동작했고, 2x RTX 4090도 보였다.
문제는 `flash-attn` source build에 필요한 host compiler toolchain, 특히 `nvcc` 또는
`CUDA_HOME`이 plain sync path에서 보이지 않는다는 점이다.

의미:

A1-A4가 wheel 기반 runtime을 사용한다면 진행 가능성이 있다. 하지만 setup 문서나
재현성 기준에서 "plain `uv sync --active`만으로 된다"고 쓰면 안 된다.

### AlpaSim runtime/packaging blocker

남은 문제는 HF access 문제가 아니다. NuRec artifact 접근과 download는 성공했다.
현재 evidence상 blocker는 AlpaSim container 내부의 generated gRPC Python module
packaging/import 문제와 sensorsim crash다.

의미:

A5 AlpaSim Closed-Loop Baseline은 별도 진단 track으로 남아야 한다. A0 완료를
"closed-loop simulator까지 검증됨"으로 해석하면 잘못이다.

### single-clip inference 한계

PAI official inference 1회는 baseline contract anchor로는 충분하지만, 모델 품질이나
dataset-wide behavior를 주장하기에는 부족하다.

의미:

A3 inference experiment suite가 여러 clip, seed, sample 수, runtime, VRAM, metric을
다뤄야 하는 이유가 여기에 있다.

## 5. 핵심 개념 설명

### HF access

HF access는 단순히 Hugging Face 계정에 로그인했다는 뜻만이 아니다. Track A에서는
두 조건이 함께 필요했다.

첫째, local CLI/runtime이 어떤 계정으로 인증되어 있는지 확인해야 한다. A0에서는
`.venv/bin/hf auth whoami`가 `kimdh1st`를 보고했다.

둘째, 해당 계정이 gated NVIDIA dataset/model artifact에 접근할 권한이 있어야 한다.
A0에서는 PAI `features.csv`, NuRec metadata, configured USDZ artifact 접근으로 Track A
범위의 권한을 확인했다.

따라서 "HF login 성공"과 "모든 gated asset 접근 가능"은 같은 말이 아니다. 파일별,
repo별로 실제 접근 probe가 필요하다.

### `.venv` / `.venv/bin/hf`

`.venv`는 Alpamayo repo 안에서 Track A 실행을 위해 준비한 Python virtual
environment다. `.venv/bin/hf`는 별도의 custom script가 아니라, 그 environment 안에
설치된 `huggingface_hub` package의 Hugging Face CLI executable이다.

system `hf`와 `.venv/bin/hf`가 다를 수 있는 이유는 Python environment마다 설치된
package version과 executable path가 다르기 때문이다. 사용자가 global shell에서
`hf auth whoami`를 실행해 성공했다고 해도, Alpamayo 실행에 쓰는 `.venv/bin/hf`가 같은
token 상태인지 별도로 확인해야 한다.

### `flash-attn`

`flash-attn`은 Alpamayo project requirement로 기록된 dependency다. A0에서 중요한
구분은 세 가지다.

runtime import 성공:

official prebuilt wheel로 설치한 `flash-attn 2.8.3`이 import되었다. 그래서 현재
Track A runtime에서 inference를 돌릴 수 있었다.

plain lock sync 실패:

`uv sync --active`는 locked source distribution을 build하려고 했고, host `nvcc` 또는
`CUDA_HOME`이 없어 실패했다.

해석:

`flash-attn import 성공`은 "현재 환경에서 해당 module을 사용할 수 있다"는 뜻이지,
"dependency setup 문제가 완전히 해결되었다"는 뜻이 아니다.

### PAI inference

PAI inference는 공개 PAI sample을 Alpamayo loader/processor/model path에 넣어
CoC reasoning과 future trajectory를 생성하고 metric까지 계산하는 open-loop 실행이다.

A0에서 공식 inference 성공은 다음을 확인한다.

- PAI sample 접근 가능
- model checkpoint load 가능
- processor/model inference path 실행 가능
- CoC text 생성 가능
- `pred_xyz` 기반 minADE 계산 가능

하지만 이것은 closed-loop simulator, full dataset evaluation, training readiness를
보장하지 않는다.

### AlpaSim smoke

AlpaSim smoke는 open-loop inference보다 많은 시스템을 포함한다. scene artifact,
renderer/runtime, driver service, controller, simulator service, generated proto
package가 함께 맞아야 한다.

A0에서 AlpaSim은 artifact download와 container start까지 갔지만, 내부 services가
죽었기 때문에 smoke 성공이 아니다. 특히 wizard exit code 0만 보고 성공이라고
판단하면 안 된다. container logs와 metrics/video 생성 여부를 함께 확인해야 한다.

## 6. A0 결과가 A1-A4에 주는 영향

### A1 Code and Model Flow Study

A1은 "무엇이 실행 가능한가"보다 "어떤 code/data/model path가 실행되었는가"를
설명해야 한다. A0의 PAI official inference 성공은 A1이 따라갈 기준 경로를 제공한다.

A1 Expert에게 물어야 할 핵심 질문:

PAI sample에서 image frames, ego history, tokenized data가 어떤 함수들을 지나
CoC text와 `pred_xyz`로 바뀌는가?

### A2 PAI Dataset Literacy and Storage Strategy

A0는 PAI 접근 가능성을 확인했지만, storage budget이나 component/chunk strategy는
확인하지 않았다. A2는 full download를 전제로 하지 말고 manifest, selected component,
selected chunk 기준으로 필요한 data size를 계산해야 한다.

### A3 Inference Experiment Suite

A0는 단일 sample의 successful inference만 제공한다. A3는 여러 clip에서 CoC,
trajectory metric, runtime, VRAM, seed/sample 수 변화가 어떻게 달라지는지 확인해야
한다.

### A4 Visualization and Demo Lab

A0의 output은 textual CoC와 minADE 중심이다. A4는 사용자가 image input, ego history,
ground truth future, predicted trajectory를 눈으로 비교할 수 있게 만들어야 한다.

## 7. 이해도 테스트

### Short-Answer Questions

#### Q1. HF login은 성공했는데 AlpaSim이 실패했다. 이 둘은 같은 문제인가?

기대 답변:

아니다. A0에서 HF access는 `kimdh1st` 계정으로 PAI `features.csv`, NuRec metadata,
configured USDZ artifact 접근까지 확인되었다. AlpaSim 실패는 이후 container 내부에서
`alpasim_grpc.v0.common_pb2`가 import되지 않고 sensorsim이 exit 139로 죽은
runtime/packaging 문제다.

오답 징후:

- "HF가 안 돼서 AlpaSim이 실패했다"고만 말함
- NuRec artifact download 성공을 언급하지 못함
- wizard exit code 0을 이유로 AlpaSim 성공이라고 말함

#### Q2. `flash-attn` import 성공은 `uv sync` 문제가 완전히 해결됐다는 뜻인가?

기대 답변:

아니다. official wheel로 설치한 runtime import는 성공했지만, plain
`uv sync --active`는 locked source distribution을 build하려고 하며 host `nvcc` 또는
`CUDA_HOME`이 없어 실패한다. runtime 가능성과 lock-sync 재현성은 구분해야 한다.

오답 징후:

- "`flash-attn`이 import되니 dependency 문제는 끝났다"고 말함
- `nvcc`/`CUDA_HOME` caveat를 빼먹음
- wheel install path와 source build path를 구분하지 못함

#### Q3. PAI inference 1회 성공으로 전체 데이터셋 학습 가능성을 주장할 수 있는가?

기대 답변:

아니다. A0의 official inference 1회는 PAI sample 접근, model load, CoC generation,
trajectory prediction, minADE calculation을 확인한 open-loop smoke다. full dataset
evaluation, SFT/RL training, throughput, memory budget, learning stability는 확인하지
않았다.

오답 징후:

- "minADE가 나왔으니 학습도 가능하다"고 말함
- inference와 training을 구분하지 못함
- single sample과 dataset-wide 평가를 구분하지 못함

#### Q4. `.venv/bin/hf`는 무엇이며 왜 system `hf`와 다를 수 있는가?

기대 답변:

`.venv/bin/hf`는 Alpamayo Track A virtual environment 안에 설치된
`huggingface_hub`의 CLI executable이다. system `hf`와 package version, executable
path, token 상태가 다를 수 있으므로 Alpamayo 실행에 쓰는 environment의 CLI로
`auth whoami`를 확인해야 한다.

오답 징후:

- `.venv/bin/hf`를 custom script라고 말함
- global `hf` 로그인만 확인하면 충분하다고 말함
- virtual environment와 CLI executable path의 관계를 설명하지 못함

#### Q5. A0에서 가장 강한 성공 evidence는 무엇인가?

기대 답변:

공식 `src/alpamayo_r1/test_inference.py`가 PAI sample에서 dataset/model load, CoC text
생성, 64-step trajectory prediction, `minADE: 2.5593724 meters` 계산까지 완료한
것이다.

오답 징후:

- synthetic dummy smoke만 언급함
- 모델 weight download만 언급함
- `minADE`가 무엇을 통해 나온 결과인지 설명하지 못함

### Scenario Questions

#### S1. A1 Expert가 "이제 A0가 끝났으니 AlpaSim closed-loop도 된다고 보면 되나요?"라고 묻는다. 어떻게 답할 것인가?

기대 답변:

아니다. A0는 AlpaSim이 container start까지 도달했음을 확인했지만, 내부 services가
generated gRPC module import 실패와 sensorsim crash로 종료되었다. closed-loop
success는 metrics/video나 정상 rollout evidence가 있어야 하며, A5에서 별도로 진단해야
한다.

오답 징후:

- "wizard가 finished라서 됐다"고 답함
- "A0 done이면 closed-loop도 통과"라고 답함
- container 내부 실패 로그를 무시함

#### S2. A1 Expert가 plain `uv sync --active`를 실행하다 실패했다. A0가 틀렸다고 봐야 하는가?

기대 답변:

아니다. A0도 plain `uv sync --active` 실패를 caveat로 기록했다. A0의 성공은 official
wheel 기반 runtime import와 PAI inference 성공이다. plain sync 실패는 host
`nvcc`/`CUDA_HOME`이 없는 lock-sync 재현성 blocker로 남아 있다.

오답 징후:

- A0가 dependency 문제를 완전히 해결했다고 착각함
- plain sync 실패와 runtime wheel 성공을 같은 것으로 취급함
- A1에서 어떤 install path를 쓰는지 확인하지 않음

#### S3. A3를 시작하려는 사람이 "A0에서 minADE가 2.5593724니까 모델 성능은 이미 검증됐다"고 말한다. 무엇이 문제인가?

기대 답변:

단일 PAI sample의 minADE는 baseline smoke evidence이지 model quality validation이
아니다. A3는 여러 clip, seed, sample 수, runtime, VRAM, metric 분포를 봐야 한다.
따라서 A0 결과는 A3의 출발점이지 결론이 아니다.

오답 징후:

- single metric을 dataset-wide 성능으로 일반화함
- A3의 필요성을 설명하지 못함
- minADE가 나온 실행 범위를 말하지 못함

#### S4. HF access를 확인할 때 user 계정 로그인만 보면 충분한가?

기대 답변:

충분하지 않다. local environment의 CLI가 어떤 계정으로 인증되어 있는지와, 해당
계정이 필요한 gated asset에 실제로 접근 가능한지를 모두 확인해야 한다. A0에서는
`.venv/bin/hf auth whoami`, PAI `features.csv`, NuRec metadata, USDZ download로 확인했다.

오답 징후:

- 로그인만 성공하면 모든 asset 접근이 된다고 말함
- repo별/file별 gated access 차이를 무시함
- `.venv` environment의 인증 상태를 확인하지 않음

### Misconception Check

#### M1. "A0 done = Alpamayo 개발 환경이 완전히 재현 가능하다."

정답:

틀림. A0 done은 wheel 기반 runtime과 PAI single-sample inference가 가능하다는 뜻이다.
plain lock sync와 AlpaSim closed-loop는 남은 blocker다.

오답 징후:

재현성 caveat를 생략하고 "환경 완료"라고만 말함.

#### M2. "AlpaSim wizard가 exit 0이면 smoke 성공이다."

정답:

틀림. A0에서는 wizard가 exit 0을 반환했지만 container services가 실패했다. smoke
성공 여부는 내부 logs, metrics/video 생성, rollout 정상 종료를 봐야 한다.

오답 징후:

process exit code만 보고 simulator 검증을 완료 처리함.

#### M3. "HF access 실패와 dependency 실패는 같은 환경 문제다."

정답:

틀림. HF access는 인증/권한 문제이고, dependency 실패는 package build/runtime 문제다.
A0에서는 HF access가 해결되었고, `flash-attn` plain source build caveat가 남았다.

오답 징후:

접근권, dependency, simulator runtime blocker를 하나의 "환경 문제"로 뭉뚱그림.

#### M4. "Synthetic smoke가 성공했으니 PAI official inference는 필요 없다."

정답:

틀림. synthetic smoke는 모델/processor 경로의 보조 evidence다. PAI official inference는
실제 sample 접근, loader, model, metric path까지 확인하므로 더 강한 evidence다.

오답 징후:

dummy input과 실제 PAI sample의 차이를 설명하지 못함.

## 8. 채점 기준

| Grade | Criteria |
| --- | --- |
| pass | A0의 성공, 실패, 한계를 분리해서 설명하고, HF access/dependency/simulator blocker를 서로 구분하며, A1-A4에 어떤 질문을 넘겨야 하는지 말할 수 있음 |
| partial | 핵심 성공은 기억하지만 caveat 일부를 빼먹거나, `flash-attn`/AlpaSim/HF access 중 하나를 다른 문제와 혼동함 |
| fail | A0 done을 전체 환경/학습/closed-loop 검증 완료로 과장하거나, single-sample inference와 full evaluation/training을 구분하지 못함 |

Pass 판정에 필요한 최소 답변:

- A0의 가장 강한 성공 evidence는 official PAI `test_inference.py`의 CoC와
  `minADE: 2.5593724 meters` 출력이라고 말할 수 있어야 한다.
- HF access는 Track A 범위에서 해결되었고, AlpaSim blocker는 HF가 아니라 simulator
  runtime/packaging 문제라고 말할 수 있어야 한다.
- `flash-attn`은 wheel runtime import는 성공했지만 plain `uv sync --active`는
  `nvcc`/`CUDA_HOME` caveat가 남았다고 말할 수 있어야 한다.
- A0는 A1-A4의 출발점이지 full dataset, training, closed-loop 성공 증명이 아니라고
  말할 수 있어야 한다.

## 9. 사용자가 틀리기 쉬운 지점

### "환경"이라는 말을 너무 넓게 쓰는 것

A0에는 여러 종류의 환경 문제가 섞여 있었다. HF access, Python virtual environment,
CUDA runtime, `flash-attn` build path, simulator container runtime은 서로 다른
layer다. 하나가 해결되어도 다른 하나가 자동으로 해결되지 않는다.

### login과 gated asset approval을 같은 것으로 보는 것

로그인은 identity 확인이고, gated asset approval은 repo/file 접근권이다. A0에서는
둘 다 확인했기 때문에 HF access resolved라고 말할 수 있다.

### synthetic smoke와 official inference를 같은 무게로 보는 것

synthetic smoke는 모델/processor가 실행 가능하다는 보조 근거다. official PAI
inference는 실제 sample과 metric path를 지나므로 더 강한 근거다.

### open-loop inference와 closed-loop simulator를 혼동하는 것

PAI inference는 sample을 넣어 prediction과 metric을 계산하는 open-loop path다.
AlpaSim smoke는 simulator runtime, scene, services, controller, driver가 함께 돌아야
하는 closed-loop 계열 path다.

### exit code만 보고 성공 판단하는 것

AlpaSim wizard는 내부 container failure에도 exit 0을 반환했다. simulator 계열 검증은
exit code 외에 service logs와 output artifact를 봐야 한다.

## 10. A0에 대해 과장하면 안 되는 주장

다음 문장은 A0 evidence보다 강한 주장이다. Manager나 A1 Expert에게 그대로 말하면 안
된다.

- "Alpamayo 환경은 완전히 재현 가능하다."
- "plain `uv sync --active`만 실행하면 모든 dependency가 설치된다."
- "AlpaSim closed-loop smoke가 성공했다."
- "HF login 성공만으로 모든 PAI/NuRec asset 접근권이 보장된다."
- "PAI inference 한 번 성공했으니 모델 성능이 검증됐다."
- "minADE 2.5593724는 dataset-wide 성능이다."
- "SFT/RL training도 가능하다고 봐도 된다."
- "`flash-attn` import 성공은 CUDA toolchain 문제가 없다는 뜻이다."
- "synthetic smoke 성공만으로 실제 PAI loader path도 검증됐다."

## Manager에게 답변해야 할 체크리스트

사용자는 A1 Expert와 대화하기 전에 아래 질문에 자기 말로 답해야 한다.

- A0에서 성공한 가장 강한 evidence는 무엇인가?
- A0에서 HF access resolved라고 말할 수 있는 근거는 무엇인가?
- `.venv/bin/hf`와 system `hf`가 다를 수 있는 이유는 무엇인가?
- `flash-attn` wheel runtime 성공과 plain `uv sync --active` 실패는 어떻게 함께
  존재할 수 있는가?
- PAI official inference 성공이 의미하는 것과 의미하지 않는 것은 무엇인가?
- AlpaSim 실패는 왜 HF access 문제가 아닌가?
- A0 done이 A1, A2, A3, A4 각각에 어떤 출발점을 제공하는가?
- A0 결과를 근거로 절대 과장하면 안 되는 주장은 무엇인가?

## Teacher Follow-Up Rule

사용자가 위 질문 중 두 개 이상에서 blocker layer를 혼동하거나, A0 done을
closed-loop/training/full-dataset 검증으로 과장하면 A1로 넘어가기 전에 이 문서의
5장과 7장을 다시 읽고 다음 세 문장으로 재설명해야 한다.

1. A0가 실제로 증명한 것.
2. A0가 아직 증명하지 못한 것.
3. 다음 track에서 확인해야 할 질문.
