"use strict";
// Public tool flow — everyone gets the full compass (the real product).
// No group assignment, no Barnum control, no experiment artifacts. Journal lives
// in localStorage (zero data collection). Honesty guardrails kept throughout.

const JOURNAL_KEY = "decision-compass-journal";
const state = { scenarioId: null, scenario: null, facts: {}, reflections: {} };

function show(id) {
  document.querySelectorAll(".step").forEach((s) => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
  window.scrollTo(0, 0);
}

// --- Welcome: scenario picker ----------------------------------------------
function renderPicker() {
  const wrap = document.getElementById("scenario-picker");
  wrap.innerHTML = "";
  const items = [
    ["custom", "✏️ 我自己的決定", "用你真實正在猶豫的事"],
    ...Object.entries(DC.SCENARIOS).map(([id, s]) => [id, s.title, "範例（含真實統計基準）"]),
  ];
  items.forEach(([id, title, sub]) => {
    const b = document.createElement("button");
    b.className = "picker";
    b.innerHTML = `<strong>${title}</strong><span class="muted">${sub}</span>`;
    b.addEventListener("click", () => startScenario(id));
    wrap.appendChild(b);
  });
}

function startScenario(id) {
  state.scenarioId = id;
  state.facts = {};
  state.reflections = {};
  if (id === "custom") {
    show("step-custom");
    return;
  }
  state.scenario = DC.SCENARIOS[id];
  renderFacts();
  show("step-facts");
}

// --- Custom decision -------------------------------------------------------
document.getElementById("btn-custom").addEventListener("click", () => {
  const title = document.getElementById("custom-title").value.trim();
  const a = document.getElementById("custom-opt-a").value.trim();
  const b = document.getElementById("custom-opt-b").value.trim();
  if (!title || !a || !b) {
    alert("請填好決定與兩個選項。");
    return;
  }
  state.scenario = {
    title,
    prompt: "（你自訂的真實決定）",
    options: [a, b],
    factFields: DC.CUSTOM_FACT_FIELDS,
    baseRates: [], // honest: no reliable reference class for a one-off personal decision
  };
  renderFacts();
  show("step-facts");
});

// --- Facts -----------------------------------------------------------------
function renderFacts() {
  const s = state.scenario;
  document.getElementById("scenario-title").textContent = s.title;
  document.getElementById("scenario-prompt").textContent = s.prompt;
  document.getElementById("scenario-options").textContent = s.options.join("　/　");
  const wrap = document.getElementById("fact-fields");
  wrap.innerHTML = "";
  s.factFields.forEach((f) => {
    const label = document.createElement("label");
    label.textContent = f.q;
    const input = document.createElement("input");
    input.type = "text";
    input.dataset.key = f.key;
    label.appendChild(input);
    wrap.appendChild(label);
  });
}

document.getElementById("btn-facts").addEventListener("click", () => {
  const facts = {};
  document.querySelectorAll("#fact-fields input").forEach((i) => {
    facts[i.dataset.key] = i.value.trim();
  });
  state.facts = facts;
  renderReflect();
  show("step-reflect");
});

// --- Reflect: Layer 1 + Layer 2 (full compass) -----------------------------
function renderReflect() {
  const s = state.scenario;
  const l1 = document.getElementById("layer1");
  if (s.baseRates && s.baseRates.length) {
    l1.classList.remove("hidden");
    const ul = document.getElementById("base-rates");
    ul.innerHTML = "";
    s.baseRates.forEach((r) => {
      const li = document.createElement("li");
      li.innerHTML =
        `${r.label}：<strong>${Math.round(r.point * 100)}%</strong> ` +
        `[${Math.round(r.low * 100)}–${Math.round(r.high * 100)}%]` +
        `<br><span class="src">來源：${r.source}　${r.note}</span>`;
      ul.appendChild(li);
    });
  } else {
    l1.classList.add("hidden");
  }

  const l2 = document.getElementById("layer2");
  l2.innerHTML = "";
  state.reflections = {};

  // I Ching symbol: a fact-free LABEL that only prefixes the protocol.
  const hx = DC.drawHexagram(Object.values(state.facts).join("|") || state.scenario.title);
  const hbox = document.createElement("div");
  hbox.className = "hexagram";
  hbox.innerHTML =
    `<p class="muted">${DC.HEX_DISCLAIMER}</p>` +
    `<p>🧭 第 ${hx.n} 卦「${hx.zh}」（${hx.en}）：${hx.trigger}</p>`;
  l2.appendChild(hbox);

  DC.debiasingPrompts(state.facts, state.scenario.baseRates).forEach((p) => {
    const label = document.createElement("label");
    label.textContent = p.text;
    const ta = document.createElement("textarea");
    ta.dataset.key = p.technique;
    ta.rows = 3;
    label.appendChild(ta);
    l2.appendChild(label);
  });
}

document.getElementById("btn-reflect").addEventListener("click", () => {
  document.querySelectorAll("#layer2 textarea").forEach((t) => {
    state.reflections[t.dataset.key] = t.value.trim();
  });
  renderDecision();
  show("step-decision");
});

// --- Decision --------------------------------------------------------------
function renderDecision() {
  const wrap = document.getElementById("decision-options");
  wrap.innerHTML = "";
  state.scenario.options.forEach((opt) => {
    const label = document.createElement("label");
    label.className = "radio";
    const input = document.createElement("input");
    input.type = "radio";
    input.name = "choice";
    input.value = opt;
    label.appendChild(input);
    label.appendChild(document.createTextNode(" " + opt));
    wrap.appendChild(label);
  });
}

document.getElementById("btn-decision").addEventListener("click", () => {
  const choiceEl = document.querySelector('input[name="choice"]:checked');
  const sat = document.getElementById("satisfaction").value;
  const prob = document.getElementById("probability").value;
  if (!choiceEl || !sat || prob === "") {
    alert("請完成選擇與兩個數字。");
    return;
  }
  const entry = {
    ts: new Date().toISOString(),
    title: state.scenario.title,
    choice: choiceEl.value,
    predicted_satisfaction: parseInt(sat, 10),
    outcome_probability: parseFloat(prob) / 100,
    follow_up: followUpDate(),
  };
  saveEntry(entry);
  renderDone(entry);
  show("step-done");
});

// --- Journal (localStorage) ------------------------------------------------
function loadJournal() {
  try {
    return JSON.parse(localStorage.getItem(JOURNAL_KEY) || "[]");
  } catch {
    return [];
  }
}
function saveEntry(entry) {
  const j = loadJournal();
  j.push(entry);
  localStorage.setItem(JOURNAL_KEY, JSON.stringify(j));
}
function followUpDate() {
  const d = new Date();
  d.setDate(d.getDate() + 90);
  return d.toISOString().slice(0, 10);
}

function renderDone(entry) {
  document.getElementById("done-summary").innerHTML =
    `<strong>${entry.title}</strong><br>你的決定：${entry.choice}<br>` +
    `預測一年後滿意度：${entry.predicted_satisfaction}/10　` +
    `你給的「會走得好」機率：${Math.round(entry.outcome_probability * 100)}%`;
  document.getElementById("follow-up").textContent = entry.follow_up + "（約 3 個月後）";
}

function renderJournal() {
  const list = document.getElementById("journal-list");
  const j = loadJournal().slice().reverse();
  if (!j.length) {
    list.innerHTML = '<p class="muted">還沒有任何紀錄。</p>';
    return;
  }
  list.innerHTML = "";
  j.forEach((e) => {
    const div = document.createElement("div");
    div.className = "reading";
    div.innerHTML =
      `<strong>${e.title}</strong><br>` +
      `決定：${e.choice}　|　預測滿意 ${e.predicted_satisfaction}/10　|　` +
      `P(好結果) ${Math.round(e.outcome_probability * 100)}%<br>` +
      `<span class="muted">記於 ${e.ts.slice(0, 10)}　·　校準回訪 ${e.follow_up}</span>`;
    list.appendChild(div);
  });
}

document.getElementById("btn-restart").addEventListener("click", () => {
  renderPicker();
  show("step-welcome");
});
document.getElementById("btn-journal").addEventListener("click", () => {
  renderJournal();
  show("step-journal");
});
document.getElementById("btn-back").addEventListener("click", () => show("step-done"));

// --- init ------------------------------------------------------------------
renderPicker();
