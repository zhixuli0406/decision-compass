"""The I Ching symbol interface for group A — a ZERO-COMPUTE lookup table.

Per ADR-003 and RESEARCH-FOUNDATION §3: the hexagram carries NO predictive
content and NO mathematical/computational power. Empirically, the King Wen
sequence has zero computational value (arXiv:2604.09234). Here a hexagram is
nothing more than a human-readable label that *triggers* a reflection — a UI
shuffle, never divination.

draw_hexagram() is DETERMINISTIC from a seed precisely so it cannot pretend to
be a mystical draw. The mapping below is a small prototype subset of the 64.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Hexagram:
    number: int
    name_zh: str
    name_en: str
    reflection_trigger: str  # which reflection theme this label surfaces


# Prototype subset. The trigger text is generic-by-theme on purpose, but in
# group A it only ever PREFIXES the fact-bound debiasing protocol; it never
# stands alone as advice (that would be the Barnum failure mode = group C).
HEXAGRAMS: tuple[Hexagram, ...] = (
    Hexagram(1, "乾", "The Creative", "若一切順利推進，你是否高估了自己的掌控度？"),
    Hexagram(2, "坤", "The Receptive", "若選擇承接與等待，你在等的是什麼條件成熟？"),
    Hexagram(3, "屯", "Difficulty at the Beginning", "起步的混亂，哪些是暫時的、哪些是結構性的？"),
    Hexagram(29, "坎", "The Abysmal", "你正面對的風險，最壞情況具體長什麼樣？"),
    Hexagram(47, "困", "Oppression", "什麼情況會讓你被困住、進退不得？"),
    Hexagram(64, "未濟", "Before Completion", "在尚未完成之前，哪一步沒走好會前功盡棄？"),
)


def draw_hexagram(seed: str) -> Hexagram:
    """Deterministic, non-mystical selection from `seed`.

    Using a hash makes the pick reproducible and explicitly arbitrary — it has
    no bearing on the outcome and must never be presented as if it did.
    """
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(HEXAGRAMS)
    return HEXAGRAMS[index]


DISCLAIMER = (
    "（以下卦象僅作為觸發反思的符號標籤，無任何預測力。"
    "它幫你想得更全，不告訴你結果。）"
)
