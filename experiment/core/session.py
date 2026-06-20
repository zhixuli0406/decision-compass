"""Immutable session records. We accumulate frozen records through the flow and
emit one SessionResult at the end (immutability principle, ADR / coding-style).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class InteractionRecord:
    """One thing shown to / collected from the participant."""

    step: str
    prompt: str
    response: object = None

    def to_dict(self) -> dict:
        return {"step": self.step, "prompt": self.prompt, "response": self.response}


@dataclass(frozen=True)
class SessionResult:
    participant_id: str
    group_id: str
    scenario_id: str
    facts: tuple[tuple[str, str], ...]
    interactions: tuple[InteractionRecord, ...]
    choice: str
    predicted_satisfaction: int  # forecast for 1yr, 1..10
    outcome_probability: float   # participant's P(decision goes well), 0..1
    own_fit_score: int | None    # misattribution test: fit of OWN reflection (1..5)
    swapped_fit_score: int | None  # fit of a SWAPPED reflection (1..5)
    timestamp: str

    @property
    def misattribution_gap(self) -> int | None:
        """own - swapped. High positive => fact-bound (anti-Barnum working).
        Near zero => generic/Barnum (the swapped output fit just as well).
        """
        if self.own_fit_score is None or self.swapped_fit_score is None:
            return None
        return self.own_fit_score - self.swapped_fit_score

    def to_dict(self) -> dict:
        return {
            "participant_id": self.participant_id,
            "group_id": self.group_id,
            "scenario_id": self.scenario_id,
            "facts": [list(pair) for pair in self.facts],
            "interactions": [r.to_dict() for r in self.interactions],
            "choice": self.choice,
            "predicted_satisfaction": self.predicted_satisfaction,
            "outcome_probability": self.outcome_probability,
            "own_fit_score": self.own_fit_score,
            "swapped_fit_score": self.swapped_fit_score,
            "misattribution_gap": self.misattribution_gap,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True)
class SessionDraft:
    """Mutable-by-replacement builder threaded through the flow."""

    participant_id: str
    group_id: str
    scenario_id: str
    facts: tuple[tuple[str, str], ...] = ()
    interactions: tuple[InteractionRecord, ...] = ()

    def with_facts(self, facts: dict[str, str]) -> "SessionDraft":
        return replace(self, facts=tuple(facts.items()))

    def add(self, *records: InteractionRecord) -> "SessionDraft":
        return replace(self, interactions=self.interactions + records)

    def finalize(
        self,
        *,
        choice: str,
        predicted_satisfaction: int,
        outcome_probability: float,
        own_fit_score: int | None,
        swapped_fit_score: int | None,
        timestamp: str,
    ) -> SessionResult:
        return SessionResult(
            participant_id=self.participant_id,
            group_id=self.group_id,
            scenario_id=self.scenario_id,
            facts=self.facts,
            interactions=self.interactions,
            choice=choice,
            predicted_satisfaction=predicted_satisfaction,
            outcome_probability=outcome_probability,
            own_fit_score=own_fit_score,
            swapped_fit_score=swapped_fit_score,
            timestamp=timestamp,
        )

    def facts_dict(self) -> dict[str, str]:
        return dict(self.facts)
