---
doc_type: note
status: done
task_id: alpamayo-rnd-a1-code-model-flow
role: teacher
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-06-06 [Task] Track A1 Alpamayo Code and Model Flow Study.md
source_report: docs/2026-06-06 [Report] Track A1 Expert Code Path Analysis.md
source_review: docs/2026-06-06 [Review] Track A1 Expert Code Path Review.md
created_at: 2026-06-06 22:50:41 KST
updated_at: 2026-06-06 22:50:41 KST
---

# Track A1 Code Flow Review Guide

## Document Frame

Purpose:

이 문서는 A1 Expert report를 다시 요약하는 문서가 아니라, 사용자가 official
`src/alpamayo_r1/test_inference.py` code path를 자기 말로 설명할 수 있는지 확인하는
Teacher/Evaluator guide다.

Primary reader:

Alpamayo Phase A를 진행하는 사용자와 Manager. 사용자는 이 문서를 읽고 A1 경로를
설명하고, Manager는 A2/A3/A4로 넘어가기 전에 이해도 gate를 확인한다.

Decision question:

사용자가 PAI sample이 loader, processor, model, output, metric을 거치는 흐름과 그 한계를
구분해 설명할 수 있는가?

Exclusion scope:

새 inference, 새 dataset probe, 코드 수정, Root Task 수정, A2/A3/A4 실험 설계 확정은
이 문서 범위가 아니다. 불확실한 부분은 A2/A3/A4 또는 별도 Expert task에서 다시 확인한다.

## 1. A1 한 문장 요약

A1에서 확인한 official inference path는 PAI clip의 4-camera x 4-frame 이미지와 16-step
ego history를 prompt와 trajectory token으로 넣고, VLM이 CoC text를 생성하다가
`<|traj_future_start|>`에서 멈춘 뒤, expert/diffusion/action-space 경로가 64-waypoint
`pred_xyz`와 `pred_rot`를 만들고, official script가 single-sample XY ADE에 가까운
`minADE`를 계산하는 흐름이다.

## 2. A1에서 확인된 code path

확인된 official path:

```text
README command
  -> src/alpamayo_r1/test_inference.py
  -> load_physical_aiavdataset(clip_id, t0_us=5_100_000)
  -> helper.create_message(data["image_frames"].flatten(0, 1))
  -> helper.get_processor(model.tokenizer)
  -> processor.apply_chat_template(...)
  -> model_inputs = tokenized_data + ego_history_xyz + ego_history_rot
  -> AlpamayoR1.sample_trajectories_from_data_with_vlm_rollout(...)
  -> extra["cot"], pred_xyz, pred_rot
  -> NumPy XY distance mean over time, then min over sample axis
```

핵심 code evidence:

- `test_inference.py:28-36`: fixed `clip_id`, loader 호출, image flatten, model/processor 로드.
- `test_inference.py:38-50`: chat template 적용 후 model input을 `tokenized_data`,
  `ego_history_xyz`, `ego_history_rot`로 구성.
- `test_inference.py:54-63`: `num_traj_samples=1`, `return_extra=True`로 model sampling 호출.
- `test_inference.py:65-72`: `extra["cot"]` 출력 후 `ego_future_xyz`와 `pred_xyz`의 XY 거리로
  `minADE` 계산.
- `load_physical_aiavdataset.py:27-37`: 16 history, 64 future, 0.1s timestep, 4 image frames.
- `helper.py:28-37`: flattened images와 48 history placeholder token으로 message 생성.
- `models/alpamayo_r1.py:153-209`: history token fusion 후 VLM generation, stop boundary.
- `models/alpamayo_r1.py:256-329`: expert/diffusion/action-space로 `pred_xyz`, `pred_rot`,
  `extra` 생성.

## 3. A1에서 아직 확인되지 않은 것

A1은 code path 이해 task이며, 다음을 증명하지 않는다.

- 새 live inference 재실행 결과. Expert report는 read-only 분석과 기존 evidence 기반이다.
- A3에서 사용할 여러 clip, 여러 seed, 여러 `num_traj_samples` 설정의 성능 분포.
- CoC reasoning의 품질. `extra["cot"]`가 추출된다는 것과 좋은 reasoning이라는 것은 다르다.
- closed-loop driving 성능. Official script는 open-loop single clip inference와 metric 계산이다.
- nuScenes/a2z/self dataset adapter 적합성. PAI contract와 외부 dataset contract는 별도 문제다.
- local HF cache config가 future remote revision에서도 동일하다는 보장.
- richer repo processor path가 official `test_inference.py`에서 실제로 사용된다는 증거.

불확실성은 blocker가 아니라 경계다. A1은 “공식 단일 sample 경로를 설명할 수 있다”까지가
목표이고, “다음 실험을 모두 설계할 수 있다”가 목표가 아니다.

## 4. Expert report와 Review 문서의 핵심 차이

| 항목 | Expert report 결론 | Review 보정 | Teacher 반영 |
| --- | --- | --- | --- |
| 전체 판정 | Official path 설명 가능 | `APPROVE_WITH_NOTES` | A1 Teacher Note 작성 진행 |
| 16 vs 48 | 구분되어 있음 | 더 명시해야 함 | 별도 오해 방지 항목으로 분리 |
| `pred_rot` | 함께 생성됨 | 의미와 shape 보강 필요 | 3x3 rotation matrix sequence로 설명 |
| local config | 현재 cache 근거 | canonical remote evidence 아님 | A3에서 runtime config 재기록 질문 포함 |
| `minADE` | XY min over samples | sample=1이면 사실상 ADE | 이해도 테스트 핵심 문제로 포함 |

Teacher 판단:

Review 문서는 Expert report를 뒤집지 않는다. Review의 역할은 사용자 오해 가능성이 높은
지점을 보정하는 것이다. 따라서 이 문서는 Expert report의 end-to-end flow를 기준으로 삼고,
Review note의 네 가지 위험을 이해도 테스트와 checklist에 반영한다.

## 5. `test_inference.py` 전체 흐름

`test_inference.py`는 데모용 end-to-end script다. 이 파일은 training loop도 아니고,
general metric runner도 아니며, richer repository processor abstraction 전체를 통과하는
경로도 아니다.

흐름:

1. 고정된 `clip_id`와 `t0_us=5_100_000`으로 PAI sample을 load한다.
2. loader가 반환한 `image_frames`를 camera/frame 축에서 flatten해 image list처럼 helper에 넘긴다.
3. helper가 system/user/assistant message를 만들고, user message에는 image들과 history
   trajectory placeholder, future trajectory 요청 문장을 넣는다.
4. `AlpamayoR1.from_pretrained("nvidia/Alpamayo-R1-10B")`로 model을 로드한다.
5. Qwen base processor를 만들되 tokenizer는 Alpamayo model tokenizer로 교체한다.
6. `processor.apply_chat_template(...)`로 multimodal prompt를 tokenize한다.
7. model input은 `tokenized_data`, `ego_history_xyz`, `ego_history_rot`만 포함한다.
8. model이 CoC text와 trajectory를 sample한다.
9. script는 `extra["cot"][0]`를 출력한다.
10. script는 `ego_future_xyz`와 `pred_xyz`를 XY plane에서 비교해 `minADE`를 출력한다.

주의할 점:

`ego_future_xyz`는 model input이 아니라 metric 계산용 ground truth다. Official script의
model execution에는 `camera_indices`, `relative_timestamps`, `absolute_timestamps`도 직접
전달되지 않는다.

## 6. PAI sample loader 흐름

`load_physical_aiavdataset`의 책임은 PAI/PhysicalAIAVDatasetInterface sample을 Alpamayo
inference가 기대하는 tensor dictionary로 바꾸는 것이다.

Loader가 만드는 주요 field:

- `image_frames`: `(N_cameras, num_frames, 3, H, W)`
- `camera_indices`: `(N_cameras,)`
- `ego_history_xyz`: `(1, 1, 16, 3)`
- `ego_history_rot`: `(1, 1, 16, 3, 3)`
- `ego_future_xyz`: `(1, 1, 64, 3)`
- `ego_future_rot`: `(1, 1, 64, 3, 3)`
- `relative_timestamps`: `(N_cameras, num_frames)`
- `absolute_timestamps`: `(N_cameras, num_frames)`
- `t0_us`, `clip_id`

Loader contract와 model input contract는 다르다.

Loader contract는 sample이 갖춰야 하는 전체 field set이다. Model input contract는 official
script에서 실제로 model call에 넘기는 field set이다. A1 기준 official model input은
`tokenized_data`, `ego_history_xyz`, `ego_history_rot`이다. `ego_future_xyz`는 metric에서
사용되고, camera/timestamp field는 loader output과 richer processor path에서는 의미가 있지만
official script의 model call에는 직접 들어가지 않는다.

## 7. image frames / camera order / timestamps / ego history 의미

Image frames:

기본 설정은 4개 camera와 camera당 4개 frame이다. `t0` 기준으로 image timestamp는
대략 `[t0-0.3s, t0-0.2s, t0-0.1s, t0]`가 된다. Official script는 이 tensor를 flatten해서
helper message의 image sequence로 넣는다.

Camera order:

Loader default camera feature는 cross-left, front-wide, cross-right, front-tele이고,
camera name을 index로 바꾼 뒤 index 순서로 sort한다. 이 정렬은 loader output의 일관성을
위한 것이다.

Timestamps:

Loader는 absolute timestamps와 relative timestamps를 반환한다. Review가 지적했듯 official
`test_inference.py` helper path에서는 이 timestamp field들이 model input으로 직접 소비되지
않는다. 다만 richer `qwen_processor.py` path는 camera IDs와 relative timestamps를 다룰 수
있으므로, “repo 전체에서는 중요하지만 official script 직접 evidence는 아니다”라고 구분해야 한다.

Ego history:

`ego_history_xyz`와 `ego_history_rot`는 t0 ego frame 기준의 16개 과거 pose다. Loader는 world
pose를 `t0` pose 기준 local frame으로 변환한다. 이 field들은 model이 trajectory history를
이해하기 위한 핵심 input이다.

반드시 구분할 숫자:

- 4 cameras: loader default camera 수.
- 4 frames: camera당 image frame 수.
- 16 history steps: 시간축 ego pose sample 수.
- 48 history placeholders: 16-step history trajectory를 tokenized representation으로 넣기 위한
  prompt token slot 수.
- 64 future steps: output future waypoint 수.

## 8. processor와 chat template 역할

Official helper path에서 processor/chat template의 역할은 image와 text prompt를 model이 읽을
수 있는 multimodal tokenized input으로 바꾸는 것이다.

Helper message는 세 덩어리다.

System:

Driving assistant 역할을 부여한다.

User:

Flattened images를 순서대로 넣고, `<|traj_history_start|>`, 48개의 `<|traj_history|>`,
`<|traj_history_end|>` placeholder를 넣은 뒤, driving process CoC reasoning과 future
trajectory를 요청한다.

Assistant prefix:

`<|cot_start|>`로 assistant response를 시작하게 만든다.

중요한 점:

Prompt 안에 48개의 history placeholder가 들어가지만, 이 숫자는 16 history pose와 같은
개념이 아니다. 16은 loader가 만든 물리적 time step 수이고, 48은 history trajectory tokenizer가
채울 token slot 수다. Model은 generation 전에 `fuse_traj_tokens`로 placeholder token IDs를
encoded history trajectory token IDs로 교체한다.

## 9. model generation 흐름

### CoC reasoning

Model은 먼저 VLM generation을 수행한다. `AlpamayoR1.sample_trajectories_from_data_with_vlm_rollout`
안에서 `ego_history_xyz`와 `ego_history_rot`가 history trajectory token으로 fusion된 뒤,
VLM이 assistant text를 생성한다.

이때 generation은 일반 텍스트처럼 무한히 이어지지 않는다. `<|traj_future_start|>` token을
effective stop boundary로 사용하고, 그 이후의 trajectory token logits는 masked/controlled된다.

### trajectory token boundary

`<|traj_future_start|>`는 “여기부터 future trajectory로 넘어간다”는 경계다. Official release
path에서 이 경계 이후의 future trajectory는 일반 자연어 token decoding으로 만들어지는 것이
아니다.

경계 token이 발견되면 model은 그 위치와 VLM prompt cache를 사용해 expert/diffusion/action-space
sampling을 준비한다.

### `pred_xyz`

`pred_xyz`는 64 future waypoint의 위치 sequence다. Action space는 acceleration/curvature 형태의
continuous action을 다루고, flow matching diffusion sampler가 noisy action을 반복적으로 update한
뒤, unicycle action space가 이를 future trajectory로 적분한다.

공식 script의 shape 관점에서는 `pred_xyz`가 `(B, num_traj_sets, num_traj_samples, T, 3)` 구조로
정리된다. A1 official script는 `num_traj_samples=1`이므로 sample 후보는 하나다.

### `pred_rot`

`pred_rot`는 text가 아니고 yaw scalar 하나도 아니다. `pred_xyz`의 각 future waypoint에 대응하는
3x3 rotation matrix sequence다. Shape의 leading axes는 `pred_xyz`와 맞춰진다.

### `extra["cot"]`

`extra["cot"]`는 VLM이 생성한 token sequence에서 CoC special token 사이의 text를 추출한 결과다.
Trajectory output과 같은 leading axes, 즉 `(batch, trajectory set, trajectory sample)`에 맞춰
reshape된다.

중요한 해석:

`extra["cot"]`가 있다는 것은 model이 reasoning trace를 출력했다는 뜻이다. 그 reasoning이
정확한지, action과 일관되는지, closed-loop에서 안전한지는 별도 평가가 필요하다.

## 10. minADE가 계산하는 것과 계산하지 않는 것

Official script의 `minADE` 계산:

1. `ego_future_xyz`에서 GT XY future path를 가져온다.
2. `pred_xyz`에서 prediction XY path를 가져온다.
3. 각 timestamp마다 XY L2 distance를 계산한다.
4. time axis 평균을 낸다.
5. sample axis에서 minimum을 고른다.

계산하는 것:

- 한 PAI sample에서 predicted XY waypoint sequence가 GT future XY sequence와 평균적으로 얼마나
  가까운지.
- `num_traj_samples > 1`이면 여러 candidate 중 평균 error가 가장 작은 candidate의 ADE.

계산하지 않는 것:

- CoC reasoning 품질.
- `pred_rot` 품질.
- z coordinate error.
- closed-loop control 안정성.
- route following.
- collision, traffic rule, comfort, intervention, recovery.
- dataset generalization.
- A3 multi-clip, multi-seed, best-of-K 성능.

Review 반영:

Official script는 `num_traj_samples=1`이다. 따라서 이 경우의 `minADE`는 “여러 후보 중 가장
좋은 후보” 성능이 아니라 사실상 “단일 sampled trajectory의 ADE”로 읽어야 한다.

## 11. A1 결과가 A2/A3/A4에 주는 영향

A2 PAI Dataset Literacy:

A2는 어떤 data field가 storage와 adapter에 중요한지 판단해야 한다. A1은 PAI loader가 image,
camera index, timestamps, ego history/future를 반환한다는 contract를 보여준다. A2는 전체 PAI
download 전에 component/chunk budget을 세울 때 이 field들이 어디서 오는지 확인해야 한다.

A3 Inference Experiment Suite:

A3는 official single-sample path를 반복/확장한다. A1 때문에 A3는 다음을 반드시 기록해야 한다.

- runtime-loaded model config 또는 snapshot 정보.
- `clip_id`, `t0_us`, seed, `num_traj_samples`, max generation length.
- CoC text와 `pred_xyz`/`pred_rot` output.
- `num_traj_samples=1`인지 best-of-K minADE인지.
- variance가 sampling/hardware 차이로 생길 수 있다는 점.

A4 Visualization and Demo Lab:

A4는 image inputs, ego history, GT future, prediction, CoC를 함께 보여줘야 한다. A1 때문에 A4는
`extra["cot"]`와 `pred_xyz`를 같은 sample axis로 맞춰 해석해야 하며, `pred_rot`와 timestamp는
시각화 범위에 포함할지 명시적으로 결정해야 한다.

다음 단계 제한:

A1 code path 이해만으로 A3 multi-clip inference matrix나 A4 visualization design을 바로 완성할
수는 없다. A2 storage/data profile, A3 runtime config logging, A4 visualization target이 추가로
필요하다.

## 12. 이해도 테스트

### Short-answer questions

1. `test_inference.py`에서 model execution에 직접 들어가는 loader field는 무엇인가?

기대 답변:

`tokenized_data`와 함께 `ego_history_xyz`, `ego_history_rot`가 들어간다. `ego_future_xyz`는
metric 계산에 쓰이고, `camera_indices`, timestamps는 loader output이지만 official model call에는
직접 들어가지 않는다.

오답 징후:

`ego_future_xyz`를 model input이라고 말하거나, timestamp가 official helper path의 model input에
들어간다고 단정한다.

2. 16 history steps와 48 history placeholders는 같은 뜻인가?

기대 답변:

아니다. 16은 loader가 만드는 시간축 ego pose sample 수이고, 48은 그 trajectory를 encoded token으로
넣기 위한 prompt placeholder slot 수다.

오답 징후:

“history가 48 frame이다”, “16을 48로 upsample한다”처럼 물리 time step과 token slot을 섞는다.

3. `<|traj_future_start|>`는 어떤 역할을 하는가?

기대 답변:

CoC text generation과 trajectory sampling의 boundary다. VLM은 이 token까지 CoC prefix를 생성하고,
그 후 continuous future trajectory는 expert/diffusion/action-space path에서 만들어진다.

오답 징후:

이 token 이후에도 future trajectory를 일반 text token으로 계속 decoding한다고 설명한다.

4. `pred_xyz`와 `pred_rot`의 차이는 무엇인가?

기대 답변:

`pred_xyz`는 64 future waypoint 위치 sequence이고, `pred_rot`는 각 waypoint에 대응하는 3x3
rotation matrix sequence다.

오답 징후:

`pred_rot`를 CoC text, yaw scalar 하나, metric 전용 값으로 설명한다.

5. Official script의 `minADE`는 무엇을 비교하는가?

기대 답변:

`pred_xyz`와 `ego_future_xyz`의 XY path를 비교해 timestep별 L2 distance를 평균하고, sample 축에서
minimum을 고른다.

오답 징후:

CoC quality, rotation quality, collision, closed-loop safety를 평가한다고 말한다.

### Scenario questions

1. `pred_xyz`가 나왔다는 것은 모델이 closed-loop driving을 잘한다는 뜻인가?

기대 답변:

아니다. `pred_xyz`는 open-loop future trajectory prediction output이다. Closed-loop driving은
simulator/replay에서 state transition, controller/replanning, intervention, collision, rule
compliance 등을 별도로 봐야 한다.

오답 징후:

Trajectory tensor가 생성되었으니 closed-loop가 검증됐다고 말한다.

2. minADE는 CoC reasoning의 품질을 평가하는가?

기대 답변:

아니다. Official minADE는 XY trajectory error metric이다. CoC text가 action과 일관되는지, 상황
판단이 맞는지는 별도 annotation/evaluator/qualitative review가 필요하다.

오답 징후:

minADE가 낮으면 reasoning도 좋다고 단정한다.

3. ego history가 빠진 self dataset adapter도 Alpamayo input contract를 만족한다고 볼 수 있는가?

기대 답변:

Official A1 path 기준으로는 어렵다. Model input에는 `ego_history_xyz`와 `ego_history_rot`가 필요하고,
history placeholders는 이 trajectory token으로 fusion된다. Self adapter가 이를 만들 수 없으면
contract gap이다.

오답 징후:

이미지만 있으면 Alpamayo input이 충분하다고 말한다.

4. A1 code path 이해만으로 A3 multi-clip inference 실험을 바로 설계할 수 있는가?

기대 답변:

일부 기반은 된다. 하지만 A3에는 clip selection, storage/data availability, runtime config logging,
seed/sample count, variance 기록, output table schema가 추가로 필요하다. A1만으로 바로 충분하다고
보면 과하다.

오답 징후:

A1이 끝났으니 clip만 늘리면 된다고 답한다.

5. A3에서 `num_traj_samples`를 1에서 6으로 늘리면 `minADE` 해석은 어떻게 달라지는가?

기대 답변:

`num_traj_samples=1`에서는 사실상 single-sample ADE다. 6이면 여섯 후보 중 평균 XY error가 가장
낮은 후보를 고르는 best-of-K 성격의 minADE가 된다. 둘을 같은 metric number처럼 비교하면 안 된다.

오답 징후:

sample 수가 달라도 minADE 의미가 완전히 같다고 말한다.

6. Review 문서에서 Expert report의 어떤 부분을 조심하라고 했는가?

기대 답변:

48 history placeholders와 16 history steps 혼동, `pred_rot` 의미 부족, local HF cache config의
한계, `num_traj_samples=1` minADE 해석을 조심하라고 했다.

오답 징후:

Review가 Expert report를 반려했다고 말하거나, Review 지적사항을 하나도 언급하지 못한다.

### Misconception check

1. “Official loader가 timestamps를 반환하므로 official model inference는 timestamps를 직접 쓴다.”

기대 답변:

틀림. Loader는 timestamps를 반환하지만, official `test_inference.py` helper path의 model input에는
직접 들어가지 않는다. Richer processor path에서는 관련될 수 있으나 official path evidence와
분리해야 한다.

오답 징후:

Loader output field와 official model input field를 같은 것으로 취급한다.

2. “Future trajectory는 `<|traj_future_start|>` 뒤에 text token으로 decoding된다.”

기대 답변:

틀림. Official release path에서는 boundary 이후 expert/diffusion/action-space path가 continuous
action을 sample하고 trajectory로 변환한다.

오답 징후:

VLM language decoding만으로 `pred_xyz`가 만들어진다고 설명한다.

3. “A1의 local cache config 근거는 모든 future run에 대해 canonical이다.”

기대 답변:

틀림. 현재 머신의 cached snapshot을 설명하는 useful evidence다. A3에서 새 실행 evidence를 만들 때
runtime-loaded config를 다시 기록해야 한다.

오답 징후:

Remote revision이나 다른 machine cache 가능성을 무시한다.

4. “Route/navigation input이 없으면 A1 path가 불완전하게 실행된 것이다.”

기대 답변:

틀림. README 기준 release v1.0은 route/navigation conditioning, meta-actions/general VQA,
RL post-trained weights를 포함하지 않는다. 이는 official release surface의 제한이지 A1 runtime
field 누락이라고 볼 수 없다.

오답 징후:

Release limitation과 bug/missing input을 구분하지 못한다.

## 13. 채점 기준

| 등급 | 기준 |
| --- | --- |
| pass | 입력 -> loader -> prompt/processor -> model boundary -> diffusion/action output -> metric 순서를 자기 말로 설명하고, evidence와 limitation을 함께 말함 |
| partial | 큰 흐름은 설명하지만 loader contract와 model input contract, 16 vs 48, minADE 해석 중 하나 이상을 혼동함 |
| fail | 이미지만 model에 넣는다고 보거나, CoC text decoding이 곧 trajectory라고 보거나, minADE/closed-loop/CoC quality를 구분하지 못함 |

Pass에 필요한 최소 답변:

- `ego_history_xyz`/`ego_history_rot`가 model input의 핵심이라는 점.
- `ego_future_xyz`는 official script에서 metric GT로 쓰인다는 점.
- 16 history pose와 48 placeholder token이 다른 층위라는 점.
- `<|traj_future_start|>`가 CoC와 trajectory sampling의 boundary라는 점.
- `pred_xyz`/`pred_rot`는 action-space conversion 결과라는 점.
- `num_traj_samples=1`의 `minADE`는 single-sample ADE처럼 읽어야 한다는 점.

## 14. 사용자가 틀리기 쉬운 지점

첫째, loader output과 model input을 섞기 쉽다.

Loader는 future GT, camera IDs, timestamps까지 반환한다. 하지만 official script의 model call은
`tokenized_data`, `ego_history_xyz`, `ego_history_rot` 중심이다.

둘째, 16과 48을 같은 종류의 숫자로 보기 쉽다.

16은 pose sample count이고 48은 trajectory token slot count다. 이 차이를 설명하지 못하면
adapter 설계에서 필요한 history tensor와 prompt token을 혼동하게 된다.

셋째, CoC text와 trajectory output을 같은 생성 방식으로 보기 쉽다.

CoC는 VLM text generation이고, future trajectory는 boundary 이후 expert/diffusion/action-space
sampling이다.

넷째, `minADE`라는 이름 때문에 best-of-K 성능으로 과장하기 쉽다.

Official script는 `num_traj_samples=1`이다. 이 값은 multi-sample search 결과가 아니다.

다섯째, A1 성공을 closed-loop 또는 generalization 성공으로 확대하기 쉽다.

A1은 code path literacy다. Driving quality, simulation safety, data generalization은 아직 다음
track의 질문이다.

## 15. A1에 대해 과장하면 안 되는 주장

다음 표현은 A1 evidence를 넘어선다.

- “Alpamayo가 closed-loop driving을 검증했다.”
- “`pred_xyz`가 나왔으므로 self dataset adapter도 곧바로 가능하다.”
- “minADE가 낮으면 CoC reasoning도 좋다.”
- “A1은 route/navigation 없는 문제를 해결했다.”
- “Official script의 `minADE`는 multi-sample best-of-K 성능이다.”
- “Local HF cache config 값은 future remote model revision에서도 항상 같다.”
- “`qwen_processor.py`의 richer path가 official `test_inference.py`에서 그대로 실행된다.”
- “A1만으로 A3/A4 실험 설계가 완료됐다.”

허용되는 표현:

- “A1은 official single-sample inference code path를 설명 가능한 수준으로 분해했다.”
- “A1은 PAI loader contract와 official model input/metric 사용 지점을 구분했다.”
- “A1은 CoC text generation과 continuous trajectory sampling의 boundary를 확인했다.”
- “A1은 A2/A3/A4가 확인해야 할 후속 질문을 만들 수 있는 기반이다.”

## 16. A2/A3/A4로 넘어가기 전 Manager에게 답해야 할 체크리스트

사용자 이해 체크:

- PAI sample이 image frames, ego history, ego future를 어떤 field로 반환하는지 설명할 수 있는가?
- Official model input에 들어가는 field와 metric-only field를 구분할 수 있는가?
- 4 cameras, 4 image frames, 16 history steps, 48 history placeholders, 64 future waypoints를
  각각 다른 개념으로 설명할 수 있는가?
- CoC text generation이 어디서 멈추고 trajectory sampling이 어디서 시작되는지 설명할 수 있는가?
- `pred_xyz`, `pred_rot`, `extra["cot"]`의 의미와 alignment를 설명할 수 있는가?
- Official script의 `minADE`가 계산하는 것과 계산하지 않는 것을 설명할 수 있는가?
- Review 문서의 non-blocking notes 네 가지를 말할 수 있는가?

A2에 넘길 질문:

- PAI component/chunk 중 A1 loader contract를 만족하는 데 필요한 최소 field는 무엇인가?
- `camera_indices`, timestamps, egomotion, image components를 storage budget에서 어떻게 계산할 것인가?
- Full PAI download 없이 A3/A4에 충분한 curated subset을 만들 수 있는가?

A3에 넘길 질문:

- 각 run마다 `clip_id`, `t0_us`, seed, `num_traj_samples`, model snapshot/config를 어떻게 기록할 것인가?
- `num_traj_samples=1`과 larger K의 minADE를 같은 table에서 어떻게 구분할 것인가?
- CoC text와 trajectory output을 어떤 schema로 함께 저장할 것인가?
- Variance와 nondeterminism을 어떤 반복 run으로 확인할 것인가?

A4에 넘길 질문:

- Image grid, ego history, GT future, `pred_xyz`, `pred_rot`, CoC를 어떤 화면/파일에서 함께 볼 것인가?
- Camera order와 timestamps는 visualization에서 표시할 것인가, 아니면 official script path와 분리해 별도 view로 둘 것인가?
- CoC와 trajectory sample axis를 어떻게 맞춰 보여줄 것인가?
- Visualization이 model quality를 과장하지 않도록 어떤 caption/legend를 둘 것인가?

Manager gate:

A1을 완료로 볼 수 있으려면 사용자가 위 checklist 중 핵심 항목을 자기 말로 답해야 한다. 특히
loader contract와 model output contract를 구분하지 못하거나, `minADE`를 CoC/closed-loop 평가로
오해하면 A2/A3/A4 착수 전에 Teacher review를 한 번 더 진행해야 한다.
