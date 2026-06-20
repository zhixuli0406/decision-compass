"""Base Intervention: the shared four-step contract each group fills in.

The session flow (run_experiment) is identical across groups; groups differ ONLY
in these hooks. That isolation is what lets the experiment attribute any effect
to the intervention rather than to flow differences.
"""
from __future__ import annotations

from .io_adapter import Prompter
from .scenario import Scenario
from .session import InteractionRecord


class Intervention:
    group_id: str = "?"
    label: str = "?"
    shows_probability: bool = False  # Layer 1 on/off

    # --- hook 1: Layer 2 reflection -----------------------------------------
    def reflect(
        self, prompter: Prompter, facts: dict[str, str], scenario: Scenario
    ) -> tuple[InteractionRecord, ...]:
        """Deliver the group's Layer 2 content and collect responses.
        Default: nothing (group D)."""
        return ()

    # --- hook 2: output used by the misattribution test ----------------------
    def reflective_output(self, facts: dict[str, str], seed: str) -> str | None:
        """The text we later show back (own vs swapped) in the misattribution
        test. Return None for groups that produce no reflective output (D)."""
        return None
