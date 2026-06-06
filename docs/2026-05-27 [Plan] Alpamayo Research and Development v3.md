---
doc_type: plan
status: active
plan_id: alpamayo-rnd
version: 3
canonical: true
created_at: 2026-05-27 12:39:31 KST
approved_at: 2026-06-06 13:51:36 KST
root_plan: docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md
supersedes: docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md
superseded_by:
root_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
revision_type: full_replacement_proposal
revision_reason: Reframe Phase A from a public-reproduction gate into a deep Alpamayo baseline lab before nuScenes/a2z expansion
---

# Alpamayo Research and Development Plan v3

This is the active canonical Plan for Alpamayo R&D. It replaces v2 and makes Phase A a deep
Alpamayo baseline lab before broad nuScenes/a2z expansion.

## Revision Intent

The previous v2 roadmap treated Track A mainly as a public reproduction gate before moving to
nuScenes and self-dataset work. That is too thin for the current goal. The new goal is to make
Phase A a deep Alpamayo baseline learning and experiment phase:

- learn the model, data, inference, visualization, simulation, SFT, and RL paths inside Alpamayo;
- run enough experiments to understand baseline behavior, not just prove that one command runs;
- defer or parallelize nuScenes/a2z work until the Alpamayo baseline is explainable and reviewable;
- avoid downloading the full PAI dataset unless a specific experiment justifies the storage cost.

## North Star

Build a practical VLA research workflow that starts from a well-understood Alpamayo baseline,
then expands to public datasets, self datasets, simulation/replay, learning, and eventually
vehicle shadow-mode. The first success is not a metric number. The first success is that the user
can inspect an Alpamayo sample, explain how images and ego history become CoC reasoning and
future trajectory, visualize the result, and make an informed decision about what to scale.

## Evidence Anchors

- README inference path downloads example data plus 22 GB model weights, and suggests increasing
  `num_traj_samples` for more trajectories and reasoning traces:
  `README.md:71-82`.
- README release surface includes CoC reasoning, VLA architecture, 64-waypoint trajectory
  prediction, SFT code, and RL post-training code; it excludes RL-trained weights, route
  conditioning, and meta-actions/general VQA: `README.md:88-105`.
- The public loader defines 4 cameras, 4 image frames, 16 history steps, 64 future steps, 10 Hz
  sampling, timestamps, and ego-frame transforms: `src/alpamayo_r1/load_physical_aiavdataset.py:27-190`.
- The model flow first fuses history trajectory tokens, runs VLM generation, stops at
  `<traj_future_start>`, then uses the expert/diffusion/action-space path to produce `pred_xyz`
  and `pred_rot`: `src/alpamayo_r1/models/alpamayo_r1.py:124-330`.
- Visualization utilities already support image grids, trajectory plotting, and waypoint
  projection with camera intrinsics/extrinsics: `src/alpamayo_r1/visualization/viz.py`.
- The SFT guide supports chunk/component PAI subsets, explains Stage 1/Stage 2, and states the
  official examples were validated on 8x H100 80 GB: `docs/FINETUNE_SFT.md:1-126`.
- The PAI download script always includes metadata and can restrict chunk ids and components;
  omitting `--chunk-ids` downloads all selected component files: `scripts/download_pai.py:17-159`.
- The RL guide is designed as an end-to-end local verification path but requires at least 5 GPUs
  with 80 GB VRAM for the official local test: `finetune/rl/README.md:28-181`.
- Track A has already verified official PAI single-sample inference, `flash-attn` runtime import,
  and the current AlpaSim runtime blocker in
  `docs/2026-05-26 [Task] Track A Public Alpamayo Reproduction.md`.

## Planning Principles

1. Phase A is a baseline lab, not a gate to rush through.
2. Every experiment must produce a reusable artifact: command, log, data note, visualization,
   diagram, or review note.
3. Storage is planned before download. Full PAI download is prohibited until a manifest-based
   estimate and user approval exist.
4. User understanding is an explicit gate. If the user cannot explain the code path or result,
   the phase is not done.
5. Closed-loop, SFT, RL, and 3D exploration stay inside Alpamayo first. nuScenes/a2z work can run
   in parallel only when it does not starve Phase A learning.

## Execution Operating Model

This Plan is executed through a multi-session, document-bus workflow rather than a single
agent silently spawning hidden workers.

- Manager session: owns the Root Task, Subtask registry, scope control, blocker roll-up, and
  next user decision.
- VLA Expert session: performs code, data, experiment, simulator, SFT, and RL analysis from
  concrete repo/log evidence.
- Teacher session: turns Expert evidence into user-facing review notes, diagrams, questions,
  and concept explanations.
- Reviewer session: optional independent check for important milestones, plan changes, or
  claims that affect later tracks.

Agent sessions communicate through repo documents. The Manager is the only role that should
update the Root Task. Expert and Teacher sessions should write separate reports or notes and
report directly to the user in their own Codex conversations.

## Program Topology

```text
Phase A: Alpamayo Baseline Lab
  A0 Environment and Access Baseline
  A1 Code and Model Flow Study
  A2 PAI Dataset Literacy and Storage Strategy
  A3 Inference Experiment Suite
  A4 Visualization and Demo Lab
  A5 AlpaSim Closed-Loop Baseline
  A6 Scene/3D Reconstruction Exploration
  A7 SFT Micro-Learning Baseline
  A8 RL Pipeline Literacy and Tiny Smoke

Phase B: Public Dataset Mapping
  B1 nuScenes/NAVSIM/Waymo feasibility
  B2 public dataset converter prototype

Phase C: Self Dataset Mapping
  C1 a2z/self data inventory
  C2 self dataset Alpamayo adapter prototype

Phase D/E/F: Replay, adaptation, shadow-mode
  only after Phase A evidence and B/C contract decisions
```

## Track Registry

This table is only an index. Long goals, gates, and deliverables are written below as blocks so
the document stays readable in narrow panes.

| Track | Area | v3 placement | First action |
| --- | --- | --- | --- |
| A0 | Environment/access | carry_forward | Review existing Track A Task |
| A1 | Code/model flow | new_phase_a_track | Create study Subtask |
| A2 | PAI data/storage | new_phase_a_track | Build manifest and subset budget |
| A3 | Inference experiments | new_phase_a_track | Run 5-clip pilot matrix |
| A4 | Visualization/demo | new_phase_a_track | Export first notebook visuals |
| A5 | AlpaSim closed-loop | new_phase_a_track | Diagnose container runtime blocker |
| A6 | 3D/BEV exploration | new_phase_a_track | Inventory geometry assets |
| A7 | SFT micro-learning | new_phase_a_track | Run dataloader sanity |
| A8 | RL literacy/smoke | new_phase_a_track | Run reward/prefetch smoke |
| B | Public dataset mapping | deferred_until_a1_a4 | Start after A1-A4 review |
| C | Self dataset mapping | deferred_until_a1_a4 | Start after A1-A4 review |

## Track Summary Blocks

### A0. Environment and Access Baseline

Question: Can the current machine run the minimum public Alpamayo path?

First gate: Official PAI inference or AlpaSim smoke plus blocker classification.

v3 placement: Carry forward from the existing Track A Task.

### A1. Code and Model Flow Study

Question: Can the user explain the loader, processor, VLM, diffusion, and output path?

First gate: Annotated code-path note plus review questions.

v3 placement: New Phase A track.

### A2. PAI Dataset Literacy and Storage Strategy

Question: What data is needed, how large is it, and how do we stay within storage limits?

First gate: Manifest/component/chunk budget and first curated subset plan.

v3 placement: New Phase A track.

### A3. Inference Experiment Suite

Question: How does baseline behavior vary across clips, seeds, samples, and memory settings?

First gate: 5-20 clip inference table with CoC, minADE, ADE, runtime, and VRAM.

v3 placement: New Phase A track.

### A4. Visualization and Demo Lab

Question: Can we inspect image inputs, ego history, ground truth, predictions, and CoC?

First gate: Exported notebook or script outputs with plots and short interpretation.

v3 placement: New Phase A track.

### A5. AlpaSim Closed-Loop Baseline

Question: Can Alpamayo run in AlpaSim to metrics/video, or what exact runtime blocker remains?

First gate: Fixed smoke or code-path blocker note with container logs.

v3 placement: New Phase A track.

### A6. Scene/3D Reconstruction Exploration

Question: What 3D, BEV, or reconstruction-style views are feasible from PAI/Alpamayo assets?

First gate: Feasibility report plus at least one 3D/BEV/projection demo if possible.

v3 placement: New Phase A track.

### A7. SFT Micro-Learning Baseline

Question: Can we run a small learning sanity check before large SFT?

First gate: Dataloader sanity, tiny overfit, or explicit compute blocker.

v3 placement: New Phase A track.

### A8. RL Pipeline Literacy and Tiny Smoke

Question: Can we understand and minimally validate the RL reward, prefetch, and export path?

First gate: Reward unit smoke, prefetch test, or explicit hardware blocker.

v3 placement: New Phase A track.

### B. Public Dataset Mapping

Question: Which external public datasets can match the Alpamayo contract?

First gate: nuScenes/NAVSIM/Waymo feasibility matrix.

v3 placement: Deferred until A1-A4 are reviewable, or parallel low priority.

### C. Self Dataset Mapping

Question: Can a2z/self data match the Alpamayo contract?

First gate: Inventory and adapter feasibility.

v3 placement: Deferred until A1-A4 are reviewable, or parallel low priority.

## Phase A Detailed Plan

### A0 Environment and Access Baseline

Carry forward existing Track A evidence:

- HF login as `kimdh1st`.
- PAI `features.csv` and official single-sample inference accessible.
- `flash-attn 2.8.3` runtime import works via official wheel.
- Plain `uv sync --active` still fails without host `nvcc` because it builds the locked sdist.
- AlpaSim reaches container start but fails internally on missing `alpasim_grpc.v0.common_pb2`
  and sensorsim exit 139.

Acceptance:

- Existing Task is reviewed by the user.
- Environment setup note is clear enough to reproduce or intentionally skip known blockers.
- Any future task states whether it uses the wheel-based runtime environment or attempts a
  lock-clean `uv sync --active`.

### A1 Code and Model Flow Study

Produce an explainable code-path note for the user:

- `test_inference.py`: fixed clip, loader call, message construction, processor call, model
  sampling, minADE calculation.
- `load_physical_aiavdataset.py`: camera order, timestamps, ego-frame transform, history/future
  tensors, `maybe_stream`.
- `helper.py` and processor path: chat template, image flattening, trajectory placeholder tokens.
- `AlpamayoR1`: VLM rollout, `<traj_future_start>`, expert diffusion sampling, action-to-trajectory.
- metrics: ADE, minADE, corner distance, sample-level outputs.

Deliverables:

- `docs/<date> [Task] Track A1 Alpamayo Code and Model Flow Study.md`
- one diagram showing data flow from PAI clip to `pred_xyz` and CoC text;
- a user review checklist with 8-12 questions.

### A2 PAI Dataset Literacy and Storage Strategy

Before any large download:

- read cached `features.csv`, `clip_index.parquet`, `metadata/feature_presence.parquet`, and
  `metadata/data_collection.parquet`;
- summarize feature groups: camera, calibration, labels, lidar, radar;
- compute chunk/split counts from `clip_index.parquet`;
- create a manifest-size estimator using Hugging Face metadata where feasible;
- define safe download profiles:
  - metadata only;
  - one chunk, four cameras, calibration, egomotion;
  - 10 chunks, four cameras, calibration, egomotion;
  - optional lidar/radar add-on for A6 only;
  - capped plan for the available 50 TB budget.

Rules:

- Do not run `scripts/download_pai.py` without explicit `--chunk-ids`.
- Do not include lidar/radar until the 3D/BEV question is concrete.
- Do not target full PAI unless the user approves a separate storage plan.

Deliverables:

- storage budget table with component/chunk assumptions;
- chosen pilot chunk list and output path;
- decision note explaining why 133 TB is not needed for Phase A.

### A3 Inference Experiment Suite

Run a small but meaningful baseline matrix:

- clips: start with 5, then expand to 20 if runtime and storage are manageable;
- seeds: at least 3 for one clip to show sampling variance;
- `num_traj_samples`: compare 1 vs 2/3 where VRAM permits;
- outputs: CoC text, minADE, ADE, runtime, peak VRAM, failure reason;
- variants:
  - official PAI streaming sample;
  - local PAI subset sample;
  - synthetic image/control sample only as a control, not quality evidence.

Deliverables:

- CSV/Markdown result table;
- short result interpretation: what is stable, what varies, what should not be overclaimed;
- reusable command script if repeated runs become painful.

### A4 Visualization and Demo Lab

Convert "it ran" into inspectable artifacts:

- run or adapt `notebooks/inference.ipynb` and `notebooks/inspect_dataset.ipynb`;
- generate image grids for 4 cameras x 4 frames;
- plot ego history, ground-truth future, predicted future, and per-sample ADE;
- project waypoints onto the front-wide camera when calibration is available;
- save selected artifacts under a non-committed or explicitly documented output directory.

Deliverables:

- a demo notebook or script output;
- 3-5 representative visual examples;
- a short "how to read this plot" note for the user.

### A5 AlpaSim Closed-Loop Baseline

Focus on Alpamayo inside AlpaSim before external datasets:

- inspect why generated `common_pb2` files are absent from the AlpaSim container runtime;
- distinguish local package build issue, proto generation issue, Docker build context issue,
  or import path issue;
- rerun dry-run/full smoke only after the import blocker is understood;
- capture whether wizard exit code 0 is trustworthy when containers fail;
- if fixed, produce rollout directory, metrics, logs, and optional video/reasoning overlay.

Deliverables:

- AlpaSim blocker note or successful smoke report;
- exact container/service logs;
- decision whether AlpaSim can be a Phase D foundation.

### A6 Scene/3D Reconstruction Exploration

This is exploration, not a promise of full 3D reconstruction:

- inventory what PAI provides for camera intrinsics/extrinsics, egomotion, lidar, radar, and
  obstacle labels;
- verify whether multi-camera projection/BEV/ego-trajectory visualization is possible with the
  current four-camera subset;
- if lidar is needed, estimate its incremental chunk storage before download;
- evaluate practical 3D outputs:
  - ego-frame trajectory and camera frustum plot;
  - waypoint projection onto images;
  - simple BEV with ego path and prediction;
  - optional point cloud overlay if lidar subset is approved;
  - full NeRF/Gaussian/reconstruction only after feasibility and storage review.

Deliverables:

- feasibility matrix: available now, needs subset download, not supported by release;
- at least one BEV/projection demo if supported by current data.

### A7 SFT Micro-Learning Baseline

Do not jump to official-scale SFT. The official SFT examples assume 8x H100 80 GB.

Micro-learning sequence:

1. run PAIDataset/local interface sanity on a tiny local subset;
2. verify tokenizer/processor and batch collation;
3. attempt a tiny overfit only if memory fits, otherwise document the exact compute blocker;
4. if possible, run a short Stage 1 or Stage 2 probe with reduced batch/steps;
5. verify checkpoint save/load or explain why not possible on RTX 4090 resources.

Deliverables:

- tiny dataset readiness note;
- training command candidates and expected hardware;
- loss/log screenshot or explicit blocker;
- no claim of real model improvement unless held-out metric supports it.

### A8 RL Pipeline Literacy and Tiny Smoke

RL-trained weights are not released, but code is present. Treat this as literacy and feasibility:

- read Cosmos-RL entrypoint/config path and TOML;
- run available low-risk tests such as `finetune/rl/prefetch/test_prefetch.py`;
- unit-smoke reward functions on toy trajectory tensors;
- inspect checkpoint export script requirements;
- classify official local RL test as hardware-blocked unless 5x 80 GB GPUs are available.

Deliverables:

- RL flow diagram: rollout, reward, policy update, checkpoint export;
- toy reward output table for ADE/comfort;
- hardware gap note and possible future cluster plan.

## Phase B/C Position Under v3

nuScenes and a2z/self data remain important, but they are not the next default step after a
single Track A smoke. They proceed when at least A1-A4 are reviewable, and preferably after A2
defines the Alpamayo contract and storage strategy.

Allowed parallel work:

- schema inventory that does not require large conversion;
- mapping checklist reuse from A1/A2;
- small adapter sketches.

Blocked until Phase A evidence:

- large-scale conversion;
- training on external/self data;
- claims that nuScenes/a2z results are comparable to PAI baseline.

## Data and Storage Policy

Current known constraints:

- full PAI is on the order of 97 TB in the local SFT guide and the user currently references
  a 133 TB total figure for the broader dataset/assets;
- immediately available storage is about 50 TB;
- Track A has so far needed only small streamed PAI blobs and a 1.5 GB NuRec USDZ artifact.

Policy:

- metadata and manifest work first;
- chunk/component subsets second;
- large subset only with a written storage budget;
- no full dataset download in Phase A;
- keep model cache, PAI subset, NuRec artifacts, experiment logs, and generated visual outputs in
  separate directories so cleanup is possible.

## Acceptance Criteria for v3 Phase A

Phase A is complete only when all of these are true:

- A0 environment/access state is reviewed and reproducible enough for the user.
- A1 code/model flow note exists and the user can explain the sample path.
- A2 storage strategy identifies safe PAI subset profiles under the available budget.
- A3 has a 5-20 clip inference result table with CoC/minADE/ADE/runtime/VRAM.
- A4 has visual artifacts that show image context, history/future/prediction, and interpretation.
- A5 either produces a valid AlpaSim smoke or a code-path blocker that is specific enough to fix.
- A6 states what 3D/BEV/reconstruction experiments are feasible from released assets.
- A7 states whether tiny SFT/overfit can run locally, with evidence.
- A8 states whether RL can be smoke-tested locally and which parts are hardware-blocked.
- Root Task and Subtask docs contain review notes that a non-author user can follow.

## User Understanding Gates

Before moving to large public/self dataset work, the user should be able to answer:

- Which tensors are required by Alpamayo inference, and what are their shapes?
- Why are there 4 cameras, 4 image frames, 16 history steps, and 64 future steps?
- Where does CoC text come from, and where does trajectory sampling begin?
- What does minADE prove and not prove?
- Which files are PAI metadata, which are per-chunk camera/calibration/label files?
- Why is a 50 TB storage budget enough for meaningful Phase A but not a reason to download all data?
- What failed in AlpaSim, and why is that not the same as HF access failure?
- What parts of SFT/RL are code-literacy feasible on the current machine, and what needs H100-class compute?

## Initial Execution Order After Approval

1. Convert this review Plan to active canonical v3 and supersede v2 administratively.
2. Create A1/A2 Subtask docs.
3. Run A1 code/model flow study and A2 storage manifest work in parallel if useful.
4. Create a small PAI subset plan and ask for download approval before any large transfer.
5. Run A3/A4 experiments and visualization on streamed and/or approved local subset.
6. Investigate A5 AlpaSim runtime blocker.
7. Decide whether A6, A7, and A8 run on local resources or become explicit hardware-blocked notes.
8. Only then decide how much Track B/C should proceed.

## Risks and Mitigations

- Scope creep: Phase A now contains many learning tracks. Mitigation: each A-track must have a
  small first gate and stop condition.
- Storage overrun: subset downloads can grow fast. Mitigation: manifest estimate and explicit
  `--chunk-ids` are mandatory.
- Compute mismatch: SFT/RL docs target H100-class systems. Mitigation: tiny sanity checks first,
  no quality claims from underpowered runs.
- Visualization drift: pretty plots can hide wrong frames. Mitigation: every visualization must
  cite the tensor/sample fields used.
- AlpaSim ambiguity: wizard may exit 0 despite container failure. Mitigation: container status and
  service logs are part of acceptance.

## Review Questions for the User

- Is the A0-A8 decomposition the right level of granularity, or should any tracks be merged?
- Should A5 AlpaSim be fixed before A3/A4 inference experiments, or can it run after them?
- Where should approved PAI subsets live on disk, given the 50 TB storage plan?
- How many clips should the first inference suite target: 5, 10, or 20?
- Should A6 include lidar/point-cloud work in the first pass, or only camera/calibration/BEV?
- Do we have access to H100-class resources for A7/A8, or should local RTX 4090 checks be the
  boundary for now?

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-05-27 12:39:31 KST | created | Phase A를 빠른 재현 gate에서 Alpamayo baseline lab으로 확장하는 v3 검토안 작성 |
| 2026-06-06 12:25:33 KST | Track Registry, Track Summary Blocks | 긴 설명을 표 밖의 블록 구조로 이동하여 narrow pane 가독성 개선 |
| 2026-06-06 12:25:33 KST | Track Registry, Track Summary Blocks | Plan에서 실행 status를 관리하는 것으로 오해되지 않도록 `Status` 표현을 `v3 placement`로 교체 |
| 2026-06-06 13:51:36 KST | status, canonical, approved_at, opening, Execution Operating Model | 사용자 승인에 따라 v3를 canonical Plan으로 활성화하고 multi-session 운영 모델 반영 |
