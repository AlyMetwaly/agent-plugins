---
name: draft-security-data-checklist
description: Draft a security and data-handling checklist for an AI coding tool rollout from the user's answers, marking every unknown. Use before a pilot starts or when a review must be reopened.
---

# Draft a security and data checklist

## Trigger

A pilot is about to start, a setting or integration changed, or a security review needs a written record.

## Workflow

1. Use `templates/security-data-checklist.md` in this plugin, relative to the plugin root, as the structure. Copy it to the user's working folder first.
2. Go through the control questions with the user: retention, model training, indexing, residency, secrets, repository access, extensions, model providers, integrations, telemetry, audit logs, offboarding, incident response, generated dependencies, licenses, and restricted code.
3. For each row, record the answer, the evidence, the owner as a role, the decision, the date and the next review date.
4. Mark every answer that depends on the plan or product behavior. How the product behaves can change, so verify against current Cursor docs.

## Rules

- Do not treat procurement approval as technical approval.
- Record what was actually reviewed: the product configuration, model providers, retention settings, repository permissions, enabled integrations and telemetry behavior.
- Reopen the review when any of those change.
- An unanswered row stays "[fill in]" or "unknown". Never write a plausible answer.
- Do not put secrets, tokens, or internal URLs into the checklist.

## Output

The completed checklist and a list of unanswered rows, each with a suggested owner role.
