---
doc_type: report
status: done
task_id: alpamayo-rnd-a2-pai-dataset-literacy
role: vla_expert
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-06-07 [Task] Track A2 PAI Dataset Literacy and Storage Strategy.md
created_at: 2026-06-07 01:03:01 KST
updated_at: 2026-06-08 10:13:47 KST
---

# Track A2 PAI Dataset Literacy and Storage Strategy

## Document Frame

Purpose:

This report gives the Manager a current evidence basis for Phase A PAI work. It explains which PAI
metadata and per-chunk files matter for Alpamayo A3 inference and A4 visualization, records the
approved local dataset root structure, and keeps A6 lidar/radar add-ons separate from the A3/A4
minimum profile.

Primary reader:

Manager, VLA Expert, and Teacher sessions for Alpamayo R&D v3 Phase A.

Decision question:

Is the local PAI root now sufficient for A3/A4 to start with selective chunk/clip loading, and what
A6 add-on evidence is available without claiming full lidar/radar experiment readiness?

Exclusion scope:

No full PAI download, no inference run, no visualization run, no Root Task update, no
training/SFT/RL decision, and no claim that A6 lidar/radar experiments are fully validated.

## 1. Executive Summary

Current verdict:

PAI is usable for Phase A without downloading the 133 TB dataset. The approved local payload is
now organized as a single reusable PAI dataset root on the NVMe SSD:

```text
/data/datasets/physical_ai_av
```

Current completed state:

- `features.csv`, `clip_index.parquet`, `metadata/feature_presence.parquet`, and
  `metadata/data_collection.parquet` are available in the current HF cache for commit
  `b719eea7f0a63619ef51ec7f54178af0937ef050`.
- The Hub file list exposes 70,775 files and all required metadata paths. The dataset is gated;
  metadata was read only because it was already cached locally.
- PAI has 306,152 clips across 3,146 chunks. Most chunks contain about 100 clips.
- A1/A3/A4 minimum data is four cameras, `egomotion`, `camera_intrinsics`, and
  `sensor_extrinsics`. This supports the A1 official path plus A4 image/trajectory/projection work.
- The approved post-review download includes the A3/A4 minimum profile plus A6-oriented lidar,
  radar, vehicle dimensions, lidar intrinsics, and obstacle/offline support files for 10 selected
  chunks.

Historical first Manager decision:

The original pre-download recommendation was a single-chunk A3/A4 pilot on `chunk 3119`. This
chunk contains the official `test_inference.py` clip
`030c760c-ae38-49aa-9ad8-f5650a545d26`, has all required A3/A4 features, and is estimated at
`6.081 GiB` for four cameras + egomotion + camera intrinsics + sensor extrinsics.

Historical storage-minimal alternative:

`chunk 2558` was identified as a cheaper 10-clip pilot candidate at `0.435 GiB`, but it does not
include the official A0/A1 clip and therefore gives weaker continuity with prior evidence.

Post-approval update:

After Manager/user approval, the local dataset was expanded from the single `chunk 3119` pilot to
a purpose-sampled 10-chunk multisensor payload. It was then merged into the canonical dataset root
instead of keeping purpose-specific subdirectories:

```text
/data/datasets/physical_ai_av
```

Selected chunks:

```text
156 297 727 1843 1864 1875 2129 2281 3119 3135
```

Actual result:

- Actual local size: `271G`.
- Remaining `/data/datasets` free space after root consolidation: about `308G`.
- Local root contains `243` files under canonical PAI top-level categories.
- The full local `clip_index.parquet` remains the 306,152-clip catalog. Passing the selected
  `chunk_ids` to Alpamayo's local interface yields `772` selected clips for iteration.
- Required A3/A4 files had no missing chunk files in validation.
- Official A1 clip `030c760c-ae38-49aa-9ad8-f5650a545d26` is included in `chunk 3119`.
- Representative clips from `chunk 3119`, `chunk 156`, and `chunk 727` loaded through the local
  interface for camera, egomotion, calibration, lidar, and obstacle files.
- Representative radar checks passed for low-radar and high-radar clips. Some radar features are
  clip/config-specific, so per-feature A6 usage still needs clip-level availability checks.

Interpretation:

This update supersedes the earlier "download one chunk first" operational recommendation for the
current machine. The earlier single-chunk and selected-subset directories were staging layouts and
have been removed. A3/A4/A6 should select clips and chunks through metadata, manifests, or
`chunk_ids` against the single root above. The root keeps the full catalog for future selection,
while `get_all_clip_ids()` and `PAIDataset.__len__()` use `chunk_ids` to limit iteration. For A6,
the available lidar/radar files are ready for inventory and targeted probes, but full lidar/radar
experiment readiness remains an A6 task.

## 2. Read-only Checks Performed

Local repository checks:

- Read `AGENTS.md` and followed the VLA R&D document-bus rule: this Expert session writes a
  separate report and does not update the Root Task.
- Read the active v3 Plan, Root Task, A1 Task, A1 Expert report, and A1 Teacher note.
- Inspected `scripts/download_pai.py`, `scripts/curate_pai_samples.py`,
  `src/alpamayo_r1/load_physical_aiavdataset.py`, `src/alpamayo_r1/data/pai_utils.py`, and
  `src/alpamayo_r1/data/pai.py`.
- Inspected installed `physical_ai_av==0.2.0` source from `ar1_venv` to confirm metadata loading,
  chunk-feature download behavior, and streaming/open-file behavior.

Hub and metadata checks:

- Used Hugging Face Hub metadata APIs through `ar1_venv/bin/python`.
- Used `repo_info(..., files_metadata=True)` for file existence, sizes, and component/chunk
  storage estimates.
- Used `try_to_load_from_cache` to verify that the four requested metadata files were already
  cached locally. No new metadata or component file download was needed.
- Read the cached metadata tables with pandas:
  - `features.csv`: `(36, 4)`
  - `clip_index.parquet`: `(306152, 3)`
  - `metadata/feature_presence.parquet`: `(306152, 36)`
  - `metadata/data_collection.parquet`: `(306152, 5)`

Non-blocking failed probes:

- Plain `python` was not present in this shell.
- Plain `python3` did not have `huggingface_hub`.
- `hf_hub_download(..., dry_run=True)` is unsupported by the installed Hugging Face Hub version, so
  no dry-run download proof was recorded. File existence and size were checked through
  `repo_info`/`get_paths_info` instead.

External current source:

- Hugging Face dataset card and file tree for
  `nvidia/PhysicalAI-Autonomous-Vehicles`, checked on 2026-06-07 KST.

## 3. PAI Metadata Files and Meaning

Short metadata index:

| File | Cached size | Meaning for A2 |
| --- | ---: | --- |
| `features.csv` | 7,076 B | Feature catalog: feature name, top directory, chunk path template, zip-internal file templates |
| `clip_index.parquet` | 11,132,300 B | Clip index keyed by `clip_id`; current cached columns are `clip_is_valid`, `chunk`, `split` |
| `metadata/feature_presence.parquet` | 11,209,035 B | Per-clip boolean feature availability for all 36 features |
| `metadata/data_collection.parquet` | 11,339,400 B | Per-clip collection attributes: `country`, `month`, `hour_of_day`, `platform_class`, `radar_config` |

Evidence:

`features.csv` contains 36 features grouped into `labels`, `calibration`, `camera`, `lidar`, and
`radar`. Each row maps a feature to a chunk path template such as
`camera/camera_front_wide_120fov/camera_front_wide_120fov.chunk_{chunk_id:04d}.zip` or
`calibration/camera_intrinsics/camera_intrinsics.chunk_{chunk_id:04d}.parquet`.

`clip_index.parquet` is keyed by `clip_id`. The cached main-branch table has only three columns:
`clip_is_valid`, `chunk`, and `split`. The official A1 clip
`030c760c-ae38-49aa-9ad8-f5650a545d26` is valid, in `chunk 3119`, and in `train`.

`metadata/feature_presence.parquet` has one boolean column per feature. The A3/A4 minimum features
are present for all 306,152 clips:

- `egomotion`
- `camera_intrinsics`
- `sensor_extrinsics`
- `camera_cross_left_120fov`
- `camera_front_wide_120fov`
- `camera_cross_right_120fov`
- `camera_front_tele_30fov`

`metadata/data_collection.parquet` supports safe subset selection by geography, month, hour, sensor
platform, and radar configuration. The current table reports `hyperion_8.1` for 218,588 clips and
`hyperion_8` for 87,564 clips.

Important limit:

The cached `clip_index.parquet` does not contain `event_t0s`. `PAIDataset.__getitem__` defaults to
`use_default_keyframe=False`, which calls `get_clip_key_frame()` and would require `event_t0s`.
For A3/A4 inference using the official loader path, this is not a blocker because
`load_physical_aiavdataset()` has a default `t0_us=5_100_000` and `test_inference.py` passes that
value directly. For SFT/A7, this becomes a separate dataloader configuration issue.

Version note:

The dataset card says version `26.03` renamed/updated `metadata/sensor_presence.parquet` to
`metadata/feature_presence.parquet`, moved `radar_config` into `metadata/data_collection.parquet`,
and added offline-optimized features for most clips. The installed `physical_ai_av` interface
also falls back to the older `sensor_presence.parquet` only for older revisions.

## 4. Component/chunk Structure

PAI stores sensor/label/calibration payloads by feature and chunk. The dataset card states that
features are chunked in groups of up to about 100 clips, while clip-level metadata is separate so
researchers can choose which chunks and sensors to download.

Current cached metadata and Hub file list show:

| Area | Feature count / files | A2 interpretation |
| --- | ---: | --- |
| Metadata | 4 requested files available | Required before any pilot decision |
| Camera | 7 camera features, 3,146 chunk files each | A3/A4 need only 4 front/cross cameras |
| Calibration | 6 calibration features, chunked parquet | A4 projection needs intrinsics/extrinsics |
| Labels | `egomotion`, `egomotion.offline`, `obstacle.offline` | A3/A4 need `egomotion` only |
| Lidar | 1 top 360 feature | A6 add-on, not A3/A4 minimum |
| Radar | up to 19 radar feature/model directories | A6 add-on, availability varies |
| Reasoning | `reasoning/ood_reasoning.parquet` | Optional A3/A4 evaluation context, not required for official input contract |

File-list evidence:

- Total files: 70,775.
- Total chunks in `clip_index`: 3,146, numbered `0` to `3145`.
- Chunk row count summary from `clip_index`: min `10`, median `99`, max `100`.
- Camera payload is by zip chunk. Example: each selected camera feature has
  `camera/<feature>/<feature>.chunk_XXXX.zip`.
- Calibration payload is by parquet chunk.
- `labels/egomotion` is by zip chunk.

Operational implication:

The repository download script does not download individual clips. It builds `allow_patterns` for
metadata plus selected component/subpart files and chunk IDs. Therefore, a "5-10 clip pilot" is
first a metadata curation decision, but the local component download cost is the whole chunk or
chunks containing those clips.

## 5. What A3/A4 Minimally Need

A1 official contract recap:

The A1 official path takes 4 cameras x 4 frames and 16-step ego history, generates CoC text up to
`<|traj_future_start|>`, then samples a 64-waypoint future trajectory as `pred_xyz` plus
`pred_rot`. `ego_future_xyz` is used as ground truth for ADE/minADE.

A3 minimum:

- `clip_index.parquet` and metadata tables to pick clip IDs and chunks.
- Four camera chunk files:
  - `camera_cross_left_120fov`
  - `camera_front_wide_120fov`
  - `camera_cross_right_120fov`
  - `camera_front_tele_30fov`
- `labels/egomotion` for 16 history poses and 64 future ground-truth poses.

A4 minimum:

- Everything in A3.
- `calibration/camera_intrinsics` and `calibration/sensor_extrinsics` for waypoint projection,
  camera frustums, and geometry-aware visual checks.

Not minimum for A3/A4:

- `lidar_top_360fov`
- radar features
- `obstacle.offline`
- offline lidar intrinsics
- all 7 cameras
- full dataset

Reasoning labels:

`reasoning/ood_reasoning.parquet` is small and can be useful for OOD CoC evaluation planning, but
it is not part of the official A1 input/output contract. Treat it as an optional metadata-level
analysis file, not as a blocker for A3/A4.

## 6. Storage Budget Profiles

All storage estimates below are from Hugging Face file metadata, not from payload downloads.
`GiB` means bytes divided by `1024^3`.

### Metadata only

Profile:

Download or use cache for `features.csv`, `clip_index.parquet`,
`metadata/feature_presence.parquet`, and `metadata/data_collection.parquet`.

Estimated storage:

`32.127 MiB`

Use:

Clip/chunk selection, component availability checks, regional/platform filtering, and storage
planning. This profile is already satisfied in the current local cache.

### 1 chunk camera/calibration/egomotion

Profile:

One chunk with four A1 cameras, `labels/egomotion`, `calibration/camera_intrinsics`, and
`calibration/sensor_extrinsics`.

Estimated storage:

| Candidate | Reason | Required-feature estimate |
| --- | --- | ---: |
| `chunk 3119` | Contains official A1 clip | `6.081 GiB` |
| `chunk 2558` | Smallest required-feature chunk; 10 clips | `0.435 GiB` |
| Typical chunk | Median over 3,146 chunks | `5.048 GiB` |
| `chunk 0` | Conventional first chunk | `7.913 GiB` |

Use:

Best first A3/A4 local subset. `chunk 3119` is preferred for continuity with A0/A1.

### 5-10 clip pilot

Profile:

Select 5-10 clip IDs from one approved chunk. The download still uses whole chunk component files.

Recommended pilot:

Use `chunk 3119` and include the official clip plus 5-10 neighboring candidate clips from the same
chunk. The first ten cached metadata candidates in `chunk 3119` are:

```text
ac321da3-3848-4736-a9c2-053be0bea770
ac7ac12e-7371-47ec-987d-61e0b3c7693f
b8fa0288-f799-4443-ba62-4601c45fe133
c23d0ac1-fe93-4f25-bf71-198ccec5c190
cb656c5d-7520-4cc2-9e87-889f061fc6cb
cff33400-2c50-48f2-8e90-7618d32b94fd
d4c978ba-a90b-43b8-af17-39577d694ca3
e89b7fbb-3a92-4b70-a1c1-e4ade18ad19d
eb610823-376f-411c-b8ab-7f0371ea81fb
ee08aa05-d47c-4c0b-9b69-ffd75e1bc7bf
```

Add the official A1 clip explicitly:

```text
030c760c-ae38-49aa-9ad8-f5650a545d26
```

Estimated storage:

Same as `chunk 3119`: `6.081 GiB` for required A3/A4 features.

### 10 chunk pilot

Profile:

Ten chunks with four A1 cameras, `egomotion`, `camera_intrinsics`, and `sensor_extrinsics`.

Estimated storage:

| Choice | Estimate | Interpretation |
| --- | ---: | --- |
| `chunks 0-9` | `77.599 GiB` | Reproducible contiguous range, but not storage-minimal |
| Median x 10 | about `50.48 GiB` | Typical expected cost |
| Ten smallest chunks by required-feature size | `15.209 GiB` | Cheapest by file size, weaker representativeness |

Use:

This should not be the first A3/A4 step. It is appropriate only after the 5-10 clip pilot proves
that local loading, inference, output logging, and visualization all work.

### Optional lidar/radar add-on for A6

Profile:

Add lidar or radar only after A6 asks a concrete 3D/BEV/reconstruction question.

Estimated storage:

| Add-on | Per-chunk estimate | Dataset-level file-list estimate | A2 decision |
| --- | ---: | ---: | --- |
| `lidar_top_360fov` | median `29.885 GiB`; `chunk 3119` `25.479 GiB` | about `92,761 GiB` | A6-only |
| all radar features present in a chunk | median `0.552 GiB`; `chunk 3119` `0.488 GiB` | about `1,270 GiB` | A6-only |

Interpretation:

Lidar dominates storage. Pulling lidar for even one chunk can cost several times the A3/A4 camera
profile. Radar is smaller than lidar, but feature/model availability varies by clip and should not
be bundled into A3/A4 by default.

## 7. Risks and Blockers

Gated dataset access:

The HF page marks the dataset as gated and requires license agreement acceptance. This session
could read cached metadata and Hub file metadata. Any fresh machine or uncached metadata run still
needs authenticated HF access and accepted terms.

Chunk-level granularity:

Clip selection does not imply clip-only local downloads. The official download script selects
whole component chunk files. A 5-10 clip pilot can still cost one full chunk.

Official clip vs storage-minimal clip:

`chunk 3119` preserves A0/A1 continuity but costs `6.081 GiB`. `chunk 2558` is much cheaper
(`0.435 GiB`) but is not the official clip path and has only 10 clips, all Germany / Hyperion 8.1
in the cached metadata sample.

Local `PAIDataset` keyframe behavior:

The cached main `clip_index.parquet` has no `event_t0s`. A7/SFT or local `PAIDataset` use with
`use_default_keyframe=False` may fail unless a curated clip index with keyframes is supplied or
`use_default_keyframe=True` is used. This is not an A3/A4 blocker for the official
`load_physical_aiavdataset()` path.

Storage estimate precision:

The estimates use current Hub file metadata, not filesystem post-download size. Compression,
cache layout, symlink/local-dir behavior, and partial/cached files can change local disk usage.
Use a margin of at least 20 percent for approved downloads.

Separate A6 add-on from A3/A4 minimum:

Lidar/radar were downloaded after explicit user approval to avoid repeated large transfers on the
NVMe SSD. They should still be treated as A6 add-ons, not as A3/A4 minimum data. A3/A4 completion
must not depend on lidar/radar success, and A6 still needs per-feature/per-clip readiness checks
before claiming full lidar/radar experiment support.

## 8. Historical First Pilot Proposal and Current Canonical Root

Current status after approval:

The first pilot subset was downloaded, then expanded by user request into the purpose-sampled
10-chunk multisensor payload documented in the Executive Summary. The final local layout is a
single canonical PAI dataset root:

```text
/data/datasets/physical_ai_av
```

The old purpose-specific staging directories are no longer present. Keep this section as
historical decision context for why `chunk 3119` remains the anchor chunk, not as the current
directory layout.

Historical primary recommendation:

Use `chunk 3119` with four A1 cameras, `labels/egomotion`,
`calibration/camera_intrinsics`, and `calibration/sensor_extrinsics`.

Why:

- It contains the official A1 clip:
  `030c760c-ae38-49aa-9ad8-f5650a545d26`.
- It lets A3 compare local-subset inference against prior official-path evidence.
- It gives A4 calibration for projection and visual sanity checks.
- It keeps storage around `6.081 GiB` plus existing metadata, far below any full-dataset scale.

Historical suggested output directory:

```text
/data/datasets/physical_ai_av/chunk_3119_a3a4_min
```

This single-chunk directory was created during staging but has since been merged into the
canonical root and removed. Fast smoke tests should now be expressed as `chunk_ids=[3119]` or a
small clip manifest against `/data/datasets/physical_ai_av`, not as a separate dataset copy.

A2 completion signal:

A2 is complete when the approved local root supports storage/profile/subset availability:

- local presence of selected metadata and component/chunk files in canonical PAI layout;
- no missing required A3/A4 files for the selected chunks;
- local interface access for representative camera, egomotion, calibration, lidar, obstacle, and
  radar files;
- clear limits on what remains for A3/A4/A6 runtime validation.

A3/A4 next-track validation signal:

A3/A4 still need to prove model and visualization behavior on this selected local data:

- CoC text and `pred_xyz` inference;
- ADE/minADE/runtime/VRAM logging;
- image grid, BEV/history/future/prediction plot, and front-wide projection if calibration works.

## 9. Executed and Reference Commands

The single-chunk commands below were originally proposed before approval. The approved work has
now been executed, consolidated into `/data/datasets/physical_ai_av`, and verified. They remain
here as reproducibility/reference commands; do not run them again unless intentionally rebuilding
or adding to the canonical root.

Metadata refresh only:

```bash
python - <<'PY'
from physical_ai_av import PhysicalAIAVDatasetInterface
dataset = PhysicalAIAVDatasetInterface(confirm_download_threshold_gb=1.0)
print(dataset.features.features_df.shape)
print(dataset.clip_index.shape)
print(dataset.feature_presence.shape)
print(dataset.data_collection.shape)
PY
```

Risk:

About `32.127 MiB` if metadata is not already cached. Requires HF authentication and accepted
dataset terms.

Historical primary A3/A4 local subset download:

```bash
python scripts/download_pai.py \
  --chunk-ids 3119 \
  --camera camera_front_wide_120fov camera_cross_left_120fov camera_cross_right_120fov camera_front_tele_30fov \
  --calibration camera_intrinsics sensor_extrinsics \
  --labels egomotion \
  --output-dir /data/datasets/physical_ai_av
```

Risk:

Estimated `6.081 GiB` plus metadata. It downloads whole chunk component files, not only selected
clips. If this is run after the canonical root exists, it should append missing files into that
root rather than create a purpose-specific dataset copy.

Storage-minimal alternative:

```bash
python scripts/download_pai.py \
  --chunk-ids 2558 \
  --camera camera_front_wide_120fov camera_cross_left_120fov camera_cross_right_120fov camera_front_tele_30fov \
  --calibration camera_intrinsics sensor_extrinsics \
  --labels egomotion \
  --output-dir /data/datasets/physical_ai_av
```

Risk:

Estimated `0.435 GiB`, but weaker continuity with A0/A1 because it does not include the official
clip.

Curate same-chunk pilot clip index after the approved chunk exists:

```bash
python scripts/curate_pai_samples.py \
  --clip-index-path /data/datasets/physical_ai_av/clip_index.parquet \
  --chunk 3119 \
  --num-samples 10 \
  --output-path /data/datasets/physical_ai_av/metadata/clip_index_3119_10clip.parquet
```

Risk:

Small file output only, but the current script samples randomly and does not guarantee inclusion
of the official A1 clip. If Manager requires the official clip in the curated set, create a
manual curated parquet or update the script in a separate approved task.

A6-only lidar add-on for the primary pilot:

```bash
python scripts/download_pai.py \
  --chunk-ids 3119 \
  --lidar lidar_top_360fov \
  --output-dir /data/datasets/physical_ai_av
```

Historical risk:

Estimated `25.479 GiB` for `chunk 3119`. This command was not the final executed A6 add-on path;
the user later approved a broader purpose-sampled multisensor subset.

Executed purpose-sampled multisensor download:

```bash
python scripts/download_pai.py \
  --chunk-ids "156 297 727 1843 1864 1875 2129 2281 3119 3135" \
  --camera camera_front_wide_120fov camera_cross_left_120fov camera_cross_right_120fov camera_front_tele_30fov \
  --calibration camera_intrinsics sensor_extrinsics vehicle_dimensions lidar_intrinsics.offline camera_intrinsics.offline sensor_extrinsics.offline \
  --labels egomotion obstacle.offline egomotion.offline \
  --lidar lidar_top_360fov \
  --radar radar_corner_front_left_srr_0 radar_corner_front_left_srr_3 radar_corner_front_right_srr_0 radar_corner_front_right_srr_3 radar_corner_rear_left_srr_0 radar_corner_rear_left_srr_3 radar_corner_rear_right_srr_0 radar_corner_rear_right_srr_3 radar_front_center_imaging_lrr_1 radar_front_center_mrr_2 radar_front_center_srr_0 radar_rear_left_mrr_2 radar_rear_left_srr_0 radar_rear_right_mrr_2 radar_rear_right_srr_0 radar_side_left_srr_0 radar_side_left_srr_3 radar_side_right_srr_0 radar_side_right_srr_3 \
  --output-dir /data/datasets/physical_ai_av
```

Note:

The download was originally staged under a purpose-specific directory and then consolidated into
the canonical root. Future additions should use the canonical root directly, preserving the
official PAI top-level categories (`camera`, `calibration`, `labels`, `lidar`, `radar`,
`metadata`, `features.csv`, and `clip_index.parquet`).

Executed validation:

```bash
find /data/datasets/physical_ai_av -maxdepth 1 -mindepth 1 -printf '%f\n' | sort
du -sh /data/datasets/physical_ai_av
df -hT /data/datasets/physical_ai_av
```

```text
calibration
camera
clip_index.parquet
features.csv
labels
lidar
metadata
radar
271G    /data/datasets/physical_ai_av
/dev/nvme1n1p3 ext4 1.8T 1.4T 308G 82% /
```

Local interface checks:

- `PhysicalAIAVDatasetLocalInterface(local_dir="/data/datasets/physical_ai_av", chunk_ids=[...])`
  kept `306152` safe-margin-filtered `clip_index` rows and returned `772` selected clips from
  `get_all_clip_ids()`.
- `PAIDataset(local_dir="/data/datasets/physical_ai_av", chunk_ids=[...])` reported length `772`.
- Required A3/A4 files had `missing_required_count 0`.
- For official clip `030c760c-ae38-49aa-9ad8-f5650a545d26`, four camera features loaded as
  `SeekVideoReader`, `egomotion` loaded as `Interpolator`, calibration loaded as pandas objects,
  and lidar/obstacle add-ons loaded as dictionaries through the generic zip reader.
- For the same official low-radar clip, `radar_front_center_srr_0`,
  `radar_corner_front_left_srr_0`, and `radar_side_right_srr_0` loaded as dictionaries with
  `scans`.
- For a `chunk 3135` high-radar clip, `radar_front_center_mrr_2`,
  `radar_front_center_imaging_lrr_1`, `radar_side_left_srr_3`, and `radar_side_right_srr_3`
  loaded as dictionaries with `scans`.
- A6 must still choose radar features per clip/config; some radar files exist for the selected
  chunks but do not contain every clip.

## 10. Teacher Handoff Questions

Use these questions to check whether the user can review A2 before Manager closes A2 and opens
A3/A4/A6 follow-up work:

- Which four metadata files let us choose a PAI subset before downloading sensor payloads?
- Why does `features.csv` matter if `clip_index.parquet` already lists clip IDs?
- Why is a 5-10 clip pilot still priced as one or more chunk downloads?
- Which component files are needed for A1/A3 official inference, and which extra calibration
  files make A4 projection possible?
- Why does `chunk 3119` have stronger continuity with A1 than `chunk 2558`?
- Why is a single canonical PAI root plus `chunk_ids`/manifest selection preferable to
  purpose-specific dataset copies?
- What does `feature_presence.parquet` prove, and what does it not prove?
- Why are lidar and radar classified as A6 add-ons rather than A3/A4 minimum data?
- Which Manager decision has already been resolved by the executed download, and which decisions
  remain for A3/A4/A6?
- If a local `PAIDataset` run fails on `event_t0s`, why is that a dataloader/keyframe issue rather
  than a camera or HF access issue?
- What evidence should A3/A4 produce before treating the selected 10 chunks as an evaluated
  inference/visualization suite rather than only an available local dataset?

## Evidence References

Local files:

- `docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md`
- `docs/2026-05-26 [Task] Alpamayo R&D Root Task.md`
- `docs/2026-06-06 [Report] Track A1 Expert Code Path Analysis.md`
- `docs/2026-06-06 [Note] Track A1 Code Flow Review Guide.md`
- `scripts/download_pai.py`
- `scripts/curate_pai_samples.py`
- `src/alpamayo_r1/load_physical_aiavdataset.py`
- `src/alpamayo_r1/data/pai_utils.py`
- `src/alpamayo_r1/data/pai.py`

External sources:

- Hugging Face dataset card:
  <https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles>
- Hugging Face file tree:
  <https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles/tree/main>
- Physical AI AV developer kit:
  <https://github.com/NVlabs/physical_ai_av>
