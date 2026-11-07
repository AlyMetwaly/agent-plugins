"""Run with `python tools/adoption_scorecard data/sample_usage.csv`
or `python -m adoption_scorecard data/sample_usage.csv` from inside tools/."""

import sys
from pathlib import Path

# Make the package importable when this directory is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adoption_scorecard.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
