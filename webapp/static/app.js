"use strict";
// Thin client: renders steps and POSTs to the server, which owns all experiment
// logic (group assignment, reflection content, logging). The UI never reveals
// the study hypotheses (see DEBRIEF for what is disclosed, and when).

const state = { token: null, group: null, scenario: null, reflections: {} };

function show(stepId) {
  document.querySelectorAll(".step").forEach((s) => s.classList.remove("active"));
  document.getElementById(stepId).classList.add("active");
  window.scrollTo(0, 0);
}

async function postJSON(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

// --- Step: consent ---------------------------------------------------------
const consentBox = document.getElementById("consent-box");
const btnConsent = document.getElementById("btn-consent");
consentBox.addEventListener("change", () => {
  btnConsent.disabled = !consentBox.checked;
});

btnConsent.addEventListener("click", async () => {
  const participant = document.getElementById("participant-id").value.trim();
  const { ok, status, data } = await postJSON("/api/start", {
    consent: true,
    participant_id: participant || null,
  });
  if (!ok) {
    const msg = document.getElementById("gate-msg");
    msg.classList.remove("hidden");
    msg.textContent =
      status === 423
        ? "研究尚未開放（基準率待驗證）。請稍後再試。"
        : status === 400
        ? "請先勾選同意。"
        : "無法開始，請稍後再試。";
    return;
  }
  state.token = data.token;
  state.group = data.group_id;
  state.scenario = data.scenario;
  renderFacts();
  show("step-facts");
});

// --- Step: scenario + facts ------------------------------------------------
function renderFacts() {
  const s = state.scenario;
  document.getElementById("scenario-title").textContent = s.title;
  document.getElementById("scenario-prompt").textContent = s.prompt;
  document.getElementById("scenario-options").textContent = s.options.join("　/　");
  const wrap = document.getElementById("fact-fields");
  wrap.innerHTML = "";
  s.fact_fields.forEach((f) => {
    const label = document.createElement("label");
    label.textContent = f.question;
    const input = document.createElement("input");
    input.type = "text";
    input.dataset.key = f.key;
    label.appendChild(input);
    wrap.appendChild(label);
  });
}

document.getElementById("btn-facts").addEventListener("click", async () => {
  const facts = {};
  document.querySelectorAll("#fact-fields input").forEach((i) => {
    facts[i.dataset.key] = i.value.trim();
  });
  state.facts = facts;
  const { data } = await postJSON("/api/reflect", { token: state.token, facts });
  renderReflect(data);
  show("step-reflect");
});

// --- Step: layer1 + layer2 -------------------------------------------------
function renderReflect(data) {
  const l1 = document.getElementById("layer1");
  if (data.shows_probability) {
    l1.classList.remove("hidden");
    const ul = document.getElementById("base-rates");
    ul.innerHTML = "";
    data.base_rates.forEach((r) => {
      const li = document.createElement("li");
      const flag = r.verified ? "" : " ⟨示意資料·待驗證⟩";
      li.textContent = `${r.label}：${Math.round(r.point * 100)}% [${Math.round(
        r.low * 100
      )}–${Math.round(r.high * 100)}%]${flag}`;
      ul.appendChild(li);
    });
    document.getElementById("individual-warning").textContent = data.individual_warning;
  } else {
    l1.classList.add("hidden");
  }

  const l2 = document.getElementById("layer2");
  l2.innerHTML = "";
  state.reflections = {};
  const spec = data.layer2;

  if (spec.type === "protocol") {
    if (spec.hexagram) {
      const h = document.createElement("div");
      h.className = "hexagram";
      h.innerHTML =
        `<p class="muted">${spec.hexagram.disclaimer}</p>` +
        `<p>🧭 第 ${spec.hexagram.number} 卦「${spec.hexagram.name_zh}」` +
        `（${spec.hexagram.name_en}）：${spec.hexagram.trigger}</p>`;
      l2.appendChild(h);
    }
    spec.prompts.forEach((p) => {
      const label = document.createElement("label");
      label.textContent = p.text;
      const ta = document.createElement("textarea");
      ta.dataset.key = p.technique;
      ta.rows = 3;
      label.appendChild(ta);
      l2.appendChild(label);
    });
  } else if (spec.type === "barnum") {
    const box = document.createElement("div");
    box.className = "reading";
    box.innerHTML =
      "🔮 為你解讀如下：<br>" + spec.lines.map((x) => "◦ " + x).join("<br>");
    l2.appendChild(box);
    const label = document.createElement("label");
    label.textContent = "讀完這段解讀，你打算怎麼做？（一句話）";
    const ta = document.createElement("textarea");
    ta.dataset.key = "barnum_response";
    ta.rows = 2;
    label.appendChild(ta);
    l2.appendChild(label);
  } else {
    const p = document.createElement("p");
    p.className = "muted";
    p.textContent = "（請直接進入決定。）";
    l2.appendChild(p);
  }
}

document.getElementById("btn-reflect").addEventListener("click", () => {
  document.querySelectorAll("#layer2 textarea").forEach((t) => {
    state.reflections[t.dataset.key] = t.value.trim();
  });
  renderDecision();
  show("step-decision");
});

// --- Step: decision --------------------------------------------------------
function renderDecision() {
  const wrap = document.getElementById("decision-options");
  wrap.innerHTML = "";
  state.scenario.options.forEach((opt) => {
    const id = "opt-" + opt;
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

document.getElementById("btn-decision").addEventListener("click", async () => {
  const choiceEl = document.querySelector('input[name="choice"]:checked');
  const sat = document.getElementById("satisfaction").value;
  const prob = document.getElementById("probability").value;
  if (!choiceEl || !sat || prob === "") {
    alert("請完成選擇與兩個數字。");
    return;
  }
  state.decision = {
    choice: choiceEl.value,
    predicted_satisfaction: parseInt(sat, 10),
    outcome_probability: parseFloat(prob) / 100,
  };
  const { data } = await postJSON("/api/misattribution", { token: state.token });
  if (!data.applicable) {
    await submitAll(null, null);
    show("step-debrief");
    return;
  }
  document.getElementById("mis-own").textContent = "[甲] " + data.own;
  document.getElementById("mis-swapped").textContent = "[乙] " + data.swapped;
  show("step-misattribution");
});

// --- Step: misattribution --------------------------------------------------
document.getElementById("btn-misattribution").addEventListener("click", async () => {
  const own = document.getElementById("own-fit").value;
  const swapped = document.getElementById("swapped-fit").value;
  if (!own || !swapped) {
    alert("請為甲、乙各評一個 1–5 的分數。");
    return;
  }
  await submitAll(parseInt(own, 10), parseInt(swapped, 10));
  show("step-debrief");
});

async function submitAll(ownFit, swappedFit) {
  await postJSON("/api/submit", {
    token: state.token,
    reflections: state.reflections,
    choice: state.decision.choice,
    predicted_satisfaction: state.decision.predicted_satisfaction,
    outcome_probability: state.decision.outcome_probability,
    own_fit: ownFit,
    swapped_fit: swappedFit,
  });
}
