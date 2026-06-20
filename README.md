# Decision Compass（決策羅盤）

> 一個融合「統計概率引擎」與「結構化反思層」的決策輔助工具。
> 它**不是預言機**——它是羅盤：指方向、量化不確定性，而非預測命運。

## 核心定位（一句話）

> 在資訊有限、後果重大的個人決策情境下，用**有實證撐腰的統計概率**估計趨勢與風險區間，
> 再用**有 RCT 證據的去偏誤協議**強迫使用者做結構化反思——
> 易經符號只作為這套協議的「易讀符號介面」，**絕不承載任何預測力**。

## 為什麼叫「羅盤」而不是「水晶球」

三輪深度研究（見 [`docs/RESEARCH-FOUNDATION.md`](docs/RESEARCH-FOUNDATION.md)）確立了三條硬結論：

1. **拉普拉斯妖在物理上不可能**——無法比宇宙更快地模擬宇宙（宇宙史運算上限 ~10¹²⁰ ops）。
2. **AI 對「個體高後果人生結果」的預測有內在天花板**——160 隊頂尖團隊用富資料集，R² 仍 <0.2（Fragile Families Challenge）。
3. **術數無客觀預測力**——占星雙盲被反駁（Carlson 1985），「準確感」來自巴納姆效應（Forer 1949）。

因此本專案放棄「預測命運」，改做**「不確定性管理 + 去偏誤決策」**——這是現實中真正做得到、且有證據支持的目標。

## 雙層架構（一眼版）

```
┌─────────────────────────────────────────────────────┐
│  Layer 1：統計概率引擎（Probability Engine）          │
│  → 算「會怎樣」的概率分佈與風險區間                    │
│  → 誠實標註信賴區間與「個體天花板」                    │
├─────────────────────────────────────────────────────┤
│  Layer 2：結構化反思層（Reflection Protocol）         │
│  → 不算命，強迫「考慮相反 / 事前驗屍 / 外部視角」      │
│  → 易經 64 卦 = 觸發反思的符號介面，非預測來源         │
└─────────────────────────────────────────────────────┘
        ▲ 兩層之間有「防火牆」：符號層的輸出永不回灌污染概率層
```

完整藍圖見 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)。

## 最大的產品風險 = 最大的研究機會

「一個明確聲明無預測力、純做結構化反思的符號框架，能否在**不誘發巴納姆效應**下真正改善決策」——
**這個假設至今無人用對照實驗驗證過**。它是本專案的核心驗證假設，
MVP 必須設計成可證偽的實驗，見 [`docs/MVP-EXPERIMENT.md`](docs/MVP-EXPERIMENT.md)。

## 文件導覽

| 文件 | 內容 |
|------|------|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | 雙層架構落地藍圖（主交付物） |
| [`docs/RESEARCH-FOUNDATION.md`](docs/RESEARCH-FOUNDATION.md) | 三輪深度研究的引用證據基礎 |
| [`docs/MVP-EXPERIMENT.md`](docs/MVP-EXPERIMENT.md) | 「去巴納姆」核心假設的可驗證 MVP 實驗設計 |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | 設計決策紀錄（ADR）與已知陷阱 |
| [`docs/PRE-REGISTRATION.md`](docs/PRE-REGISTRATION.md) | OSF/AsPredicted 預先註冊文件（含 `TODO` 待補） |
| [`docs/INFORMED-CONSENT.md`](docs/INFORMED-CONSENT.md) | 知情同意書範本（須 IRB 核准） |
| [`docs/DEBRIEF.md`](docs/DEBRIEF.md) · [`docs/PRIVACY.md`](docs/PRIVACY.md) | 事後說明與隱私處理 |

## 程式

| 路徑 | 內容 |
|------|------|
| [`experiment/`](experiment/) | 四組 MVP 實驗（CLI 版 + 分析器，`--simulate` 可驗證管線） |
| [`webapp/`](webapp/) | 可部署的線上實驗版（零依賴 stdlib server + 瀏覽器 SPA） |

## 狀態

🟡 **發射準備中**。已完成：四組原型（CLI + Web）、預先註冊/同意/隱私文件、
基準率「來源治理」與發射閘門。

🚦 **發射阻擋項（real run 前必須清除）**：
1. ~~基準率示意數據~~ → ✅ **已查證並換上紮實情境**。三個情境皆有真實基準率：
   退休 4% 法則（~95%, Trinity Study）、戒菸 varenicline（~23%, Cochrane）、外派完成率（~93%, Brookfield）。
   無可靠數據的指標已誠實移除（見 `docs/RESEARCH-FOUNDATION.md` §5）。發射閘門現已通過。
2. 預先註冊文件的 `TODO` 未補齊、尚未提交鎖定。
3. IRB/倫理審查未核准。
4. Web 版尚未配置 HTTPS（明文 HTTP 不可收真實資料）。

> 個人自我試用（N=1）：`python3 -m experiment.self_pilot` — 不受上述阻擋，現在就能用。
> 發射閘門已實作：基準率為佔位假數據時，CLI 與 Web 都會擋下真實受試者（回 423 / SystemExit）。
