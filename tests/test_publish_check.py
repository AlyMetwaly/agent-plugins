"""Tests for the publish gate."""

from __future__ import annotations

import json
from pathlib import Path

import publish_check as p

REPO = Path(__file__).resolve().parent.parent
MIT = "MIT License\n\nPermission is hereby granted.\n"


def make_clean(tmp_path: Path) -> Path:
    plugin = tmp_path / "demo-plugin"
    (plugin / ".cursor-plugin").mkdir(parents=True)
    (plugin / ".cursor-plugin" / "plugin.json").write_text(json.dumps({"name": "demo-plugin", "license": "MIT"}), encoding="utf-8")
    (plugin / "LICENSE").write_text(MIT, encoding="utf-8")
    (plugin / "README.md").write_text("A clean readme.\n", encoding="utf-8")
    (tmp_path / "PROVENANCE.md").write_text("demo-plugin was written for this repo.\n", encoding="utf-8")
    return tmp_path


def test_real_repo_passes_the_publish_check():
    assert p.check(REPO) == []


def test_clean_repo_passes(tmp_path):
    assert p.check(make_clean(tmp_path)) == []


def test_em_dash_is_flagged(tmp_path):
    root = make_clean(tmp_path)
    (root / "demo-plugin" / "README.md").write_text("Bad — dash.\n", encoding="utf-8")
    assert any("em or en dash" in x for x in p.check(root))


def test_en_dash_is_flagged(tmp_path):
    root = make_clean(tmp_path)
    (root / "demo-plugin" / "README.md").write_text("2025 – 2026\n", encoding="utf-8")
    assert any("em or en dash" in x for x in p.check(root))


def test_emoji_is_flagged(tmp_path):
    root = make_clean(tmp_path)
    (root / "demo-plugin" / "README.md").write_text("Nice \U0001F680\n", encoding="utf-8")
    assert any("emoji" in x for x in p.check(root))


def test_banned_word_is_flagged(tmp_path):
    root = make_clean(tmp_path)
    word = "lever" + "age"
    (root / "demo-plugin" / "README.md").write_text(f"We {word} this.\n", encoding="utf-8")
    assert any("banned word" in x for x in p.check(root))


def test_forbidden_name_is_flagged(tmp_path):
    root = make_clean(tmp_path)
    name = "no" + "kia"
    (root / "demo-plugin" / "README.md").write_text(f"From {name} work.\n", encoding="utf-8")
    assert any("forbidden name" in x for x in p.check(root))


def test_secret_is_flagged(tmp_path):
    root = make_clean(tmp_path)
    (root / "demo-plugin" / "README.md").write_text('api_key = "abcdefghijklmnop1234"\n', encoding="utf-8")
    assert any("possible secret" in x for x in p.check(root))


def test_plugin_missing_from_provenance(tmp_path):
    root = make_clean(tmp_path)
    (root / "PROVENANCE.md").write_text("Nothing listed.\n", encoding="utf-8")
    assert any("not listed in PROVENANCE.md" in x for x in p.check(root))


def test_missing_provenance_file(tmp_path):
    root = make_clean(tmp_path)
    (root / "PROVENANCE.md").unlink()
    assert any("PROVENANCE.md is missing" in x for x in p.check(root))


def test_license_must_be_mit(tmp_path):
    root = make_clean(tmp_path)
    (root / "demo-plugin" / "LICENSE").write_text("All rights reserved.\n", encoding="utf-8")
    assert any("LICENSE must be the MIT license" in x for x in p.check(root))


def test_manifest_license_must_be_mit(tmp_path):
    root = make_clean(tmp_path)
    (root / "demo-plugin" / ".cursor-plugin" / "plugin.json").write_text(
        json.dumps({"name": "demo-plugin", "license": "GPL-3.0"}), encoding="utf-8"
    )
    assert any("manifest license must be MIT" in x for x in p.check(root))
