"use strict";
// Self-contained data for the public tool. Mirrors experiment/core (base rates,
// hexagrams, debiasing prompts) so the site is a static, zero-backend deploy.
// Only VERIFIED base rates are included — honesty parity with the launch gate.

const DC = {};

// --- Scenarios (verified base rates only; custom has none on purpose) -------
DC.SCENARIOS = {
  retirement_4pct: {
    title: "退休後要不要採用「每年提領 4%」的計畫？",
    prompt:
      "你即將退休，有一筆退休儲蓄。顧問建議採用「第一年提領 4%、之後每年隨通膨調整」" +
      "的計畫；你也可以更保守地只提領 3%（花得少但更安全）。",
    options: ["採用 4% 計畫", "改採更保守的 3%"],
    factFields: [
      { key: "driver", q: "你最希望退休生活能做到什麼？（一句話）" },
      { key: "fear", q: "你最擔心的財務風險是什麼？（一句話）" },
      { key: "constraint", q: "有什麼現實因素影響你的提領需求？（一句話）" },
    ],
    baseRates: [
      {
        label: "「4% 提領計畫」在歷史 30 年期間不耗盡的成功率",
        point: 0.95, low: 0.64, high: 1.0,
        source: "Trinity Study 1998；Pfau/Finke 更新",
        note: "95% 是『歷史頻率』非『今日機率』。低利率 Monte Carlo 曾降到 64%、國際多數國家撐不住 4%。",
      },
    ],
  },
  quit_smoking: {
    title: "要戒菸，要不要使用藥物（如 varenicline）輔助？",
    prompt:
      "你決定戒菸。醫師提到可以用 varenicline 這類處方藥輔助，也可以只靠意志力。",
    options: ["用藥物輔助", "只靠意志力"],
    factFields: [
      { key: "driver", q: "你最想透過戒菸得到什麼？（一句話）" },
      { key: "fear", q: "你最擔心戒菸失敗的原因是什麼？（一句話）" },
      { key: "constraint", q: "有什麼讓你猶豫用藥的考量？（一句話）" },
    ],
    baseRates: [
      {
        label: "使用 varenicline 藥物，6 個月後仍持續戒菸的成功率",
        point: 0.23, low: 0.21, high: 0.25,
        source: "Cochrane 2023 (RR 2.32, NNT≈8)",
        note: "戒菸不易，數字是群體平均；若需要協助，請洽醫療專業或戒菸專線。",
      },
    ],
  },
  relocation: {
    title: "要不要接受海外外派？",
    prompt:
      "你收到一個為期三年的海外外派機會，薪資更高但要離開現有生活圈。",
    options: ["接受外派", "婉拒留任"],
    factFields: [
      { key: "driver", q: "你最想透過這次外派得到什麼？（一句話）" },
      { key: "fear", q: "你最擔心失去或搞砸的是什麼？（一句話）" },
      { key: "constraint", q: "有哪個現實限制讓你猶豫？（一句話）" },
    ],
    baseRates: [
      {
        label: "外派人員完成整個任期（不提前返國）的比例",
        point: 0.93, low: 0.9, high: 0.95,
        source: "Brookfield 2012（企業自報, n=123）",
        note: "經典『16-40% 失敗率』是無實證基礎的迷思（Harzing 1995）。",
      },
    ],
  },
};

// custom: a real decision the user is facing — no reliable reference class.
DC.CUSTOM_FACT_FIELDS = [
  { key: "driver", q: "你最想透過這個決定得到什麼？（一句話）" },
  { key: "fear", q: "你最擔心失去或搞砸的是什麼？（一句話）" },
  { key: "constraint", q: "有哪個現實限制讓你猶豫？（一句話）" },
];

// --- I Ching symbol interface: a ZERO-PREDICTION lookup label ---------------
DC.HEXAGRAMS = [
  { n: 1, zh: "乾", en: "The Creative", trigger: "若一切順利推進，你是否高估了自己的掌控度？" },
  { n: 2, zh: "坤", en: "The Receptive", trigger: "若選擇承接與等待，你在等的是什麼條件成熟？" },
  { n: 3, zh: "屯", en: "Difficulty at the Beginning", trigger: "起步的混亂，哪些是暫時的、哪些是結構性的？" },
  { n: 29, zh: "坎", en: "The Abysmal", trigger: "你正面對的風險，最壞情況具體長什麼樣？" },
  { n: 47, zh: "困", en: "Oppression", trigger: "什麼情況會讓你被困住、進退不得？" },
  { n: 64, zh: "未濟", en: "Before Completion", trigger: "在尚未完成之前，哪一步沒走好會前功盡棄？" },
];

DC.HEX_DISCLAIMER =
  "（以下卦象只是觸發反思的符號標籤，沒有任何預測力。它幫你想得更全，不告訴你結果。）";

// Deterministic, non-mystical pick from a seed string (FNV-1a hash).
DC.drawHexagram = function (seed) {
  let h = 0x811c9dc5;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = (h * 0x01000193) >>> 0;
  }
  return DC.HEXAGRAMS[h % DC.HEXAGRAMS.length];
};

// --- Debiasing protocol (ported from reflection.py; fact-bound = anti-Barnum) -
DC.debiasingPrompts = function (facts, baseRates) {
  const driver = facts.driver || "你想要的東西";
  const fear = facts.fear || "你擔心的事";
  const constraint = facts.constraint || "你的限制";
  const rateHint =
    baseRates && baseRates.length
      ? `${baseRates[0].label}：${Math.round(baseRates[0].point * 100)}%`
      : "（此決定沒有可靠的群體基準）";
  return [
    {
      technique: "consider_opposite",
      text:
        `【考慮相反】你說你最想得到「${driver}」。\n` +
        "請寫出 3 個具體情境，在其中這個決定反而讓你得不到它、甚至後悔。",
    },
    {
      technique: "premortem",
      text:
        `【事前驗屍】想像一年後，這個決定徹底失敗了，正是因為「${fear}」成真。\n` +
        "請回推：在做決定的當下，有哪些訊號其實已經能看出來？",
    },
    {
      technique: "outside_view",
      text:
        "【外部視角】先別管「我這次」，改問「像我這樣、有同樣限制" +
        `（${constraint}）的人，通常會怎樣」。\n參照：${rateHint}\n` +
        "請寫下：這個群體基準，和你心裡的預期差多少？為什麼？",
    },
  ];
};
