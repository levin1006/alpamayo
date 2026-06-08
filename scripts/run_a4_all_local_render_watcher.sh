#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

cd "$(dirname "$0")/.."

CUDA_VISIBLE_DEVICES="" ar1_venv/bin/python scripts/render_a4_completed_clips.py \
  --manifest-path docs/artifacts/a4_visualization/2026-06-08-summary/a4-all-local-windows-100ms.jsonl \
  --output-root experiments/a4_visualization/2026-06-08-a4-demo/all-local-100ms \
  --run-name 2026-06-08-a4-all-local-100ms \
  --fps 10 \
  --poll-sec 60
