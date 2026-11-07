---
name: run-decision-review
description: Fill in a rollout decision review from the evidence the user provides, ending in expand, hold, fix first, or pause. Use when preparing an executive or account review of an AI coding tool rollout.
---

# Run a decision review

## Trigger

The user must decide whether to expand, hold, fix first, or pause an AI coding tool rollout, and needs one page that supports the decision.

## Workflow

1. Ask for the decision requested first. Write it at the top.
2. Use `templates/decision-review.md` in this plugin, relative to the plugin root, as the structure. Copy it to the user's working folder before you fill it in.
3. Collect, in this order:
   - the objective and the baseline, each with a date, a definition and a population
   - the usage numbers, ideally from a scorecard report
   - the outcomes the teams already track, each with a quality guardrail and one alternative explanation
   - what cannot be attributed
   - the cost lines
   - open risks and stop conditions
4. Fill the template using only what the user gave you.
5. Finish with a recommendation: expand, hold, fix first, or pause. Give the reason, the owners and the next review date.

## Rules

- Never fill in a number the user did not provide. Write "unknown" and list it under "What we do not yet know".
- Keep usage and outcomes in separate sections.
- Pair every speed measure with a quality measure.
- Use "associated with", not "caused by", unless a controlled comparison was run.
- Triggers and stop conditions must be the ones set before the review period. If the user wants to change one, ask them to log why.
- Do not report hours saved unless the user describes how they were measured.
- The recommendation is the user's decision. Draft it and show your reasoning. Do not present it as settled.

## Output

The completed decision review, plus a short list of what is unknown and who could resolve each item.
