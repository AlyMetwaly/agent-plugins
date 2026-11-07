"""Pure functions that turn per-user usage rows into adoption measures.

There is no composite score. Each signal is reported on its own.

No network access and no file writes. Dates are ISO strings (YYYY-MM-DD).
The definitions match docs/04-measure.md.
"""

from __future__ import annotations

import csv
import io
import statistics
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Mapping, Sequence

REQUIRED_COLUMNS: tuple[str, ...] = (
    "user_id",
    "team",
    "licensed_date",
    "last_active_date",
    "active_days_last_28",
    "agent_sessions_last_28",
    "accepted_suggestions_last_28",
)
OPTIONAL_COLUMNS: tuple[str, ...] = ("active_weeks_last_4",)

WEEKLY_WINDOW_DAYS = 7
SUSTAINED_MIN_WEEKS = 3
# Used only when the export has no active_weeks_last_4 column.
SUSTAINED_PROXY_MIN_ACTIVE_DAYS = 8
TREND_DELTA = 0.05

# Flag thresholds. These are defaults. Set your own before you rely on them.
FLAG_ACTIVATION_BELOW = 0.70
FLAG_STICKING_BELOW = 0.40
FLAG_TEAM_EXCESS = 0.20
FLAG_DEPTH_BELOW = 0.25


@dataclass(frozen=True)
class User:
    user_id: str
    team: str
    licensed: date
    last_active: date | None
    active_days: int
    agent_sessions: int
    accepted: int
    active_weeks: int | None


@dataclass(frozen=True)
class ParseResult:
    users: tuple[User, ...]
    skipped: tuple[tuple[int, str], ...]  # (file line number, reason)


@dataclass(frozen=True)
class Funnel:
    licensed: int
    activated: int
    weekly_active: int
    sustained: int


@dataclass(frozen=True)
class TeamRow:
    team: str
    users: int
    sustained: int
    sustained_rate: float
    median_active_days: float
    trend: str


@dataclass(frozen=True)
class Depth:
    active_users: int
    agent_users: int
    completions_only_users: int
    no_acceptance_users: int


@dataclass(frozen=True)
class Spread:
    teams: int
    teams_with_sustained: int
    top_team: str | None
    top_team_share: float
    top_team_headcount_share: float


def rate(part: int, whole: int) -> float:
    return part / whole if whole else 0.0


def _parse_date(text: str) -> date:
    return date.fromisoformat(text.strip())


def _parse_int(text: str, low: int, high: int | None = None) -> int:
    value = int(text.strip())
    if value < low or (high is not None and value > high):
        raise ValueError("out of range")
    return value


def parse_rows(rows: Iterable[Mapping[str, str]]) -> ParseResult:
    """Validate rows. Bad rows are skipped and listed, never silently fixed."""
    users: list[User] = []
    skipped: list[tuple[int, str]] = []
    seen: set[str] = set()
    for line_no, row in enumerate(rows, start=2):
        user_id = (row.get("user_id") or "").strip()
        if not user_id:
            skipped.append((line_no, "missing user_id"))
            continue
        if user_id in seen:
            skipped.append((line_no, f"duplicate user_id {user_id}"))
            continue
        try:
            licensed = _parse_date(row.get("licensed_date") or "")
        except ValueError:
            skipped.append((line_no, "bad licensed_date"))
            continue
        last_text = (row.get("last_active_date") or "").strip()
        try:
            last_active = _parse_date(last_text) if last_text else None
        except ValueError:
            skipped.append((line_no, "bad last_active_date"))
            continue
        if last_active is not None and last_active < licensed:
            skipped.append((line_no, "last_active_date before licensed_date"))
            continue
        try:
            active_days = _parse_int(row.get("active_days_last_28") or "", 0, 28)
            agent = _parse_int(row.get("agent_sessions_last_28") or "", 0)
            accepted = _parse_int(row.get("accepted_suggestions_last_28") or "", 0)
        except ValueError:
            skipped.append((line_no, "bad count value"))
            continue
        weeks_text = (row.get("active_weeks_last_4") or "").strip()
        try:
            active_weeks = _parse_int(weeks_text, 0, 4) if weeks_text else None
        except ValueError:
            skipped.append((line_no, "bad active_weeks_last_4"))
            continue
        seen.add(user_id)
        team = (row.get("team") or "").strip() or "unassigned"
        users.append(
            User(user_id, team, licensed, last_active, active_days, agent, accepted, active_weeks)
        )
    return ParseResult(tuple(users), tuple(skipped))


def load_csv_text(text: str) -> ParseResult:
    """Parse CSV text. A file with no header is an error. A header-only file is valid."""
    if not text.strip():
        raise ValueError("the file is empty: expected a header row")
    reader = csv.DictReader(io.StringIO(text))
    header = reader.fieldnames or []
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        raise ValueError("missing columns: " + ", ".join(missing))
    return parse_rows(reader)


def resolve_as_of(users: Sequence[User], override: date | None = None) -> date | None:
    if override is not None:
        return override
    last_dates = [u.last_active for u in users if u.last_active is not None]
    if last_dates:
        return max(last_dates)
    if users:
        return max(u.licensed for u in users)
    return None


def is_activated(user: User) -> bool:
    return user.last_active is not None


def is_weekly_active(user: User, as_of: date) -> bool:
    if user.last_active is None:
        return False
    days_ago = (as_of - user.last_active).days
    return 0 <= days_ago < WEEKLY_WINDOW_DAYS


def is_sustained(user: User, as_of: date) -> bool:
    if user.active_weeks is not None:
        return user.active_weeks >= SUSTAINED_MIN_WEEKS
    return is_weekly_active(user, as_of) and user.active_days >= SUSTAINED_PROXY_MIN_ACTIVE_DAYS


def uses_weekly_column(users: Sequence[User]) -> bool:
    return any(u.active_weeks is not None for u in users)


def compute_funnel(users: Sequence[User], as_of: date | None) -> Funnel:
    if as_of is None:
        return Funnel(len(users), 0, 0, 0)
    return Funnel(
        licensed=len(users),
        activated=sum(1 for u in users if is_activated(u)),
        weekly_active=sum(1 for u in users if is_weekly_active(u, as_of)),
        sustained=sum(1 for u in users if is_sustained(u, as_of)),
    )


def _team_sustained_rates(users: Sequence[User], as_of: date | None) -> dict[str, float]:
    by_team: dict[str, list[User]] = {}
    for u in users:
        by_team.setdefault(u.team, []).append(u)
    out: dict[str, float] = {}
    for team, members in by_team.items():
        count = sum(1 for u in members if as_of is not None and is_sustained(u, as_of))
        out[team] = rate(count, len(members))
    return out


def compute_teams(
    users: Sequence[User],
    as_of: date | None,
    previous_rates: Mapping[str, float] | None = None,
) -> list[TeamRow]:
    by_team: dict[str, list[User]] = {}
    for u in users:
        by_team.setdefault(u.team, []).append(u)
    rows: list[TeamRow] = []
    for team in sorted(by_team):
        members = by_team[team]
        sustained = sum(1 for u in members if as_of is not None and is_sustained(u, as_of))
        current = rate(sustained, len(members))
        if previous_rates is None:
            trend = "n/a"
        elif team not in previous_rates:
            trend = "new"
        else:
            delta = current - previous_rates[team]
            trend = "up" if delta >= TREND_DELTA else "down" if delta <= -TREND_DELTA else "flat"
        rows.append(
            TeamRow(
                team=team,
                users=len(members),
                sustained=sustained,
                sustained_rate=current,
                median_active_days=float(statistics.median(u.active_days for u in members)),
                trend=trend,
            )
        )
    return rows


def previous_team_rates(users: Sequence[User], as_of: date | None) -> dict[str, float]:
    return _team_sustained_rates(users, as_of)


def compute_depth(users: Sequence[User]) -> Depth:
    active = [u for u in users if u.active_days > 0]
    agent = [u for u in active if u.agent_sessions > 0]
    completions = [u for u in active if u.agent_sessions == 0 and u.accepted > 0]
    return Depth(
        active_users=len(active),
        agent_users=len(agent),
        completions_only_users=len(completions),
        no_acceptance_users=len(active) - len(agent) - len(completions),
    )


def top_team_share(users: Sequence[User]) -> tuple[str, float] | None:
    """Largest single team's share of all active days. None if there is no usage."""
    totals: dict[str, int] = {}
    for u in users:
        totals[u.team] = totals.get(u.team, 0) + u.active_days
    grand = sum(totals.values())
    if not grand:
        return None
    team = max(sorted(totals), key=lambda t: totals[t])
    return team, totals[team] / grand


def compute_spread(users: Sequence[User], as_of: date | None) -> Spread:
    """How usage is spread across teams. No threshold is applied here."""
    teams = {u.team for u in users}
    with_sustained = {
        u.team for u in users if as_of is not None and is_sustained(u, as_of)
    }
    top = top_team_share(users)
    headcount = rate(sum(1 for u in users if top and u.team == top[0]), len(users))
    return Spread(
        teams=len(teams),
        teams_with_sustained=len(with_sustained),
        top_team=top[0] if top else None,
        top_team_share=top[1] if top else 0.0,
        top_team_headcount_share=headcount,
    )


def early_warning_flags(users: Sequence[User], funnel: Funnel, depth: Depth) -> list[str]:
    """Up to three plain-language flags, most important first."""
    flags: list[str] = []
    if funnel.licensed and rate(funnel.activated, funnel.licensed) < FLAG_ACTIVATION_BELOW:
        flags.append(
            f"Activation is below {FLAG_ACTIVATION_BELOW:.0%} of licensed users: "
            "check access, onboarding, and first-use friction."
        )
    if funnel.activated and rate(funnel.sustained, funnel.activated) < FLAG_STICKING_BELOW:
        flags.append(
            f"Sustained use is below {FLAG_STICKING_BELOW:.0%} of activated users: "
            "check whether first use is turning into repeat use."
        )
    top = top_team_share(users)
    if len({u.team for u in users}) >= 2 and top is not None:
        head = rate(sum(1 for u in users if u.team == top[0]), len(users))
        if top[1] - head >= FLAG_TEAM_EXCESS:
            flags.append(
                f"One team ({top[0]}) has {top[1]:.0%} of active days but {head:.0%} of licensed "
                "users: check whether adoption is concentrated."
            )
    if depth.active_users and rate(depth.agent_users, depth.active_users) < FLAG_DEPTH_BELOW:
        flags.append(
            f"Agent use is below {FLAG_DEPTH_BELOW:.0%} of active users: "
            "check whether people have found agent workflows."
        )
    return flags[:3]
