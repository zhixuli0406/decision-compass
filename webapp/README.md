# Webapp — 可部署的線上實驗版

零依賴（Python 標準庫 `http.server`）。伺服器擁有全部實驗邏輯（隨機分派、反思內容、記錄），瀏覽器只是薄客戶端。

## 本機跑

```bash
# 從專案根目錄 decision-compass/ 執行

# 正式模式：基準率未驗證時，/api/start 會回 423 擋下真實受試者
python3 -m webapp.server                      # http://127.0.0.1:8000

# 開發測試（略過發射閘門，資料不可用於正式研究）
ALLOW_UNVERIFIED=1 PORT=8000 python3 -m webapp.server
```

環境變數：
- `PORT`（預設 8000）
- `DC_DATA`（結果 JSONL 路徑，預設 `experiment/data/web_results.jsonl`）
- `ALLOW_UNVERIFIED=1`（僅開發；正式研究務必移除，讓閘門生效）

## 流程（與 CLI 同邏輯）
consent → scenario+facts → Layer1 概率(A/B) + Layer2 反思 → 決定+預測 → 錯置回饋 → debrief

分析沿用 CLI 的分析器：
```bash
python3 -m experiment.analyze --data experiment/data/web_results.jsonl \
                              --outcomes experiment/data/outcomes.jsonl
```

## ⚠️ 上線前必做（不可省略）

1. **HTTPS/TLS**：內建伺服器是明文 HTTP，**不可**直接對外收真實資料。
   置於 Nginx/Caddy 反向代理後啟用 TLS，或部署到有 TLS 的 PaaS。
2. **發射閘門**：確認 `base_rates.json` 全部 `status=verified`，且**不要**設 `ALLOW_UNVERIFIED`。
3. **會話儲存**：目前 pending session 存在記憶體（重啟會掉未送出的）。
   正式上線建議換成 Redis/DB，或接受「未完成不計入」。
4. **防濫用**：加上速率限制、平台 ID 驗證、注意力檢核題（見 `PRE-REGISTRATION.md` 排除規則）。
5. **倫理**：consent 頁為精簡版，正式須對齊 IRB 核准的 [`../docs/INFORMED-CONSENT.md`](../docs/INFORMED-CONSENT.md)；
   結束頁對齊 [`../docs/DEBRIEF.md`](../docs/DEBRIEF.md)。
6. **隱私**：依 [`../docs/PRIVACY.md`](../docs/PRIVACY.md) 設定儲存、保存期限、去識別化。

## 與 Prolific/MTurk 整合（提示）
- 用網址參數帶入平台 ID（如 `?PROLIFIC_PID=...`），前端塞入「參與者代碼」欄即可配對追蹤。
- 完成頁顯示 completion code 供平台核銷（`TODO` 實作）。
- 報酬與最低時薪：見 `INFORMED-CONSENT.md`。

## 檔案
```
webapp/
├── server.py            # stdlib HTTP server + JSON API（重用 experiment/core）
└── static/
    ├── index.html       # 多步驟 SPA
    ├── app.js           # 薄客戶端：渲染步驟、POST 作答
    └── style.css
```
