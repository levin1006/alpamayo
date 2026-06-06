---
doc_type: report
status: done
report_id: track-a0-official-environment-reproduction
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-05-26 [Task] Track A Public Alpamayo Reproduction.md
created_at: 2026-06-06 18:08:00 KST
updated_at: 2026-06-06 20:35:48 KST
role: a0_environment_expert
---

# Track A0 Official Environment Reproduction Report

## Executive Summary

A0의 공식 환경 재현성 blocker는 현재 host에서 해결되었다.

최종 결론:

- 공식 README 경로가 성공한다.
- `uv sync --active`가 locked `flash-attn==2.8.3`을 source build한다.
- Dao-AILab prebuilt wheel workaround는 더 이상 현재 host의 기본 경로가 아니다.
- 같은 `ar1_venv`에서 `python src/alpamayo_r1/test_inference.py`가 PAI inference까지 성공한다.
- 남은 A0 관련 blocker는 공식 설치 재현성이 아니라 AlpaSim closed-loop runtime이다.

핵심 성공 evidence:

```text
Built flash-attn==2.8.3
Prepared 1 package without build isolation in 16.08s
Installed 1 package ... flash-attn==2.8.3
```

```text
Chain-of-Causation (per trajectory):
 [['Nudge to the left to increase clearance from the construction cones encroaching into the lane.']]
minADE: 2.5593724 meters
```

검증 로그:

- `docs/logs/2026-06-06-a0-cuda128-readme-uv-sync-active.log`
- `docs/logs/2026-06-06-a0-cuda128-readme-test-inference.log`

## Current Reproduction Path

A0의 현재 기준 경로는 README inference path다.

```bash
uv venv ar1_venv
source ar1_venv/bin/activate
uv sync --active
hf auth login
python src/alpamayo_r1/test_inference.py
```

현재 host에서는 위 경로 중 `uv sync --active`가 `flash-attn==2.8.3` source build까지
통과한다. `hf auth login`은 이미 `kimdh1st` 계정으로 인증된 상태에서 재검증되었다.

RL guide의 2-step path는 보조 기준이다.

```bash
uv sync --active --no-install-package flash-attn
uv sync --active
```

이 경로는 Torch 등 dependency를 먼저 설치한 뒤 `flash-attn`을 build하려는 training-oriented
절차다. 최종적으로는 README path와 동일하게 host CUDA compiler toolchain을 요구한다.

## Final Environment

### System packages

User approval after investigation:

- 승인 시점: 2026-06-06 KST
- 목적: host에서 공식 README/RL guide의 locked `flash-attn` source build 재현성 확보

Installed NVIDIA CUDA APT keyring/repository:

```bash
curl -fsSL -o /tmp/cuda-keyring_1.1-1_all.deb \
  https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i /tmp/cuda-keyring_1.1-1_all.deb
sudo apt-get update
```

Installed CUDA Toolkit 12.8:

```bash
sudo apt-get install -y cuda-toolkit-12-8
```

Key installed packages:

- `cuda-keyring==1.1-1`
- `cuda-toolkit-12-8==12.8.2-1`
- `cuda-compiler-12-8==12.8.2-1`
- `cuda-nvcc-12-8==12.8.93-1`
- `cuda-cudart-dev-12-8==12.8.90-1`
- `cuda-libraries-12-8==12.8.2-1`
- `cuda-libraries-dev-12-8==12.8.2-1`

Installed paths:

```text
/usr/local/cuda -> /etc/alternatives/cuda
/usr/local/cuda-12.8/bin/nvcc
```

Compiler validation:

```text
nvcc: NVIDIA (R) Cuda compiler driver
Cuda compilation tools, release 12.8, V12.8.93
```

GPU/driver validation:

```text
Driver 590.48.01
2x NVIDIA GeForce RTX 4090
24564 MiB per GPU
```

### Shell environment

Added to `/home/user/.zshrc`:

```bash
# CUDA Toolkit 12.8 for Alpamayo flash-attn source builds
export CUDA_HOME="/usr/local/cuda-12.8"
export CUDA_PATH="$CUDA_HOME"
export PATH="$CUDA_HOME/bin:$PATH"
```

Verified with a fresh zsh shell:

```text
/usr/local/cuda-12.8/bin/nvcc
CUDA_HOME=/usr/local/cuda-12.8
CUDA_PATH=/usr/local/cuda-12.8
```

Dynamic linker state:

- CUDA install added CUDA library paths under `/etc/ld.so.conf.d/`.
- `ldconfig` resolves CUDA runtime libraries from `/usr/local/cuda/targets/x86_64-linux/lib`.

## Official Sync Validation

Command:

```bash
zsh -ic 'uv venv ar1_venv && source ar1_venv/bin/activate && uv sync --active'
```

Result:

- `uv venv ar1_venv`: success
- `uv sync --active`: success
- `flash-attn==2.8.3`: source build success
- command exit code: 0

Evidence excerpt:

```text
Built flash-attn==2.8.3
Prepared 1 package without build isolation in 16.08s
Installed 1 package ... flash-attn==2.8.3
```

Import validation from `ar1_venv`:

```text
torch 2.8.0+cu128
torch.version.cuda 12.8
torch.cuda.is_available True
flash_attn 2.8.3
```

Log:

- `docs/logs/2026-06-06-a0-cuda128-readme-uv-sync-active.log`

## Official Inference Validation

Command:

```bash
source ar1_venv/bin/activate
CUDA_VISIBLE_DEVICES=0 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
python src/alpamayo_r1/test_inference.py
```

Result:

- PAI sample load: success
- checkpoint shard load: success
- CoC reasoning generation: success
- minADE calculation: success
- command exit code: 0

Evidence:

```text
Chain-of-Causation (per trajectory):
 [['Nudge to the left to increase clearance from the construction cones encroaching into the lane.']]
minADE: 2.5593724 meters
```

Log:

- `docs/logs/2026-06-06-a0-cuda128-readme-test-inference.log`

## Wheel Workaround Status

The Dao-AILab prebuilt wheel workaround is now historical context only.

Previous workaround:

- skip `flash-attn` during sync;
- install official Dao-AILab prebuilt wheel;
- use `.venv/bin/python` for runtime import and inference.

Current status:

- runtime wheel workaround is no longer required on this host;
- `ar1_venv` built `flash-attn==2.8.3` from source through plain `uv sync --active`;
- future A0/A1-A4 work should prefer the README source-build environment unless a task explicitly
  needs the legacy `.venv` state for comparison.

Do not conflate:

- "wheel runtime works" with "official install reproducibility";
- the first was a temporary smoke workaround;
- the second is now satisfied by CUDA Toolkit 12.8.

## Remaining Blockers

### Resolved

- Host `nvcc` absence: resolved.
- `CUDA_HOME` absence in user shell: resolved.
- `flash-attn==2.8.3` source build failure: resolved.
- README PAI inference from source-build env: resolved.

### Still open

AlpaSim closed-loop smoke remains blocked.

Existing evidence indicates:

- NuRec artifact access/download reached container runtime;
- AlpaSim services then failed internally on missing `alpasim_grpc.v0.common_pb2`;
- sensorsim exited 139;
- wizard returned exit code 0 despite container failures.

This is not an A0 official install blocker anymore. It belongs to the AlpaSim runtime/packaging
follow-up path, likely Track A5.

## Manager Closure Decisions

1. Root Task roll-up

   Completed at `2026-06-06 20:35:48 KST`. The Root Task A0 block, blocker summary, and
   decision log now state that CUDA Toolkit 12.8 resolved the README `uv sync --active`
   / `flash-attn` source-build blocker on the current host.

2. Track A Task lineage

   Completed at `2026-06-06 20:35:48 KST`. The Track A Task now points to canonical v3 and records
   v2 as the origin Plan.

3. Plan v3 stale evidence

   The approved canonical Plan v3 body contains stale A0 evidence. Because approved Plan bodies are
   baseline artifacts, this was not edited. Current A0 state is carried by the Root Task, Track A
   Task, and this report. If the baseline planning statement must change, create a new canonical
   Plan revision.

## Historical Investigation Appendix

This appendix preserves the failed paths that led to the final fix. These are historical evidence,
not the current host state.

### Pre-install host state

Before CUDA Toolkit 12.8 installation:

- `which nvcc`: not found
- `nvcc --version`: command not found
- `CUDA_HOME`: unset
- `CUDA_PATH`: unset
- `/usr/local/cuda*`: absent
- Torch runtime: `2.8.0+cu128`
- `torch.version.cuda`: `12.8`
- `torch.cuda.is_available()`: `True`
- GPU: 2x RTX 4090, driver `590.48.01`
- Ubuntu repo `nvidia-cuda-toolkit` candidate: 12.0 series, not aligned with Torch `cu128`

Interpretation:

GPU runtime worked. The missing component was the host CUDA compiler toolchain required by
`flash-attn` source build.

### README path before Toolkit install

Command:

```bash
uv venv ar1_venv
source ar1_venv/bin/activate
uv sync --active
```

Result before Toolkit install:

- dependency wheels installed;
- `flash-attn==2.8.3` build started;
- build failed because `nvcc` was not found and `CUDA_HOME` was unset.

Failure excerpt:

```text
flash_attn was requested, but nvcc was not found.
OSError: CUDA_HOME environment variable is not set. Please set it to your CUDA install root.
```

### RL guide 2-step before Toolkit install

Command:

```bash
source ar1_venv/bin/activate
uv sync --active --no-install-package flash-attn
uv sync --active
```

Result before Toolkit install:

- first step succeeded;
- second step failed at the same `flash-attn==2.8.3` source-build point.

Interpretation:

The RL guide's two-step path fixed dependency ordering, not the absence of host `nvcc`.

### Python CUDA package attempt

Attempted packages:

```bash
uv pip install --python ar1_venv/bin/python \
  nvidia-cuda-nvcc-cu12==12.8.93 \
  nvidia-cuda-cccl-cu12==12.8.90
```

Result:

- package install succeeded;
- headers, `ptxas`, and `nvvm` files appeared;
- no usable `nvidia/cuda_nvcc/bin/nvcc` executable was provided;
- setting `CUDA_HOME` to package paths still failed.

Failure excerpt:

```text
FileNotFoundError: .../nvidia/cuda_nvcc/bin/nvcc
```

Interpretation:

The Python package path was not a sufficient substitute for host CUDA Toolkit 12.8.

### CUDA 12.8 container comparison

Existing local image:

```bash
nvcr.io/nvidia/nre/nre-ga:26.02
```

Container `nvcc`:

```text
/usr/local/cuda/bin/nvcc
Cuda compilation tools, release 12.8, V12.8.61
```

In a one-off container with `uv` and `git` installed, `uv sync --active` built
`flash-attn==2.8.3` successfully.

Interpretation:

This proved the failure was not a physical GPU limitation or upstream `flash-attn` impossibility.
CUDA 12.8 compiler availability was the decisive missing condition.

### Legacy wheel runtime confirmation

Before host Toolkit installation, the existing `.venv` with Dao-AILab wheel could still run PAI
inference:

```bash
CUDA_VISIBLE_DEVICES=0 \
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
.venv/bin/python src/alpamayo_r1/test_inference.py
```

Result:

```text
Chain-of-Causation (per trajectory):
 [['Nudge to the left to increase clearance from the construction cones encroaching into the lane.']]
minADE: 2.5593724 meters
```

Interpretation:

This confirmed runtime feasibility, but it did not satisfy official install reproducibility.

## External References

- Dao-AILab FlashAttention README: CUDA Toolkit or ROCm Toolkit required, PyTorch 2.2+ required,
  `pip install flash-attn --no-build-isolation`, NVIDIA PyTorch container recommended
  (`https://github.com/Dao-AILab/flash-attention`)
- NVIDIA CUDA 12.8 Linux Installation Guide: CUDA Toolkit package, `cuda-toolkit-12-8`,
  `cuda-compiler-12-8`, and PATH/LD_LIBRARY_PATH setup guidance
  (`https://docs.nvidia.com/cuda/archive/12.8.0/cuda-installation-guide-linux/`)
