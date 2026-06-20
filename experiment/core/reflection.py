"""The debiasing protocol that powers Layer 2 for groups A and B.

These are the ONLY decision-aid techniques with RCT-grade evidence
(Morewedge 2015; Lord et al. 1984; Schmidt 2020 — see RESEARCH-FOUNDATION §4).
Every prompt QUOTES the participant's own facts: that fact-binding is the
anti-Barnum guardrail (ADR-005). A prompt that would read the same for any
person is a bug, not a feature.
"""
from __future__ import annotations

from dataclasses import dataclass

from .scenario import BaseRate


@dataclass(frozen=True)
class ReflectionPrompt:
    technique: str  # consider_opposite | premortem | outside_view
    text: str
    requires_falsification: bool  # must the participant write a concrete counter-case?


def consider_opposite(facts: dict[str, str]) -> ReflectionPrompt:
    driver = facts.get("driver", "你想要的東西")
    return ReflectionPrompt(
        technique="consider_opposite",
        text=(
            f"【考慮相反】你說你最想得到「{driver}」。\n"
            "請寫出 3 個具體情境，在其中這個決定**反而讓你得不到它、甚至後悔**。"
        ),
        requires_falsification=True,
    )


def premortem(facts: dict[str, str]) -> ReflectionPrompt:
    fear = facts.get("fear", "你擔心的事")
    return ReflectionPrompt(
        technique="premortem",
        text=(
            f"【事前驗屍】想像一年後，這個決定徹底失敗了，而且正是因為「{fear}」成真。\n"
            "請回推：在做決定的當下，有哪些訊號其實已經能看出來？"
        ),
        requires_falsification=True,
    )


def outside_view(facts: dict[str, str], base_rates: tuple[BaseRate, ...]) -> ReflectionPrompt:
    constraint = facts.get("constraint", "你的限制")
    rate_hint = base_rates[0].as_line().strip() if base_rates else "（無基準率）"
    return ReflectionPrompt(
        technique="outside_view",
        text=(
            "【外部視角】先別管「我這次」，改問「像我這樣、有同樣限制"
            f"（{constraint}）的人，通常會怎樣」。\n"
            f"參照基準：{rate_hint}\n"
            "請寫下：這個群體基準率，和你心裡的預期差多少？為什麼？"
        ),
        requires_falsification=False,
    )


def debiasing_protocol(
    facts: dict[str, str], base_rates: tuple[BaseRate, ...]
) -> tuple[ReflectionPrompt, ...]:
    """The full evidence-backed protocol, in order."""
    return (
        consider_opposite(facts),
        premortem(facts),
        outside_view(facts, base_rates),
    )


def reflective_summary(facts: dict[str, str]) -> str:
    """A short fact-bound recap used for the misattribution test.

    Because it quotes the participant's specifics, a SWAPPED copy should fit a
    different person poorly — that gap is what we measure.
    """
    driver = facts.get("driver", "—")
    fear = facts.get("fear", "—")
    constraint = facts.get("constraint", "—")
    return (
        f"你的核心動機是「{driver}」，最大的擔憂是「{fear}」，"
        f"而讓你猶豫的現實限制是「{constraint}」。"
    )
