# Alpamayo 1.5 Migration Manager Request

- Created: 2026-06-08 12:44:06 KST
- Request status: ready for Project Manager review
- Source active plan: `docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md`
- Proposed replacement plan: `docs/2026-06-08 [Plan] Alpamayo 1.5 Migration and R&D Rebaseline.md`
- Supporting analysis: `docs/2026-06-08 [Report] Alpamayo 1.5 Migration Impact Analysis.md`

## 1. Request Summary

Project Manager should review and, if accepted, initiate a controlled rebaseline from Alpamayo 1/R1
to Alpamayo 1.5. The request is not to replace code immediately. The request is to update the
program baseline first, then assign migration work that preserves prior R1 evidence while rerunning
the minimum gates needed for Alpamayo 1.5.

## 2. Why This Request Exists

Alpamayo 1.5 is now public and materially changes the target baseline:

- public model id changes from `nvidia/Alpamayo-R1-10B` to `nvidia/Alpamayo-1.5-10B`;
- model class/package changes from `AlpamayoR1` / `alpamayo_r1` to `Alpamayo1_5` /
  `alpamayo1_5`;
- navigation conditioning, VQA, flexible camera support, and RL-posttrained weights become public
  baseline capabilities;
- SFT/RL recipe ownership moves to `NVlabs/alpamayo-recipes`.

The current v3 Plan and Root Task are still organized around the R1 public reproduction path. If
the project keeps executing A3/A4/B/C under v3 without rebaseline, it will spend effort validating a
baseline that no longer matches the best public release.

## 3. Requested Manager Actions

### Action 1: Review the Proposed v4 Plan

Review:

- `docs/2026-06-08 [Plan] Alpamayo 1.5 Migration and R&D Rebaseline.md`
- `docs/2026-06-08 [Report] Alpamayo 1.5 Migration Impact Analysis.md`

Decision needed:

- approve v4 as the next canonical Plan;
- request revision;
- reject migration and continue v3.

### Action 2: Freeze or Reclassify Active A3 Before More R1 Work

Current A3 is `in_progress` under v3 and has R1 artifacts:

- `docs/2026-06-08 [Task] Track A3 Inference Experiment Suite.md`
- `docs/2026-06-08 [Report] Track A3 Inference Experiment Suite.md`
- `docs/2026-06-08 [Note] Track A3 Inference Review Guide.md`
- `docs/artifacts/a3_inference/`
- `docs/logs/2026-06-08-a3-5clip-pilot.log`
- `docs/logs/2026-06-08-a3-seed-check.log`

Manager should decide whether to:

- close A3 as `done` for R1 historical evidence only;
- mark A3 `superseded` after opening Alpamayo 1.5 A3;
- keep A3 `in_progress` but pause additional R1 expansion.

Recommended Manager decision:

Pause R1 A3 expansion now. Preserve the existing artifacts as historical R1 baseline evidence. Open a
new 1.5 inference rebaseline Subtask after v4 approval.

### Action 3: Update Plan Lineage Only After Approval

If v4 is approved:

- update v3 frontmatter administratively:
  - `canonical: false`
  - `status: superseded`
  - `superseded_by: docs/2026-06-08 [Plan] Alpamayo 1.5 Migration and R&D Rebaseline.md`
- add an Admin Changelog row to v3 explaining the supersession;
- update v4 frontmatter:
  - `status: active`
  - `canonical: true`
  - `approved_at: <approval time KST>`
- update Root Task `parent_plan` and roll-up to v4.

Do not edit the approved body of v3 except administrative metadata and changelog.

### Action 4: Assign Migration Subtasks

Recommended Subtasks:

1. `M1 Codebase Migration Study`
   - compare R1 and 1.5 code surfaces;
   - select repository lineage and source integration strategy;
   - decide whether to keep the current fork/workspace, create a new Alpamayo 1.5 fork/workspace,
     or split R&D documents and 1.5 code across two repos;
   - prepare branch, new fork, or cross-repo migration manifest.

2. `M2 Alpamayo 1.5 Environment Smoke`
   - run `uv sync --active`;
   - run `python src/alpamayo1_5/test_inference.py`;
   - classify blockers.

3. `M3 Alpamayo 1.5 Code Flow Study`
   - redo A1 for 1.5;
   - include navigation, VQA, camera indices, and CFG.

4. `M4 Alpamayo 1.5 Data Contract Extension`
   - check local selected chunks;
   - check navigation sample overlap;
   - decide VQA/LingoQA data needs;
   - classify camera-count data needs.

5. `M5 Alpamayo 1.5 Inference Rebaseline`
   - run small 1.5 pilot;
   - keep standard, navigation, camera-count, and VQA outputs separate.

### Action 5: Hold Downstream Tracks

Do not start or expand the following until M2-M5 have produced reviewable 1.5 evidence:

- A4 visualization beyond schema compatibility checks;
- A5 AlpaSim runtime work beyond 1.5 driver availability reading;
- A6 lidar/radar expansion;
- A7 metrics expansion;
- A8 RL literacy;
- B/C public/self dataset mapping;
- D/E/F simulation, learning, and vehicle-shadow work.

## 4. Proposed Status Reclassification

| Existing work | Current state | Proposed migration interpretation |
| --- | --- | --- |
| A0 Environment/access | done | mostly valid; rerun 1.5 smoke |
| A1 Code/model flow | done | conceptually useful; concrete contract must be redone |
| A2 Dataset/storage | done | mostly valid; add nav/VQA/flexible-camera extension |
| A3 Inference suite | in_progress | pause R1 expansion; rerun 1.5 pilot |
| A4-A8 | mostly not started | hold until 1.5 evidence exists |
| B-F | deferred | keep deferred until v4 rebaseline review |

## 5. Repository Lineage Decision

Manager must decide this before source replacement:

| Option | When to choose | Main risk |
| --- | --- | --- |
| Keep current fork/workspace | Local docs, Root Task, and R1 historical evidence should stay in one repo | Harder future sync with separate `NVlabs/alpamayo1.5` upstream |
| New Alpamayo 1.5 fork/workspace | Clean upstream relation to 1.5 matters more than current code history | Need to port docs/artifacts and preserve task lineage carefully |
| Split docs repo and code repo | Existing repo should remain the R&D document bus while code experiments use clean 1.5 source | Cross-repo paths and evidence can drift |

Recommended PM question:

```text
Should the active codebase remain this existing Alpamayo fork with source replaced on a migration
branch, or should we create a fresh fork/workspace from NVlabs/alpamayo1.5 and port the R&D docs and
selected artifacts? Decide this before any source replacement.
```

Recommended default:

If ongoing upstream sync with `NVlabs/alpamayo1.5` is expected, use a fresh 1.5 fork/workspace and
port the R&D documents through a migration manifest. If this workspace's document lineage is the
primary project asset and upstream sync is secondary, keep this workspace and replace source on a
migration branch.

## 6. Acceptance Criteria for Manager Response

Manager response should clearly state:

- whether v4 is accepted, revised, or rejected;
- what happens to active A3 R1 artifacts;
- whether a new Root Task is needed;
- which repository lineage option is selected;
- which migration Subtask opens first;
- who owns user understanding notes for the 1.5 contract.

## 7. Handoff Instruction for a Manager Session

Use the following instruction if this request is handed to a separate Project Manager session:

```text
You are the Alpamayo R&D Project Manager. Read AGENTS.md, then read:

1. docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
2. docs/2026-05-26 [Task] Alpamayo R&D Root Task.md
3. docs/2026-06-08 [Report] Alpamayo 1.5 Migration Impact Analysis.md
4. docs/2026-06-08 [Plan] Alpamayo 1.5 Migration and R&D Rebaseline.md
5. docs/2026-06-08 [Plan Request] Alpamayo 1.5 Migration Manager Request.md

Your job is not to edit source code first. Decide whether the proposed v4 migration Plan should
become canonical. If approved, update only administrative Plan/Task lineage fields and open the
first migration Subtask. Preserve R1 A0/A1/A2/A3 artifacts as historical evidence unless you
explicitly mark them superseded. Do not mix R1 and 1.5 inference results without model id and model
class fields.

Return:

- PLAN_DECISION: approve / revise / reject
- A3_R1_DECISION: done_historical / superseded / paused / other
- ROOT_TASK_DECISION: update_existing / create_new
- REPO_LINEAGE_DECISION: keep_current_fork / new_1_5_fork / split_docs_and_code
- FIRST_SUBTASK: chosen migration Subtask and owner role
- USER_REVIEW_GATE: what the user must understand before downstream tracks reopen
```
