# Rollout decision review

A Cursor plugin for the decisions in an AI coding tool rollout: expand, hold, fix first, or pause.

It is independent. It is not affiliated with or endorsed by Cursor. Where a step depends on product behavior, the components say "verify against current Cursor docs".

## What it adds

| Component | Name | What it does |
| --- | --- | --- |
| Skill | `run-decision-review` | Fills a one-page decision review from the evidence you give it, and never invents a number |
| Skill | `check-stop-conditions` | Checks evidence against the stop conditions and reports pause, continue, or continue with conditions |
| Skill | `draft-security-data-checklist` | Drafts a security and data-handling checklist and marks every unknown |
| Command | `/decision-review` | Starts the review and asks for the decision first |
| Rule | `claims-need-evidence` | Keeps reports tied to a source, a date and a population |
| Templates | `templates/` | The decision review and the security and data checklist |

The plugin drafts and checks. People decide. Each skill says so.

## Install for local testing

Copy this folder to `~/.cursor/plugins/local/rollout-decision-review/`, then reload Cursor and check the components under Customize. Details can change, so verify against current Cursor docs.

## Limits

- It cannot know your configuration. Anything it states about product settings must be checked.
- It works from what you tell it. Unknown values stay unknown.
- It does not decide to pause a pilot. A named owner does.

## License

[MIT](LICENSE).
