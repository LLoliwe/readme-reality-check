"""Offline command-line interface to README Reality Check."""
import argparse
import json
import sys
from pathlib import Path
from .checker import scan_paths, SKIP_DIRS

def sarif(findings):
    codes = sorted({f.code for f in findings})
    return {"version": "2.1.0", "$schema": "https://json.schemastore.org/sarif-2.1.0.json", "runs": [{
        "tool": {"driver": {"name": "readme-reality-check", "rules": [{"id": c, "name": c} for c in codes]}},
        "results": [{"ruleId": f.code, "level": "error" if f.severity == "error" else "warning",
                     "message": {"text": f.message},
                     "locations": [{"physicalLocation": {"artifactLocation": {"uri": f.path},
                                     "region": {"startLine": max(1, f.line)}}}]} for f in findings]
    }]}

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="readme-reality",
        description="Catch broken Markdown links and quickstarts offline, without running commands.")
    parser.add_argument("paths", nargs="*", help="Markdown paths, default README.md")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--all", action="store_true", help="Check all Markdown excluding vendor and hidden directories")
    parser.add_argument("--no-snippets", action="store_true", help="Skip static shell quickstart checks")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as errors")
    parser.add_argument("--format", choices=["text", "json", "sarif"], default="text")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        parser.error("--root must exist and be a directory")
    files = [root / p for p in (args.paths or ["README.md"])]
    if args.all:
        files = [p for p in root.rglob("*.md") if not
                 any((part in SKIP_DIRS or part.startswith(".")) for part in p.relative_to(root).parts[:-1])]
    findings = scan_paths(root, files, snippets=not args.no_snippets)
    errors = sum(x.severity == "error" for x in findings)
    warnings = sum(x.severity == "warning" for x in findings)
    if args.format == "json":
        print(json.dumps({"summary": {"files": len(files), "errors": errors, "warnings": warnings},
                          "findings": [f.to_dict() for f in findings]}, indent=2))
    elif args.format == "sarif":
        print(json.dumps(sarif(findings), indent=2))
    else:
        for f in findings:
            print(f"{f.path}:{f.line}: {f.severity.upper()} {f.code}: {f.message}")
        print(f"Checked {len(files)} file(s): {errors} error(s), {warnings} warning(s).")
    return 1 if errors or args.strict and warnings else 0

if __name__ == "__main__":
    sys.exit(main())

