---
doc_type: plan
status: review
plan_id: alpamayo-rnd
version: 4
canonical: false
created_at: 2026-06-08 12:44:06 KST
approved_at:
root_plan: docs/2026-05-26 [Plan] Alpamayo Research and Development v2.md
supersedes: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
superseded_by:
root_task: docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
revision_type: rebaseline
revision_reason: Alpamayo 1.5 public release changes the baseline model contract, capabilities, and recipe ownership.
---

# Alpamayo 1.5 Migration and R&D Rebaseline

## Plan State

This is a proposed v4 Plan in `review` state. It is not canonical yet.

Manager must not mark the existing v3 Plan as superseded until the user approves this v4 Plan and
Manager records the administrative lineage update. The v3 Plan body remains the current baseline
until that approval happens.

## Decision

Move the Alpamayo R&D program baseline from Alpamayo 1/R1 to Alpamayo 1.5.

Do this through a staged rebaseline rather than immediate in-place code replacement:

1. preserve R1 evidence as historical baseline;
2. establish a clean 1.5 code/runtime contract;
3. rerun the minimum completed and active Phase A gates under 1.5;
4. only then reopen downstream A4-A8 and B-F decisions.

## Requirements Summary

- Replace the active baseline model target from `nvidia/Alpamayo-R1-10B` / `AlpamayoR1` to
  `nvidia/Alpamayo-1.5-10B` / `Alpamayo1_5`.
- Treat navigation conditioning, VQA, flexible camera support, and RL-posttrained weight status as
  first-class baseline capabilities.
- Keep prior A0/A1/A2/A3 artifacts available as R1 historical evidence.
- Do not mutate approved Plan bodies except administrative frontmatter and changelog entries after
  canonical approval.
- Pause closure of the active A3 R1 inference suite until Manager decides whether to mark it
  `done` as historical R1 evidence, `superseded`, or `invalidated` for the new baseline.
- Use `alpamayo-recipes` as the source of truth for 1.5 SFT/RL recipe planning, not the old
  in-repo `finetune/sft` and `finetune/rl` layout alone.

## Evidence Base

- R1 README says the public v1.0 release does not include RL post-trained weights,
  route/navigation conditioning, or meta-actions/general VQA.
- R1 official inference uses `src/alpamayo_r1/test_inference.py`, `AlpamayoR1`, and
  `nvidia/Alpamayo-R1-10B`.
- Active v3 Plan is `docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md`.
- Root Task marks A0, A1, and A2 done, and A3 in progress.
- A3 Report records `model_id: nvidia/Alpamayo-R1-10B` and `model_class: AlpamayoR1`.
- Alpamayo 1.5 README says 1.5 is RL-posttrained and supports navigation conditioning, general
  VQA, and flexible multi-camera input.
- Alpamayo 1.5 helper/model code exposes `camera_indices`, `nav_text`, `create_vqa_message`,
  `generate_text`, and navigation CFG.
- `alpamayo-recipes` contains `recipes/alpamayo1_5_sft/` and `recipes/alpamayo1_x_rl/`.

## Track Registry

| Track | Area | v4 placement | First action |
| --- | --- | --- | --- |
| M0 | Plan/Task lineage | new_migration_gate | Manager reviews this Plan and request |
| M1 | Codebase migration | new_migration_gate | Compare side-by-side R1/1.5 files before replacement |
| M2 | Environment/access | revalidate_a0 | Run 1.5 environment and official inference smoke |
| M3 | Code/model flow | rerun_a1 | Produce 1.5 code path report and learning note |
| M4 | Data contract | extend_a2 | Check nav/VQA/flexible-camera data requirements |
| M5 | Inference experiments | rebaseline_a3 | Run 1.5 pilot before closing A3 as current baseline |
| M6 | Downstream roadmap | hold | Reopen A4-A8/B-F after M2-M5 review |

## Track Summary Blocks

### M0. Plan and Task Lineage

Role: Manager-owned control gate.

Goal: make the rebaseline explicit before source replacement or runtime experiments.

Actions:

- Review this v4 Plan and the matching Manager request.
- If approved, update v3 administrative frontmatter only: `canonical: false`, `status:
  superseded`, `superseded_by: docs/2026-06-08 [Plan] Alpamayo 1.5 Migration and R&D Rebaseline.md`.
- Decide whether the existing Root Task remains the root task or whether a new migration Root Task is
  needed.
- Mark active A3 as paused or reclassified before launching 1.5 A3 work.

Verification:

- Exactly one canonical Plan exists in the `alpamayo-rnd` lineage.
- Root Task points to the canonical Plan.
- R1 A3 artifacts are not confused with 1.5 baseline artifacts.

### M1. Codebase Migration

Role: implementation planning gate before file replacement.

Goal: decide how to bring `NVlabs/alpamayo1.5` into this workspace.

Preferred approach:

1. Create a branch for migration work.
2. Keep R1 and 1.5 side-by-side during analysis.
3. Compare package names, `pyproject.toml`, source tree, notebooks, helper/model APIs, and README.
4. Decide repository lineage before source replacement.
5. Decide one of:
   - replace the current source tree with 1.5;
   - keep R1 historical files and add 1.5 as a separate package;
   - create a fresh 1.5 workspace and link R&D docs across repos.

Repository lineage options:

1. Keep the current fork/workspace and replace source on a migration branch.
   - Use when preserving local docs, Root Task, untracked A3 evidence, and project history in one
     repository is more important than a clean upstream fork relationship.
   - Requires careful source replacement and explicit upstream remote handling.

2. Create a new fork/workspace from `NVlabs/alpamayo1.5` and port only the R&D documents and
   selected artifacts.
   - Use when the original upstream is a separate repository and future sync with 1.5 matters more
     than preserving the current fork as the active code repository.
   - Requires a migration manifest listing which docs/artifacts move and which remain historical.

3. Keep this repository as the R&D/document bus and use a separate 1.5 code fork for execution.
   - Use when Manager wants zero risk to the existing document lineage while code experiments happen
     in a clean 1.5 fork.
   - Requires cross-repo path discipline in every Task and report.

Recommended default:

Manager should first decide whether future upstream sync with `NVlabs/alpamayo1.5` is important. If
yes, prefer a new 1.5 fork/workspace and port the R&D documents. If not, keep the current workspace
and replace source on a migration branch while preserving R1 evidence in docs. Do not keep both model
packages long-term unless an explicit comparative study needs it.

Verification:

- imports point to `alpamayo1_5`;
- model id is `nvidia/Alpamayo-1.5-10B`;
- official test script path exists;
- notebooks for nav, camera count, and VQA are present or intentionally excluded.

### M2. Environment and Access Revalidation

Role: A0 revalidation.

Goal: prove the current host can run the 1.5 release path.

Actions:

- Create a 1.5 venv, e.g. `uv venv a1_5_venv`.
- Run `uv sync --active`.
- Authenticate to Hugging Face if needed.
- Run `python src/alpamayo1_5/test_inference.py`.
- Record runtime-loaded config, model class, model id, VRAM, and output schema.

Verification:

- `Alpamayo1_5.from_pretrained("nvidia/Alpamayo-1.5-10B")` loads.
- One official PAI clip produces CoC text and 64-step trajectory tensors.
- If the command fails, the blocker is classified as access, dependency, GPU memory, data, or
  source integration.

### M3. 1.5 Code and Model Flow Study

Role: A1 rebaseline.

Goal: make the new 1.5 inference contract explainable before broader experiments.

Questions:

- What changed from `helper.create_message(frames)` to `create_message(frames, camera_indices,
  nav_text, use_nav_prompt)`?
- How are route tokens represented?
- What does `sample_trajectories_from_data_with_vlm_rollout_cfg_nav` do differently from standard
  rollout?
- What does `generate_text` return for VQA?
- How do flexible camera counts appear in the prompt and notebooks?
- Which claims are model-card/README claims, and which are proven by local execution?

Verification:

- A new 1.5 Expert report exists.
- A new Teacher/Evaluator note exists.
- The user can explain standard trajectory inference, navigation conditioning, and VQA boundaries.

### M4. Dataset Contract Extension

Role: A2 extension.

Goal: separate still-valid PAI storage evidence from new 1.5 data requirements.

Actions:

- Check whether local selected chunks support standard 1.5 inference.
- Check overlap between local chunks and 1.5 `nav_demo_samples.json`.
- Decide whether flexible camera experiments require additional rear camera downloads.
- Decide whether VQA smoke is inference-only with PAI images or requires LingoQA assets.
- Check whether PAI reasoning labels are needed for RL planning.

Verification:

- A short extension note classifies current local data as sufficient, partially sufficient, or
  insufficient for each 1.5 capability.
- No large data download is approved without a storage estimate and a named experiment.

### M5. 1.5 Inference Experiment Rebaseline

Role: A3 rebaseline.

Goal: produce a small 1.5 pilot that can replace R1 A3 as the current baseline evidence.

Minimum matrix:

- one official-like standard inference clip;
- five standard inference clips from selected local data, if runtime allows;
- one navigation-conditioned clip;
- one camera-count ablation;
- one VQA smoke.

Metrics and fields:

- model id, model class, commit or source snapshot;
- clip id, chunk id, `t0_us`, camera set;
- seed and `num_traj_samples`;
- CoC text;
- `pred_xyz`, `pred_rot`, ground-truth future when available;
- ADE/minADE for trajectory tasks;
- answer text for VQA;
- runtime and peak VRAM;
- failure reason.

Verification:

- Results are stored under a distinct `a1_5` or `alpamayo1_5` artifact namespace.
- R1 and 1.5 results are never mixed in the same result table without a model-id column.
- Manager can decide whether A4 visualization can start from the 1.5 outputs.

### M6. Downstream Roadmap Hold

Role: sequencing gate.

Goal: prevent downstream work from depending on stale R1 assumptions.

Hold until M2-M5 review:

- A4 visualization beyond minimal schema check;
- A5 AlpaSim driver work beyond reading 1.5 driver availability;
- A6 multisensor/lidar expansion;
- A7 metrics expansion;
- A8 RL pipeline literacy;
- B/C public/self dataset mapping;
- D/E/F simulation, learning, and vehicle-shadow tracks.

## Acceptance Criteria

This v4 rebaseline is ready for canonical approval when:

- Manager confirms this Plan is the intended replacement for v3.
- Existing v3 administrative lineage can be updated without changing its approved body.
- Active A3 R1 evidence is explicitly classified.
- A 1.5 codebase integration strategy is selected.
- M2-M5 have owner sessions and expected report/note artifacts.

The migration execution is complete when:

- codebase baseline is 1.5 or a clearly linked 1.5 workspace exists;
- 1.5 official inference succeeds or has a classified blocker;
- 1.5 A1-style code flow report and learning note exist;
- 1.5 A2 extension note classifies data sufficiency;
- 1.5 A3 pilot exists or has a classified blocker;
- Manager updates Root Task roll-up and opens the next downstream track only from 1.5 evidence.

## Risks and Mitigations

Risk: R1 and 1.5 evidence get mixed.

Mitigation: add model id, model class, and source snapshot to every result table and artifact path.

Risk: in-place replacement breaks current docs or scripts before the new baseline is proven.

Mitigation: branch first, keep R1 evidence in docs, and perform side-by-side comparison before source
replacement.

Risk: VQA/navigation/flexible-camera claims are accepted from README only.

Mitigation: require at least one local smoke per capability before downstream planning treats it as
operational.

Risk: training recipes are assumed to live in the old repo layout.

Mitigation: treat `alpamayo-recipes` as a separate source of truth and assign an explicit recipe
dependency study before SFT/RL execution.

Risk: A0/A1/A2 completed work is thrown away unnecessarily.

Mitigation: reclassify by dependency: A0 mostly valid, A1 conceptually reusable but contract-specific,
A2 mostly valid with extensions, A3 historical R1 evidence until 1.5 pilot exists.

## Verification Steps

Read-only verification before execution:

```bash
git status --short
rg -n "Alpamayo-R1-10B|AlpamayoR1|alpamayo_r1" README.md src finetune docs
rg -n "Alpamayo-1.5-10B|Alpamayo1_5|alpamayo1_5|nav_text|create_vqa_message" /path/to/alpamayo1.5
```

Runtime verification after codebase integration:

```bash
uv venv a1_5_venv
source a1_5_venv/bin/activate
uv sync --active
python src/alpamayo1_5/test_inference.py
```

Capability smoke examples after standard inference:

```bash
# Navigation notebook/script equivalent
# Verify route text changes prompt and output is captured with model id.

# Camera-count notebook/script equivalent
# Verify 1, 2, and 4 camera paths do not collapse output schema.

# VQA notebook/script equivalent
# Verify create_vqa_message -> generate_text returns answer text.
```

## Implementation Review Gate

Before reporting migration execution complete, perform a requirement-to-code-path review:

- baseline model id -> actual load path -> runtime evidence;
- navigation support -> `nav_text` prompt path -> local smoke output;
- VQA support -> question prompt path -> `generate_text` output;
- flexible camera support -> camera-index prompt path -> camera-count smoke output;
- old R1 artifacts -> explicit historical namespace -> Manager roll-up.

If any item lacks an executed path or classified blocker, do not close the migration.

## User Understanding Gate

The user should be able to answer:

- What changed between R1 and 1.5 at the input prompt level?
- Which completed R1 tasks remain useful, and why?
- Why is A3 not complete for the new baseline until a 1.5 pilot exists?
- Which 1.5 capability should drive the next vehicle-oriented experiment?

## Open Manager Decisions

- Should v4 become canonical immediately after user review, or should Manager request an independent
  review first?
- Should the current Root Task be updated in place, or should a new migration Root Task be created?
- Should A3 R1 be marked `done` as historical evidence, `superseded`, or left `in_progress` until
  1.5 A3 starts?
- Should source replacement happen in this existing fork/workspace, in a fresh Alpamayo 1.5 fork, or
  in a separate code fork while this repo remains the R&D document bus?
- Should VQA be part of Phase A baseline, or deferred until navigation/trajectory rebaseline is done?

## Plan Review Gate

Review type: self-review. Independent reviewer unavailable in the current outside-tmux surface.

Verdict: `DONE_WITH_CONCERNS`

Accepted:

- The Plan avoids immediate code replacement and makes Plan/Task lineage the first gate.
- Existing A0/A1/A2/A3 artifacts are reclassified rather than discarded.
- The new baseline capabilities have corresponding verification paths.
- Downstream tracks are held until 1.5 evidence exists.

Concerns for Manager:

- Source integration strategy is intentionally unresolved and must be decided before code edits.
- A3 R1 status requires Manager action because artifacts already exist but are untracked.
- VQA scope may expand data requirements through LingoQA and should not be bundled into trajectory
  rebaseline unless explicitly chosen.

## Admin Changelog

| Time (KST) | Field | Reason |
| --- | --- | --- |
| 2026-06-08 12:44:06 KST | created | Alpamayo 1.5 공개 후 R1 기준 v3 roadmap의 baseline reclassification 및 migration sequencing 초안 작성 |
| 2026-06-08 22:06:13 KST | M1, Open Manager Decisions | 기존 fork 유지와 새 Alpamayo 1.5 fork 전환 사이의 repository lineage 결정 gate 추가 |
