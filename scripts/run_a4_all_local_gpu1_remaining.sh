#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

cd "$(dirname "$0")/.."

RUN_NAME="2026-06-08-a4-all-local-100ms"
MANIFEST="docs/artifacts/a4_visualization/2026-06-08-summary/a4-all-local-windows-100ms.jsonl"
OUTPUT_ROOT="experiments/a4_visualization/2026-06-08-a4-demo/all-local-100ms"

export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

# The worker reads the canonical manifest and skips clips whose output directory
# already contains complete inference artifacts.
CUDA_VISIBLE_DEVICES=1 ar1_venv/bin/python scripts/run_a4_clip_window_worker.py \
  --worker-name gpu1-resume \
  --manifest-path "$MANIFEST" \
  --output-root "$OUTPUT_ROOT" \
  --run-name "$RUN_NAME" \
  --chunk-ids 156 297 727 1843 1864 1875 2129 2281 3119 3135 \
  --skip-video \
  --continue-on-failure
