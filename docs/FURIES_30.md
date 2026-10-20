# 30 Furies: release gate v0.1

These are **30 adversarial checks**, not 30 independent human or autonomous reviewers. Every release and substantial change repeats this matrix, records test logs and separately obtains human approval for unresolved issues.

| # | Fury asks | Evidence or remaining gate |
| -- | -- | -- |
| 01 | Is the problem specific? | Broken docs and quickstarts demonstrated |
| 02 | Is first value immediate? | Module one-liner |
| 03 | Does it work offline? | No network use in source |
| 04 | No registration or lock-in? | No account/API |
| 05 | Is standalone value concrete? | Links, anchors, snippets |
| 06 | Is setup reproducible? | Python standard library |
| 07 | Can beginners find help? | README and CLI --help |
| 08 | Is output deterministic? | Ordered file and diagnostic sorting |
| 09 | Can people locate faults? | Path/line/code diagnostics |
| 10 | Are file limits bounded? | 2 MiB per file |
| 11 | Does it refuse execution of snippets? | No subprocess or eval in code |
| 12 | Does it refuse network access? | No HTTP operations |
| 13 | Can it read outside project root? | Path.resolve/relative_to guard |
| 14 | Is telemetry absent? | No data collection |
| 15 | Does it avoid printing raw secret values? | Only broken path references; **human audit pending** |
| 16 | Does it avoid overstated guarantees? | README limits |
| 17 | Are unsupported formats disclosed? | HTML/complex CommonMark not covered |
| 18 | Is proprietary Pryntor source excluded? | New generic implementation, provenance review pending |
| 19 | Is third-party license compliance respected? | No bundled outside sources |
| 20 | Is the MIT grant explicit? | LICENSE |
| 21 | Does CLI run without install? | __main__.py |
| 22 | Can CI ingest it? | JSON and SARIF |
| 23 | Is text accessible without colored output? | Plain text |
| 24 | Are findings actionable? | Diagnostic codes |
| 25 | Is the UX predictable on failure? | Exit code and --strict |
| 26 | Do edge cases have fixtures? | unittest regressions |
| 27 | Is QA versioned in source? | CI test workflow |
| 28 | Can vulnerabilities be reported privately? | SECURITY.md |
| 29 | Can community members contribute? | CONTRIBUTING.md |
| 30 | Has human release review independently passed? | **Hosted CI passed on initial commit. Founder authorized public alpha; independent external reviewer sign-off still absent.** |

Use failures to change code, then retest. Do not count a checklist as independent expert review, or claim a GitHub badge before the check runs.


## Publication classification

Original, narrowly scoped open-source **alpha** authorized by the founder on 20 October 2026. Live production guarantees, external independent expert approvals, partnerships and star/adoption counts are **not** claimed. Re-run hosted checks on the final hardened commit before a public launch.
