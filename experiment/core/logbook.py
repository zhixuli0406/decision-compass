"""JSONL persistence for session results and follow-up outcomes.

The decision journal is the closed-loop calibration mechanism (ADR-004): we log
the participant's at-the-moment forecast now, and reconcile it against reality
at the 3-month follow-up. That reconciliation is what makes a false 'accuracy
feeling' impossible to hide.
"""
from __future__ import annotations

import json
from pathlib import Path

from .session import SessionResult


def append_result(path: str | Path, result: SessionResult) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")


def read_results(path: str | Path) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    rows: list[dict] = []
    with p.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_outcomes(path: str | Path) -> dict[str, dict]:
    """Follow-up file: one JSON object per line with at least
    {participant_id, went_well: bool, actual_satisfaction: int 1..10}.
    Returns a map keyed by participant_id.
    """
    p = Path(path)
    if not p.exists():
        return {}
    outcomes: dict[str, dict] = {}
    with p.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                row = json.loads(line)
                outcomes[row["participant_id"]] = row
    return outcomes
