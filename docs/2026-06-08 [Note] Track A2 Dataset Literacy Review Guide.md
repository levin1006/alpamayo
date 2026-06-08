---
doc_type: note
status: done
task_id: alpamayo-rnd-a2-pai-dataset-literacy
role: teacher_evaluator
parent_plan: docs/2026-05-27 [Plan] Alpamayo Research and Development v3.md
parent_task: docs/2026-06-07 [Task] Track A2 PAI Dataset Literacy and Storage Strategy.md
source_report: docs/2026-06-07 [Report] Track A2 PAI Dataset Literacy and Storage Strategy.md
source_note: docs/2026-06-06 [Note] Track A1 Code Flow Review Guide.md
created_at: 2026-06-08 08:32:27 KST
updated_at: 2026-06-08 10:20:24 KST
---

# Track A2 Dataset Literacy Review Guide

## Document Frame

Purpose:

이 문서는 A2 Expert report를 다시 요약하는 문서가 아니라, 사용자가 PAI metadata,
chunk/component 구조, storage budget, A3/A4 minimum profile, A6 add-on을 자기 말로
설명하고 다음 다운로드 판단을 내릴 수 있는지 확인하는 Teacher/Evaluator guide다.

Primary reader:

Alpamayo Phase A를 진행하는 사용자와 Manager. 사용자는 이 문서를 읽고 A2 데이터 구조와
저장소 판단을 설명한다. Manager는 A3/A4로 넘어가기 전에 사용자의 이해도 gate를 확인한다.

Decision question:

사용자가 현재 local PAI root가 A3/A4 시작에는 충분하지만 전체 PAI나 A6 full readiness를
증명하지 않는다는 점을 구분하고, 단일 dataset root와 `chunk_ids`/manifest 기반 선택 로딩의
차이를 설명할 수 있는가? 추가 다운로드가 필요한 경우 chunk/component 단위 비용을 근거로
승인 또는 보류 결정을 내릴 수 있는가?

Exclusion scope:

새 다운로드, 새 실험, 코드 수정, Root Task 수정, A3/A4 실행 계획 확정은 이 문서 범위가
아니다. 이 문서는 기존 A2 Expert evidence를 사용해 학습과 평가 기준만 만든다.

## 1. A2 한 문장 요약

A2는 PAI를 전체 다운로드하지 않고도 metadata로 clip, chunk, feature availability, 수집 조건을
읽어 안전한 component/chunk subset을 고르는 방법을 확인했고, 현재 local data는
`/data/datasets/physical_ai_av` 단일 root 아래 공식 PAI 대분류 구조로 정리되어 있다. 이 root는
전체 catalog를 보존하면서 10 selected chunks, 271G payload, 772 selected clips로 A3/A4를
시작할 수 있게 하지만, 이것이 전체 데이터셋 확보나 A6 full readiness를 뜻하지는 않는다고
결론낸 track이다.

## 2. PAI Metadata 4종

### `features.csv`

역할:

PAI feature catalog다. 어떤 feature가 camera, calibration, labels, lidar, radar 중 어디에
속하는지와, 각 feature가 어떤 chunk file path template으로 저장되는지를 알려준다.

사용자가 설명해야 할 핵심:

`clip_index.parquet`가 clip과 chunk를 알려줘도, 실제로 어떤 component file을 내려받아야 하는지는
`features.csv`를 봐야 한다. 예를 들어 camera feature는 camera zip chunk로, calibration feature는
calibration parquet chunk로 내려받는다.

### `clip_index.parquet`

역할:

Clip ID 중심 index다. A2 Expert report 기준 cached table은 `clip_is_valid`, `chunk`, `split`을
갖고 있으며, clip이 어느 chunk에 들어 있는지 알려준다.

사용자가 설명해야 할 핵심:

Clip pilot을 고르는 첫 단계는 clip ID를 고르는 일이지만, 다운로드 판단은 그 clip들이 속한
chunk와 필요한 component를 기준으로 다시 계산해야 한다.

### `metadata/feature_presence.parquet`

역할:

Clip별 feature availability matrix다. 36개 feature가 각 clip에 있는지 boolean column으로
확인한다.

사용자가 설명해야 할 핵심:

이 파일은 "이 clip에 A3/A4 minimum feature가 있는가"를 판단하게 해준다. 하지만 feature가
있다는 사실만으로 model inference, visualization, lidar/radar 실험이 성공했다는 뜻은 아니다.

### `metadata/data_collection.parquet`

역할:

Clip별 collection attribute를 담는다. A2 Expert report 기준 `country`, `month`, `hour_of_day`,
`platform_class`, `radar_config` 같은 subset selection 조건을 제공한다.

사용자가 설명해야 할 핵심:

이 파일은 storage를 늘리기 전에 pilot의 다양성이나 조건을 조절하는 필터다. 예를 들어 특정
radar configuration이나 platform class가 필요한 A6 질문이 생기면 이 metadata가 clip 후보
선정 근거가 된다.

## 3. Clip과 Chunk의 차이

Clip:

모델 평가나 시각화에서 사용자가 고르는 sample 단위다. A3에서는 clip별로 CoC, `pred_xyz`,
ADE/minADE, runtime, VRAM 같은 결과를 기록한다.

Chunk:

PAI payload가 저장되고 다운로드되는 묶음 단위다. A2 Expert report 기준 PAI는 306,152 clips를
3,146 chunks로 나누며, 대부분 chunk는 약 100 clips를 포함한다.

핵심 구분:

사용자가 "5 clips만 테스트하겠다"고 말할 수는 있지만, local payload download는 보통 그 5 clips가
들어 있는 chunk의 camera/calibration/label component files를 받는 방식이다. 따라서 clip 수와
download size는 1:1로 줄어들지 않는다.

## 4. 왜 5-10 Clip Pilot도 Chunk 단위 비용이 드는가

PAI download script와 dataset layout은 individual clip file을 직접 고르는 구조가 아니라,
metadata와 selected component/subpart, chunk IDs를 조합해 allow pattern을 만든다. Camera payload는
예를 들어 `camera_front_wide_120fov.chunk_3119.zip`처럼 chunk file로 묶여 있다.

따라서 5-10 clip pilot의 비용은 다음처럼 계산해야 한다.

1. Metadata로 clip 후보를 고른다.
2. 각 clip이 속한 chunk를 찾는다.
3. A3/A4 또는 A6에 필요한 component를 정한다.
4. 해당 chunk/component file 전체의 크기를 storage budget으로 잡는다.

예:

`chunk 3119`에서 official A1 clip과 주변 clip 5-10개를 고르면, A3/A4 minimum download 비용은
그 clip들만의 크기가 아니라 `chunk 3119`의 4 cameras, `egomotion`,
`camera_intrinsics`, `sensor_extrinsics` component files 전체 비용이다.

## 5. A3/A4 Minimum Profile

A3/A4 minimum profile은 A1 official path와 A4 projection/visual sanity check를 이어가기 위한
최소 component set이다.

### 4 Cameras

필요한 camera features:

- `camera_cross_left_120fov`
- `camera_front_wide_120fov`
- `camera_cross_right_120fov`
- `camera_front_tele_30fov`

의미:

A1 official loader의 4-camera input과 맞는 image context다. A3 inference와 A4 image grid의
기본 재료다. 전체 7 cameras가 없어도 A3/A4 minimum profile은 성립한다.

### `egomotion`

의미:

16-step ego history와 64-step future ground truth를 만들기 위한 label component다. A3에서는
model input의 history와 ADE/minADE ground truth에 연결되고, A4에서는 ego history/future plot에
연결된다.

### `camera_intrinsics`

의미:

Camera projection에 필요한 internal calibration이다. A4에서 waypoint projection이나 camera-aware
visual check를 하려면 필요하다.

### `sensor_extrinsics`

의미:

Sensor frame과 ego/world frame 사이의 관계를 설명하는 external calibration이다. A4에서 trajectory,
camera, ego frame을 같은 기준으로 해석하는 데 필요하다.

## 6. A6 Add-On

A6 add-on은 A3/A4 minimum profile이 아니다. 현재 local root에 포함되어 있더라도 A6가 full readiness를
얻었다고 쓰면 안 된다. A6는 별도 질문, 별도 clip/feature availability check, 별도 visualization
또는 probe가 필요하다.

### `lidar`

역할:

`lidar_top_360fov`는 point cloud 또는 BEV/3D-style exploration에 필요한 add-on이다.

주의:

Lidar는 storage를 크게 지배한다. A2 Expert report는 lidar가 chunk 단위로 수십 GiB까지 커질 수
있다고 분리했다. 따라서 A3/A4 inference나 camera visualization 때문에 lidar를 필수로 보면 안 된다.

### `radar`

역할:

Radar features는 A6에서 sensor fusion, radar availability, radar-config별 probe를 할 때 의미가
있다.

주의:

Radar는 lidar보다 작을 수 있지만 clip/config별 availability가 달라진다. Selected chunks에 radar
files가 있다는 사실만으로 모든 selected clip의 모든 radar feature가 실험 가능하다고 말하면 안 된다.

### `obstacle/offline files`

역할:

`obstacle.offline`, `egomotion.offline`, offline calibration, offline lidar intrinsics 같은 파일은
A6에서 offline-optimized geometry, obstacle, projection, inventory probe를 할 때 쓰는 add-on이다.

주의:

Obstacle/offline files가 local root에 있다는 것은 A6 inventory를 시작할 수 있다는 뜻이다.
Obstacle-aware 3D experiment, lidar/radar fusion, full reconstruction readiness가 검증됐다는 뜻은
아니다.

## 7. 현재 Local PAI Root의 의미

현재 A2 Expert report가 기록한 local root:

```text
/data/datasets/physical_ai_av
```

현재 의미:

- 공식 PAI top-level 구조인 `camera`, `calibration`, `labels`, `lidar`, `radar`, `metadata`,
  `features.csv`, `clip_index.parquet`가 단일 root 아래에 있다.
- 10 selected chunks의 payload가 local에 있다.
- Actual local size는 271G다.
- Local root에는 243 files가 있다.
- Full `clip_index.parquet` catalog는 306,152 clips를 유지한다.
- Selected `chunk_ids`를 Alpamayo local interface 또는 `PAIDataset`에 넘기면 iteration 대상은
  772 clips로 제한된다.
- A3/A4 required files validation에서 missing required count가 0이었다.
- Official A1 clip은 selected chunks 중 `chunk 3119`에 포함된다.
- Representative camera, egomotion, calibration, lidar, obstacle, radar interface check가
  통과했다.

이 root로 말할 수 있는 것:

- A3/A4를 새 대형 다운로드 없이 시작할 수 있는 local data base가 있다.
- A6 inventory와 targeted probe를 시작할 수 있는 add-on 후보가 있다.
- Full catalog를 유지하므로 future pilot selection과 현재 selected-payload 사용을 분리할 수 있다.
- Single `chunk 3119` smoke보다 더 넓은 10-chunk pilot pool이 있다.

이 root로 말하면 안 되는 것:

- 전체 PAI dataset을 확보했다.
- 133 TB 전체 또는 97 TB scale storage 문제가 해결됐다.
- A6 lidar/radar experiment가 full readiness 상태다.
- 모든 selected clips에서 모든 radar features가 사용 가능하다.
- A3/A4 inference/visualization 성능이 이미 검증됐다.

경로 구조에서 배워야 할 점:

목적별 하위 디렉터리를 여러 개 만들면 같은 PAI dataset 안의 파일이 실험 목적 이름으로 쪼개진다.
앞으로 필요한 데이터를 추가할수록 loader path와 문서가 복잡해지고, 어느 디렉터리가 canonical인지
헷갈릴 수 있다. 반대로 단일 root는 원본 dataset 구조를 유지하고, "무엇을 쓸 것인가"는
`chunk_ids`, curated clip index, manifest, metadata filter로 표현한다.

Loader 선택 방식:

Alpamayo의 `PhysicalAIAVDatasetLocalInterface`는 root의 full `clip_index.parquet`를 보존한다.
그 대신 `get_all_clip_ids()`와 `PAIDataset.__len__()`가 `chunk_ids`를 반영해 iteration 대상을
선택한다. 따라서 "root에 전체 catalog가 있다"와 "이번 run이 772 selected clips만 돈다"는 서로
충돌하지 않는다.

## 8. A2가 증명한 것과 증명하지 않은 것

### 증명한 것

- Metadata 4종으로 clip, chunk, feature availability, collection condition을 읽고 subset 후보를
  고를 수 있다.
- PAI는 clip-level decision과 chunk/component-level download decision을 분리해서 봐야 한다.
- A3/A4 minimum profile은 4 cameras, `egomotion`, `camera_intrinsics`,
  `sensor_extrinsics`로 정의할 수 있다.
- Full PAI download 없이도 A3/A4 시작에 필요한 local root를 구성할 수 있다.
- 단일 local root는 full catalog를 보존하면서 `chunk_ids`/manifest로 run 대상을 선택할 수 있다.
- 현재 10-chunk multisensor payload는 A3/A4 minimum files를 포함하고, A6 inventory용 add-on
  후보도 포함한다.

### 증명하지 않은 것

- A3 model inference가 772 selected clips 또는 selected clip matrix에서 성공한다.
- A4 visualization이 projection, BEV, plot artifact까지 성공한다.
- Lidar/radar/obstacle add-on이 A6의 모든 clip-level experiment에 충분하다.
- CoC quality, driving quality, closed-loop safety, route following, collision/comfort metric이
  검증됐다.
- Full dataset download가 필요 없다는 영구 결론. A2 결론은 Phase A의 현재 질문에 한정된다.
- A7/SFT dataloader issue까지 해결됐다. `event_t0s` 같은 keyframe/config 문제는 별도 track에서
  다시 확인해야 한다.

## 9. A3/A4로 넘어가기 전에 내려야 할 결정

사용자는 A3/A4 착수 전에 다음 결정을 자기 말로 설명할 수 있어야 한다.

1. A3/A4는 단일 local root에서 기본적으로 10 selected chunks를 쓸지, 더 빠른 smoke를 위해
   `chunk_ids=[3119]` 또는 작은 clip manifest를 먼저 쓸지 결정한다.
2. 첫 A3 table의 clip 수를 정한다. 5, 10, 20 중 하나를 고르고, clip 수가 download size가 아니라
   run/analysis workload를 바꾼다는 점을 설명한다.
3. A3 minimum evidence를 정한다. 각 run은 `clip_id`, `t0_us`, seed, `num_traj_samples`, CoC,
   `pred_xyz`, ADE/minADE, runtime, VRAM, failure reason을 남겨야 한다.
4. A4 minimum visual evidence를 정한다. 4-camera image grid, ego history, GT future, predicted
   future, calibration-based projection 여부를 명시한다.
5. A6 add-on을 A3/A4 gate에서 분리한다. Lidar/radar/obstacle files는 A6 inventory 대상으로
   유지하되, A3/A4 success condition에 넣지 않는다.
6. 추가 다운로드를 보류할지 승인할지 결정한다. 현재 A3/A4에는 새 대형 다운로드가 필요 없고,
   A6에서 추가가 필요하면 같은 root에 어떤 component/chunk를 더할지, estimated size와 질문을
   먼저 써야 한다.

## 10. 이해도 테스트

### Short-answer questions

1. PAI metadata 4종의 역할을 각각 한 문장으로 설명하라.

기대 답변:

`features.csv`는 feature catalog와 path template, `clip_index.parquet`는 clip-validity/chunk/split
index, `feature_presence.parquet`는 clip별 feature availability, `data_collection.parquet`는
country/month/hour/platform/radar_config 같은 subset selection 조건을 제공한다.

오답 징후:

네 파일을 모두 "metadata"라고만 말하거나, `features.csv`와 `feature_presence.parquet`의 차이를
구분하지 못한다.

2. Clip과 chunk의 차이는 무엇인가?

기대 답변:

Clip은 평가/시각화 sample 단위이고, chunk는 sensor/calibration/label payload가 묶여 다운로드되는
storage 단위다.

오답 징후:

5 clips를 고르면 5 clips 분량만 정확히 다운로드된다고 말한다.

3. 5-10 clip pilot도 왜 chunk 단위 비용이 드는가?

기대 답변:

PAI payload file이 component별 chunk file로 저장되며, download script가 chunk IDs와 component
allow pattern을 기준으로 받기 때문이다.

오답 징후:

Clip count를 download size의 직접 비례값으로 계산한다.

4. A3/A4 minimum profile은 무엇인가?

기대 답변:

4 cameras, `egomotion`, `camera_intrinsics`, `sensor_extrinsics`다. 4 cameras는
cross-left, front-wide, cross-right, front-tele다.

오답 징후:

Lidar, radar, obstacle/offline files, 전체 7 cameras를 A3/A4 필수라고 말한다.

5. `egomotion`은 A3와 A4에서 각각 왜 필요한가?

기대 답변:

A3에서는 ego history와 future GT/ADE 계산에 필요하고, A4에서는 ego history/future trajectory
visualization에 필요하다.

오답 징후:

`egomotion`을 camera calibration 또는 lidar file로 설명한다.

6. A6 add-on에는 무엇이 포함되고, 왜 A3/A4 minimum과 분리해야 하는가?

기대 답변:

Lidar, radar, obstacle/offline files가 A6 add-on이다. 이들은 3D/BEV/reconstruction 또는 sensor
inventory 질문에 필요하지만 A3/A4의 official camera+egomotion inference/visualization minimum은
아니다.

오답 징후:

A6 add-on이 있으므로 A6가 완료됐다고 말한다.

7. 현재 local root의 path와 selected iteration 범위를 말하라.

기대 답변:

`/data/datasets/physical_ai_av`가 canonical root다. 이 root는 full 306,152-clip catalog를
보존하고, 현재 selected `chunk_ids` 10개를 쓰면 A3/A4 iteration 대상은 772 clips다. Local
payload size는 271G다.

오답 징후:

이 root를 full PAI payload 확보로 설명하거나, full catalog 306,152 clips와 selected iteration
772 clips를 같은 뜻으로 설명한다.

8. A2는 무엇을 증명했고, 무엇을 증명하지 않았는가?

기대 답변:

A2는 metadata 기반 subset selection, chunk/component storage 판단, A3/A4 minimum profile, 현재
local root availability와 selected iteration 가능성을 증명했다. A3/A4 inference/visualization
result, A6 full readiness, closed-loop/driving quality, full dataset readiness는 증명하지 않았다.

오답 징후:

271G root payload가 있으니 A3/A4/A6가 모두 끝났다고 말한다.

### Scenario questions

1. 사용자가 "A3는 clip 5개만 볼 거니까 다운로드도 거의 0에 가깝겠지?"라고 말한다. 어떻게
   정정하겠는가?

기대 답변:

Clip 수는 run workload를 줄이지만, payload download는 clip이 속한 chunk의 selected component
files를 받는다. 따라서 먼저 clip의 chunk를 확인하고, 그 chunk의 4 cameras/egomotion/calibration
component size를 예산으로 잡아야 한다.

2. A3/A4를 시작하려는데 이미 단일 root에 10-chunk 271G payload가 있다. 지금 추가 다운로드를
   승인해야 하는가?

기대 답변:

기본 답은 보류다. 현재 root는 A3/A4 minimum files를 갖고 있으므로 먼저 `chunk_ids` 또는 clip
manifest로 선택한 범위에서 inference와 visualization evidence를 만들어야 한다. 추가 다운로드는
A3/A4 실패 원인이 data 부족으로 분류되거나 A6가 구체적 feature/chunk 질문을 제시할 때 같은
root에 추가하는 방식으로 다시 판단한다.

3. A6에서 radar를 쓰고 싶다. Local root에 radar files가 있으니 곧바로 모든 clip에서 radar
   experiment가 가능하다고 말해도 되는가?

기대 답변:

아니다. Radar availability는 clip/config별로 달라질 수 있다. 먼저 `data_collection.parquet`와
`feature_presence.parquet`, selected chunk files를 함께 보고 clip-level availability를 확인해야
한다.

4. A4 projection이 안 된다면 가장 먼저 어떤 component를 의심해야 하는가?

기대 답변:

`camera_intrinsics`와 `sensor_extrinsics`가 selected clip/chunk에서 올바르게 로드되는지 확인한다.
단, component 존재와 projection code correctness는 별도 문제다.

5. Manager가 "271G root payload가 있으니 full PAI는 필요 없다고 결론내도 되는가?"라고 묻는다.

기대 답변:

Phase A A3/A4 시작에는 full PAI payload가 필요 없다고 말할 수 있다. 하지만 root가 full catalog를
갖고 있다는 점과 full 133 TB payload를 갖고 있다는 점은 다르다. 앞으로의 training, broader
generalization, A6 full-scale question에는 별도 storage plan과 approval이 필요하므로 full PAI가
영구적으로 불필요하다고 결론내면 안 된다.

### Misconception check

1. "Metadata가 있으면 sensor payload도 있는 것이다."

기대 답변:

틀림. Metadata는 선택과 계획을 위한 index/evidence다. Camera/lidar/radar/calibration payload는
별도 component/chunk files다.

2. "Feature presence가 true면 model inference도 통과한 것이다."

기대 답변:

틀림. Feature availability는 data가 있다는 뜻이고, loader/model/visualization runtime 성공은
A3/A4/A6에서 별도로 증명해야 한다.

3. "Lidar/radar가 local root에 있으니 A3/A4 minimum profile도 더 강해졌다."

기대 답변:

틀림. A3/A4 minimum은 그대로 4 cameras, `egomotion`, `camera_intrinsics`,
`sensor_extrinsics`다. Lidar/radar는 A6 add-on이다.

4. "10 chunks, 772 selected clips가 있으니 전체 데이터셋 대표성이 보장된다."

기대 답변:

틀림. 10 selected chunks는 Phase A pilot pool이다. 전체 PAI distribution이나 full generalization을
대표한다고 말하려면 별도 sampling 설계와 평가가 필요하다.

5. "단일 root에 full `clip_index.parquet`가 있으니 payload도 full PAI다."

기대 답변:

틀림. Full catalog metadata를 보존하는 것과 sensor payload 전체를 보유하는 것은 다르다. 현재
root는 selected component/chunk payload만 갖고 있으며, run 대상은 `chunk_ids`나 manifest로
선택한다.

## 11. Pass / Partial / Fail Rubric

Pass:

Metadata 4종, clip/chunk 차이, chunk-level download cost, A3/A4 minimum, A6 add-on,
local root의 의미와 한계를 자기 말로 설명한다. 특히 full catalog 보존과 selected iteration의
차이를 구분한다. 추가 다운로드 승인/보류 판단도 근거와 함께 말한다.

Partial:

큰 흐름은 이해하지만 metadata 파일 역할, clip vs chunk, A3/A4 minimum과 A6 add-on,
271G root payload의 한계, full catalog와 selected iteration의 차이 중 하나 이상을 혼동한다.

Fail:

271G root payload를 full PAI나 A6 full readiness로 보거나, clip 수를 download size와 직접
동일시한다. 또는 lidar/radar/obstacle files를 A3/A4 필수로 설명한다.

Pass에 필요한 최소 답변:

- `features.csv`와 `feature_presence.parquet`의 차이.
- `clip_index.parquet`가 clip-to-chunk 판단의 기준이라는 점.
- `data_collection.parquet`가 subset diversity/config filtering에 쓰인다는 점.
- 5-10 clip pilot도 chunk/component file 단위 비용을 가진다는 점.
- A3/A4 minimum profile이 4 cameras, `egomotion`, `camera_intrinsics`,
  `sensor_extrinsics`라는 점.
- A6 add-on은 lidar, radar, obstacle/offline files이며 A3/A4 success gate가 아니라는 점.
- 현재 local root는 `/data/datasets/physical_ai_av`, 10 selected chunks, 271G payload,
  306,152-clip catalog, 772 selected iteration clips이며 full dataset payload나 A6 full
  readiness가 아니라는 점.
- A3/A4로 넘어가기 전에는 새 다운로드보다 existing root 기반 inference/visual evidence가 먼저라는
  점.

## 12. Manager Gate Checklist

사용자가 다음 질문에 답하면 A3/A4 착수 gate를 통과한 것으로 볼 수 있다.

- "A3/A4 minimum profile을 component 이름으로 말해보라."
- "5 clips만 고르면 왜 download size가 5 clips 크기로 줄지 않는가?"
- "왜 `/data/datasets/physical_ai_av` 아래 단일 root로 유지하고 `chunk_ids`나 manifest로 선택하는가?"
- "현재 271G root payload로 할 수 있는 일과 하면 안 되는 주장을 각각 말해보라."
- "A6 add-on이 local에 있다는 사실과 A6 full readiness는 어떻게 다른가?"
- "추가 다운로드를 지금 승인할지 보류할지, 그 이유를 말해보라."

통과 기준:

사용자가 추가 다운로드를 보류하고 현재 단일 root에서 `chunk_ids`/manifest로 A3/A4 evidence를
먼저 만들자는 판단을 근거와 함께 말할 수 있으면 pass다. 단, 특정 A6 질문을 새로 연다면 해당
질문, required feature, chunk IDs, estimated size, 실패 시 cleanup/rollback 기준을 먼저 요구해야
한다.
