"""Command line entry point."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Sequence

from .core import load_csv_text, previous_team_rates, resolve_as_of
from .report import render_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="adoption_scorecard",
        description="Turn a per-user usage CSV into a Markdown adoption report.",
    )
    parser.add_argument("csv_path", type=Path, help="usage export, see the README for columns")
    parser.add_argument("--as-of", help="report date, YYYY-MM-DD (default: latest last_active_date)")
    parser.add_argument("--previous", type=Path, help="an earlier export, used to compute the trend")
    parser.add_argument("--out", type=Path, help="write the report to this file instead of stdout")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        as_of = date.fromisoformat(args.as_of) if args.as_of else None
        parsed = load_csv_text(args.csv_path.read_text(encoding="utf-8"))
        previous_rates = None
        if args.previous:
            previous = load_csv_text(args.previous.read_text(encoding="utf-8"))
            previous_rates = previous_team_rates(previous.users, resolve_as_of(previous.users))
        report = render_report(parsed, as_of, previous_rates, source_label=args.csv_path.name)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if args.out:
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0
