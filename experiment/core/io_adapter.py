"""IO abstraction so the same session flow runs interactively or simulated.

InteractivePrompter   -> real human via stdin/stdout.
ScriptedPrompter      -> deterministic auto-answers for end-to-end pipeline tests
                         (--simulate). Simulated runs validate the plumbing only;
                         they must NEVER be treated as experimental findings.
"""
from __future__ import annotations

import random


class Prompter:
    """Interface every prompter implements."""

    def show(self, text: str) -> None:
        raise NotImplementedError

    def ask(self, text: str) -> str:
        raise NotImplementedError

    def ask_scale(self, text: str, lo: int = 1, hi: int = 10) -> int:
        raise NotImplementedError

    def ask_prob(self, text: str) -> float:
        """Return a probability in [0, 1]."""
        raise NotImplementedError


class InteractivePrompter(Prompter):
    def show(self, text: str) -> None:
        print(text)

    def ask(self, text: str) -> str:
        return input(f"{text}\n> ").strip()

    def ask_scale(self, text: str, lo: int = 1, hi: int = 10) -> int:
        while True:
            raw = self.ask(f"{text}（{lo}-{hi}）")
            try:
                value = int(raw)
            except ValueError:
                print(f"請輸入 {lo}-{hi} 的整數。")
                continue
            if lo <= value <= hi:
                return value
            print(f"請輸入 {lo}-{hi} 的整數。")

    def ask_prob(self, text: str) -> float:
        while True:
            raw = self.ask(f"{text}（0-100，可不含 % 號）")
            try:
                pct = float(raw.rstrip("%").strip())
            except ValueError:
                print("請輸入 0-100 的數字。")
                continue
            if 0.0 <= pct <= 100.0:
                return pct / 100.0
            print("請輸入 0-100 的數字。")


class ScriptedPrompter(Prompter):
    """Deterministic auto-responder for --simulate pipeline checks."""

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng
        self._counter = 0
        self.transcript: list[tuple] = []

    def show(self, text: str) -> None:
        self.transcript.append(("show", text))

    def ask(self, text: str) -> str:
        self._counter += 1
        answer = f"（模擬回答 #{self._counter}）"
        self.transcript.append(("ask", text, answer))
        return answer

    def ask_scale(self, text: str, lo: int = 1, hi: int = 10) -> int:
        value = self._rng.randint(lo, hi)
        self.transcript.append(("scale", text, value))
        return value

    def ask_prob(self, text: str) -> float:
        value = round(self._rng.random(), 2)
        self.transcript.append(("prob", text, value))
        return value
