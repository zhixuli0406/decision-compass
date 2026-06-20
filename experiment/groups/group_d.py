"""Group D — 無介入對照: scenario + decision logging only. No Layer 1, no Layer 2.
The baseline everything else is measured against (A vs D).
"""
from __future__ import annotations

from ..core.intervention import Intervention


class GroupD(Intervention):
    group_id = "D"
    label = "無介入對照（只記錄決策）"
    shows_probability = False

    # Inherits the no-op reflect() and reflective_output() -> None from base.
