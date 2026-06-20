"""Decision scenarios and their reference-class base rates (Layer 1 inputs).

Base-rate numbers now live in `base_rates.json` with mandatory provenance
fields. A rate with status != 'verified' is a PLACEHOLDER and must not reach
real participants — see verify_base_rates() and the launch gate in
run_experiment.py. This enforces the "outside-view / reference-class forecasting"
honesty requirement (RESEARCH-FOUNDATION §4).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_BASE_RATES_PATH = Path(__file__).with_name("base_rates.json")


@dataclass(frozen=True)
class BaseRate:
    """A group-level base rate with an honest interval and its provenance."""

    label: str
    point: float
    low: float
    high: float
    status: str          # verified | needs_source
    source: str
    url: str
    confidence: str
    note: str

    @property
    def verified(self) -> bool:
        return self.status == "verified"

    def as_line(self) -> str:
        flag = "" if self.verified else "  ⟨示意資料·待驗證⟩"
        return (
            f"  • {self.label}：{self.point:.0%} "
            f"[區間 {self.low:.0%}–{self.high:.0%}]{flag}"
        )


@dataclass(frozen=True)
class FactField:
    """A specific fact we collect about THIS participant's situation.

    Fact-binding is the core anti-Barnum mechanism: every reflection prompt must
    quote these, never emit generic statements (see ADR-005).
    """

    key: str
    question: str


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    prompt: str
    options: tuple[str, ...]
    base_rates: tuple[BaseRate, ...]
    fact_fields: tuple[FactField, ...]


def _load_base_rates(scenario_id: str, *, all_statuses: bool = False) -> tuple[BaseRate, ...]:
    """Load base rates for a scenario.

    By default returns only DISPLAYABLE rates (status='verified'). Rates marked
    'no_reliable_data' are honestly omitted from what participants see (research
    found no trustworthy number — showing 0% would be worse than showing nothing).
    'needs_source' placeholders are also excluded from display but flagged by
    verify_base_rates(). Pass all_statuses=True to inspect every entry.
    """
    data = json.loads(_BASE_RATES_PATH.read_text(encoding="utf-8"))
    entries = data.get(scenario_id, {}).get("base_rates", [])
    rates = tuple(
        BaseRate(
            label=e["label"],
            point=e["point"],
            low=e["low"],
            high=e["high"],
            status=e.get("status", "needs_source"),
            source=e.get("source", ""),
            url=e.get("url", ""),
            confidence=e.get("confidence", "none"),
            note=e.get("note", ""),
        )
        for e in entries
    )
    if all_statuses:
        return rates
    return tuple(r for r in rates if r.verified)


# --- Scenario definitions (text) -------------------------------------------

_SCENARIO_TEXT = {
    "relocation": dict(
        title="要不要接受海外外派？",
        prompt=(
            "你收到一個為期三年的海外外派機會，薪資更高但要離開現有生活圈。"
            "你正在決定要不要接受。"
        ),
        options=("接受外派", "婉拒留任"),
        fact_fields=(
            FactField("driver", "你最想透過這次外派得到什麼？（一句話）"),
            FactField("fear", "你最擔心失去或搞砸的是什麼？（一句話）"),
            FactField("constraint", "有哪個現實限制讓你猶豫？（一句話）"),
        ),
    ),
    "retirement_4pct": dict(
        title="退休後要不要採用「每年提領 4%」的計畫？",
        prompt=(
            "你即將退休，有一筆退休儲蓄。顧問建議採用「第一年提領 4%、之後每年隨通膨調整」"
            "的計畫；你也可以更保守地只提領 3%（花得少但更安全）。你正在決定。"
        ),
        options=("採用 4% 計畫", "改採更保守的 3%"),
        fact_fields=(
            FactField("driver", "你最希望退休生活能做到什麼？（一句話）"),
            FactField("fear", "你最擔心的財務風險是什麼？（一句話）"),
            FactField("constraint", "有什麼現實因素影響你的提領需求？（一句話）"),
        ),
    ),
    "quit_smoking": dict(
        title="要戒菸，要不要使用藥物（如 varenicline）輔助？",
        prompt=(
            "你決定戒菸。醫師提到可以用 varenicline 這類處方藥輔助，也可以只靠意志力。"
            "你正在決定要不要用藥物輔助。"
        ),
        options=("用藥物輔助", "只靠意志力"),
        fact_fields=(
            FactField("driver", "你最想透過戒菸得到什麼？（一句話）"),
            FactField("fear", "你最擔心戒菸失敗的原因是什麼？（一句話）"),
            FactField("constraint", "有什麼讓你猶豫用藥的考量？（一句話）"),
        ),
    ),
}


def get_scenario(scenario_id: str) -> Scenario:
    if scenario_id not in _SCENARIO_TEXT:
        raise KeyError(f"unknown scenario: {scenario_id}")
    text = _SCENARIO_TEXT[scenario_id]
    return Scenario(
        id=scenario_id,
        title=text["title"],
        prompt=text["prompt"],
        options=text["options"],
        base_rates=_load_base_rates(scenario_id),
        fact_fields=text["fact_fields"],
    )


def list_scenario_ids() -> tuple[str, ...]:
    return tuple(_SCENARIO_TEXT.keys())


def verify_base_rates() -> list[str]:
    """Return human-readable problems: any base rate still a PLACEHOLDER
    (status='needs_source'). 'no_reliable_data' is an honest decision to omit a
    rate (not a blocker); 'verified' is ready. Empty list == ready for a real run.
    """
    problems: list[str] = []
    for sid in list_scenario_ids():
        for rate in _load_base_rates(sid, all_statuses=True):
            if rate.status == "needs_source":
                problems.append(f"[{sid}] 未驗證基準率（佔位假數據）：{rate.label}")
    return problems
