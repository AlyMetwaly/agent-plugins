---
name: prepare-usage-export
description: Shape a raw usage export into the CSV the adoption scorecard reads, without personal data. Use when the user has admin analytics or usage data that is not yet in the scorecard's column layout.
---

# Prepare a usage export

## Trigger

The user has raw usage data and needs the scorecard's CSV layout, or the scorecard rejected rows.

## Workflow

1. Ask where the data comes from. What an admin export contains depends on the plan and product, so verify against current Cursor docs. Do not assume a column exists.
2. Map the source fields to the scorecard columns: `user_id`, `team`, `licensed_date`, `last_active_date`, `active_days_last_28`, `agent_sessions_last_28`, `accepted_suggestions_last_28`, and optionally `active_weeks_last_4`.
3. Remove names and emails. Replace them with a stable id such as `u001`. Keep the mapping file out of the repo and out of the report.
4. Check each row:
   - dates are `YYYY-MM-DD`
   - counts are whole numbers, never negative
   - `active_days_last_28` is 0 to 28
   - `active_weeks_last_4` is 0 to 4 if present
   - `last_active_date` is not before `licensed_date`
   - no duplicate ids
5. Write the CSV. List every row you changed or dropped, with the reason.

## Rules

- Never invent a value. An empty `last_active_date` is allowed and means the person never used the tool. Any other missing value means the row is dropped and listed.
- If a column is not in the source, say so. Do not estimate it.
- Do not combine teams to hide small groups. Tell the user that small teams are noisy.
- Do not write personal data into any file in the repository.

## Output

1. The CSV path.
2. The number of rows kept and dropped.
3. The reasons for any dropped rows.
4. Any column that is missing from the source, and what that limits.
