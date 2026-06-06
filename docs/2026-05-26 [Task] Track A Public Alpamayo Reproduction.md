---
doc_type: task
task_role: subtask
status: done
task_id: alpamayo-track-a-public-reproduction
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
created_at: 2026-05-26 18:24:55 KST
updated_at: 2026-06-06 20:35:48 KST
---

# Track A Public Alpamayo/PAI Reproduction Task

## Objective

공개 Alpamayo 1/PAI/AlpaSim 경로가 현재 환경에서 실제로 재현 가능한지 확인한다.
이 Subtask는 후속 Track B-F가 의존하는 baseline contract와 환경 리스크를
검증하는 첫 gate다.

## Parent Plan

- Canonical Plan: `docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md`
- Origin Plan: `docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md`
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
| HF access 확인 | done | `.venv/bin/hf auth whoami`; `hf_hub_download(... PhysicalAI-Autonomous-Vehicles/features.csv ...)`; `HfApi().dataset_info('nvidia/PhysicalAI-Autonomous-Vehicles-NuRec', files_metadata=True)`; AlpaSim wizard NuRec USDZ download | HF CLI is logged in as `kimdh1st`; PAI `features.csv` downloads successfully; NuRec repo metadata is accessible and AlpaSim downloaded the configured USDZ artifact | Treat HF access as resolved for Track A; old direct NuRec `labels.json` probe was a stale/wrong path, not current evidence of access failure |
| Python/uv 환경 확인 | done | `uv sync --no-install-package flash-attn`; official flash-attn wheel install from Dao-AILab release; CUDA Toolkit 12.8 host install; `zsh -ic 'uv venv ar1_venv && source ar1_venv/bin/activate && uv sync --active'`; `ar1_venv` import check; `python src/alpamayo_r1/test_inference.py` | Previous wheel workaround remains historical context. After CUDA Toolkit 12.8 installation, plain README `uv sync --active` succeeds and locked `flash-attn==2.8.3` builds from source. Official PAI inference also succeeds from `ar1_venv`. | Treat README environment reproduction as resolved on this host; keep wheel workaround only as historical fallback |
| Alpamayo inference | done | `.venv/bin/python src/alpamayo_r1/test_inference.py`; synthetic `.venv/bin/python` smoke with dummy 4-camera tensors and `AlpamayoR1.from_pretrained(..., device_map={'': 0})`; official-like synthetic path through `helper.create_message`, Qwen processor, and `sample_trajectories_from_data_with_vlm_rollout` | Official PAI script now completes: dataset loads, checkpoint shards load, CoC says `Nudge to the left...`, and `minADE: 2.5593724 meters`. Synthetic model and processor smokes also produce 64-step trajectories. | Use this as the Track B/C baseline contract anchor; do not interpret one clip as model quality validation |
| PAI subset 확인 | done | `scripts/download_pai.py`; direct `features.csv` `hf_hub_download`; official `test_inference.py` dataset loader | Direct `features.csv` download succeeds and official inference loads the PAI sample path enough to calculate minADE | Full public-dataset evaluation remains Track B scope |
| AlpaSim driver smoke | blocked_on_simulator_runtime | AlpaSim `uv sync --extra wizard`; `.venv/bin/python -m alpasim_wizard.check_config deploy=local topology=1gpu driver=alpamayo1 ...`; `.venv/bin/alpasim_wizard ... wizard.dry_run=true` | Wizard extra installed; config check finds 1 scene; dry-run downloads NuRec USDZ, generates compose/configs, pulls `nvcr.io/nvidia/nre/nre-ga:26.02`, builds `alpasim-base:0.70.0`, and starts containers. Containers then fail: `alpasim_grpc.v0.common_pb2` missing in physics/runtime/controller/driver and sensorsim segfaults. Wizard exits 0 despite container failures. | Classify as simulator/runtime packaging blocker, not HF/dataset blocker; inspect AlpaSim generated proto packaging and sensorsim runtime before treating closed-loop smoke as valid |
| Synthetic model-only smoke | done | PAI 없이 zero image/ego-history dummy input; `AlpamayoR1.from_pretrained('nvidia/Alpamayo-R1-10B', dtype=torch.bfloat16, device_map={'': 0}, max_memory={0: '23GiB'})`; official-like synthetic processor path | Weights are downloaded and direct single-GPU synthetic trajectory sampling succeeds. The stronger smoke also tokenizes 16 dummy camera images and returns CoC text plus 64-step trajectory tensors. Earlier `.to('cuda')` load OOM and naive two-GPU `device_map='auto'` cache mismatch remain useful caveats. | Treat model weights, processor path, and core trajectory sampler as executable; official reproduction still needs HF data access |
| Reproduction report | done | This Task document | Environment, blockers, contract draft, official inference result, AlpaSim blocker, and review note recorded | Track A is ready for user review; Track B/C may proceed from the contract with known caveats |

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

## Environment Setup Note

- `.venv` is the local Python virtual environment created in this repository during Track A.
- It was created by `uv` while preparing the Alpamayo runtime. The relevant recorded commands are
  `uv run --no-sync python --version`, which created `.venv`, and
  `uv sync --no-install-package flash-attn`, which installed project dependencies into `.venv`
  while skipping the `flash-attn` package that requires `nvcc`.
- `.venv/bin/python` points to `/usr/bin/python3` and runs Python 3.12.3 inside the isolated
  virtual environment.
- `.venv/bin/hf` is not a custom script. It is the Hugging Face CLI executable installed into the
  virtual environment by the `huggingface_hub` package. Current version:
  `huggingface_hub version: 0.36.2`.
- The task uses `.venv/bin/...` commands to ensure checks run against the exact dependency set
  installed for Alpamayo Track A, not an unrelated global Python environment.
- Current HF state: `.venv/bin/hf auth whoami` reports `user: kimdh1st`; PAI `features.csv`
  downloads successfully, NuRec repo metadata is accessible, and the AlpaSim wizard downloaded the
  configured NuRec USDZ scene artifact.

## FlashAttention Dependency Note

- `flash-attn` is a project requirement, not an optional dependency for the final Alpamayo
  environment. `pyproject.toml` declares `flash-attn>=2.8.3`, and `uv.lock` pins
  `flash-attn==2.8.3`.
- The earlier `uv sync --no-install-package flash-attn` path was only a temporary Track A smoke
  workaround to separate HF/data/model feasibility from CUDA build-tool feasibility.
- The project README under `finetune/rl/` explicitly describes a two-step install:
  install all dependencies except `flash-attn` first, then run `uv sync --active` to build
  `flash-attn` after torch is available.
- Current failure mode: `uv sync --active` starts building `flash-attn==2.8.3`, sees
  `torch.__version__ = 2.8.0+cu128`, then fails because `nvcc` is not found and `CUDA_HOME` is
  unset.
- Current system has NVIDIA driver/runtime access and Torch CUDA works, but no CUDA compiler
  toolkit is visible on `PATH`.
- Attempted Python-wheel `nvcc` path: `nvidia-cuda-nvcc-cu12==12.8.93` and
  `nvidia-cuda-cccl-cu12==12.8.90` install into `.venv`, but the installed package does not expose
  an `nvcc` executable suitable for the `flash-attn` source build.
- Historical runtime fallback: install the official prebuilt Dao-AILab wheel matching this environment:
  `flash_attn-2.8.3+cu12torch2.8cxx11abiTRUE-cp312-cp312-linux_x86_64.whl`. Import validation
  succeeds with `flash_attn 2.8.3` and `flash_attn_func`.
- Current primary host path: after CUDA Toolkit 12.8 installation, plain README `uv sync --active`
  source-builds locked `flash-attn==2.8.3` successfully in `ar1_venv`.

### 2026-06-06 CUDA Toolkit 12.8 Reopen Addendum

The previous lock-sync caveat is superseded for the current host.

User approved system installation of CUDA Toolkit 12.8. The following host-level changes were made:

- NVIDIA CUDA Ubuntu 24.04 APT keyring/repository added via `cuda-keyring_1.1-1_all.deb`.
- `cuda-toolkit-12-8==12.8.2-1` installed with `sudo apt-get install -y cuda-toolkit-12-8`.
- Key installed compiler packages include `cuda-compiler-12-8==12.8.2-1`,
  `cuda-nvcc-12-8==12.8.93-1`, and `cuda-cudart-dev-12-8==12.8.90-1`.
- `/usr/local/cuda` now points to `/usr/local/cuda-12.8`.
- `/usr/local/cuda-12.8/bin/nvcc --version` reports CUDA compilation tools release 12.8,
  `V12.8.93`.
- `/home/user/.zshrc` now exports `CUDA_HOME=/usr/local/cuda-12.8`,
  `CUDA_PATH=$CUDA_HOME`, and prepends `$CUDA_HOME/bin` to `PATH`.

Revalidated README path:

```bash
uv venv ar1_venv
source ar1_venv/bin/activate
uv sync --active
```

Result:

- `flash-attn==2.8.3` built from source.
- `uv sync --active` exited 0.
- `ar1_venv` import check reports `torch 2.8.0+cu128`, CUDA 12.8 available, and
  `flash_attn 2.8.3`.

Revalidated README inference from the same `ar1_venv`:

```bash
CUDA_VISIBLE_DEVICES=0 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
python src/alpamayo_r1/test_inference.py
```

Result:

```text
Chain-of-Causation (per trajectory):
 [['Nudge to the left to increase clearance from the construction cones encroaching into the lane.']]
minADE: 2.5593724 meters
```

Logs:

- `docs/logs/2026-06-06-a0-cuda128-readme-uv-sync-active.log`
- `docs/logs/2026-06-06-a0-cuda128-readme-test-inference.log`

Manager closure decision: A0 is `done` again under the new official-install evidence. The
remaining AlpaSim failure is carried forward to A5 as a simulator/runtime blocker.

## Execution Log

| Time (KST) | Action | Evidence | Result | Next |
| --- | --- | --- | --- | --- |
| 2026-05-26 18:45:22 KST | Track A execution approved and started | User approval; Root Task/Track A Task status update | Execution state moved to `in_progress` | Check HF, Python/uv, CUDA/GPU, then smoke paths |
| 2026-05-26 18:45:46 KST | Host GPU checked | `nvidia-smi` | Driver 590.48.01, CUDA 13.1 runtime support, 2x RTX 4090, 24564 MiB each, nearly idle | Continue Python/Torch check |
| 2026-05-26 18:46:10 KST | Base Python and uv checked | `python`, `python3`, `uv python list --only-installed`, `uv run --no-sync python --version` | `python` is not on PATH, `python3`/`python3.12` are 3.12.3, `uv` is 0.9.2, `.venv` created | Use `.venv/bin/python` or `python3.12` explicitly |
| 2026-05-26 18:47:55 KST | Project dependencies installed without `flash-attn` | `uv sync --no-install-package flash-attn` | 230 packages installed, including `torch==2.8.0`, `transformers==4.57.1`, `physical-ai-av==0.2.0`, `vllm==0.11.0` | Avoid normal `uv run` because it tries to complete `flash-attn` |
| 2026-05-26 18:48:10 KST | Full sync risk classified | `uv run ...`; `which nvcc` | `flash-attn==2.8.3` build fails: `nvcc` not found and `CUDA_HOME` unset | Dependency blocker, separate from GPU availability |
| 2026-05-26 18:48:35 KST | Installed Python/Torch checked | `.venv/bin/python -c 'import torch ...'` | Torch 2.8.0+cu128, CUDA available, 2 GPUs visible, device0 RTX 4090, 23.52 GiB | GPU meets README minimum; still may OOM at 10B runtime |
| 2026-05-26 18:48:40 KST | HF model/dataset metadata checked | `.venv/bin/python -c 'from huggingface_hub import HfApi ...'` | Alpamayo model metadata accessible (`gated=False`); PAI and NuRec datasets report `gated=auto`; HF CLI says `Not logged in` | Test actual file access |
| 2026-05-26 18:48:55 KST | Gated PAI file access tested | `hf_hub_download('nvidia/PhysicalAI-Autonomous-Vehicles', 'features.csv', repo_type='dataset')` | 401 `GatedRepoError`: must be authenticated and have dataset access | HF blocker confirmed for PAI |
| 2026-05-26 18:49:20 KST | Alpamayo inference attempted | `.venv/bin/python src/alpamayo_r1/test_inference.py` | Fails at `PhysicalAIAVDatasetInterface()` before model load because PAI refs return 401 `GatedRepoError` | Inference smoke blocked by PAI access |
| 2026-05-26 18:50:20 KST | AlpaSim wizard installed and config checked | In `/home/user/Workspace/alpasim`: `uv sync --extra wizard`; `.venv/bin/python -m alpasim_wizard.check_config deploy=local topology=1gpu driver=alpamayo1 ...` | Wizard install succeeds; config check loads scene catalog and finds 1 scene | Try dry-run |
| 2026-05-26 18:50:36 KST | AlpaSim dry-run attempted | `.venv/bin/alpasim_wizard deploy=local topology=1gpu driver=alpamayo1 ... wizard.dry_run=true` | Blocks while downloading NuRec USDZ from gated HF dataset with 401 `GatedRepoError` | HF blocker confirmed for AlpaSim scene data |
| 2026-05-26 19:01:37 KST | Alpamayo weights cache completed | Hugging Face cache under `models--nvidia--Alpamayo-R1-10B`; five safetensor shards present; no `.incomplete` shards | Model weights access/download confirmed without HF login | Try synthetic model-only smoke |
| 2026-05-26 19:02:10 KST | Synthetic one-GPU model smoke attempted | `CUDA_VISIBLE_DEVICES=0 .venv/bin/python - <<'PY' ... AlpamayoR1.from_pretrained(...).to('cuda') ...` | Checkpoint shards load, then `.to('cuda')` fails with CUDA OOM on 23.52 GiB RTX 4090 | Classify GPU memory risk; try two-GPU auto sharding |
| 2026-05-26 19:03:19 KST | Synthetic two-GPU model smoke attempted | `CUDA_VISIBLE_DEVICES=0,1 .venv/bin/python - <<'PY' ... device_map='auto' ... sample_trajectories...` | Weights load and auto device map splits layers across two GPUs, but sampling fails with `RuntimeError: Expected all tensors to be on the same device` during KV cache update | Naive auto-sharding is not a validated inference path; need supported model-parallel/offload strategy |
| 2026-05-26 19:03:34 KST | Synthetic one-GPU direct-placement model smoke succeeded | `CUDA_VISIBLE_DEVICES=0 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv/bin/python - <<'PY' ... AlpamayoR1.from_pretrained(..., device_map={'': 0}, max_memory={0: '23GiB'}) ... sample_trajectories...` | Succeeds: `pred_xyz_shape (1, 1, 1, 64, 3)`, `pred_rot_shape (1, 1, 1, 64, 3, 3)`, `extra_keys ['answer', 'cot', 'meta_action']`; GPU memory freed afterward | Official PAI/AlpaSim smoke still requires HF access |
| 2026-05-27 08:14:41 KST | HF access blocker rechecked | `.venv/bin/hf auth whoami`; direct PAI `features.csv` and NuRec `labels.json` `hf_hub_download`; `nvidia-smi --query-gpu=...` | HF still reports `Not logged in`; PAI and NuRec downloads still return 401 `GatedRepoError`; both RTX 4090 GPUs are nearly idle with about 24069 MiB free each | User HF login/access is still required before official PAI inference or AlpaSim smoke can proceed |
| 2026-05-27 08:17:40 KST | Official-like synthetic inference smoke succeeded | `CUDA_VISIBLE_DEVICES=0 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv/bin/python - <<'PY' ... helper.create_message ... processor.apply_chat_template ... sample_trajectories_from_data_with_vlm_rollout ...` | Succeeds with 16 dummy images shaped `(16, 3, 256, 640)`, `input_ids_shape (1, 2686)`, `pred_xyz_shape (1, 1, 1, 64, 3)`, `pred_rot_shape (1, 1, 1, 64, 3, 3)`, `extra_keys ['answer', 'cot', 'meta_action']`, and CoC prefix `Keep lane...` | This satisfies local model/processor inference feasibility; official PAI minADE and AlpaSim rollout remain gated by HF data access |
| 2026-05-27 08:49:32 KST | Environment setup provenance clarified | `ls -la .venv/bin/hf .venv/bin/python .venv/pyvenv.cfg`; `.venv/bin/hf version`; `.venv/bin/python --version`; `uv --version` | `.venv/bin/hf` is the Hugging Face CLI from `huggingface_hub 0.36.2` installed in the Track A virtual environment; `.venv/bin/python` is Python 3.12.3; `uv` is 0.9.2 | Use `.venv/bin/hf auth login` for the same environment used by Track A checks |
| 2026-05-27 09:00:53 KST | `flash-attn` requirement and `nvcc` fix path investigated | `pyproject.toml`; `uv.lock`; `finetune/rl/README.md`; `uv sync --active`; `uv pip install --dry-run 'nvidia-cuda-nvcc-cu12==12.8.*' 'nvidia-cuda-cccl-cu12==12.8.*'`; web check of NVIDIA CUDA and flash-attn docs | `flash-attn` is required; full sync fails because CUDA compiler toolkit is missing; dry-run resolves CUDA 12.8 wheel candidates: `nvidia-cuda-nvcc-cu12==12.8.93`, `nvidia-cuda-cccl-cu12==12.8.90` | Ask user before modifying `.venv` to attempt the wheel-based `nvcc` path |
| 2026-05-27 09:01:33 KST | HF login and gated dataset access rechecked after user login | `.venv/bin/hf auth whoami`; direct PAI `features.csv` and NuRec `labels.json` `hf_hub_download`; `git diff --check` | HF login succeeds as `kimdh1st`; PAI and NuRec downloads return 403 `GatedRepoError`; diff check passes | User must accept/request the two gated dataset accesses before official PAI/AlpaSim smoke can proceed |
| 2026-05-27 09:06:10 KST | HF dataset access corrected and verified | `.venv/bin/hf auth whoami`; direct PAI `features.csv` `hf_hub_download`; `HfApi().dataset_info('nvidia/PhysicalAI-Autonomous-Vehicles-NuRec', files_metadata=True)` | HF login is `kimdh1st`; PAI `features.csv` downloads; NuRec metadata lists accessible release files. The earlier NuRec direct probe used a stale/wrong file path. | Rerun official inference and AlpaSim dry-run |
| 2026-05-27 09:08:30 KST | Required `flash-attn` runtime installed from official wheel | `uv pip install --python .venv/bin/python https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/flash_attn-2.8.3%2Bcu12torch2.8cxx11abiTRUE-cp312-cp312-linux_x86_64.whl`; `.venv/bin/python -c 'import flash_attn; from flash_attn import flash_attn_func ...'`; `uv sync --active --inexact --no-install-package flash-attn` | `flash_attn 2.8.3` imports successfully and the runtime env remains usable; plain `uv sync --active` still fails on source build without host `nvcc` | Treat as runtime-resolved, lock-sync caveat remaining |
| 2026-05-27 09:10:08 KST | Official PAI inference succeeded | `PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True .venv/bin/python src/alpamayo_r1/test_inference.py` | Dataset and model load; CoC output: `Nudge to the left to increase clearance from the construction cones encroaching into the lane.`; `minADE: 2.5593724 meters` | Track A inference acceptance criterion satisfied |
| 2026-05-27 09:18:07 KST | AlpaSim dry-run reached container runtime but failed internally | In `/home/user/Workspace/alpasim`: `.venv/bin/alpasim_wizard deploy=local topology=1gpu driver=alpamayo1 wizard.log_dir=/home/user/Workspace/alpasim/.track_a_smoke wizard.dry_run=true` | NuRec USDZ download, compose/config generation, NRE image pull, local `alpasim-base:0.70.0` build, and container start all occur. Runtime fails with missing `alpasim_grpc.v0.common_pb2` in multiple services plus sensorsim exit 139. Wizard still reports `Alpasim finished` and exits 0. | Simulator blocker: generated proto/package/runtime issue; not an HF access blocker |
| 2026-06-06 19:32:44 KST | Host CUDA Toolkit 12.8 installed and official README env revalidated | `sudo dpkg -i /tmp/cuda-keyring_1.1-1_all.deb`; `sudo apt-get install -y cuda-toolkit-12-8`; `zsh -ic 'uv venv ar1_venv && source ar1_venv/bin/activate && uv sync --active'`; `python src/alpamayo_r1/test_inference.py` | CUDA Toolkit 12.8 provides `nvcc V12.8.93`; plain `uv sync --active` builds locked `flash-attn==2.8.3` from source; PAI inference from `ar1_venv` succeeds with `minADE: 2.5593724 meters` | Manager should update Root Task roll-up; wheel workaround is historical fallback, not current primary path |

## Baseline Input/Output Contract Draft

### Evidence

- `src/alpamayo_r1/load_physical_aiavdataset.py` defines the public inference sample contract:
  `image_frames`, `camera_indices`, `ego_history_xyz`, `ego_history_rot`, `ego_future_xyz`,
  `ego_future_rot`, `relative_timestamps`, `absolute_timestamps`, `t0_us`, and `clip_id`.
- The default public inference cameras are
  `camera_cross_left_120fov`, `camera_front_wide_120fov`,
  `camera_cross_right_120fov`, and `camera_front_tele_30fov`.
- Camera IDs are sorted by the index mapping
  `cross_left=0`, `front_wide=1`, `cross_right=2`, `front_tele=6`.
- Trajectory history is 16 steps at 10 Hz ending at `t0`; future target is 64 steps at 10 Hz
  after `t0`.
- Image context is 4 frames per camera, sampled at `t0-0.3s`, `t0-0.2s`, `t0-0.1s`, and `t0`.
- Coordinates are transformed into the ego frame at `t0`.
- `src/alpamayo_r1/helper.py` expects flattened image frames shaped `(N, C, H, W)`, inserts
  48 history trajectory placeholder tokens, and asks the model for CoC reasoning followed by the
  future trajectory.
- `src/alpamayo_r1/test_inference.py` builds model inputs with `tokenized_data`,
  `ego_history_xyz`, and `ego_history_rot`, then expects `pred_xyz`, `pred_rot`, and `extra`.
- AlpaSim `driver=alpamayo1` uses the same 4 camera names, context length 4, max batch size 1,
  device `cuda`, and checkpoint `nvidia/Alpamayo-R1-10B`.
- AlpaSim converts model output to `ModelPrediction(trajectory_xy, headings, reasoning_text)`;
  trajectory is `(T, 2)` from `pred_xyz[0, 0, 0, :, :2]`, headings are yaw extracted from
  `pred_rot[0, 0, 0]`, and reasoning comes from `extra["cot"]`.

### Draft Contract For Track B/C

Track B/C dataset adapters should first produce this minimal sample:

- `image_frames`: `uint8` tensor or array convertible to tensor, shape
  `(4 cameras, 4 frames, 3, H, W)`, camera order after sorting `[0, 1, 2, 6]`.
- `camera_indices`: tensor `[0, 1, 2, 6]` for the four public Alpamayo cameras.
- `absolute_timestamps`: shape `(4, 4)`, microsecond timestamps aligned to the selected frames.
- `relative_timestamps`: shape `(4, 4)`, seconds relative to the earliest selected image timestamp.
- `ego_history_xyz`: shape `(1, 1, 16, 3)`, ego-frame coordinates relative to pose at `t0`.
- `ego_history_rot`: shape `(1, 1, 16, 3, 3)`, ego-frame rotations relative to pose at `t0`.
- `ego_future_xyz`: shape `(1, 1, 64, 3)` for open-loop metric ground truth.
- `ego_future_rot`: shape `(1, 1, 64, 3, 3)` for heading/rotation validation.
- `t0_us`: keyframe timestamp in microseconds, with at least 1.6 s history and 6.4 s future.
- Optional for AlpaSim: convert the model output to `(T, 2)` trajectory plus yaw headings and
  optional CoC text.

### Blocker Classification

- HF access: resolved for Track A. "HF access" means both local Hugging Face login and approval for
  gated NVIDIA PAI/NuRec assets. Current environment is logged in as `kimdh1st`; PAI `features.csv`
  downloads; NuRec metadata and the AlpaSim-configured USDZ artifact are accessible.
- Dependency: resolved for the current host. CUDA Toolkit 12.8 provides `nvcc`, and plain README
  `uv sync --active` source-builds locked `flash-attn==2.8.3`. The earlier Dao-AILab wheel remains
  historical fallback evidence.
- GPU memory/model execution: partially verified. Two RTX 4090 GPUs with 23.52 GiB each are
  visible. A naive `.to("cuda")` placement can OOM, and naive two-GPU `device_map=auto` fails
  during sampling because KV cache tensors span `cuda:0` and `cuda:1`. Direct single-GPU placement
  with `device_map={'': 0}` and `max_memory={0: '23GiB'}` succeeds for a synthetic 4-camera
  trajectory sampling smoke.
- Dataset: PAI single-sample path verified by official `test_inference.py`; full public dataset
  sweep remains Track B scope.
- Simulator: blocked at runtime. Docker and Docker Compose are available, AlpaSim wizard config
  check passes, NuRec artifact download works, and containers start. The dry-run is not a valid
  closed-loop smoke because services fail on missing generated gRPC Python modules and sensorsim
  segfaults.

## Validation

| Check | Evidence | Result |
| --- | --- | --- |
| Python/uv | `uv 0.9.2`, Python 3.12.3 via `.venv/bin/python` | Usable with direct `.venv/bin/python`; plain `python` command absent |
| CUDA/GPU | `nvidia-smi`; `.venv/bin/python -c 'import torch ...'` | 2x RTX 4090 visible, Torch CUDA available |
| HF auth | `.venv/bin/hf auth whoami` | Logged in as `kimdh1st` |
| HF PAI data | direct `features.csv` download; official dataset loader | Direct download succeeds; official inference loads the sample |
| HF NuRec data | NuRec repo metadata listing; AlpaSim wizard USDZ download | Accessible for the configured scene artifact |
| Alpamayo inference | `.venv/bin/python src/alpamayo_r1/test_inference.py` | Completes on official PAI sample; CoC text produced; `minADE: 2.5593724 meters` |
| Synthetic Alpamayo model inference | HF cache inspection; dummy 4-camera tensors; direct single-GPU `device_map={'': 0}`; official-like processor path | 20.6 GiB model weights downloaded; processor/tokenizer/model trajectory sampling succeeds with 64-step output tensors and CoC text |
| AlpaSim config | `alpasim_wizard.check_config ... driver=alpamayo1` | Config-level smoke passes; 1 scene selected |
| AlpaSim dry-run | `.venv/bin/alpasim_wizard ... wizard.dry_run=true` | Reaches container start, but services fail with missing `alpasim_grpc.v0.common_pb2`; sensorsim exits 139 |
| FlashAttention | Official Dao-AILab wheel install; CUDA Toolkit 12.8 install; `ar1_venv` README sync; source-built import check | Runtime import succeeds. Previous wheel workaround is superseded by host source build: plain `uv sync --active` now builds locked `flash-attn==2.8.3` successfully with CUDA Toolkit 12.8. |

## Review Note

Track A가 지금 증명한 것은 "공개 Alpamayo 10B 가중치와 PAI 단일 샘플 inference 경로는
현재 머신에서 실행 가능"하다는 점이다. 공식 `test_inference.py`가 dataset/model load,
CoC reasoning 생성, 64-step trajectory 예측, minADE 계산까지 완료했다. 또한 synthetic
processor/model smoke와 `flash-attn` 런타임 import도 확인했다.

반대로 아직 증명하지 못한 것은 "AlpaSim closed-loop rollout이 끝까지 metrics/video를 만든다"이다.
`flash-attn` 공식 설치 재현성 caveat는 2026-06-06 CUDA Toolkit 12.8 host 설치 후 해소되었다.
이제 README 경로의 plain `uv sync --active`가 locked `flash-attn==2.8.3` source build까지
통과한다. AlpaSim은 HF 접근이 아니라 컨테이너 내부 gRPC generated module 누락과 sensorsim
segfault에서 막혔다.

사용자가 다음 단계 전에 설명할 수 있어야 하는 핵심은 다음과 같다.

- 공개 inference는 PAI clip에서 4카메라 x 4프레임과 1.6초 ego history를 읽고,
  CoC reasoning과 6.4초 future trajectory를 생성한다.
- Track B/C adapter의 첫 목표는 모델을 바꾸는 것이 아니라 위 tensor/key contract를 맞추는 것이다.
- AlpaSim smoke는 open-loop 파일 평가가 아니라 scene artifact, renderer/runtime, driver service,
  controller가 맞물리는 closed-loop 계열 검증이다.
- 현재 남은 실패 원인은 HF 접근권이 아니라 AlpaSim 컨테이너 런타임/패키징 문제다.
  `alpasim_grpc.v0.common_pb2`가 컨테이너 안에서 import되지 않아 주요 service가 시작 직후 종료된다.
- HF access는 Hugging Face 로그인과 gated dataset 승인 상태를 뜻한다. 현재 Track A에 필요한
  PAI/NuRec 접근은 `kimdh1st` 계정으로 통과했다.

## Open Issues

- Plan v3 stale evidence: 승인된 Plan 본문에는 과거 `plain uv sync` 실패 caveat가 남아 있어 새 canonical Plan revision 또는 별도 Manager note 필요
- AlpaSim full rollout 미검증: generated gRPC module packaging/import 문제와 sensorsim segfault 조사 필요
- AlpaSim wizard가 내부 컨테이너 실패에도 exit code 0/`Alpasim finished`를 반환하는 상태 해석 필요

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-05-26 18:24:55 KST | created | Track A legacy Plan의 Progress Tracker를 Subtask 실행 문서로 이관 |
| 2026-05-26 18:45:22 KST | status, execution log | Track A 실행 승인 반영 |
| 2026-05-26 18:50:58 KST | status, checklist, execution log, validation, open issues, contract draft, review note | Track A 환경/접근권 실행 결과 및 HF blocker 반영 |
| 2026-05-26 19:03:19 KST | updated_at, checklist, execution log, blocker classification, validation, review note, open issues | synthetic 모델 가중치/추론 blocker 반영 |
| 2026-05-26 19:03:34 KST | updated_at, checklist, execution log, blocker classification, validation, review note, open issues | synthetic Alpamayo 10B inference smoke 성공 반영 |
| 2026-05-27 08:14:41 KST | updated_at, execution log | HF access blocker 재확인 결과 반영 |
| 2026-05-27 08:17:40 KST | updated_at, checklist, execution log, blocker classification, validation, review note | official-like synthetic inference smoke 및 HF access 설명 반영 |
| 2026-05-27 08:49:32 KST | updated_at, environment setup note, execution log | `.venv/bin/hf`와 Track A 가상환경 생성/사용 맥락 명확화 |
| 2026-05-27 09:00:53 KST | updated_at, checklist, FlashAttention dependency note, execution log | `flash-attn` skip 경로를 임시 smoke workaround로 정정하고 `nvcc` 해결 후보 기록 |
| 2026-05-27 09:01:33 KST | updated_at, checklist, environment setup note, execution log | HF 로그인 성공 및 gated dataset 403 상태 반영 |
| 2026-05-27 09:18:15 KST | status, updated_at, checklist, environment setup note, FlashAttention dependency note, execution log, blocker classification, validation, review note, open issues | HF 접근권 정정, 공식 PAI inference 성공, `flash-attn` wheel runtime 해결, AlpaSim runtime blocker 반영 |
| 2026-06-06 19:32:44 KST | status, updated_at, checklist, FlashAttention note, validation, review note, open issues | CUDA Toolkit 12.8 host 설치 후 README `uv sync --active`/`flash-attn` source build/PAI inference 성공 반영 및 Manager review 위해 Task reopen |
| 2026-06-06 20:35:48 KST | status, parent_plan, updated_at, checklist, FlashAttention note, blocker classification, open issues | Manager review로 A0를 done 처리하고 v3 carry-forward 및 AlpaSim A5 이관 반영 |
