import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from readme_reality.checker import check_file, scan_paths
from readme_reality.cli import main, sarif

class TestReadmeReality(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "README.md").write_text("# Getting started\n", encoding="utf-8")

    def put(self, name, text):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def codes(self, content, snippets=True):
        doc = self.put("README.md", content)
        return [x.code for x in check_file(self.root, doc, snippets)]

    def test_valid_local_link(self):
        self.put("docs/start.md", "# Hello")
        self.assertEqual(self.codes("[go](docs/start.md)"), [])

    def test_broken_local_link(self):
        self.assertIn("RRC101", self.codes("[go](docs/missing.md)"))

    def test_remote_links_skipped(self):
        self.assertEqual(self.codes("[go](https://example.com/help)"), [])

    def test_valid_anchor(self):
        self.assertEqual(self.codes("# My Title\n[go](#my-title)"), [])

    def test_missing_anchor(self):
        self.assertIn("RRC106", self.codes("# My Title\n[go](#nope)"))

    def test_anchor_in_another_file(self):
        self.put("docs/start.md", "# Hello World")
        self.assertEqual(self.codes("[go](docs/start.md#hello-world)"), [])

    def test_duplicate_heading_anchor(self):
        self.assertEqual(self.codes("# Hi\n# Hi\n[go](#hi-1)"), [])

    def test_image_path_checked(self):
        self.assertIn("RRC101", self.codes("![image](assets/nope.png)"))

    def test_fenced_markdown_ignored(self):
        self.assertEqual(self.codes("~~~md\n[no](missing.md)\n~~~"), [])

    def test_existing_python_file(self):
        self.put("demo.py", "print('ok')")
        self.assertEqual(self.codes("~~~bash\npython demo.py\n~~~"), [])

    def test_missing_python_file(self):
        self.assertIn("RRC103", self.codes("~~~bash\npython missing.py\n~~~"))

    def test_missing_directory(self):
        self.assertIn("RRC102", self.codes("~~~sh\ncd nowhere\n~~~"))

    def test_npm_missing_script(self):
        self.put("package.json", json.dumps({"scripts":{"test":"node test.js"}}))
        self.assertIn("RRC104", self.codes("~~~bash\nnpm run build\n~~~"))

    def test_npm_existing_script(self):
        self.put("package.json", json.dumps({"scripts":{"test":"node test.js"}}))
        self.assertEqual(self.codes("~~~bash\nnpm run test\n~~~"), [])

    def test_remote_shell_warning(self):
        self.assertIn("RRC201", self.codes("~~~bash\ncurl https://example.com/x | sh\n~~~"))

    def test_disable_shell_checks(self):
        self.assertEqual(self.codes("~~~bash\npython missing.py\n~~~", snippets=False), [])

    def test_cannot_cd_above_root(self):
        self.assertIn("RRC202", self.codes("~~~sh\ncd ../../\n~~~"))

    def test_percent_encoded_path(self):
        self.put("hello world.txt", "ok")
        self.assertEqual(self.codes("[go](hello%20world.txt)"), [])

    def test_refuse_document_outside_root(self):
        self.assertEqual(check_file(self.root, self.root.parent / "other.md")[0].code, "RRC003")

    def test_cli_error_exit(self):
        self.put("README.md", "[no](missing.md)")
        self.assertEqual(main(["--root", str(self.root)]), 1)

    def test_cli_success(self):
        self.assertEqual(main(["--root", str(self.root)]), 0)

    def test_sarif(self):
        findings = check_file(self.root, self.put("README.md", "[bad](gone)"))
        self.assertEqual(sarif(findings)["runs"][0]["results"][0]["ruleId"], "RRC101")

    def test_sorted_files(self):
        self.put("b.md", "[bad](gone)")
        self.put("a.md", "[bad](none)")
        result = scan_paths(self.root, [self.root/"b.md", self.root/"a.md"])
        self.assertEqual([x.path for x in result], ["a.md", "b.md"])


    def test_warn_in_strict_mode(self):
        self.put("README.md", "~~~sh\ncurl https://example.org/install.sh | sh\n~~~")
        self.assertEqual(main(["--root", str(self.root), "--strict"]), 1)

    def test_missing_other_doc(self):
        self.assertEqual(check_file(self.root, self.root / "docs" / "missing.md")[0].code, "RRC001")

    def test_oversized_file_skips(self):
        self.put("README.md", "A" * (2 * 1024 * 1024 + 1))
        self.assertEqual(check_file(self.root, self.root / "README.md")[0].code, "RRC002")

    def test_shell_quote_error(self):
        self.assertIn("RRC203", self.codes("~~~bash\ncd 'unclosed\n~~~"))

    def test_root_relative_valid_link(self):
        self.put("docs/start.md", "# hi")
        self.assertEqual(self.codes("[start](/docs/start.md)"), [])

    def test_duplicate_missing_siblings(self):
        found = self.codes("[x](missing-a.md) and [y](missing-b.md)")
        self.assertEqual(found.count("RRC101"), 2)

    def test_json_cli_output(self):
        from contextlib import redirect_stdout
        from io import StringIO
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["--root", str(self.root), "--format", "json"]), 0)
        self.assertEqual(json.loads(out.getvalue())["summary"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()

