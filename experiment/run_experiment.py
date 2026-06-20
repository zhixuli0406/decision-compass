"""Driver for the four-arm MVP experiment.

Shared flow (identical for every group; groups differ only via their hooks):
  1. intro + consent
  2. present scenario
  3. collect the participant's specific facts (fact-binding = anti-Barnum)
  4. Layer 1 probability  (groups A, B only)
  5. Layer 2 reflection   (A=protocol+symbol, B=protocol, C=barnum, D=none)
  6. capture decision + forecast (choice, 1yr satisfaction, P(goes well))
  7. misattribution test  (own vs swapped reflective output)
  8. log immutable SessionResult to JSONL

Usage:
  python3 -m experiment.run_experiment --participant p001 --group A --scenario relocation
  python3 -m experiment.run_experiment --simulate            # auto-runs one of each group
"""
from __future__ import annotations

import argparse
import datetime as _dt
import random

from .core.io_adapter import InteractivePrompter, Prompter, ScriptedPrompter
from .core.logbook import append_result
from .core.scenario import get_scenario, list_scenario_ids, verify_base_rates
from .core.session import InteractionRecord, SessionDraft, SessionResult
from .groups import registry

DEFAULT_DATA = "experiment/data/results.jsonl"


def _now_iso(rng: random.Random) -> str:
    # Date.now()-free environments: derive a stable-ish stamp; real runs use utcnow.
    try:
        return _dt.datetime.now(_dt.UTC).isoformat()
    except Exception:  # pragma: no cover - fallback for restricted sandboxes
        return f"sim-{rng.randint(10**6, 10**7)}"


def run_session(
    *,
    participant_id: str,
    intervention,
    scenario_id: str,
    prompter: Prompter,
    rng: random.Random,
) -> SessionResult:
    scenario = get_scenario(scenario_id)
    draft = SessionDraft(
        participant_id=participant_id,
        group_id=intervention.group_id,
        scenario_id=scenario_id,
    )

    # 1-2 intro + scenario
    prompter.show(f"\n=== 決策羅盤實驗 · 組別 {intervention.group_id} ===")
    prompter.show(f"情境：{scenario.title}\n{scenario.prompt}")
    prompter.show("選項：" + " / ".join(scenario.options))

    # 3 collect facts
    facts: dict[str, str] = {}
    for field in scenario.fact_fields:
        facts[field.key] = prompter.ask(field.question)
    draft = draft.with_facts(facts)

    # 4 Layer 1 probability (A, B)
    if intervention.shows_probability:
        prompter.show("\n📊 Layer 1 統計事實（群體基準，非你個人的命運預測）：")
        for rate in scenario.base_rates:
            prompter.show(rate.as_line())
        prompter.show("  ⚠️ 個體結果存在不可化約誤差（R²<0.2）；以上為群體概率，不是你的結局。")
        draft = draft.add(
            InteractionRecord(step="layer1_probability", prompt=scenario.id,
                              response=[r.point for r in scenario.base_rates])
        )

    # 5 Layer 2 reflection
    prompter.show("\n🧭 Layer 2 反思：")
    draft = draft.add(*intervention.reflect(prompter, facts, scenario))

    # 6 decision + forecast
    prompter.show("\n✍️ 你的決策（由你決定，工具不替你決定）：")
    choice = prompter.ask("你的決定是？（" + " / ".join(scenario.options) + "）")
    predicted_satisfaction = prompter.ask_scale("你預測一年後對此決定的滿意度", 1, 10)
    outcome_probability = prompter.ask_prob("你認為這個決定『最終會走得好』的機率")

    # 7 misattribution test
    own_fit, swapped_fit = _misattribution_test(
        prompter, intervention, facts, rng
    )

    result = draft.finalize(
        choice=choice,
        predicted_satisfaction=predicted_satisfaction,
        outcome_probability=outcome_probability,
        own_fit_score=own_fit,
        swapped_fit_score=swapped_fit,
        timestamp=_now_iso(rng),
    )
    return result


def _misattribution_test(
    prompter: Prompter, intervention, facts: dict[str, str], rng: random.Random
) -> tuple[int | None, int | None]:
    """Show the participant their OWN reflective output and a SWAPPED one
    (built from someone else's facts), each rated 1-5 for fit.
    Fact-bound output (A, B) -> swapped fits worse -> large gap.
    Generic output (C)       -> swapped fits the same -> small gap.
    Group D has no output -> skipped.
    """
    own = intervention.reflective_output(facts, seed="|".join(facts.values()))
    if own is None:
        return None, None

    # A plausible "other participant" with different facts.
    other_facts = {
        "driver": "更高的收入",
        "fear": "離開熟悉的人際圈",
        "constraint": "家人短期內無法搬遷",
    }
    swapped = intervention.reflective_output(other_facts, seed="other-participant")

    prompter.show("\n🔎 錯置回饋測試（巴納姆汙染檢查）：")
    prompter.show(f"[甲] {own}")
    own_fit = prompter.ask_scale("『甲』有多貼合你的真實處境", 1, 5)
    prompter.show(f"[乙] {swapped}")
    swapped_fit = prompter.ask_scale("『乙』有多貼合你的真實處境", 1, 5)
    return own_fit, swapped_fit


def _simulate(data_path: str, seed: int) -> None:
    rng = random.Random(seed)
    print("[simulate] 跑一次 A/B/C/D 四組的完整管線（僅驗證流程，非實驗數據）")
    for i, group_id in enumerate(("A", "B", "C", "D")):
        prompter = ScriptedPrompter(rng)
        result = run_session(
            participant_id=f"sim-{group_id}-{i}",
            intervention=registry.build(group_id),
            scenario_id="retirement_4pct",
            prompter=prompter,
            rng=rng,
        )
        append_result(data_path, result)
        gap = result.misattribution_gap
        print(
            f"  ✓ 組 {group_id}: 決定={result.choice!r} "
            f"P(好結果)={result.outcome_probability:.2f} "
            f"巴納姆gap={gap if gap is not None else 'n/a'} "
            f"互動數={len(result.interactions)}"
        )
    print(f"[simulate] 已寫入 {data_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Decision Compass — 四組 MVP 實驗跑測器")
    parser.add_argument("--participant", help="參與者 ID")
    parser.add_argument("--group", help="A/B/C/D；省略則隨機分派")
    parser.add_argument("--scenario", default="retirement_4pct",
                        choices=list_scenario_ids(), help="決策情境")
    parser.add_argument("--data", default=DEFAULT_DATA, help="結果 JSONL 輸出路徑")
    parser.add_argument("--seed", type=int, default=42, help="隨機種子（分派/模擬）")
    parser.add_argument("--simulate", action="store_true",
                        help="自動跑四組驗證管線，不需真人")
    parser.add_argument("--allow-unverified", action="store_true",
                        help="允許在基準率尚未驗證下進行真實跑測（不建議）")
    args = parser.parse_args()

    if args.simulate:
        _simulate(args.data, args.seed)
        return

    # Launch gate: real runs must not show placeholder base rates to participants.
    problems = verify_base_rates()
    if problems and not args.allow_unverified:
        print("⛔ 發射閘門：基準率尚未驗證，無法對真實受試者展示假數據。")
        for problem in problems:
            print(f"   - {problem}")
        print("   → 請先在 base_rates.json 填入真實來源並設 status='verified'，")
        print("     或加 --allow-unverified 僅供內部測試（資料不可用於正式研究）。")
        raise SystemExit(2)

    rng = random.Random(args.seed)
    if not args.participant:
        parser.error("互動模式需要 --participant")
    intervention = registry.build(args.group) if args.group else registry.assign(rng)
    result = run_session(
        participant_id=args.participant,
        intervention=intervention,
        scenario_id=args.scenario,
        prompter=InteractivePrompter(),
        rng=rng,
    )
    append_result(args.data, result)
    print(f"\n已記錄。組別={result.group_id}，寫入 {args.data}")
    print("（3 個月後請用 follow-up 範本回填真實結果，再跑 analyze。）")


if __name__ == "__main__":
    main()
