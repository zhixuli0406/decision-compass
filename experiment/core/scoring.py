"""Analysis primitives: Brier score, calibration, and the per-group summary that
maps onto the pre-registered judgement rules in MVP-EXPERIMENT.md.

The PRIMARY outcome is calibration (Brier) measured against real follow-up
results — NOT self-reported usefulness, which is exactly what Barnum inflates.
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


def brier_score(probability: float, went_well: bool) -> float:
    """Lower is better. (p - y)^2 with y in {0, 1}."""
    y = 1.0 if went_well else 0.0
    return (probability - y) ** 2


@dataclass(frozen=True)
class GroupSummary:
    group_id: str
    n: int
    mean_outcome_probability: float | None
    mean_predicted_satisfaction: float | None
    mean_misattribution_gap: float | None  # own - swapped fit
    mean_brier: float | None               # needs follow-up outcomes
    satisfaction_abs_error: float | None   # |predicted - actual|, needs follow-up

    def as_row(self) -> str:
        def fmt(value, spec="6.3f"):
            return "  n/a " if value is None else format(value, spec)

        return (
            f"  {self.group_id:<2}  n={self.n:<3}  "
            f"P(好結果)={fmt(self.mean_outcome_probability, '5.2f')}  "
            f"預測滿意={fmt(self.mean_predicted_satisfaction, '4.1f')}  "
            f"巴納姆gap={fmt(self.mean_misattribution_gap, '5.2f')}  "
            f"Brier={fmt(self.mean_brier)}  "
            f"滿意誤差={fmt(self.satisfaction_abs_error, '4.1f')}"
        )


def _safe_mean(values: list[float]) -> float | None:
    return mean(values) if values else None


def summarize_group(
    group_id: str, results: list[dict], outcomes: dict[str, dict]
) -> GroupSummary:
    probs: list[float] = []
    sats: list[float] = []
    gaps: list[float] = []
    briers: list[float] = []
    sat_errors: list[float] = []

    for row in results:
        probs.append(row["outcome_probability"])
        sats.append(row["predicted_satisfaction"])
        if row.get("misattribution_gap") is not None:
            gaps.append(row["misattribution_gap"])

        outcome = outcomes.get(row["participant_id"])
        if outcome is not None:
            briers.append(brier_score(row["outcome_probability"], outcome["went_well"]))
            if "actual_satisfaction" in outcome:
                sat_errors.append(
                    abs(row["predicted_satisfaction"] - outcome["actual_satisfaction"])
                )

    return GroupSummary(
        group_id=group_id,
        n=len(results),
        mean_outcome_probability=_safe_mean(probs),
        mean_predicted_satisfaction=_safe_mean(sats),
        mean_misattribution_gap=_safe_mean(gaps),
        mean_brier=_safe_mean(briers),
        satisfaction_abs_error=_safe_mean(sat_errors),
    )


def interpret(summaries: dict[str, GroupSummary]) -> list[str]:
    """Translate numbers into the pre-registered judgement hints.
    Honest hedging: with no follow-up outcomes, calibration verdicts are withheld.
    """
    notes: list[str] = []
    a, b, c, d = (summaries.get(g) for g in ("A", "B", "C", "D"))

    if a and c and a.mean_misattribution_gap is not None and c.mean_misattribution_gap is not None:
        if a.mean_misattribution_gap - c.mean_misattribution_gap >= 1.0:
            notes.append(
                "✅ 巴納姆檢查：A 的『錯置回饋落差』明顯大於 C → A 的反思綁定具體事實，"
                "不是通用巴納姆語句。"
            )
        else:
            notes.append(
                "⚠️ 巴納姆檢查：A 與 C 的錯置落差相近 → A 的『有用感』可能來自巴納姆，"
                "需重新設計 Layer 2。"
            )

    have_brier = a and a.mean_brier is not None
    if not have_brier:
        notes.append(
            "ℹ️ 尚無 3 個月追蹤結果，校準度（主指標 Brier）暫不裁決。"
            "請收集 outcomes 後重跑 analyze。"
        )
    else:
        if a and d and a.mean_brier is not None and d.mean_brier is not None:
            if a.mean_brier < d.mean_brier:
                notes.append("✅ 校準度：A 的 Brier 優於 D（完整羅盤優於無介入）。")
            else:
                notes.append("❌ 校準度：A 未優於 D → 核心假設受質疑，回到研究。")
        if a and c and a.mean_brier is not None and c.mean_brier is not None:
            if a.mean_brier < c.mean_brier:
                notes.append("✅ A 校準度優於 C → 去偏誤協議帶來真價值（非純占卜）。")
            else:
                notes.append("⚠️ A ≈ C 或更差 → 真價值存疑。")
    return notes
