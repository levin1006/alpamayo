# Repository Guidelines

## Project Structure & Module Organization

Alpamayo is a Python 3.12 project packaged from `src/alpamayo_r1` and `finetune/rl` via Hatchling. Core model, processor, geometry, metrics, data, visualization, and utility code live under `src/alpamayo_r1/`. Supervised fine-tuning code is in `finetune/sft/`, with Hydra configs under `finetune/sft/configs/`. RL post-training code is in `finetune/rl/`, including model wrappers, rewards, prefetching, TOML configs, and Cosmos-RL entry points. Utility scripts live in `scripts/`, documentation in `docs/`, and exploratory examples in `notebooks/`.

## Alpamayo VLA R&D Collaboration Harness

For Alpamayo/VLA research and development, the goal is not for the AI agent to
finish artifacts alone. The goal is for the user to grow into a reviewer and
participant who can explain the relevant implementation, experiment setup, and
result interpretation at a practical engineering level.

- Treat user understanding as a project gate. A plan, implementation, or
  experiment is not complete until the user can review the key logic and give
  informed feedback.
- Before moving past a meaningful planning, coding, experiment, or analysis
  milestone, document the concept, code path, experiment purpose, result
  meaning, limitations, and next decision in terms the user can inspect.
- Track the user's understanding continuously. If the user cannot explain why
  the work matters, what code changed, how the experiment was run, or what the
  result does and does not prove, pause and provide a learning/review note
  before continuing.
- Prefer explainable handoff artifacts over AI-only summaries. Track plans,
  experiment logs, and result reports should include the review questions the
  user should be able to answer.
- Do not let final VLA closed-loop ambitions obscure near-term learning. Each
  track should stay small enough for the user to understand, reproduce, and
  challenge before the roadmap advances.

## Build, Test, and Development Commands

- `uv venv ar1_venv && source ar1_venv/bin/activate`: create and activate the local Python environment.
- `uv sync --active`: install locked runtime dependencies from `pyproject.toml` and `uv.lock`.
- `python src/alpamayo_r1/test_inference.py`: run the example inference path; this may download gated model/data assets.
- `python -m pytest finetune/rl/prefetch/test_prefetch.py -v -x`: run the available RL prefetch tests.
- `pre-commit format`: apply the repository formatting rules before submitting changes.
- `torchrun --nproc_per_node 8 -m finetune.sft.train_hf --config-path pkg://finetune/sft/configs --config-name sft_stage1`: launch SFT stage 1; see `docs/FINETUNE_SFT.md` before changing training defaults.

## Coding Style & Naming Conventions

Follow the conventions of the touched module. Ruff is configured with a 100-character line length. Prefer clear Python names in `snake_case` for functions, variables, and modules; use `PascalCase` for classes. Keep changes focused, avoid commented-out code, and do not add abstraction unless it removes real duplication or complexity.

## Testing Guidelines

Add or update tests when introducing a new component or behavior. Place tests close to the relevant package when practical, following the existing `test_*.py` pattern. Run targeted tests first, then any broader manual validation required by the training or inference path. Because CI is not currently available, include the exact commands and hardware assumptions used for verification in the PR.

## Commit & Pull Request Guidelines

Begin changes from an approved GitHub issue. Commit titles should be imperative and reference the issue in the project format, for example `#73 - Replace assert with ValueError`. Sign commits with `git commit -s`. Keep PRs single-purpose, link the issue, describe testing, note warnings or known issues, and include screenshots or logs when changing notebooks, visualizations, training output, or user-facing docs. Mark unfinished PRs with `[WIP]`.

## Security & Configuration Tips

Model weights, datasets, W&B, and Hugging Face access may require tokens. Pass secrets through environment variables such as `HF_TOKEN`, `HF_HOME`, and `WANDB_API_KEY`; do not commit credentials, local cache paths, downloaded datasets, checkpoints, or generated training logs.
