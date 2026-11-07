"""Tests for the plugin validator. Fixtures build tiny plugin repos in a temp folder."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import validate_plugins as v

REPO = Path(__file__).resolve().parent.parent


def make_repo(tmp_path: Path, **overrides) -> Path:
    """A minimal valid repo with one plugin. Overrides tweak the manifest."""
    plugin = tmp_path / "demo-plugin"
    (plugin / ".cursor-plugin").mkdir(parents=True)
    (plugin / "skills" / "do-thing").mkdir(parents=True)
    (plugin / "commands").mkdir()
    (plugin / "rules").mkdir()
    manifest = {
        "name": "demo-plugin",
        "description": "A demo.",
        "version": "0.1.0",
        "license": "MIT",
        "author": {"name": "Someone"},
        "skills": "./skills/",
        "commands": "./commands/",
        "rules": "./rules/",
    }
    manifest.update(overrides)
    (plugin / ".cursor-plugin" / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
    (plugin / "skills" / "do-thing" / "SKILL.md").write_text(
        "---\nname: do-thing\ndescription: Does a thing.\n---\n# Do thing\n", encoding="utf-8"
    )
    (plugin / "commands" / "go.md").write_text("---\nname: go\ndescription: Go.\n---\nGo.\n", encoding="utf-8")
    (plugin / "rules" / "r.mdc").write_text("---\ndescription: A rule.\nalwaysApply: false\n---\nBe good.\n", encoding="utf-8")
    for name in ("README.md", "CHANGELOG.md", "LICENSE"):
        (plugin / name).write_text("x\n", encoding="utf-8")
    (tmp_path / ".cursor-plugin").mkdir()
    (tmp_path / ".cursor-plugin" / "marketplace.json").write_text(
        json.dumps({"name": "demo", "plugins": [{"name": "demo-plugin", "source": "demo-plugin", "description": "A demo."}]}),
        encoding="utf-8",
    )
    return tmp_path


def test_real_repo_is_valid():
    assert v.validate(REPO) == []


def test_minimal_repo_is_valid(tmp_path):
    assert v.validate(make_repo(tmp_path)) == []


def test_missing_manifest(tmp_path):
    root = make_repo(tmp_path)
    (root / "demo-plugin" / ".cursor-plugin" / "plugin.json").unlink()
    assert any("plugin.json is missing" in p for p in v.validate(root))


def test_invalid_json_manifest(tmp_path):
    root = make_repo(tmp_path)
    (root / "demo-plugin" / ".cursor-plugin" / "plugin.json").write_text("{nope", encoding="utf-8")
    assert any("not valid JSON" in p for p in v.validate(root))


def test_name_must_be_kebab_case(tmp_path):
    root = make_repo(tmp_path, name="Demo_Plugin")
    problems = v.validate(root)
    assert any("kebab-case" in p for p in problems)


def test_name_must_match_marketplace_and_folder(tmp_path):
    root = make_repo(tmp_path, name="other-name")
    problems = v.validate(root)
    assert any("must match the folder name" in p for p in problems)
    assert any("differs from marketplace name" in p for p in problems)


def test_absolute_and_traversal_paths_are_rejected(tmp_path):
    root = make_repo(tmp_path, rules="/etc/rules", commands="../outside")
    problems = v.validate(root)
    assert sum("must be relative" in p for p in problems) == 2


def test_declared_path_must_exist(tmp_path):
    root = make_repo(tmp_path, agents="./agents/")
    assert any("agents path './agents/' does not exist" in p for p in v.validate(root))


def test_skill_needs_frontmatter(tmp_path):
    root = make_repo(tmp_path)
    (root / "demo-plugin" / "skills" / "do-thing" / "SKILL.md").write_text("# no frontmatter\n", encoding="utf-8")
    assert any("missing frontmatter" in p for p in v.validate(root))


def test_skill_name_must_match_folder(tmp_path):
    root = make_repo(tmp_path)
    (root / "demo-plugin" / "skills" / "do-thing" / "SKILL.md").write_text(
        "---\nname: another\ndescription: x\n---\n", encoding="utf-8"
    )
    assert any("must match its folder" in p for p in v.validate(root))


def test_command_needs_description(tmp_path):
    root = make_repo(tmp_path)
    (root / "demo-plugin" / "commands" / "go.md").write_text("---\nname: go\n---\n", encoding="utf-8")
    assert any("frontmatter needs 'description'" in p for p in v.validate(root))


def test_rule_needs_description(tmp_path):
    root = make_repo(tmp_path)
    (root / "demo-plugin" / "rules" / "r.mdc").write_text("---\nalwaysApply: false\n---\n", encoding="utf-8")
    assert any("r.mdc: frontmatter needs 'description'" in p for p in v.validate(root))


def test_version_must_be_semver(tmp_path):
    assert any("major.minor.patch" in p for p in v.validate(make_repo(tmp_path, version="1.0")))


def test_unlisted_plugin_is_reported(tmp_path):
    root = make_repo(tmp_path)
    other = root / "other-plugin" / ".cursor-plugin"
    other.mkdir(parents=True)
    (other / "plugin.json").write_text(json.dumps({"name": "other-plugin"}), encoding="utf-8")
    assert any("not listed in marketplace.json" in p for p in v.validate(root))


def test_duplicate_marketplace_names(tmp_path):
    root = make_repo(tmp_path)
    market = root / ".cursor-plugin" / "marketplace.json"
    entry = {"name": "demo-plugin", "source": "demo-plugin", "description": "A demo."}
    market.write_text(json.dumps({"name": "demo", "plugins": [entry, entry]}), encoding="utf-8")
    assert any("duplicate plugin name" in p for p in v.validate(root))


def test_marketplace_source_must_be_inside_repo(tmp_path):
    root = make_repo(tmp_path)
    market = root / ".cursor-plugin" / "marketplace.json"
    market.write_text(
        json.dumps({"name": "demo", "plugins": [{"name": "x", "source": "../elsewhere", "description": "d"}]}),
        encoding="utf-8",
    )
    assert any("not a folder inside the repo" in p for p in v.validate(root))


def test_frontmatter_parser():
    assert v.parse_frontmatter("---\nname: a\ndescription: \"b c\"\n---\nbody") == {"name": "a", "description": "b c"}
    assert v.parse_frontmatter("no frontmatter") is None
    assert v.parse_frontmatter("---\nname: a\n") is None  # never closed


def test_scorecard_script_runs_on_the_synthetic_example():
    script = REPO / "adoption-scorecard" / "scripts" / "adoption_scorecard"
    example = REPO / "adoption-scorecard" / "examples" / "synthetic_week6.csv"
    result = subprocess.run([sys.executable, str(script), str(example)], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "## 4. Status panel" in result.stdout
    assert "out of 100" not in result.stdout
