# Build round 2: ticket #3, `--version` flag

Commit: `8c326409f936e34460d173548579431a8e2717df` on `factory/20261111-rrc-3` (on top of round 1 `d0e4c54`). Not pushed.

## Summary
Fixed the round-1 major (code P14, evidence P13; also security/ux notes): `tests/test_version.py` no longer imports `tomllib` (3.11+). It reads `[project].version` from `pyproject.toml` with a stdlib regex scoped to the `[project]` table, so the suite imports on 3.10. `requires-python` unchanged (Lebo's call).

## Files changed
- `tests/test_version.py`: `import tomllib` → `import re`; regex read of `[project]` `version`, with clear assert messages if the table or key is missing.

## Findings
- **Fixed, major (code P14 / evidence P13):** tomllib on 3.10.
- **Fixed, minor (ux P64):** no import-time error on older Pythons; nothing skipped either, the drift check runs everywhere.
- **Addressed, note (ux P63):** console script now exercised via a throwaway venv in /tmp (`pip install -e .`), prints `readme-reality 0.1.0`, exit 0.
- **Partly addressed, minor (code P13):** no 3.10 interpreter exists here (only 3.13; no uv/pyenv; R0, nothing installed). Proxy: ran the full suite with `sys.modules["tomllib"] = None`, which reproduces the 3.10 failure (red) and passes after the fix (green). Real 3.10 proof is the CI matrix on the draft PR. ruff/mypy not installed: not run. ASSUMED, not proved, for 3.10 until CI is green.
- **Deferred to orchestrator, minor (evidence P36) and note (P35):** decider and proved/assumed labels belong in the run ADR; credit line belongs in the PR body. Decider for all choices here: builder, subject to Lebo's final merge.

## Decisions
- **Regex over a guarded `tomllib` + `skipIf`:** keeps the drift check active on 3.10 rather than skipping it there. Alternative: bump `requires-python` to 3.11; rejected as a product decision for Lebo. Trade-off: the regex only handles a plain double-quoted `version = "x"` inside `[project]`; if pyproject goes dynamic, the test fails loudly with "no version in [project]" rather than passing silently.

## Proof
| Command | Exit |
|---|---|
| suite with `sys.modules["tomllib"]=None` (unittest discover -s tests), before fix | 1 (red) |
| same, after fix | 0 (green) |
| `python3 -m unittest discover -s tests -v` (Python 3.13.5) | 0 (33 run, OK) |
| `grep -rn tomllib readme_reality tests` | 0 (only match is the explanatory comment, test_version.py:20; no import) |
| `python3 -m venv /tmp/quest/agent/rrcvenv && pip install -q -e .` | 0 |
| `/tmp/quest/agent/rrcvenv/bin/readme-reality --version` → `readme-reality 0.1.0` | 0 |
| `git commit` | 0 |
| `/tmp/quest/agent/gitleaks git . --no-banner` → no leaks found | 0 |
