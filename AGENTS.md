# README Reality Check: agent and engineer instructions

This file applies to this repository unless a deeper `AGENTS.md` imposes stricter scope. It is an onboarding aid for new/existing agents and human software engineers, **not** an authorisation to publish, spend or deploy.

## Identity and status

Public Python 3.10+ offline documentation checker. It flags potentially dangerous snippets but intentionally **never executes** inspected command snippets.

## Operating contract

1. Read this file, project README, actual source, any nested instructions and test/runbook before editing.
2. Keep PRs focused; never self-merge, add telemetry/secrets, run paid services or claim tests/deployments you did not observe.
3. Respect original/licensed assets and all contributors' rights. Work from synthetic examples and never leak customer/private data.
4. Include in every handoff: branch/commit/PR, changed paths, exact test commands and results (or `NOT_RUN`), unverified assumptions and safe next action.

## Project-specific safeguards

1. Read the existing README and rule specifications before changing diagnostics or output formats.
2. Maintain offline/no-network by default; preserve deterministic rule IDs and cautious wording where checks cannot prove safety.
3. Documented tests: `python -m unittest discover -s tests -v`. Capture actual output when claiming success.
4. Do not run commands extracted from untrusted README files as a convenience; work on synthetic controlled fixtures.
