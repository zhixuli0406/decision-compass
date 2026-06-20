"""Group A — 完整羅盤: Layer 1 probability + Layer 2 debiasing protocol WITH the
I Ching symbol interface. This is the full product hypothesis.
"""
from __future__ import annotations

from ..core.hexagram import DISCLAIMER, draw_hexagram
from ..core.intervention import Intervention
from ..core.io_adapter import Prompter
from ..core.reflection import debiasing_protocol, reflective_summary
from ..core.scenario import Scenario
from ..core.session import InteractionRecord


class GroupA(Intervention):
    group_id = "A"
    label = "完整羅盤（概率 + 去偏誤 + 易經符號）"
    shows_probability = True

    def reflect(
        self, prompter: Prompter, facts: dict[str, str], scenario: Scenario
    ) -> tuple[InteractionRecord, ...]:
        # The hexagram is a fact-free LABEL that only prefixes the protocol.
        hexagram = draw_hexagram(seed="|".join(facts.values()))
        prompter.show(DISCLAIMER)
        prompter.show(
            f"🧭 抽到第 {hexagram.number} 卦「{hexagram.name_zh}」"
            f"（{hexagram.name_en}）：{hexagram.reflection_trigger}"
        )

        records: list[InteractionRecord] = [
            InteractionRecord(step="hexagram", prompt=hexagram.name_zh, response=hexagram.number)
        ]
        for prompt in debiasing_protocol(facts, scenario.base_rates):
            answer = prompter.ask(prompt.text)
            records.append(
                InteractionRecord(step=f"reflect:{prompt.technique}", prompt=prompt.text, response=answer)
            )
        return tuple(records)

    def reflective_output(self, facts: dict[str, str], seed: str) -> str | None:
        return reflective_summary(facts)
