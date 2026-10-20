# README Reality Check

**Your README says it works. Does it?**

A tiny, offline checker for broken local links, missing heading anchors, missing quickstart scripts, undefined npm scripts and risky copy-and-paste shell commands. It never executes the snippets it inspects.

## Try it in 60 seconds

Python 3.10+, zero runtime packages, no account, no API keys, no cloud.

~~~sh
python -m readme_reality --all
python -m readme_reality --all --format sarif > docs-report.sarif
python -m unittest discover -s tests -v
~~~

For use in other repositories, install it as a standard Python CLI:

~~~sh
python -m pip install .
readme-reality --all
~~~

Typical output (illustrative, not a claim about this repository):

~~~text
README.md:17: ERROR RRC101: Broken link: docs/missing.md
README.md:24: ERROR RRC104: Undefined npm script: build
README.md:31: WARNING RRC201: Potentially dangerous copy-paste command; inspect it manually.
Checked 3 file(s): 2 error(s), 1 warning(s).
~~~

## What gets caught?

| Code | Finding |
| --- | --- |
| RRC001-003 | Missing, oversized or out-of-root Markdown input |
| RRC101 | Local link or image points to a missing file |
| RRC102 | cd destination in a shell example does not exist |
| RRC103 | Python, Node, Bash or local executable path does not exist |
| RRC104 | npm run script absent from package.json |
| RRC105 | Invalid NUL in a link path |
| RRC106 | Link points at a missing Markdown heading anchor |
| RRC201-205 | Risky snippet or a reference that cannot be verified safely |

## Use in GitHub Actions

~~~sh
python -m readme_reality --all --strict
~~~

Use --format json or --format sarif for structured output. The exit code is 1 on errors; with --strict, warnings also fail.

## Safe by default, honest about limits

- **No subprocess execution, no network requests, no telemetry and no uploading.**
- Rejects documents outside the selected root and does not follow local links outside that root.
- Recognizes common inline Markdown link forms and a small, explicitly supported subset of shell commands. It is not a full CommonMark parser or shell interpreter.
- External URLs are not checked for uptime. Remote-install snippets are flagged for review, not executed.
- Clean output is **not** proof of a working application or complete repository security.
- Keep untrusted project content inside a sandbox.

Maintainer: Pryntor Open Source. This implementation is a small, original public utility, not a release of Pryntor's private research, commercial evaluation stack, customers' data or partner assets.

## Build with us

Start with an issue containing a sanitized, minimal failing example. [CONTRIBUTING](CONTRIBUTING.md) explains tests, [SECURITY](SECURITY.md) explains disclosure, and our [30-Furies gate](docs/FURIES_30.md) discloses review criteria.

MIT licensed. No upsells or usage tracking.

