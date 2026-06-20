"""Deployable web version of the four-arm MVP experiment.

Zero dependencies (Python stdlib http.server). The server OWNS the experiment
logic (reusing experiment/core) and the browser is a thin client that renders
steps and POSTs responses. This keeps the randomization, group logic, and
logging server-side and tamper-resistant.

Run:
  python3 -m webapp.server                 # http://127.0.0.1:8000
  PORT=8080 python3 -m webapp.server

⚠️ The stdlib server speaks plain HTTP and has no auth/rate-limiting. For real
online recruitment it MUST sit behind HTTPS (TLS) + a reverse proxy. See
webapp/README.md. Do NOT collect real participant data over plain HTTP.
"""
from __future__ import annotations

import json
import os
import random
import secrets
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from experiment.core import barnum, hexagram
from experiment.core.logbook import append_result
from experiment.core.reflection import debiasing_protocol, reflective_summary
from experiment.core.scenario import get_scenario, list_scenario_ids, verify_base_rates
from experiment.core.session import InteractionRecord, SessionDraft
from experiment.groups import registry

_STATIC = Path(__file__).with_name("static")
_DATA = os.environ.get("DC_DATA", "experiment/data/web_results.jsonl")
_ALLOW_UNVERIFIED = os.environ.get("ALLOW_UNVERIFIED") == "1"
_DEFAULT_SCENARIO = "retirement_4pct"

# True randomization for group allocation (not seeded).
_RNG = random.SystemRandom()

# In-memory pending sessions: token -> dict. Completed sessions persist to JSONL.
# NOTE: restarting the server drops in-flight (not yet submitted) sessions.
_SESSIONS: dict[str, dict] = {}

_OTHER_FACTS = {
    "driver": "更高的收入",
    "fear": "離開熟悉的人際圈",
    "constraint": "家人短期內無法搬遷",
}


# --- Layer 2 content (declarative; browser renders) ------------------------

def _layer2_payload(group_id: str, facts: dict[str, str], scenario) -> dict:
    if group_id in ("A", "B"):
        prompts = [
            {"technique": p.technique, "text": p.text, "falsify": p.requires_falsification}
            for p in debiasing_protocol(facts, scenario.base_rates)
        ]
        payload = {"type": "protocol", "prompts": prompts}
        if group_id == "A":
            hx = hexagram.draw_hexagram(seed="|".join(facts.values()))
            payload["hexagram"] = {
                "number": hx.number, "name_zh": hx.name_zh,
                "name_en": hx.name_en, "trigger": hx.reflection_trigger,
                "disclaimer": hexagram.DISCLAIMER,
            }
        return payload
    if group_id == "C":
        return {"type": "barnum", "lines": list(barnum.barnum_reading(seed="|".join(facts.values())))}
    return {"type": "none"}


def _reflective_output(group_id: str, facts: dict[str, str], seed: str) -> str | None:
    if group_id in ("A", "B"):
        return reflective_summary(facts)
    if group_id == "C":
        return " ".join(barnum.barnum_reading(seed=seed))
    return None


# --- HTTP handler ----------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = "DecisionCompass/0.1"

    def log_message(self, *args):  # quieter logs
        pass

    # -- helpers --
    def _send_json(self, obj: dict, status: int = 200) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self._send_json({"error": "not found"}, 404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # -- routes --
    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._send_file(_STATIC / "index.html", "text/html; charset=utf-8")
        elif self.path == "/static/app.js":
            self._send_file(_STATIC / "app.js", "application/javascript; charset=utf-8")
        elif self.path == "/static/style.css":
            self._send_file(_STATIC / "style.css", "text/css; charset=utf-8")
        elif self.path == "/api/health":
            self._send_json({"ok": True, "unverified": verify_base_rates()})
        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self) -> None:
        try:
            if self.path == "/api/start":
                self._start()
            elif self.path == "/api/reflect":
                self._reflect()
            elif self.path == "/api/misattribution":
                self._misattribution()
            elif self.path == "/api/submit":
                self._submit()
            else:
                self._send_json({"error": "not found"}, 404)
        except Exception as exc:  # never leak stack to client
            self._send_json({"error": "server_error", "detail": str(exc)}, 500)

    def _start(self) -> None:
        # Launch gate: do not show placeholder base rates to real participants.
        problems = verify_base_rates()
        if problems and not _ALLOW_UNVERIFIED:
            self._send_json({"error": "base_rates_unverified", "problems": problems}, 423)
            return
        body = self._read_json()
        if not body.get("consent"):
            self._send_json({"error": "consent_required"}, 400)
            return
        scenario_id = body.get("scenario", _DEFAULT_SCENARIO)
        if scenario_id not in list_scenario_ids():
            scenario_id = _DEFAULT_SCENARIO
        intervention = registry.assign(_RNG)
        scenario = get_scenario(scenario_id)
        token = secrets.token_urlsafe(16)
        _SESSIONS[token] = {
            "participant_id": body.get("participant_id") or f"web-{token[:8]}",
            "group_id": intervention.group_id,
            "scenario_id": scenario_id,
            "facts": {},
        }
        self._send_json({
            "token": token,
            "group_id": intervention.group_id,  # for analysis; UI does not reveal hypotheses
            "scenario": {
                "id": scenario.id,
                "title": scenario.title,
                "prompt": scenario.prompt,
                "options": list(scenario.options),
                "fact_fields": [{"key": f.key, "question": f.question} for f in scenario.fact_fields],
            },
        })

    def _session(self, body: dict) -> dict | None:
        token = body.get("token")
        sess = _SESSIONS.get(token)
        if sess is None:
            self._send_json({"error": "invalid_token"}, 400)
            return None
        return sess

    def _reflect(self) -> None:
        body = self._read_json()
        sess = self._session(body)
        if sess is None:
            return
        facts = {k: str(v) for k, v in (body.get("facts") or {}).items()}
        sess["facts"] = facts
        scenario = get_scenario(sess["scenario_id"])
        intervention = registry.build(sess["group_id"])
        base_rates = [
            {"label": r.label, "point": r.point, "low": r.low, "high": r.high,
             "verified": r.verified}
            for r in scenario.base_rates
        ] if intervention.shows_probability else []
        self._send_json({
            "shows_probability": intervention.shows_probability,
            "base_rates": base_rates,
            "individual_warning": "個體結果存在不可化約誤差（R²<0.2）；以上為群體概率，不是你的結局。",
            "layer2": _layer2_payload(sess["group_id"], facts, scenario),
        })

    def _misattribution(self) -> None:
        body = self._read_json()
        sess = self._session(body)
        if sess is None:
            return
        facts = sess.get("facts", {})
        own = _reflective_output(sess["group_id"], facts, seed="|".join(facts.values()))
        swapped = _reflective_output(sess["group_id"], _OTHER_FACTS, seed="other-participant")
        self._send_json({"applicable": own is not None, "own": own, "swapped": swapped})

    def _submit(self) -> None:
        body = self._read_json()
        sess = self._session(body)
        if sess is None:
            return
        facts = sess.get("facts", {})
        scenario = get_scenario(sess["scenario_id"])
        draft = SessionDraft(
            participant_id=sess["participant_id"],
            group_id=sess["group_id"],
            scenario_id=sess["scenario_id"],
        ).with_facts(facts)

        # Record reflections + layer1 flag for the audit trail.
        if registry.build(sess["group_id"]).shows_probability:
            draft = draft.add(InteractionRecord(
                step="layer1_probability", prompt=scenario.id,
                response=[r.point for r in scenario.base_rates]))
        for key, value in (body.get("reflections") or {}).items():
            draft = draft.add(InteractionRecord(step=f"reflect:{key}", prompt=key, response=value))

        result = draft.finalize(
            choice=str(body.get("choice", "")),
            predicted_satisfaction=int(body.get("predicted_satisfaction", 0)),
            outcome_probability=float(body.get("outcome_probability", 0.0)),
            own_fit_score=_maybe_int(body.get("own_fit")),
            swapped_fit_score=_maybe_int(body.get("swapped_fit")),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        append_result(_DATA, result)
        _SESSIONS.pop(body.get("token"), None)
        self._send_json({"ok": True})


def _maybe_int(value) -> int | None:
    return None if value in (None, "") else int(value)


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    problems = verify_base_rates()
    if problems and not _ALLOW_UNVERIFIED:
        print("⚠️ 基準率尚未驗證；/api/start 會回 423 擋下真實受試者。")
        print("   僅供開發測試時，用 ALLOW_UNVERIFIED=1 啟動。")
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Decision Compass webapp → http://127.0.0.1:{port}  (Ctrl-C 結束)")
    print(f"結果寫入：{_DATA}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
