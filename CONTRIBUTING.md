# Contributing

We prioritize actual broken README examples, accessibility, reproducible false-positive reports and safe checks over feature count. No unreviewed new dependencies or network calls.

Run:

~~~sh
python -m unittest discover -s tests -v
python -m readme_reality --all
~~~

Include a failing fixture and passing regression test with each bug fix. Never include real customer information, secrets, private URLs or copyrighted third-party readmes in issues. Maintainers perform human code review; no automatic merges. Please include migration guidance when behavior changes.

