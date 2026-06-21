# Decision Compass（決策羅盤）

> 一個融合「統計概率引擎」與「結構化反思層」的決策輔助工具。
> 它**不是預言機**——它是羅盤：指方向、量化不確定性，而非預測命運。

**🧭 線上工具（免費、無需登入、資料只存你瀏覽器）：** https://zhixuli0406.github.io/decision-compass/

> 這是一個**開放式興趣專案**，非經驗證的產品，不構成財務/醫療/法律建議。
> 反思層是否真能改善決策**尚未經對照實驗驗證**——我們誠實地把它定位為思考輔助，而非預言。

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
| [`public/`](public/) | **面向大眾的線上工具**（純靜態，部署於 GitHub Pages，零後端零資料收集） |
| [`experiment/`](experiment/) | 研究用四組 MVP 實驗原型（CLI + 分析器，保留作研究文件） |
| [`webapp/`](webapp/) | 研究用線上實驗版（stdlib server，保留作研究文件） |

## 狀態：公開上線

依專案定位（開放式興趣專案、無商品化、無發論文預期），**刻意跳過正式 MVP 對照驗證**，
直接以誠實框定的形式面向大眾（見 [`docs/DECISIONS.md`](docs/DECISIONS.md) ADR-008）。

公開工具 = **A 組完整羅盤**（Layer 1 真實基準率 + Layer 2 去偏誤反思 + 易經符號介面 + 決策日誌），
已**移除所有實驗鷹架**（隨機分組、純巴納姆對照、錯置回饋測試、研究用知情同意）。
**保留所有誠實護欄**：不宣稱預測力、個體天花板提醒、去巴納姆的事實綁定。

三個範例情境皆有查證過的真實基準率：退休 4% 法則（~95%, Trinity Study）、
戒菸 varenicline（~23%, Cochrane）、外派完成率（~93%, Brookfield）；也支援使用者自訂決定。

> 研究文件（三輪深度研究、雙層架構、實驗設計）保留在 `docs/` 與 `experiment/`，作為這個工具的思想來源。

## 授權

本專案採用 [Apache License 2.0](LICENSE)（含專利授權條款）。詳見 [`LICENSE`](LICENSE) 與 [`NOTICE`](NOTICE)。

## 免責聲明

這是**探索性研究專案**，不是經臨床/財務驗證的產品。工具刻意**不預測**個人結果；
所有決策仍由使用者自行負責。文件中的基準率均附出處，但部分有方法學爭議（見
[`docs/RESEARCH-FOUNDATION.md`](docs/RESEARCH-FOUNDATION.md)），請勿當作財務、醫療或法律建議。
