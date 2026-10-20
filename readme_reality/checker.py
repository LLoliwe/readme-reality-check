"""Static README checks. This module never executes commands or accesses the network."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import shlex

MAX_BYTES = 2 * 1024 * 1024
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", ".tox", "dist", "build"}
LINK = re.compile(r"!?\[[^\]\n]*\]\((?:<([^>\n]+)>|([^\s)\n]+))(?:\s+['\"][^'\"]*['\"])?\)")
HEADER = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s{0,3}((?:\x60){3,}|~{3,})(.*)$")
DANGER = re.compile(r"(?:\bcurl\b|\bwget\b)[^\n]*\|\s*(?:sudo\s+)?(?:ba)?sh\b|\brm\s+-[A-Za-z]*[rf][A-Za-z]*\b", re.I)

@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    line: int
    message: str
    def to_dict(self):
        return asdict(self)

def within(root, target):
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False

def slug(label):
    label = re.sub(r"<[^>]+>", "", label)
    label = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", label)
    label = re.sub(r"[^\w\- ]", "", label.lower())
    return re.sub(r" +", "-", label.strip())

def sections(lines):
    outside = []
    fenced = []
    current = []
    delimiter = ""
    lang = ""
    for i, line in enumerate(lines, 1):
        match = FENCE.match(line)
        if delimiter:
            if match and match.group(1)[0] == delimiter[0] and len(match.group(1)) >= len(delimiter):
                fenced.append((lang, current))
                current, delimiter, lang = [], "", ""
            else:
                current.append((i, line))
            outside.append("")
        elif match:
            delimiter = match.group(1)
            lang = match.group(2).strip().split(" ")[0].lower()
            outside.append("")
        else:
            outside.append(line)
    return outside, fenced

def anchors(path):
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        return set()
    outer, _ = sections(path.read_text(encoding="utf-8-sig", errors="replace").splitlines())
    found, counts = set(), {}
    for line in outer:
        match = HEADER.match(line)
        if match:
            base = slug(match.group(1))
            n = counts.get(base, 0)
            counts[base] = n + 1
            found.add(f"{base}-{n}" if n else base)
    return found

def commands(root, doc, lines, results):
    cwd = doc.parent
    display = str(doc.relative_to(root))
    for number, original in lines:
        raw = original.strip()
        if raw.startswith("$ "):
            raw = raw[2:].strip()
        if not raw or raw.startswith(("#", "> ")):
            continue
        if DANGER.search(raw):
            results.append(Finding("warning", "RRC201", display, number, "Potentially dangerous copy-paste command; inspect it manually."))
        for command in re.split(r"\s*&&\s*", raw):
            try:
                tokens = shlex.split(command, comments=True)
            except ValueError:
                results.append(Finding("warning", "RRC203", display, number, "Shell snippet could not be parsed."))
                continue
            if not tokens:
                continue
            key = tokens[0]
            if key == "cd" and len(tokens) >= 2:
                name = tokens[1]
                if any(x in name for x in ("$", "~", "*")):
                    continue
                target = (cwd / name).resolve()
                if not within(root, target):
                    results.append(Finding("warning", "RRC202", display, number, "cd leaves the repository; not inspected."))
                elif not target.is_dir():
                    results.append(Finding("error", "RRC102", display, number, f"Missing cd directory: {name}"))
                else:
                    cwd = target
            elif key in {"python", "python3", "node", "bash", "sh"} and len(tokens) > 1 and not tokens[1].startswith("-"):
                name = tokens[1]
                if any(x in name for x in ("$", "~", "*", "{")):
                    continue
                target = (cwd / name).resolve()
                if within(root, target) and not target.is_file():
                    results.append(Finding("error", "RRC103", display, number, f"Missing script: {name}"))
            elif key.startswith("./") and not any(x in key for x in ("$", "~", "*")):
                target = (cwd / key).resolve()
                if within(root, target) and not target.exists():
                    results.append(Finding("error", "RRC103", display, number, f"Missing executable path: {key}"))
            elif tokens[:2] == ["npm", "run"] and len(tokens) >= 3:
                package = cwd / "package.json"
                if within(root, package) and package.is_file():
                    try:
                        scripts = json.loads(package.read_text(encoding="utf-8")).get("scripts", {})
                        if tokens[2] not in scripts:
                            results.append(Finding("error", "RRC104", display, number, f"Undefined npm script: {tokens[2]}"))
                    except (OSError, ValueError, AttributeError):
                        results.append(Finding("warning", "RRC204", display, number, "Could not read package.json scripts."))

def check_file(root: Path, doc: Path, snippets=True):
    root, doc = root.resolve(), doc.resolve()
    if not within(root, doc):
        return [Finding("error", "RRC003", "(outside root)", 0, "Refused file outside repository root.")]
    label = str(doc.relative_to(root))
    if not doc.is_file():
        return [Finding("error", "RRC001", label, 0, "Markdown file not found.")]
    if doc.stat().st_size > MAX_BYTES:
        return [Finding("warning", "RRC002", label, 0, "Markdown exceeds 2 MiB; skipped.")]
    lines = doc.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    outside, fences = sections(lines)
    results = []
    for number, line in enumerate(outside, 1):
        for match in LINK.finditer(line):
            url = match.group(1) or match.group(2)
            if not url or url.startswith(("https://", "http://", "mailto:", "tel:", "data:")):
                continue
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc:
                continue
            rel = unquote(parsed.path)
            if "\x00" in rel:
                results.append(Finding("error", "RRC105", label, number, "NUL in link path."))
                continue
            target = doc if not rel else ((root / rel.lstrip("/")) if rel.startswith("/") else (doc.parent / rel))
            target = target.resolve()
            if not within(root, target):
                results.append(Finding("warning", "RRC205", label, number, "Local link leaves repository; skipped."))
            elif not target.exists():
                results.append(Finding("error", "RRC101", label, number, f"Broken link: {rel}"))
            elif parsed.fragment and target.is_file() and target.suffix.lower() in {".md", ".markdown"}:
                anchor = unquote(parsed.fragment).lower()
                if anchor not in anchors(target):
                    results.append(Finding("error", "RRC106", label, number, f"Missing anchor: #{anchor}"))
    if snippets:
        for lang, body in fences:
            if lang in {"sh", "shell", "bash", "zsh", "console"}:
                commands(root, doc, body, results)
    return results

def scan_paths(root, paths, snippets=True):
    results = []
    for doc in sorted(set(p.resolve() for p in paths)):
        results.extend(check_file(root, doc, snippets))
    return sorted(results, key=lambda f: (f.path, f.line, f.code))

