"""Group B — 去符號對照: Layer 1 probability + Layer 2 debiasing protocol but
TEXT-ONLY (no I Ching symbol). Isolates whether the symbol interface adds
anything over the bare debiasing protocol (A vs B).
"""
from __future__ import annotations

from ..core.intervention import Intervention
from ..core.io_adapter import Prompter
from ..core.reflection import debiasing_protocol, reflective_summary
from ..core.scenario import Scenario
from ..core.session import InteractionRecord


class GroupB(Intervention):
    group_id = "B"
    label = "去符號對照（概率 + 去偏誤，純文字）"
    shows_probability = True

    def reflect(
        self, prompter: Prompter, facts: dict[str, str], scenario: Scenario
    ) -> tuple[InteractionRecord, ...]:
        records: list[InteractionRecord] = []
        for prompt in debiasing_protocol(facts, scenario.base_rates):
            answer = prompter.ask(prompt.text)
            records.append(
                InteractionRecord(step=f"reflect:{prompt.technique}", prompt=prompt.text, response=answer)
            )
        return tuple(records)

    def reflective_output(self, facts: dict[str, str], seed: str) -> str | None:
        return reflective_summary(facts)
