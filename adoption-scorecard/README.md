# Adoption scorecard

A Cursor plugin that turns a per-user usage export into an adoption report, and helps an agent read it without overclaiming.

It is independent. It is not affiliated with or endorsed by Cursor. Where a step depends on product behavior, the components say "verify against current Cursor docs".

## What it adds

| Component | Name | What it does |
| --- | --- | --- |
| Skill | `read-adoption-report` | Runs the scorecard and writes an honest summary: what the numbers show, what they cannot show, and questions to ask next |
| Skill | `prepare-usage-export` | Shapes raw usage data into the scorecard's CSV layout without personal data |
| Command | `/adoption-report` | Starts the first skill on a file you name |
| Rule | `metric-honesty` | Keeps reports from reading a metric as proof of the next layer |
| Script | `scripts/adoption_scorecard` | Standard-library Python. Prints funnel, team results, depth, a status panel, flags and a "what each metric can hide" table |

There is no composite score on purpose. A single number hides whether the problem is inactivity, weak repeat use, or uneven spread.

## Install for local testing

Copy this folder to `~/.cursor/plugins/local/adoption-scorecard/`, then reload Cursor and check the components under Customize. Details can change, so verify against current Cursor docs.

## Try the scorecard directly

Python 3.11 or later:

```bash
python scripts/adoption_scorecard examples/synthetic_week6.csv --previous examples/synthetic_week3.csv
```

The files in `examples/` are synthetic. They describe no real organization.

## Input columns

`user_id`, `team`, `licensed_date`, `last_active_date`, `active_days_last_28`, `agent_sessions_last_28`, `accepted_suggestions_last_28`. Optional: `active_weeks_last_4`.

Rows that fail validation are skipped and listed in the report.

## Limits

- The report cannot show outcomes, review capacity, or code quality. It says so.
- Without the weekly column, sustained use falls back to a heuristic. The report says so.
- Flag thresholds are example defaults, not benchmarks.
- Team results are diagnostics, not performance ratings.

## License

[MIT](LICENSE).
