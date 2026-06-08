#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

cd "$(dirname "$0")/.."

if [[ "$#" -ne 1 ]]; then
  echo "Usage: scripts/run_a4_window_manifest_2gpu.sh <gpu-id: 0|1>" >&2
  exit 2
fi

GPU_ID="$1"
if [[ "$GPU_ID" != "0" && "$GPU_ID" != "1" ]]; then
  echo "Invalid GPU id: $GPU_ID (expected 0 or 1)" >&2
  exit 2
fi

MANIFEST="docs/artifacts/a4_visualization/2026-06-08-summary/a4-target-windows-100ms.jsonl"
MANIFEST_LOCK="docs/artifacts/a4_visualization/2026-06-08-summary/a4-target-windows-100ms.lock"

export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

mkdir -p "$(dirname "$MANIFEST")"
(
  flock 9
  ar1_venv/bin/python scripts/create_a4_window_manifest.py \
    --output-path "$MANIFEST" \
    --stride-us 100000
) 9>"$MANIFEST_LOCK"

if [[ "$GPU_ID" == "0" ]]; then
  CUDA_VISIBLE_DEVICES=0 ar1_venv/bin/python scripts/run_a4_clip_window_worker.py \
    --worker-name gpu0 \
    --clip-ids \
      ac321da3-3848-4736-a9c2-053be0bea770 \
      b8fa0288-f799-4443-ba62-4601c45fe133 \
      cb656c5d-7520-4cc2-9e87-889f061fc6cb
else
  CUDA_VISIBLE_DEVICES=1 ar1_venv/bin/python scripts/run_a4_clip_window_worker.py \
    --worker-name gpu1 \
    --clip-ids \
      ac7ac12e-7371-47ec-987d-61e0b3c7693f \
      c23d0ac1-fe93-4f25-bf71-198ccec5c190
fi
