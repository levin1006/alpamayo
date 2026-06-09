---
doc_type: report
status: done
topic: alpamayo-1-5-migration-impact
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
created_at: 2026-06-08 12:44:06 KST
updated_at: 2026-06-08 12:44:06 KST
---

# Alpamayo 1.5 Migration Impact Analysis

## Document Frame

Purpose: decide whether the Alpamayo R&D program should rebaseline from Alpamayo 1/R1 to
Alpamayo 1.5, and identify which completed or active work remains valid.

Primary reader: Alpamayo R&D Project Manager and the user reviewing the migration decision.

Decision question: should the active v3 roadmap continue on R1, or should Manager create a new
canonical migration plan that moves the program baseline to Alpamayo 1.5?

Exclusion scope: this report does not edit source code, replace dependencies, run the 1.5 model, or
change existing Plan/Task status. Those actions require Manager acceptance and follow-up tasks.

## Current Conclusion

The program should be rebaselined to Alpamayo 1.5 before opening broader A4-A8, B, C, D, E, or F
work. The existing R1 evidence should not be discarded, but it should be reclassified as historical
baseline evidence. Alpamayo 1.5 changes the public model contract enough that A1 and A3 must be
rerun under a new baseline, while A0 and A2 can mostly carry forward with targeted validation.

The safest operational move is not an immediate in-place source replacement. The next step should be
a Manager-owned rebaseline: approve a v4 canonical Plan, open a migration Root/Subtask path, then
replace code and re-run the minimum evidence gates in order.

## Evidence

### R1 Current Baseline

- `README.md` states Alpamayo 1 released SFT and RL code, but the public v1.0 release does not
  include RL post-trained weights, route/navigation conditioning, or meta-actions/general VQA.
- `src/alpamayo_r1/test_inference.py` loads `nvidia/Alpamayo-R1-10B` through `AlpamayoR1`, builds
  messages from flattened image frames, and passes only `tokenized_data`, `ego_history_xyz`, and
  `ego_history_rot` into the model.
- `src/alpamayo_r1/load_physical_aiavdataset.py` returns camera indices and timestamps, but the
  official R1 test path does not pass those fields through the prompt helper.
- `docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md` is the active canonical Plan.
  It is built around A0-A8 Phase A baseline work before B/C/D/E/F.
- `docs/2026-05-26 [Task] Alpamayo R&D Root Task.md` marks A0, A1, and A2 done, and A3 in progress.
- `docs/2026-06-08 [Report] Track A3 Inference Experiment Suite.md` records `model_id:
  nvidia/Alpamayo-R1-10B` and `model_class: AlpamayoR1`.

### Alpamayo 1.5 Public Surface

- The `NVlabs/alpamayo1.5` README states Alpamayo 1.5 supports RL post-training, navigation
  conditioning, general VQA, and flexible multi-camera input, while Alpamayo 1 does not.
- The 1.5 README lists separate notebooks for standard inference, navigation, camera count, and VQA:
  `notebooks/inference.ipynb`, `inference_nav.ipynb`, `inference_cam_num.ipynb`,
  `inference_vqa.ipynb`.
- `src/alpamayo1_5/helper.py` accepts `camera_indices`, `nav_text`, and `use_nav_prompt`; it inserts
  `<|route_start|>...<|route_end|>` when navigation text is provided.
- `src/alpamayo1_5/helper.py` also defines `create_vqa_message`, which wraps questions in
  `<|question_start|>...<|question_end|>` and expects answer generation.
- `src/alpamayo1_5/models/base_model.py` defines route and question/answer special tokens and
  exposes `generate_text` for text generation.
- `src/alpamayo1_5/models/alpamayo1_5.py` registers model type `alpamayo1_5` and adds
  `sample_trajectories_from_data_with_vlm_rollout_cfg_nav`, which removes the navigation span to
  build unguided cache for navigation classifier-free guidance.
- Hugging Face metadata identifies `nvidia/Alpamayo-1.5-10B` as architecture `alpamayo1_5` and
  includes `base_model:nvidia/Cosmos-Reason2-8B`.
- `alpamayo-recipes` separates post-training workflows from the inference repo. Its README lists
  `recipes/alpamayo1_5_sft/` for Alpamayo 1.5 SFT and `recipes/alpamayo1_x_rl/` for Alpamayo 1 and
  1.5 RL post-training.

## Impact Classification

### A0 Environment and Access Baseline

Classification: mostly valid, needs 1.5 smoke.

R1 evidence proves the host can build the Python 3.12 / CUDA 12.8 / `flash-attn` environment and
run a gated model plus PAI sample. Alpamayo 1.5 uses the same broad runtime class and still requires
24 GB for single-sample inference, but it uses a different package, model id, and richer notebooks.

Needed recheck:

- `uv sync --active` in a 1.5 environment.
- `python src/alpamayo1_5/test_inference.py` with `nvidia/Alpamayo-1.5-10B`.
- optional SDPA fallback check if `flash-attn` build or runtime differs.

### A1 Code and Model Flow Study

Classification: conceptually reusable, contract invalidated for current baseline.

The user's understanding of the R1 path remains useful: PAI loader, image frames, ego history,
trajectory placeholders, CoC, diffusion expert, ADE/minADE. However, A1's concrete code path and
prompt contract are R1-specific. Alpamayo 1.5 adds route text, camera labels, VQA messages, text-only
generation, and navigation CFG. A1 must be reopened or mirrored as an A1.5 migration study.

Needed recheck:

- official 1.5 inference path from PAI clip to CoC and trajectory;
- difference between standard inference and navigation-conditioned inference;
- VQA path boundaries and what `generate_text` proves;
- how camera indices are represented in prompts and what flexible camera support means in practice.

### A2 PAI Dataset Literacy and Storage Strategy

Classification: mostly valid, with new navigation/VQA extensions.

The selected local PAI subset, camera/egomotion/calibration understanding, chunk storage model, and
metadata literacy remain useful. The default 1.5 inference loader still consumes PAI-like camera
frames and ego history. However, 1.5-specific navigation demos reference `nav_demo_samples.json`,
and the recipes introduce LingoQA for VQA SFT plus optional PAI reasoning labels for RL.

Needed recheck:

- whether selected chunks contain clips useful for 1.5 navigation demos;
- whether `notebooks/nav_demo_samples.json` overlaps with local selected chunks;
- whether flexible camera experiments require all seven camera features or can start from the
  existing four-camera subset;
- whether VQA work needs LingoQA data outside PAI.

### A3 Inference Experiment Suite

Classification: active R1 result; should be paused and rebaselined before closure.

A3 already produced untracked artifacts and reports for `nvidia/Alpamayo-R1-10B`. Those results are
valuable as R1 historical baseline, but they do not satisfy an Alpamayo 1.5 baseline. If the project
switches now, A3 should not be closed as the current program inference baseline until a 1.5 pilot is
run.

Needed recheck:

- 5-clip 1.5 pilot on the same or comparable selected subset;
- seed and `num_traj_samples` behavior for 1.5;
- standard vs navigation-conditioned trajectory samples;
- camera count ablation if hardware allows;
- VQA smoke if the user wants VQA as part of Phase A.

### A4-A8 and Tracks B-F

Classification: do not start from v3 assumptions without v4 rebaseline.

These tracks depend on the baseline contract. Since 1.5 changes navigation, VQA, camera-count, and
training recipe surfaces, any downstream dataset mapping, visualization, simulator, learning, or
vehicle-shadow work should wait for the 1.5 A1/A3 rebaseline.

## Migration Options

### Option 1: Continue R1 and Treat 1.5 as Future Track

Not recommended. It preserves short-term continuity but spends more effort on a baseline NVIDIA now
supersedes for improved performance, new features, and continued support.

### Option 2: Immediate In-Place Code Replacement

Not recommended as the first action. It risks mixing R1 evidence, untracked A3 artifacts, and 1.5
source changes without a clean Plan/Task status transition.

### Option 3: Manager-Owned Rebaseline Then Code Replacement

Recommended. Create a v4 Plan in review state, ask Manager to supersede v3 after approval, open a
migration Root/Subtask path, then replace or vendor/sync the 1.5 codebase and rerun A0/A1/A2/A3
minimum gates.

## Recommended Revalidation Matrix

Use the smallest matrix that proves the new baseline contract before expanding:

1. Environment smoke
   - 1.5 `uv sync --active`
   - 1.5 import and model class registration
   - 1.5 official single-sample inference

2. Code contract study
   - standard trajectory path
   - navigation prompt path
   - navigation CFG path
   - VQA `generate_text` path
   - camera-index prompt representation

3. Dataset subset check
   - local selected chunks still usable for standard inference
   - nav demo sample overlap or alternate nav smoke selection
   - camera count requirement from four-camera vs seven-camera local data

4. Pilot inference
   - same official clip where possible
   - 5-clip standard pilot
   - 1 navigation-conditioned clip
   - 1 camera-count ablation
   - 1 VQA smoke

5. Manager review
   - update Root Task roll-up;
   - classify R1 reports as historical baseline;
   - decide whether A4 can start from 1.5 artifacts.

## Unknowns and Limits

- This report did not run `nvidia/Alpamayo-1.5-10B`; runtime memory, cache, and access behavior still
  need direct validation.
- The exact integration strategy is not yet selected: replace the current repo contents, keep R1 and
  1.5 side by side, or make a new branch/worktree. The Plan recommends side-by-side analysis before
  destructive replacement.
- `alpamayo-recipes` currently depends on `NVlabs/alpamayo` in places even for 1.5 SFT. Manager
  should assign a dedicated dependency study before moving training recipes into the main program.

## Review Questions for the User

- Why does A1 need a new pass even though the high-level VLA story is similar?
- Which A2 evidence remains valid after moving from R1 to 1.5?
- Why should A3 be paused rather than closed from the existing R1 pilot?
- Which 1.5 capability matters first for the vehicle R&D direction: navigation, VQA, flexible
  cameras, or RL-posttrained weights?
