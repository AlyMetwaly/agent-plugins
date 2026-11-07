"""Validate the Cursor plugin layout in this repo.

Checks manifests, names, declared component paths and the frontmatter that
skills, commands, agents and rules need. It follows the public Cursor plugin
specification. Details can change, so verify against current Cursor docs.

Run from the repo root: python tools/validate_plugins.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
REQUIRED_FIELDS = ("name", "description", "version", "license")
PATH_KEYS = ("skills", "rules", "agents", "commands", "hooks")
REQUIRED_FILES = ("README.md", "CHANGELOG.md", "LICENSE")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Read simple `key: value` frontmatter between two --- lines. None if absent."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip("\"'")
    return None


def _load_json(path: Path) -> tuple[dict | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"{path.name} is missing"
    except json.JSONDecodeError as error:
        return None, f"{path.name} is not valid JSON: {error}"


def _declared_paths(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str)]
    return []


def _frontmatter_problems(path: Path, rel: str, required: tuple[str, ...]) -> list[str]:
    front = parse_frontmatter(path.read_text(encoding="utf-8"))
    if front is None:
        return [f"{rel}: missing frontmatter"]
    return [f"{rel}: frontmatter needs '{key}'" for key in required if not front.get(key)]


def check_plugin(plugin_dir: Path, marketplace_name: str | None = None) -> list[str]:
    label = plugin_dir.name
    problems: list[str] = []
    manifest, error = _load_json(plugin_dir / ".cursor-plugin" / "plugin.json")
    if error or manifest is None:
        return [f"{label}: {error}"]

    name = manifest.get("name", "")
    if not KEBAB.match(str(name)):
        problems.append(f"{label}: name '{name}' must be lowercase kebab-case")
    if name != plugin_dir.name:
        problems.append(f"{label}: name '{name}' must match the folder name")
    if marketplace_name is not None and name != marketplace_name:
        problems.append(f"{label}: manifest name '{name}' differs from marketplace name '{marketplace_name}'")
    for field in REQUIRED_FIELDS:
        if not manifest.get(field):
            problems.append(f"{label}: manifest needs '{field}'")
    if manifest.get("version") and not SEMVER.match(str(manifest["version"])):
        problems.append(f"{label}: version '{manifest['version']}' is not major.minor.patch")
    author = manifest.get("author")
    if not (isinstance(author, dict) and author.get("name")):
        problems.append(f"{label}: manifest needs author.name")

    for key in PATH_KEYS:
        for declared in _declared_paths(manifest.get(key)):
            if declared.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", declared) or ".." in Path(declared).parts:
                problems.append(f"{label}: {key} path '{declared}' must be relative and stay inside the plugin")
                continue
            target = plugin_dir / declared
            if not target.exists():
                problems.append(f"{label}: {key} path '{declared}' does not exist")
                continue
            problems += _component_problems(plugin_dir, key, target)

    for filename in REQUIRED_FILES:
        if not (plugin_dir / filename).is_file():
            problems.append(f"{label}: {filename} is missing")
    return problems


def _component_problems(plugin_dir: Path, key: str, target: Path) -> list[str]:
    label = plugin_dir.name
    problems: list[str] = []
    if key == "skills":
        for skill_dir in sorted(p for p in target.iterdir() if p.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            rel = f"{label}/{skill_dir.relative_to(plugin_dir).as_posix()}/SKILL.md"
            if not skill_file.is_file():
                problems.append(f"{rel} is missing")
                continue
            problems += _frontmatter_problems(skill_file, rel, ("name", "description"))
            front = parse_frontmatter(skill_file.read_text(encoding="utf-8")) or {}
            if front.get("name") and front["name"] != skill_dir.name:
                problems.append(f"{rel}: skill name '{front['name']}' must match its folder '{skill_dir.name}'")
    elif key in ("agents", "commands"):
        for file in sorted(p for p in target.iterdir() if p.suffix in (".md", ".txt")):
            rel = f"{label}/{file.relative_to(plugin_dir).as_posix()}"
            problems += _frontmatter_problems(file, rel, ("name", "description"))
    elif key == "rules":
        for file in sorted(p for p in target.iterdir() if p.suffix in (".mdc", ".md")):
            rel = f"{label}/{file.relative_to(plugin_dir).as_posix()}"
            problems += _frontmatter_problems(file, rel, ("description",))
    return problems


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    marketplace, error = _load_json(root / ".cursor-plugin" / "marketplace.json")
    if error or marketplace is None:
        return [f"marketplace: {error}"]
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or not entries:
        return ["marketplace: 'plugins' must be a non-empty list"]

    seen: set[str] = set()
    listed_dirs: set[str] = set()
    for entry in entries:
        name = entry.get("name", "") if isinstance(entry, dict) else ""
        source = entry.get("source", "") if isinstance(entry, dict) else ""
        if name in seen:
            problems.append(f"marketplace: duplicate plugin name '{name}'")
        seen.add(name)
        if not isinstance(entry, dict) or not entry.get("description"):
            problems.append(f"marketplace: entry '{name}' needs a description")
        plugin_dir = (root / source).resolve() if source else None
        if plugin_dir is None or not plugin_dir.is_dir() or root.resolve() not in plugin_dir.parents:
            problems.append(f"marketplace: source '{source}' for '{name}' is not a folder inside the repo")
            continue
        listed_dirs.add(plugin_dir.name)
        problems += check_plugin(plugin_dir, marketplace_name=name)

    for child in sorted(root.iterdir()):
        if child.is_dir() and (child / ".cursor-plugin" / "plugin.json").is_file() and child.name not in listed_dirs:
            problems.append(f"{child.name}: has a manifest but is not listed in marketplace.json")
    return problems


def main() -> int:
    problems = validate(ROOT)
    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s).")
        return 1
    print("Plugin validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
