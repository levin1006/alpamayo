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

### R&D Report Writing Discipline

Alpamayo R&D documents must be written for a clear review decision, not as a
dump of agent activity.

- Before writing a report or note, state the document purpose, primary reader,
  decision question, and exclusion scope. If those are unclear, narrow the
  document before drafting.
- Treat Track/Expert reports as decision documents. They should answer the
  assigned question with a current conclusion, supporting evidence, reproducible
  commands or paths, remaining blockers, and the next owner decision.
- Do not use the user's required coverage list as the report order. Use it as a
  checklist after deciding the argument structure.
- Keep chronological execution detail in the assigned Task, an appendix, or
  `docs/logs/`. Only include failed attempts in the main report body when they
  change the final conclusion or blocker classification.
- When historical failures and current results coexist, label each historical
  failure with the date, environment, and whether it has since been resolved.
  Resolved failures must not read like current blockers.
- Raw command output belongs in log files unless a short excerpt is necessary to
  justify the conclusion. Reports should summarize evidence and link the logs.
- Plan immutability applies to approved Plan baselines, not to report prose. If a
  report's structure is misleading, rewrite it into a complete decision document
  while preserving underlying evidence in appendices, logs, or Tasks.
- Before marking a report ready, check that a reviewer can answer: what is the
  current state, what evidence proves it, what remains unresolved, who decides
  the next step, and what historical details are no longer current.

### Multi-Session Agent Operating Model

Alpamayo R&D should be run as a multi-session, document-bus workflow when the
task spans planning, experiments, implementation, or user learning. Do not treat
role-specific agents as hidden subagents controlled only by one manager session.
Each role may be a separate Codex conversation with the user when independence is
needed, and cross-agent coordination must happen through repository documents.

- Manager session: owns the canonical Plan linkage, Root Task, Subtask registry,
  blocker roll-up, scope control, and next decision with the user.
- VLA Expert-led track session: owns repo/code/data/experiment investigation,
  reports concrete evidence, commands, logs, metrics, and blocker
  classification, and normally also produces the Teacher/Evaluator note for the
  same track.
- Teacher/Evaluator mode: usually runs inside the Expert-led track session. It
  turns Expert evidence into user-facing learning notes, diagrams, concept
  reviews, limitations, review questions, and pass/partial/fail rubrics.
- Independent Teacher session: optional. Use it only when the user still lacks
  understanding after Expert-led coaching, when the Expert explanation quality
  is insufficient, or when a foundational learning gate needs independent
  pedagogy.
- Reviewer session: optional independent check for important milestones, plan
  changes, high-risk claims, or broad implementation changes.

Default track flow:

1. Manager opens or updates the Subtask and states the decision gate.
2. Expert-led session performs evidence work, answers user questions, updates
   its own report when the explanation reveals gaps, and writes the
   Teacher/Evaluator note.
3. Manager reviews the report, Teacher/Evaluator note, and user understanding
   evidence before changing Root Task status.
4. Reviewer or independent Teacher is added only when the Manager identifies a
   concrete review or learning risk.

Manager is the only role that should update the Root Task. Expert-led sessions
may update their assigned Subtask, Expert report, Teacher/Evaluator note, and
supporting logs. Before an agent starts, it should read the canonical Plan, Root
Task, its assigned Subtask, and this AGENTS.md. If a role needs another role's
result, it should read the corresponding repo document rather than relying on
unstated conversation context.

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
