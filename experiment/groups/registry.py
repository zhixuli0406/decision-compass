"""Group registry + randomized assignment."""
from __future__ import annotations

import random

from ..core.intervention import Intervention
from .group_a import GroupA
from .group_b import GroupB
from .group_c import GroupC
from .group_d import GroupD

GROUPS: dict[str, type[Intervention]] = {
    "A": GroupA,
    "B": GroupB,
    "C": GroupC,
    "D": GroupD,
}


def build(group_id: str) -> Intervention:
    group_id = group_id.upper()
    if group_id not in GROUPS:
        raise KeyError(f"unknown group: {group_id} (expected one of {list(GROUPS)})")
    return GROUPS[group_id]()


def assign(rng: random.Random) -> Intervention:
    """Random allocation across the four arms."""
    return build(rng.choice(list(GROUPS)))
