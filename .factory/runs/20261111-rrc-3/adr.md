# Factory run 20261111-rrc-3: add --version flag to the CLI

- **Status:** APPROVE: awaiting Lebo's merge
- **Date:** 2026/11/11
- **Decision:** `readme-reality --version` prints `readme-reality 0.1.0` and exits 0. The version lives once, in `readme_reality.__version__`; a test checks it matches `pyproject.toml`.
- **Why:** Ticket LLoliwe/readme-reality-check#3 (factory proof ticket for P90). A CLI without `--version` is harder to support and to pin in CI.
- **How:** Builder (tdd) on `factory/20261111-rrc-3`; argparse `action="version"`. Two review rounds by five reviewers. Round 1: code and evidence asked for changes (test used `tomllib`, Python 3.11+, while the package supports 3.10 and CI runs 3.10). Round 2: builder replaced it with a stdlib regex read of `[project].version`; all five passed. Approver: APPROVE.
- **Who decided:** Lebohang Loliwe (final; merge is his). Run executed by AI agents under his direction via `/factory`. Requires-python left at >=3.10 on purpose: changing it is Lebo's call.
- **Evidence:** Proved: gate-2.log, `python3 -m unittest discover -s tests` 33 tests OK exit 0; `gitleaks git .` no leaks exit 0; `python -m readme_reality --version` and the installed console script print `readme-reality 0.1.0`, exit 0. Assumed: Python 3.10 compatibility (proved by proxy only, tomllib blocked; real proof is the CI 3.10 leg). Not checked: P45 scans (Semgrep, Bandit, pip-audit, osv), ruff and mypy (not installed); left to CI.
- **Dissent:** Reviewer suggestion to bump requires-python to 3.11 not taken (owner decision).
- **Reproduction steps:**
  1. `git fetch origin factory/20261111-rrc-3 && git checkout factory/20261111-rrc-3`
  2. `python3 -m unittest discover -s tests` (expect 33 OK)
  3. `python3 -m readme_reality --version` (expect `readme-reality 0.1.0`)
  4. With the factory skill installed: `python3 .claude/skills/factory/bin/factory_state.py verify 20261111-rrc-3` (expect `verify OK`)
