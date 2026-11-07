# Agent plugins

Plugins for rolling out and reviewing AI coding tool adoption, built to the Cursor plugin format.

Status: local and unsubmitted. These plugins have not been submitted to the Cursor marketplace, and nothing here is accepted or listed there.

This is an independent open source project. It is not affiliated with or endorsed by Cursor.

## Plugins

| Plugin | What it does |
| --- | --- |
| [adoption-scorecard](adoption-scorecard/) | Turns a per-user usage export into an honest adoption report and reads it without overclaiming |
| [rollout-decision-review](rollout-decision-review/) | Runs a rollout decision review, checks stop conditions, and drafts a security and data checklist |

They come from the author's [AI coding adoption playbook](https://github.com/AlyMetwaly/ai-coding-adoption-playbook). The playbook explains the method. These plugins package parts of it for an agent.

## Layout

Each plugin is a folder at the repo root with its own `.cursor-plugin/plugin.json`. The root `.cursor-plugin/marketplace.json` lists them. This follows the public Cursor plugin specification, so verify against current Cursor docs before relying on any detail.

```text
.cursor-plugin/marketplace.json
<plugin-name>/
  .cursor-plugin/plugin.json
  skills/<skill>/SKILL.md
  commands/*.md
  rules/*.mdc
  README.md
  CHANGELOG.md
  LICENSE
```

## Validate and check

```bash
python tools/validate_plugins.py
python tools/publish_check.py
python -m pytest
```

- `validate_plugins.py` checks manifests, names, declared paths, and the frontmatter that skills, commands and rules need.
- `publish_check.py` checks style, secrets, forbidden names, and provenance. Run it before any release.

## Add a plugin

1. Write it for this repo. Do not copy third-party skills or prompts.
2. Put it in its own folder with a manifest, a README, a changelog and a license.
3. Add it to `.cursor-plugin/marketplace.json` and to `PROVENANCE.md`.
4. Run the checks above.

## License

[MIT](LICENSE).
