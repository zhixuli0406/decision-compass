"""Group C — 純巴納姆對照: generic 'reading' with NO probability layer and NO
debiasing protocol. Measures the Barnum baseline. If A is no better than C, the
product's value is just the Forer effect (MVP-EXPERIMENT judgement rules).
"""
from __future__ import annotations

from ..core.barnum import barnum_reading, format_reading
from ..core.intervention import Intervention
from ..core.io_adapter import Prompter
from ..core.scenario import Scenario
from ..core.session import InteractionRecord


class GroupC(Intervention):
    group_id = "C"
    label = "純巴納姆對照（通用模糊建議，無去偏誤）"
    shows_probability = False

    def reflect(
        self, prompter: Prompter, facts: dict[str, str], scenario: Scenario
    ) -> tuple[InteractionRecord, ...]:
        # Generic, fact-free statements that fit almost anyone.
        lines = barnum_reading(seed="|".join(facts.values()))
        prompter.show("🔮 為你解讀如下：")
        prompter.show(format_reading(lines))
        answer = prompter.ask("讀完這段解讀，你打算怎麼做？（一句話）")
        return (
            InteractionRecord(step="barnum_reading", prompt="generic", response=list(lines)),
            InteractionRecord(step="barnum_response", prompt="讀後決定", response=answer),
        )

    def reflective_output(self, facts: dict[str, str], seed: str) -> str | None:
        # The 'output' is the generic reading — by design it has no facts, so a
        # swapped copy should fit just as well (=> small misattribution gap).
        return " ".join(barnum_reading(seed=seed))
