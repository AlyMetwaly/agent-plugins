---
name: check-stop-conditions
description: Check a rollout's evidence against its stop conditions and say whether the pilot should pause. Use at every review point of an AI coding tool pilot.
---

# Check stop conditions

## Trigger

The user wants to know whether a pilot should continue or pause, or a review point is due.

## Workflow

1. Ask for the stop conditions that were agreed before the pilot. If none exist, offer these as a starting point and say they are not agreed yet:
   - a confirmed sensitive-data exposure
   - repeated policy violations
   - material review overload
   - an unacceptable defect pattern
   - a loss of engineering trust that the rollout team cannot correct
2. For each condition, record:
   - status: met, not met, or unknown
   - the evidence, with its source and date
   - the role that decides
   - the restart condition, if it is met
3. Treat "unknown" as a risk. Say what evidence would settle it and who has it.
4. State the result: pause, continue, or continue with conditions.

## Rules

- You do not decide to pause. The named decision owner does. Report the evidence and the rule.
- Do not downgrade a met condition because the numbers look good elsewhere.
- Do not treat a missing report as "not met".
- Settings that decide data handling depend on the product and plan, so verify against current Cursor docs before saying a control is in place.
- Write down the date and the owner of the decision.

## Output

A table with one row per condition: condition, status, evidence, decision owner, restart condition. Then the result in one sentence and the next check date.
