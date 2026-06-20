"""Self-pilot mode — use the full compass (group A) on YOUR OWN real decision.

This is NOT a scientific test of the hypothesis. With N=1 and full knowledge of
the design, you cannot blind yourself or compare groups — self-runs are for
(1) dogfooding the instrument, and (2) starting a personal decision journal you
calibrate against reality in ~3 months. Output is explicitly labelled
non-evidential.

Run:
  python3 -m experiment.self_pilot                       # your own custom decision
  python3 -m experiment.self_pilot --scenario relocation # use a canned scenario (Layer 1 shown, flagged)
  python3 -m experiment.self_pilot --simulate            # pipeline self-test
"""
from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta, timezone

from .core.hexagram import DISCLAIMER, draw_hexagram
from .core.io_adapter import InteractivePrompter, Prompter, ScriptedPrompter
from .core.logbook import append_result
from .core.reflection import debiasing_protocol, reflective_summary
from .core.scenario import BaseRate, FactField, Scenario, get_scenario, list_scenario_ids
from .core.session import InteractionRecord, SessionDraft, SessionResult

JOURNAL = "experiment/data/self_journal.jsonl"
_FACT_FIELDS = (
    FactField("driver", "你最想透過這個決定得到什麼？（一句話）"),
    FactField("fear", "你最擔心失去或搞砸的是什麼？（一句話）"),
    FactField("constraint", "有哪個現實限制讓你猶豫？（一句話）"),
)


def _custom_scenario(prompter: Prompter) -> Scenario:
    """Build a scenario from a real decision the user is facing.

    No Layer 1 base rates: most personal decisions have no clean reference class,
    and inventing one would be dishonest (the 'black swan gatekeeper', ARCHITECTURE §1.3).
    """
    prompter.show("\n先描述你『真實正在面對』的決定：")
    title = prompter.ask("一句話說這個決定是什麼？")
    opt1 = prompter.ask("選項 A 是？")
    opt2 = prompter.ask("選項 B 是？")
    return Scenario(
        id="custom",
        title=title,
        prompt="（你自訂的真實決定）",
        options=(opt1, opt2),
        base_rates=(),  # honest: no reliable reference class for a one-off personal decision
        fact_fields=_FACT_FIELDS,
    )


def run_self_pilot(
    *, scenario: Scenario, prompter: Prompter, rng: random.Random, participant_id: str
) -> SessionResult:
    prompter.show("\n=== 決策羅盤 · 自我試用（A 組完整羅盤）===")
    prompter.show("⚠️ 這是個人試用與決策日誌，不是科學實驗數據（N=1，無對照）。")
    prompter.show(f"\n決定：{scenario.title}")
    prompter.show("選項：" + " / ".join(scenario.options))

    draft = SessionDraft(
        participant_id=participant_id, group_id="A-self", scenario_id=scenario.id
    )

    # facts
    facts: dict[str, str] = {}
    for field in scenario.fact_fields:
        facts[field.key] = prompter.ask(field.question)
    draft = draft.with_facts(facts)

    # Layer 1 (only if the scenario actually has a reference class)
    if scenario.base_rates:
        prompter.show("\n📊 群體基準（非你個人的命運預測）：")
        for rate in scenario.base_rates:
            prompter.show(rate.as_line())
        prompter.show("  ⚠️ 個體結果有不可化約誤差；群體概率不是你的結局。")
        draft = draft.add(InteractionRecord(
            step="layer1_probability", prompt=scenario.id,
            response=[r.point for r in scenario.base_rates]))
    else:
        prompter.show("\n📊 此決定沒有可靠的群體參照類別 → 誠實略過 Layer 1 概率。")

    # Layer 2 — full compass: hexagram trigger + debiasing protocol
    prompter.show("\n🧭 反思：")
    hexagram = draw_hexagram(seed="|".join(facts.values()))
    prompter.show(DISCLAIMER)
    prompter.show(
        f"🧭 第 {hexagram.number} 卦「{hexagram.name_zh}」"
        f"（{hexagram.name_en}）：{hexagram.reflection_trigger}"
    )
    draft = draft.add(InteractionRecord(step="hexagram", prompt=hexagram.name_zh, response=hexagram.number))
    for prompt in debiasing_protocol(facts, scenario.base_rates):
        answer = prompter.ask(prompt.text)
        draft = draft.add(InteractionRecord(
            step=f"reflect:{prompt.technique}", prompt=prompt.text, response=answer))

    # decision + forecast (the journal's calibration anchor)
    prompter.show("\n✍️ 你的決定（工具不替你決定）：")
    choice = prompter.ask("你的決定是？（" + " / ".join(scenario.options) + "）")
    predicted_satisfaction = prompter.ask_scale("你預測一年後對此決定的滿意度", 1, 10)
    outcome_probability = prompter.ask_prob("你認為這個決定『最終會走得好』的機率")

    # personal Barnum self-check (own vs swapped reflective summary)
    own = reflective_summary(facts)
    swapped = reflective_summary(
        {"driver": "更高的收入", "fear": "離開熟悉的人際圈", "constraint": "家人短期內無法搬遷"}
    )
    prompter.show("\n🔎 個人巴納姆自檢（你知道答案，所以這只是提醒，不是測量）：")
    prompter.show(f"[甲·你的] {own}")
    own_fit = prompter.ask_scale("『甲』有多貼合你", 1, 5)
    prompter.show(f"[乙·別人的] {swapped}")
    swapped_fit = prompter.ask_scale("『乙』有多貼合你", 1, 5)

    return draft.finalize(
        choice=choice,
        predicted_satisfaction=predicted_satisfaction,
        outcome_probability=outcome_probability,
        own_fit_score=own_fit,
        swapped_fit_score=swapped_fit,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _follow_up_date() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=90)).date().isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(description="決策羅盤 · 自我試用 / 個人決策日誌")
    parser.add_argument("--scenario", choices=list_scenario_ids(),
                        help="用內建情境（會顯示示意基準率）；省略則自訂你的真實決定")
    parser.add_argument("--id", default="self", help="你的個人代號（日誌用）")
    parser.add_argument("--data", default=JOURNAL)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--simulate", action="store_true", help="管線自測，不需真人")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    if args.simulate:
        prompter: Prompter = ScriptedPrompter(rng)
        scenario = get_scenario("relocation")
    else:
        prompter = InteractivePrompter()
        scenario = get_scenario(args.scenario) if args.scenario else _custom_scenario(prompter)

    result = run_self_pilot(
        scenario=scenario, prompter=prompter, rng=rng, participant_id=args.id
    )
    append_result(args.data, result)

    follow_up = _follow_up_date()
    if args.simulate:
        print(f"[simulate] self-pilot OK，gap={result.misattribution_gap}，寫入 {args.data}")
        return
    print(f"\n✅ 已記進你的決策日誌：{args.data}")
    print(f"   決定：{result.choice}　預測滿意={result.predicted_satisfaction}/10"
          f"　P(好結果)={result.outcome_probability:.0%}")
    print(f"\n📅 校準回訪日：{follow_up}（約 3 個月後）")
    print("   屆時回填真實結果，跑：")
    print(f"   python3 -m experiment.analyze --data {args.data} --outcomes experiment/data/outcomes.jsonl")
    print("   追蹤格式："
          f'{{"participant_id": "{args.id}", "went_well": true/false, "actual_satisfaction": 1-10}}')


if __name__ == "__main__":
    main()
