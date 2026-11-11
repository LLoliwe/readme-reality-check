# Build round 1: ticket #3, `--version` flag

Commit: `d0e4c543ead4684305ff254b33372ccb2f6f3b97` on `factory/20261111-rrc-3` (base `main` f2ef722). Not pushed.

## Summary
`readme-reality --version` and `python -m readme_reality --version` print `readme-reality 0.1.0` and exit 0. The version lives once, in `readme_reality.__version__`; the CLI imports it. A test pins it to `pyproject.toml`.

## Files changed
- `readme_reality/__init__.py`: add `__version__ = "0.1.0"`, export it.
- `readme_reality/cli.py`: import `__version__`; add argparse `--version` (`action="version"`, `"%(prog)s {__version__}"`).
- `tests/test_version.py` (new): flag through `cli.main()`; `__version__` equals pyproject `[project].version`.

3 files, +29 / -1.

## Decisions
- **argparse `action="version"`**: stdlib, standard behaviour (prints, `SystemExit(0)`). Alternative: a manual flag returning 0 from `main()`; rejected as more code and a non-standard path. Consequence: `main(["--version"])` raises `SystemExit(0)` rather than returning 0; the test asserts that.
- **Version in `__init__.py`, not read from pyproject or `importlib.metadata`**: works uninstalled and from a source checkout with no dependency. The drift risk against pyproject is covered by a test reading pyproject with stdlib `tomllib` (Python 3.11+), an independent source of truth rather than a tautology.
- **`%(prog)s`** reuses the existing `prog="readme-reality"`, so the name is not duplicated.

## Proof
| Command | Exit |
|---|---|
| `python3 -m unittest discover -s tests -v` (red, before fix) | 1 (33 run: FAIL flag test, exit code 2 != 0; ERROR pyproject test, no `__version__`) |
| `python3 -m unittest discover -s tests -v` (green, after fix) | 0 (33 run, OK) |
| `python3 -m readme_reality --version` → `readme-reality 0.1.0` | 0 |
| `git commit` | 0 |
| `/tmp/quest/agent/gitleaks git /tmp/quest/agent/rrc --no-banner` → 2 commits scanned, no leaks found | 0 |

Note: the gitleaks path in the brief (`/tmp/quest/agent/gitleaks/gitleaks`) is not a directory; the binary is `/tmp/quest/agent/gitleaks` (first attempt exit 126).
The installed `readme-reality` console script was not exercised (package not installed in this env); the module entry point and `main()` were.
