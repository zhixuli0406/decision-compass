"""Group C: the pure-Barnum control, plus the misattribution test used by all
groups that produce a reflective output.

Group C exists to MEASURE the Barnum baseline: generic, fact-free statements
that fit almost anyone (Forer 1949, RESEARCH-FOUNDATION §3). If group A's
"usefulness" is no better than group C's, then A's value is just Barnum and the
core hypothesis fails (see MVP-EXPERIMENT judgement rules).
"""
from __future__ import annotations

import hashlib

# Classic Forer-style statements: deliberately generic, reference NO specifics.
BARNUM_STATEMENTS: tuple[str, ...] = (
    "你內心其實渴望被他人認可，但對自己往往過於嚴苛。",
    "你有相當的潛能尚未發揮，這次的選擇正是轉機。",
    "表面上你看似自律，內心有時卻感到不安與懷疑。",
    "你傾向獨立思考，不喜歡未經驗證就接受別人的說法。",
    "近期的猶豫，反映你正處在一個重要的人生轉折點。",
    "順應時機而動，你會發現答案其實一直在你心中。",
)


def barnum_reading(seed: str, n: int = 3) -> tuple[str, ...]:
    """Pick a generic, fact-free 'reading'. The output is identical in spirit
    for everyone — that is the whole point of the control.
    """
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    start = int(digest, 16) % len(BARNUM_STATEMENTS)
    picked = [
        BARNUM_STATEMENTS[(start + i) % len(BARNUM_STATEMENTS)] for i in range(n)
    ]
    return tuple(picked)


def format_reading(lines: tuple[str, ...]) -> str:
    return "\n".join(f"  ◦ {line}" for line in lines)
