"""Render the adoption report as Markdown."""

from __future__ import annotations

from datetime import date
from typing import Mapping, Sequence

from .core import (
    FLAG_ACTIVATION_BELOW,
    FLAG_DEPTH_BELOW,
    FLAG_STICKING_BELOW,
    FLAG_TEAM_EXCESS,
    SUSTAINED_MIN_WEEKS,
    SUSTAINED_PROXY_MIN_ACTIVE_DAYS,
    WEEKLY_WINDOW_DAYS,
    ParseResult,
    User,
    compute_depth,
    compute_funnel,
    compute_spread,
    compute_teams,
    early_warning_flags,
    rate,
    resolve_as_of,
    uses_weekly_column,
)

MAX_SKIPPED_LISTED = 10


def _pct(value: float) -> str:
    return f"{value:.0%}"


def _table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return lines


def render_report(
    parsed: ParseResult,
    as_of: date | None = None,
    previous_rates: Mapping[str, float] | None = None,
    source_label: str = "usage export",
) -> str:
    users: Sequence[User] = parsed.users
    when = resolve_as_of(users, as_of)
    funnel = compute_funnel(users, when)
    teams = compute_teams(users, when, previous_rates)
    depth = compute_depth(users)
    spread = compute_spread(users, when)
    flags = early_warning_flags(users, funnel, depth)

    out: list[str] = []
    out.append(f"# Adoption scorecard: {source_label}")
    out.append("")
    out.append(f"As of: {when.isoformat() if when else 'n/a (no users)'}")
    out.append(f"Users read: {len(users)}. Rows skipped: {len(parsed.skipped)}.")
    out.append("")

    if not users:
        out.append("No users in the file, so there is nothing to score.")
        out.append("")

    out.append("## 1. Funnel")
    out.append("")
    stage_rows = [
        ("Licensed", funnel.licensed, 1.0 if funnel.licensed else 0.0),
        ("Activated (any use)", funnel.activated, rate(funnel.activated, funnel.licensed)),
        (
            f"Weekly active (last {WEEKLY_WINDOW_DAYS} days)",
            funnel.weekly_active,
            rate(funnel.weekly_active, funnel.licensed),
        ),
        ("Sustained", funnel.sustained, rate(funnel.sustained, funnel.licensed)),
    ]
    out += _table(
        ["Stage", "Users", "Share of licensed"],
        [[name, str(n), _pct(share)] for name, n, share in stage_rows],
    )
    out.append("")
    if uses_weekly_column(users):
        out.append(
            f"Sustained means active in at least {SUSTAINED_MIN_WEEKS} of the last 4 weeks, "
            "read from `active_weeks_last_4`."
        )
    else:
        out.append(
            "Sustained uses a fallback because the export has no weekly breakdown: active in the last "
            f"{WEEKLY_WINDOW_DAYS} days and on at least {SUSTAINED_PROXY_MIN_ACTIVE_DAYS} of the "
            "last 28 days. The fallback is a heuristic. It is not equivalent to the weekly definition. "
            "Add an `active_weeks_last_4` column to use the weekly definition."
        )
    out.append("")

    out.append("## 2. By team")
    out.append("")
    if teams:
        out += _table(
            ["Team", "Users", "Sustained", "Sustained rate", "Median active days", "Trend"],
            [
                [
                    t.team,
                    str(t.users),
                    str(t.sustained),
                    _pct(t.sustained_rate),
                    f"{t.median_active_days:g}",
                    t.trend,
                ]
                for t in teams
            ],
        )
    else:
        out.append("No teams to show.")
    out.append("")
    if previous_rates is None:
        out.append("Trend is n/a: pass an earlier export with `--previous` to compare sustained rates.")
        out.append("")

    out.append("## 3. Depth")
    out.append("")
    if depth.active_users:
        out += _table(
            ["Active users who", "Users", "Share of active"],
            [
                ["Used agent sessions", str(depth.agent_users), _pct(rate(depth.agent_users, depth.active_users))],
                [
                    "Used completions only",
                    str(depth.completions_only_users),
                    _pct(rate(depth.completions_only_users, depth.active_users)),
                ],
                [
                    "Accepted nothing",
                    str(depth.no_acceptance_users),
                    _pct(rate(depth.no_acceptance_users, depth.active_users)),
                ],
            ],
        )
    else:
        out.append("No active users in the last 28 days, so depth cannot be measured.")
    out.append("")

    out.append("## 4. Status panel")
    out.append("")
    out.append(
        "Each signal is shown on its own. There is no composite score, because a single number "
        "hides whether the problem is inactivity, weak repeat use, or uneven spread. Nothing here "
        "measures developer performance, productivity, code quality, ROI, or business impact."
    )
    out.append("")
    if users:
        activated_share = rate(funnel.activated, funnel.licensed)
        weekly_share = rate(funnel.weekly_active, funnel.licensed)
        sustained_share = rate(funnel.sustained, funnel.licensed)
        sustained_of_activated = rate(funnel.sustained, funnel.activated)
        agent_share = rate(depth.agent_users, depth.active_users)
        if spread.teams >= 2:
            spread_text = (
                f"{spread.teams_with_sustained} of {spread.teams} teams have sustained users. "
                f"Top team ({spread.top_team}) has {_pct(spread.top_team_share)} of active days "
                f"and {_pct(spread.top_team_headcount_share)} of licensed users."
            )
        else:
            spread_text = "One team in this export, so spread cannot be assessed."
        rows = [
            ["Activation", f"{_pct(activated_share)} of licensed users", "Activated divided by licensed"],
            ["Weekly active", f"{_pct(weekly_share)} of licensed users", f"Last {WEEKLY_WINDOW_DAYS} days"],
            [
                "Sustained use",
                f"{_pct(sustained_share)} of licensed, {_pct(sustained_of_activated)} of activated",
                "See the note under section 1",
            ],
            ["Team spread", spread_text, "No threshold applied"],
            [
                "Agent use",
                f"{_pct(agent_share)} of active users",
                "Reported, not scored. More agent use is not always better use",
            ],
            ["Outcome evidence", "Not in this export", "Use the decision review template"],
            ["Review capacity", "Not in this export", "Ask reviewers directly"],
            [
                "Expansion decision",
                "Not calculated",
                "Apply the triggers you set before the period (docs/05-expand.md)",
            ],
        ]
        out += _table(["Signal", "This export", "Note"], rows)
    else:
        out.append("No users, so there is nothing to show.")
    out.append("")
    if flags:
        out.append("Flags to investigate:")
        out.append("")
        out += [f"- {flag}" for flag in flags]
    else:
        out.append("No flags at the default thresholds.")
    out.append("")

    out.append("## 5. What each metric can hide")
    out.append("")
    out += _table(
        ["Metric", "What it can hide", "Check it against"],
        [
            ["Licensed", "Seats nobody asked for, or people who have left", "Activated"],
            ["Activated", "One-time sign-in trials", "Sustained"],
            ["Weekly active", "A single login or one accepted suggestion", "Active days and depth"],
            ["Sustained", "Mandates, reminders or scheduled use", "Depth and spread across teams"],
            ["Accepted suggestions", "Accepting without reading", "Review outcomes in your own process"],
        ],
    )
    out.append("")
    out.append(
        "Do not read a metric as proof of the next layer. Licenses do not prove use. Use does not "
        "prove depth. Depth does not prove productivity. Productivity does not prove business value."
    )
    out.append("")

    if parsed.skipped:
        out.append("## Rows skipped")
        out.append("")
        for line_no, reason in parsed.skipped[:MAX_SKIPPED_LISTED]:
            out.append(f"- line {line_no}: {reason}")
        extra = len(parsed.skipped) - MAX_SKIPPED_LISTED
        if extra > 0:
            out.append(f"- and {extra} more")
        out.append("")

    out.append("---")
    out.append("")
    out.append(
        "Flag thresholds are example defaults. They are not benchmarks or recommended targets, and "
        "they do not define a successful rollout. Set them from the decision they control, your "
        "support capacity, the risk of expanding, and your own baseline: "
        f"activation below {_pct(FLAG_ACTIVATION_BELOW)}, "
        f"sticking below {_pct(FLAG_STICKING_BELOW)}, "
        f"a team's share of active days {_pct(FLAG_TEAM_EXCESS)} or more above its share of users, "
        f"agent use below {_pct(FLAG_DEPTH_BELOW)}."
    )
    out.append("")
    return "\n".join(out)
