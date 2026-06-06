---
doc_type: review
status: done
task_id: alpamayo-rnd-a1-code-model-flow
role: reviewer
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-06-06 [Task] Track A1 Alpamayo Code and Model Flow Study.md
reviewed_report: docs/2026-06-06 [Report] Track A1 Expert Code Path Analysis.md
created_at: 2026-06-06 15:59:43 KST
updated_at: 2026-06-06 15:59:43 KST
---

# Track A1 Expert Code Path Review

## Review Scope

이 문서는 Reviewer agent의 독립 검토 결과다. 새 실험, 코드 수정, Root Task 수정은
수행하지 않았다. 검토는 기준 문서와 read-only 코드 확인에 한정했다.

기준 문서:

- `docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md`
- `docs/2026-05-26 [Task] Alpamayo R&D Root Task.md`
- `docs/2026-06-06 [Task] Track A1 Alpamayo Code and Model Flow Study.md`
- `docs/2026-06-06 [Report] Track A1 Expert Code Path Analysis.md`

대표 read-only 확인:

- `nl -ba src/alpamayo_r1/test_inference.py`
- `nl -ba src/alpamayo_r1/load_physical_aiavdataset.py`
- `nl -ba src/alpamayo_r1/helper.py`
- `nl -ba src/alpamayo_r1/models/alpamayo_r1.py`
- `nl -ba src/alpamayo_r1/models/base_model.py`
- `nl -ba src/alpamayo_r1/metrics/distance_metrics.py`
- `nl -ba src/alpamayo_r1/processor/qwen_processor.py`
- `nl -ba` on the local Alpamayo-R1-10B cached `config.json` snapshot:
  `/home/user/.cache/huggingface/hub/models--nvidia--Alpamayo-R1-10B/snapshots/d72c6a2757b10cacb69b688ca66ccfad3dafbf37/config.json`

## Verdict

`APPROVE_WITH_NOTES`

Expert report는 A1 Subtask의 Expert Questions에 실질적으로 답했고, official
`test_inference.py` path와 repo의 richer processor/general metric path를 대부분
정확히 구분했다. CoC generation boundary, expert/diffusion/action-space trajectory
sampling, `pred_xyz`, ADE/minADE 설명도 코드 evidence와 일치한다.

Teacher note 작성으로 넘어가도 된다. 다만 Teacher는 아래 non-blocking note를 반영해
`48 history placeholders`와 `16 history steps`, `num_traj_samples=1`의 minADE 의미,
local HF cache config의 한계를 명확히 설명해야 한다.

## Required Fixes

없음.

현재 검토 기준에서는 A2/A3/A4 handoff를 막을 정도의 기술 오류나 evidence 누락은
확인되지 않았다.

## Non-blocking Notes

### 1. 48 history placeholders와 16 history steps를 같은 개념으로 설명하면 안 됨

Expert report는 이 둘을 구분하고 있지만, Teacher 자료에서는 더 명시적으로 분리하는
편이 안전하다.

근거:

- Loader는 `num_history_steps=16`으로 16개의 ego history pose를 만든다:
  `src/alpamayo_r1/load_physical_aiavdataset.py:32`, `:105-120`, `:149-157`.
- Official helper는 prompt 안에 `<|traj_history|>` placeholder를 48개 넣는다:
  `src/alpamayo_r1/helper.py:33-37`.
- Model은 `ego_history_xyz`/`ego_history_rot`를 history trajectory tokenizer로 인코딩한
  token IDs로 placeholder를 교체한다:
  `src/alpamayo_r1/models/base_model.py:91-122`, `:168-197`.
- Local checkpoint config는 `tokens_per_history_traj: 48`을 기록한다:
  `/home/user/.cache/huggingface/hub/models--nvidia--Alpamayo-R1-10B/snapshots/d72c6a2757b10cacb69b688ca66ccfad3dafbf37/config.json:64-65`.

Teacher 설명 포인트:

16은 시간축 pose 샘플 수이고, 48은 그 history trajectory를 prompt token 위치에 넣기
위한 encoded trajectory token 수다.

### 2. `pred_rot` 의미는 Teacher 자료에서 한 문장 더 보강 필요

Expert report는 `pred_rot`가 action-space conversion에서 함께 나온다고 설명하지만,
사용자 이해도 테스트용으로는 shape와 의미를 더 직접적으로 적는 것이 좋다.

근거:

- `action_to_traj`는 `traj_future_xyz`와 `traj_future_rot`를 함께 반환한다:
  `src/alpamayo_r1/action_space/unicycle_accel_curvature.py:300-382`.
- Model은 `pred_xyz`, `pred_rot`를 `(B, num_traj_sets, num_traj_samples, ...)`로 reshape한다:
  `src/alpamayo_r1/models/alpamayo_r1.py:313-329`.

Teacher 설명 포인트:

`pred_xyz`는 64 future waypoint의 위치이고, `pred_rot`는 각 future waypoint에 대응하는
3x3 rotation matrix sequence다. 단순한 yaw scalar나 text token이 아니다.

### 3. Local HF cache config는 유용하지만 canonical remote evidence는 아님

Expert report는 local checkpoint config를 근거로 `tokens_per_history_traj`,
`tokens_per_future_traj`, action space, diffusion target을 확인했다. 이 값들은 현재
로컬에서 사용하는 모델 snapshot을 설명하는 evidence로는 적절하다. 다만 remote model
revision이 바뀌거나 cache가 다른 snapshot을 가리키면 달라질 수 있으므로, A3에서 새
실행 evidence를 만들 때는 runtime-loaded config를 다시 기록해야 한다.

Teacher 설명 포인트:

local config는 "현재 이 머신의 cached 10B snapshot 기준"이라는 한계를 붙여 설명한다.

### 4. `num_traj_samples=1`의 minADE는 single-sample ADE로 설명해야 함

Expert report의 해석은 정확하다. 다만 Teacher note에서는 이름 때문에 오해가 생기기
쉽다. Official script는 `diff.min()`을 호출하지만 sample 축 길이가 1이면 선택 가능한
후보가 하나뿐이다.

근거:

- Official script는 `num_traj_samples=1`로 호출한다:
  `src/alpamayo_r1/test_inference.py:54-63`.
- Official script의 metric은 prediction/GT XY L2 distance를 time 평균한 뒤 sample 축에서
  minimum을 취한다:
  `src/alpamayo_r1/test_inference.py:68-72`.
- General metric path도 K samples 중 평균 L2가 최소인 sample을 고르는 구조다:
  `src/alpamayo_r1/metrics/distance_metrics.py:53-95`.

Teacher 설명 포인트:

`num_traj_samples=1`일 때의 `minADE`는 "여러 후보 중 최고 후보" 성능이 아니라 "그 한
후보의 ADE"다. A3에서 sample 수를 늘리면 minADE 의미가 달라진다.

## Evidence Check

| Claim | Status | Reviewer basis |
| --- | --- | --- |
| A1 Expert Questions coverage | confirmed | A1 질문 9개 모두 Expert report의 Evidence/Inference/Unknowns에 대응 |
| Official command/file path is `python src/alpamayo_r1/test_inference.py` | confirmed | README `:69-82`, script `:28-63` |
| Official script uses fixed clip and loader call | confirmed | `test_inference.py:28-33` |
| Official model input excludes `camera_indices`, `relative_timestamps`, `absolute_timestamps` | confirmed | `test_inference.py:33`, `:46-50`, `:68-72`; `rg` 결과 official script에서 해당 필드 미사용 |
| Loader returns camera IDs and timestamps | confirmed | `load_physical_aiavdataset.py:57-68`, `:196-219` |
| Richer repo processor can use camera IDs and relative timestamps | confirmed | `processor/qwen_processor.py:226-297` |
| 4 cameras are loader defaults | confirmed | `load_physical_aiavdataset.py:52-55`, `:73-79` |
| 4 image frames are loader defaults | confirmed | `load_physical_aiavdataset.py:36`, `:164-183` |
| 16 history steps and 64 future steps are loader defaults | confirmed | `load_physical_aiavdataset.py:32-34`, `:105-120`, `:149-157` |
| Ego-frame transforms are handled in loader | confirmed | `load_physical_aiavdataset.py:131-147` |
| Prompt carries 48 history placeholders in official helper path | confirmed | `helper.py:33-37`; local config `config.json:64-65` |
| 48 placeholders are not the same thing as 16 history poses | confirmed | Loader creates 16 poses; tokenizer/config require 48 placeholder tokens |
| CoC generation stops at `<|traj_future_start|>` | confirmed | `alpamayo_r1.py:182-209`, `token_utils.py:172-209` |
| Future trajectory is not ordinary text decoding in official path | confirmed | `alpamayo_r1.py:256-311`, `flow_matching.py:60-138`, `unicycle_accel_curvature.py:300-382` |
| Module producing `pred_xyz`/`pred_rot` is AlpamayoR1 plus action space conversion | confirmed | `alpamayo_r1.py:293-329`, `unicycle_accel_curvature.py:300-382` |
| `pred_xyz` is 64-waypoint future trajectory | confirmed | local config `config.json:28-31`; action space `get_action_space_dims()` and output allocation |
| `pred_rot` is returned with trajectory rotations | partially confirmed | Code evidence is clear; Expert report could state exact shape/meaning more explicitly |
| Official script minADE is XY L2 mean over time with min over samples | confirmed | `test_inference.py:68-72` |
| `num_traj_samples=1` makes official minADE effectively single-sample ADE | confirmed | `test_inference.py:60`, `:68-72` |
| General metric path shape `[B, N, K, T, 3]` is separate from official NumPy metric path | confirmed | `distance_metrics.py:24-50`, `:53-95`; `metric_api.py:198-218` |
| Release excludes route/navigation conditioning, meta-actions/general VQA, RL weights | confirmed | `README.md:88-105`, `:119-136` |
| Local HF cache config limitations are acknowledged | confirmed | Expert report Unknowns and Limits notes this; reviewer recommends repeating runtime config capture in A3 |

## Detailed Review Blocks

### Expert Questions Coverage

The A1 Subtask asked for command/path, loader fields, 4 cameras/4 frames/16 history/64 future
reasoning, ego-frame timestamps, prompt placeholders, CoC-to-trajectory boundary,
`pred_xyz`/`pred_rot` producer, ADE/minADE computation, and release-specific assumptions.

Expert report covers all of these. The strongest sections are `Official command and entry file`,
`PAI clip loading and data contract`, `CoC generation boundary`, `Trajectory sampling and pred_xyz`,
and `ADE and minADE`.

No required correction is needed before Teacher handoff.

### Official Path vs Richer Repo Path

Expert report correctly distinguishes the official `test_inference.py` helper path from the richer
repo processor path.

Official script:

- flattens `data["image_frames"]` into the helper message;
- passes only `tokenized_data`, `ego_history_xyz`, and `ego_history_rot` to the model;
- uses `ego_future_xyz` only after inference for minADE;
- does not pass `camera_indices`, `relative_timestamps`, or `absolute_timestamps` into processor or
  model execution.

Richer repo path:

- `qwen_processor.py` sorts by `camera_indices` and can carry `relative_timestamps`;
- metric API can preserve timestamps in output metadata;
- this path is relevant for repo architecture literacy, but it is not direct evidence for the
  official single-sample script execution.

Expert report states this separation clearly enough for A1.

### CoC Boundary and Trajectory Sampling

Expert report's central claim is confirmed: the official release path is hybrid text plus action.

The VLM generates text with `<|traj_future_start|>` as the effective stopping token. Discrete
trajectory token logits are masked during CoC generation. After the boundary, the model uses the VLM
prompt cache, expert model, flow matching, and action-space conversion to sample continuous
acceleration/curvature actions and convert them into `pred_xyz` and `pred_rot`.

This is an important Teacher handoff point. The user should not come away thinking the future
trajectory is decoded as ordinary text after `<|traj_future_start|>`.

### ADE and minADE Meaning

Official script minADE is not the full metric runner. It is a small NumPy calculation in
`test_inference.py`. It compares predicted XY trajectories against `ego_future_xyz` XY, averages
L2 distance over time, and takes the minimum over the sample axis.

Because official inference uses `num_traj_samples=1`, this value is effectively the ADE of one
sample. It is still useful as a smoke metric for the single clip, but it does not prove closed-loop
driving quality, dataset generalization, or multi-sample best-of-K quality.

## Teacher Handoff Decision

Teacher note 작성으로 넘어가도 된다.

Teacher가 특히 조심해야 할 설명 포인트:

- `official test_inference.py` path와 `qwen_processor.py`/general metric path를 분리해서 설명.
- `camera_indices`, `relative_timestamps`, `absolute_timestamps`는 loader/richer processor에서는
  중요하지만 official script model input에는 들어가지 않는다는 점.
- 4 cameras, 4 image frames, 16 history steps, 64 future steps는 loader defaults이고, 64
  waypoints는 action-space/config와도 연결된다는 점.
- 48 history placeholders는 16 history poses의 개수와 같은 개념이 아니라 encoded history
  trajectory token slots라는 점.
- `<|traj_future_start|>` 이후 future trajectory는 text decoding이 아니라
  expert/diffusion/action-space path라는 점.
- `num_traj_samples=1`의 minADE는 single-sample ADE처럼 읽어야 한다는 점.
- Local HF cache config는 현재 머신의 cached snapshot evidence이며, A3 실행에서는 runtime
  config와 실제 output을 다시 기록해야 한다는 점.

## Review Outcome

Reviewer 판정: `APPROVE_WITH_NOTES`.

A1 Expert report는 Teacher note 작성과 A2/A3/A4 준비의 근거로 사용할 수 있다. 단, Teacher
note에서는 위 non-blocking note를 사용자 이해도 질문에 반영해야 한다.
