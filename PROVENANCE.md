# Provenance

Every file in this repo was written for it by its author, with AI assistance, and reviewed by the author. Nothing is copied from another project, an employer, or a third-party skill or prompt collection.

| Path | Origin |
| --- | --- |
| `adoption-scorecard/scripts/adoption_scorecard/` | Copied from the author's own `ai-coding-adoption-playbook` repo (MIT) |
| `adoption-scorecard/examples/` | Synthetic data written for the author's own playbook |
| `rollout-decision-review/templates/` | Copied from the author's own `ai-coding-adoption-playbook` repo (MIT) |
| Plugin manifests, skills, commands, rules, READMEs | Written for this repo |
| `.cursor-plugin/marketplace.json` | Written for this repo, following the structure in Cursor's public plugin docs |

The plugin layout follows the public Cursor plugin specification. No files from the official plugins were copied.

Run `python tools/publish_check.py` before any release. It checks style, secrets, forbidden names, and that every plugin is listed here.
