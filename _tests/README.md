# 自動化回歸測試

用**假的 Firebase**（資料都在記憶體裡）在真的瀏覽器裡操作網站，**不會連到正式資料庫，也不會發 Discord 訊息**。
資料夾名稱用底線開頭，GitHub Pages 不會把它發布到網站上。

## 怎麼跑

```bash
pip install -r _tests/requirements.txt
python -m playwright install chromium
python _tests/run_all.py            # 全部（約 5 分鐘）
python _tests/run_all.py survey bis # 只跑檔名含 survey 或 bis 的
```

測試會自己在 8765 埠開一個本機伺服器。截圖和產生的測試照片放在 `_tests/out/`（不會 commit）。
想用電腦上的 Chrome：`CHROME=/path/to/chrome python _tests/run_all.py`

開 PR 時，GitHub Actions 會自動跑一次（`.github/workflows/tests.yml`）。

## 涵蓋範圍

| 檔案 | 內容 |
|---|---|
| `test_lobby_nav.py` | 導覽列、使用者選單、深淺色、舊版外觀、登出、Discord 登入導向、跳到區塊 |
| `test_core.py` | 建立請假、發起揪團、回覆、分享到 Discord（帶 idToken）、一般團員與總團長權限、各頁登出 |
| `test_survey.py` | 出席調查：填寫與修改、送出回饋、團長未回覆名單、DC 提醒防重複、儲存失敗 |
| `test_agenda.py` | 大廳近期安排、請假權限（看不到別人的請假） |
| `test_consistency.py` | 同一場揪團在大廳和揪團頁的成團狀態一致 |
| `test_bis.py` | BiS 完成度計算（含未設定、待強化、開荒裝不算）、全團摘要、手機卡片 |
| `test_mit.py` | 「我的減傷」和完整時間軸逐格一致、篩選、手機預設列表 |
| `test_undo.py`、`test_loot_undo.py` | 可復原操作、未儲存保護 |
| `test_memories.py` | 回憶錄：列表、詳情、新增（真實照片壓縮）、編輯、刪除與復原、權限 |
| `test_team_picker.py` | 多個固定團時的選擇 |
| `test_keyboard.py` | 鍵盤 Tab 焦點都看得見 |
| `test_xss.py` | 三種 XSS 攻擊 × 15 個畫面 |
| `report_layout.py` | （報告，不算測試）360／390／768／1280 寬度的溢位、版面跳動、小按鈕 |

## 架構

- `mock/fb-*.js`：假的 Firebase SDK（替換 gstatic 的網址），寫入會記錄在 `window.__writes`
- `mock/fixture.js`：測試資料。網址加 `?mock=member`、`owner`、`plain`、`empty`、`signedout`、`google`、`denied`、`nosurvey` 切換身分
- `rules_check.py`：照 `firestore.rules` 寫的檢查器，確認頁面送出的回憶錄寫入會被規則接受
- `attacks/`：XSS 測試用的資料汙染腳本

## 限制

- 假 Firebase **不會執行 firestore.rules**：權限要在 Firebase 主控台的規則模擬器確認
- Worker（Discord 登入、通知）是假的：只確認網站有送出正確的請求
- 修改功能時如果改了畫面文字或按鈕，對應的測試要一起更新
