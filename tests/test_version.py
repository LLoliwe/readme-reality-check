import io
import re
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from readme_reality.cli import main

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"

class TestVersionFlag(unittest.TestCase):
    def test_version_flag_prints_name_and_version_and_exits_zero(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit) as ctx:
            main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertEqual(out.getvalue().strip(), "readme-reality 0.1.0")

    def test_package_version_matches_pyproject(self):
        import readme_reality
        # Regex, not tomllib: tomllib is 3.11+ and the project supports 3.10.
        text = PYPROJECT.read_text(encoding="utf-8")
        project = re.search(r"^\[project\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
        self.assertIsNotNone(project, "pyproject.toml has no [project] table")
        match = re.search(r'^version\s*=\s*"([^"]+)"', project.group(1), re.M)
        self.assertIsNotNone(match, "no version in [project]")
        self.assertEqual(readme_reality.__version__, match.group(1))

if __name__ == "__main__":
    unittest.main()
