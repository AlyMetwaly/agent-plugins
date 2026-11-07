"""Check this repo before any public release.

Fails on em dashes, en dashes, emojis, banned words, forbidden names, likely
secrets, a plugin missing from PROVENANCE.md, and a plugin without an MIT
license. Run from the repo root: python tools/publish_check.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()
SUFFIXES = {".md", ".mdc", ".py", ".csv", ".toml", ".txt", ".yaml", ".yml", ".json"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules"}

# Words and names are built from pieces so this file does not list them in plain text.
BANNED = [
    "lever" + "age",
    "un" + "lock",
    "ro" + "bust",
    "seam" + "less",
    "holis" + "tic",
    "em" + "power",
    "syn" + "ergy",
    "jour" + "ney",
    "deep" + r"\s+" + "dive",
    "game" + r"[\s-]+" + "changer",
    "land" + "scape",
]
FORBIDDEN_NAMES = ["no" + "kia", "key" + "stone", "launch" + "pad"]
SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key|secret|token|passwd|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}", re.I),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

DASH = re.compile("[—–]")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐️]")
BANNED_RE = re.compile(r"\b(" + "|".join(BANNED) + r")\w*\b", re.I)
NAMES_RE = re.compile(r"\b(" + "|".join(FORBIDDEN_NAMES) + r")\b", re.I)


def text_files(root: Path) -> list[Path]:
    out = []
    for path in root.rglob("*"):
        if not path.is_file() or path.resolve() == SELF:
            continue
        if path.relative_to(root).as_posix() == "tests/test_publish_check.py":
            continue  # holds deliberate bad samples for the checks above
        if SKIP_DIRS & set(path.relative_to(root).parts):
            continue
        if path.suffix.lower() in SUFFIXES:
            out.append(path)
    return sorted(out)


def check_text(root: Path) -> list[str]:
    problems: list[str] = []
    for path in text_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), start=1):
            where = f"{path.relative_to(root).as_posix()}:{number}"
            for pattern, label in (
                (DASH, "em or en dash"),
                (EMOJI, "emoji"),
                (BANNED_RE, "banned word"),
                (NAMES_RE, "forbidden name"),
            ):
                if pattern.search(line):
                    problems.append(f"{where}: {label}")
            if any(p.search(line) for p in SECRET_PATTERNS):
                problems.append(f"{where}: possible secret")
    return problems


def plugin_dirs(root: Path) -> list[Path]:
    return sorted(c for c in root.iterdir() if c.is_dir() and (c / ".cursor-plugin" / "plugin.json").is_file())


def check_plugins(root: Path) -> list[str]:
    problems: list[str] = []
    provenance_file = root / "PROVENANCE.md"
    provenance = provenance_file.read_text(encoding="utf-8") if provenance_file.is_file() else ""
    if not provenance:
        problems.append("PROVENANCE.md is missing or empty")
    for plugin in plugin_dirs(root):
        if plugin.name not in provenance:
            problems.append(f"{plugin.name}: not listed in PROVENANCE.md")
        license_file = plugin / "LICENSE"
        if not license_file.is_file() or "MIT License" not in license_file.read_text(encoding="utf-8"):
            problems.append(f"{plugin.name}: LICENSE must be the MIT license")
        try:
            manifest = json.loads((plugin / ".cursor-plugin" / "plugin.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            problems.append(f"{plugin.name}: manifest cannot be read")
            continue
        if manifest.get("license") != "MIT":
            problems.append(f"{plugin.name}: manifest license must be MIT")
    return problems


def check(root: Path) -> list[str]:
    return check_text(root) + check_plugins(root)


def main() -> int:
    problems = check(ROOT)
    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s).")
        return 1
    print(f"Publish check passed: {len(text_files(ROOT))} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
