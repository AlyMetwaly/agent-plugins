# Security and data checklist

Use this to record the security, privacy and legal answers you need before pilot users get access to an AI coding tool. It turns the data questions in `docs/01-align.md` into a table with an owner, a decision and a review date for each control. Many answers depend on the product, plan and settings you buy, so verify against current Cursor docs for every product-dependent answer in the table, and attach the evidence you used.

**Tool and plan reviewed:** [fill in] **Review date:** [fill in] **Next review date:** [fill in]
**Security owner:** [fill in] **Legal owner:** [fill in] **Rollout owner:** [fill in]

## Checklist

- [ ] The exact product, plan, version and configuration under review are written down.
- [ ] Each row below has evidence attached, a named owner (as a role) and a decision.
- [ ] Rows that affect in-scope repositories are decided before those repositories are opened to the pilot.
- [ ] Open rows have a date and a named owner.
- [ ] The decision is copied to the decision log in `docs/01-align.md`.
- [ ] A review date is set, and the events that reopen the review are listed.

Do not treat procurement approval as technical approval. Record the product configuration, model providers, retention settings, repository permissions, enabled integrations and telemetry behavior that were actually reviewed. Reopen the review when any of these change.

## Controls

| Control question | Evidence required | Owner (role) | Decision | Date | Review date |
|---|---|---|---|---|---|
| Source-code retention: is source code stored or retained, where and for how long? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Prompt and completion retention: are prompts and outputs stored, where and for how long? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Model training settings: can your code or prompts be used for training, and who controls the setting? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Repository indexing: is code indexed, where is the index kept, and can it be turned off? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Data residency: where is data processed and stored, and do you need a specific region? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Secrets handling: how are secrets kept out of prompts and context, and how do you check? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Access to private repositories: which repositories can the tool reach, and with what permissions? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Extension permissions: what can installed extensions read, write or send? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Model provider access: which providers receive your data, and under what terms? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Approved and blocked models: which models are allowed, which are blocked, and who changes the list? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| MCP server and integration approval: who approves each server, and how is it reviewed? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Third-party integrations: which outside services connect to the tool, and what data do they get? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Telemetry collection: what usage and diagnostic data is collected, and can it be limited? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Audit logs: which events are logged, who can read them, and how long are they kept? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Offboarding: how is access removed when someone leaves or changes role, and how fast? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Incident response: who is told, how fast, and what is the vendor's obligation to notify you? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Generated dependency review: how are new packages suggested by the tool checked before use? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| License and intellectual-property review: what is the written position on generated code and its origin? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |
| Restrictions for regulated or export-controlled code: which repositories are excluded or need a separate decision? | [fill in] | [fill in] | [fill in] | [fill in] | [fill in] |

## Notes and open items

[fill in]
