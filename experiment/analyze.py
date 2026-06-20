"""Post-hoc analysis: read results (+ optional follow-up outcomes) and report
per-group summaries against the pre-registered judgement rules.

Usage:
  python3 -m experiment.analyze
  python3 -m experiment.analyze --data experiment/data/results.jsonl \
                                --outcomes experiment/data/outcomes.jsonl
"""
from __future__ import annotations

import argparse
from collections import defaultdict

from .core.logbook import read_outcomes, read_results
from .core.scoring import interpret, summarize_group

DEFAULT_DATA = "experiment/data/results.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(description="Decision Compass — 結果分析")
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--outcomes", default=None,
                        help="3 個月追蹤 JSONL（含 went_well / actual_satisfaction）")
    args = parser.parse_args()

    results = read_results(args.data)
    outcomes = read_outcomes(args.outcomes) if args.outcomes else {}

    if not results:
        print(f"沒有資料：{args.data}（先跑 run_experiment 或 --simulate）")
        return

    by_group: dict[str, list[dict]] = defaultdict(list)
    for row in results:
        by_group[row["group_id"]].append(row)

    print(f"\n=== 分析（n={len(results)}，追蹤結果 {len(outcomes)} 筆）===")
    print("組別對照：A=完整羅盤  B=去符號  C=純巴納姆  D=無介入")
    print("-" * 88)
    summaries = {}
    for group_id in ("A", "B", "C", "D"):
        summary = summarize_group(group_id, by_group.get(group_id, []), outcomes)
        summaries[group_id] = summary
        print(summary.as_row())
    print("-" * 88)

    print("\n判讀（對照 MVP-EXPERIMENT.md 的事前註冊判準）：")
    for note in interpret(summaries):
        print(f"  {note}")
    print(
        "\n提醒：主指標是校準度（Brier），不是『使用者覺得有用』。"
        "自評有用可能只是巴納姆效應。"
    )


if __name__ == "__main__":
    main()
