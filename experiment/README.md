# MVP 四組實驗原型

驗證核心假設：**「無預測力的符號反思框架，能否在不誘發巴納姆效應下改善決策」**
（見 [`../docs/MVP-EXPERIMENT.md`](../docs/MVP-EXPERIMENT.md)）。

純 Python 標準庫，零依賴。

## 四組對照

| 組 | 介入 | 隔離的變因 |
|----|------|-----------|
| **A** | 概率 + 去偏誤協議 + 易經符號 | 完整產品假設 |
| **B** | 概率 + 去偏誤協議（純文字） | 易經符號是否多餘（A vs B） |
| **C** | 純巴納姆通用建議（無去偏誤） | 巴納姆基線（A vs C = 真價值） |
| **D** | 只記錄決策 | 基線（A vs D） |

## 快速開始

```bash
# 從專案根目錄 decision-compass/ 執行

# 1) 端到端管線驗證（自動跑四組，不需真人；僅測流程，非數據）
python3 -m experiment.run_experiment --simulate

# 2) 真人單次（指定組別或隨機分派）
python3 -m experiment.run_experiment --participant p001 --group A --scenario retirement_4pct
python3 -m experiment.run_experiment --participant p002            # 隨機分派組別（預設 retirement_4pct）

# 情境（皆有真實基準率）：retirement_4pct（退休4%法則，最強）/ quit_smoking（戒菸）/ relocation（外派）

# 3) 分析（先看過程指標；有 3 個月追蹤結果後再看校準度）
python3 -m experiment.analyze
python3 -m experiment.analyze --outcomes experiment/data/outcomes.jsonl
```

## 量測什麼

- **主指標：校準度（Brier score）**——當下對「決定會走得好」的機率預測，
  對照 3 個月後的真實結果。**不是**「使用者覺得有用」（那正是巴納姆會灌水的）。
- **巴納姆汙染檢查**：錯置回饋測試。給受試者看「自己的」與「別人的」反思輸出各評分，
  落差大 = 反思綁定具體事實（A/B 預期如此）；落差≈0 = 通用巴納姆（C 預期如此）。
- 輔助：預測滿意度誤差、決策過程品質（盲評）。

## 資料流

```
run_experiment ──→ experiment/data/results.jsonl   （當下記錄）
                                  │
        3 個月後回填 outcomes.jsonl（真實結果）
                                  │
analyze ──→ 各組 Brier / 巴納姆gap / 判讀（對照事前註冊判準）
```

## 追蹤結果（outcomes.jsonl）格式

每行一筆 JSON：

```json
{"participant_id": "p001", "went_well": true, "actual_satisfaction": 8}
```

範本見 [`data/outcomes.template.jsonl`](data/outcomes.template.jsonl)。

## 重要提醒

- `--simulate` 的回答是隨機產生的，**只驗證程式管線，不能當實驗結論**。
- 跑真實研究前：① 替換 `core/scenario.py` 的示意基準率為真實參照類別資料；
  ② 預先註冊假設與判準（OSF/AsPredicted）；③ 倫理審查與知情同意。
- 易經符號在程式中是**零計算的查表標籤**（`core/hexagram.py`），無任何預測角色——
  這是刻意設計（見 `../docs/DECISIONS.md` ADR-003）。

## 檔案結構

```
experiment/
├── run_experiment.py     # 跑測器（四步共用流程）
├── analyze.py            # 結果分析 + 判讀
├── core/
│   ├── io_adapter.py     # 互動 / 模擬 IO 抽象
│   ├── scenario.py       # 決策情境 + 參照類別基準率（Layer 1）
│   ├── session.py        # 不可變 session 記錄
│   ├── reflection.py     # 去偏誤協議（考慮相反/事前驗屍/外部視角）
│   ├── hexagram.py       # 易經符號介面（零計算查表）
│   ├── barnum.py         # 巴納姆基線 + 錯置回饋測試
│   ├── scoring.py        # Brier / 校準 / 判讀
│   ├── logbook.py        # JSONL 持久化（決策日誌閉環）
│   └── intervention.py   # 介入基底類別（四步 hook）
└── groups/
    ├── group_a.py … group_d.py
    └── registry.py       # 組別註冊 + 隨機分派
```
