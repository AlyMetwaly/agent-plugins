---
name: read-adoption-report
description: Run the adoption scorecard on a per-user usage CSV and explain the result without overclaiming. Use when the user has an AI coding tool usage export, or a scorecard report, to interpret.
---

# Read an adoption report

## Trigger

The user has a per-user usage export, or a report from the scorecard, and wants to know what it says.

## Workflow

1. Check the export has these columns: `user_id`, `team`, `licensed_date`, `last_active_date`, `active_days_last_28`, `agent_sessions_last_28`, `accepted_suggestions_last_28`. The optional `active_weeks_last_4` column gives the real definition of sustained use. If the file holds names or emails, stop and ask the user to remove them first.
2. Find the scorecard script in this plugin at `scripts/adoption_scorecard`, relative to the plugin root. If you cannot locate it, ask the user where it is. How a plugin's files are located depends on the product, so verify against current Cursor docs.
3. Run `python scripts/adoption_scorecard <export.csv>`. Add `--previous <earlier.csv>` for a trend, and `--as-of YYYY-MM-DD` if the export date matters.
4. Read the report in order: funnel, by team, depth, status panel, flags, what each metric can hide.
5. Write the summary using the rules below.

## Rules for the summary

- Report each signal on its own. Do not invent a combined score.
- Start with the gap between activated and sustained. That is where the questions are.
- Say whether sustained came from the weekly column or from the fallback. The fallback is a heuristic, not the same measure.
- For small teams, quote counts, not only rates.
- A flag is something to investigate, not a verdict.
- Agent use is depth, not quality. Never call more agent use better.
- Never rank people. Team results are diagnostics, not performance ratings.
- Do not turn usage into productivity, hours saved or ROI.

## Output

1. What the numbers show, in five lines at most.
2. What they cannot show: outcomes, review capacity, quality.
3. Three questions to ask next, each with a role to ask.
4. A recommendation limited to: investigate, hold, or ask for outcome evidence.

## Try it

Two synthetic files are in `examples/`: `synthetic_week3.csv` and `synthetic_week6.csv`. Run the week 6 file with `--previous` set to the week 3 file to see a trend.
