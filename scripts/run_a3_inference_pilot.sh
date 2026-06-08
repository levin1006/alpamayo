#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

cd "$(dirname "$0")/.."

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

exec ar1_venv/bin/python scripts/run_a3_inference_pilot.py \
  --pilot-name "${A3_PILOT_NAME:-2026-06-08-pilot-canonical}" \
  --seed-check-name "${A3_SEED_CHECK_NAME:-2026-06-08-seed-check-canonical}" \
  "$@"
