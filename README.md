# 光之戰士飛地

FF14 固定團的線上小據點：大廳（今日飛地）、固定團、BiS、減傷軸、出席調查、自由揪團、請假行事曆、回憶錄。

- 網站：https://lq48.github.io/ff14-static/
- 架構：純靜態網頁（GitHub Pages）＋ Firebase（Firestore、Authentication）＋ Cloudflare Worker（Discord 登入與通知）
- 沒有建置流程：改完檔案推上 `main` 就會上線

## 頁面

| 檔案 | 內容 |
|---|---|
| `index.html` | 大廳、靈魂水晶、固定團（陣容、管理、權限）、BiS 與分裝、推薦網站。用網址 `?team=` `&mod=bis` 切換畫面 |
| `schedule.html` | 出席時間調查（不登入也能填） |
| `events.html` | 自由揪團：候選時間、回覆、成團判斷、分享到 Discord |
| `away.html` | 請假行事曆 |
| `mit.html` | 減傷軸（完整時間軸／我的減傷） |
| `memories.html` | 飛地回憶錄（照片存在 Firestore） |
| `moogle.html` | 莫古莫古大收集試算（只存在瀏覽器） |

## 共用檔案

| 檔案 | 內容 |
|---|---|
| `config.js` | Firebase 設定、總團長身分、Worker 網址、團員通訊錄（**改一個地方就好**） |
| `common.js` | 職業表、`esc`／`safeUrl`、揪團成團判斷（`slotTally`、`readyState`）。**同一個數字只在這裡算** |
| `nav.js` | 全站導覽（頂部列、手機底部導覽、使用者選單） |
| `cozy.css` | 設計 tokens（色彩、字級、間距）與共用元件 |
| `skin.js` | 外觀與深淺色設定（放在 `<head>` 最前面） |
| `icons.js` | 線條圖示（24×24、線寬 1.9） |
| `ui.js` | 可以「復原」的提示 |
| `photo.js` | 照片壓縮（WebP） |
| `away-core.js`、`away-mini.js` | 請假資料讀取與大廳的請假預覽 |
| `firestore.rules` | Firestore 權限規則（**改了要到 Firebase 主控台發布才會生效**） |
| `_tests/` | 自動化回歸測試（不會發布到網站），說明見 `_tests/README.md` |

## 登入與權限

- 團員用 **Discord** 登入：Worker 完成 OAuth 後發 Firebase custom token（帳號 ID 是 `dc_` 加 Discord ID，帶 `dc` claim）
- 總團長另外可以用 Google 帳號備用登入（`config.js` 的 `OWNER_EMAIL`）
- **真正的權限在 `firestore.rules`**；頁面上隱藏按鈕只是體驗，不是保護
- Firebase 的 `apiKey` 本來就是公開的，可以放在 GitHub；**Worker 的密鑰（Discord client secret、bot token、服務帳號）絕對不能放進這個 repo**

## 修改時的注意事項

1. **快取版本號**：改了共用檔案（`cozy.css`、`nav.js`、`common.js`…），要把各頁引用的 `?v=` 數字加一，不然團員會拿到舊檔案
2. **輸出到畫面一律 `esc()`**：包含 `data-*`、`value`、`class` 屬性裡的值。資料庫裡的「選項」欄位也可能被改成任何字串
3. **連結用 `safeUrl()`**：只接受 http(s)
4. **新的計算放進 `common.js`**：大廳和功能頁要顯示同一個數字時，不要各算一次
5. **新增 Firestore collection 或欄位**：先改 `firestore.rules`，在主控台的規則模擬器測過再發布
6. **改完跑測試**：`python _tests/run_all.py`；開 PR 時 GitHub 也會自動跑

## 部署 Firestore 規則

1. Firebase 主控台 → Firestore Database → 規則
2. 貼上 `firestore.rules` 的內容 → 用「規則模擬器」試幾個情況（未登入讀取、非作者修改）→ 發布
