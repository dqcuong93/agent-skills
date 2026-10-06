#!/usr/bin/env python3
"""Structural checks for the qa plugin that `claude plugin validate` does not cover."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "qa"
REVIEW = PLUGIN / "skills" / "review"
REFS = REVIEW / "references"
SIGNALS = PLUGIN / "stack-signals.md"
BANNED = ROOT / ".banned-words"  # gitignored, one word per line, optional

WRITTEN_FOR = re.compile(r"^Written for: \S.* \d+$")
INJECTION = re.compile(r"!`([^`]*)`")
SHELL_OPS = ("|", "&&", ";", "(", ")")


def main() -> int:
    fails: list[str] = []
    checks = 0

    skill = REVIEW / "SKILL.md"
    if not skill.is_file():
        print(f"FAIL structure: {skill.relative_to(ROOT)} missing")
        return 1
    skill_text = skill.read_text()

    refs = sorted(REFS.glob("*.md"))
    if not refs:
        fails.append("structure: no reference files")

    signal_text = SIGNALS.read_text() if SIGNALS.is_file() else ""
    for ref in refs:
        name = ref.name
        text = ref.read_text()
        checks += 1
        if f"references/{name}" not in skill_text:
            fails.append(f"linked: references/{name} not linked from SKILL.md")
        checks += 1
        if re.search(r"\]\([^)]*\.md\)|references/", text):
            fails.append(f"one-level: {name} links to another file")
        if "-" in ref.stem:
            key = ref.stem.split("-", 1)[1]
            lines = text.splitlines()
            checks += 1
            if len(lines) < 3 or not WRITTEN_FOR.match(lines[2]):
                fails.append(f"written-for: {name} line 3 is not 'Written for: <stack> <major>'")
            checks += 1
            if f"| `{key}` |" not in signal_text:
                fails.append(f"signals: stack key `{key}` has no row in stack-signals.md")

    for skill_md in sorted(PLUGIN.glob("skills/*/SKILL.md")):
        for cmd in INJECTION.findall(skill_md.read_text()):
            checks += 1
            if any(op in cmd for op in SHELL_OPS):
                fails.append(f"injection: {skill_md.relative_to(ROOT)} runs `{cmd}`")

    template = PLUGIN / "skills" / "init-profile" / "profile-template.md"
    checks += 1
    layout = re.search(r"^## Layout\n(.*?)^## ", template.read_text(), re.S | re.M)
    if not layout or "- ignore:" not in layout.group(1):
        fails.append("template: profile-template.md has no '- ignore:' line under Layout")

    drift = PLUGIN / "scripts" / "drift.py"
    checks += 1
    if not drift.is_file() or "scripts/drift.py" not in skill_text:
        fails.append("drift: plugins/qa/scripts/drift.py is missing or not called from review/SKILL.md")

    if BANNED.is_file():
        words = [w.strip().lower() for w in BANNED.read_text().splitlines() if w.strip()]
        tracked = subprocess.run(
            ["git", "ls-files", "-co", "--exclude-standard"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.split()
        for rel in tracked:
            path = ROOT / rel
            if path.suffix not in {".md", ".json", ".yml", ".py", ".excalidraw"} or not path.is_file():
                continue
            low = path.read_text(errors="ignore").lower()
            for word in words:
                checks += 1
                if word in low:
                    fails.append(f"public: {rel} contains a banned word")

    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"OK ({checks} checks)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
