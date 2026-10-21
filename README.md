# 固團出席表（GitHub Pages + Firebase）

團員不用登入，拿到網址就能填；只有團長用 Google 登入後才能發起調查。

## 一、建立 Firebase（免費方案即可）

1. 到 https://console.firebase.google.com 建立新專案（Google Analytics 可以關掉）。
2. **建立資料庫**：左側「Build → Firestore Database」→「Create database」→ 選「Production mode」→ 地區建議選 `asia-east1 (Taiwan)`。
3. **貼上規則**：Firestore 的「Rules」分頁，把 `firestore.rules` 的內容整個貼上，
   把 `your-email@gmail.com` 改成你的 Google 帳號，按「Publish」。
4. **開啟 Google 登入**：「Build → Authentication」→「Get started」→「Sign-in method」→ 啟用「Google」。
5. **註冊網頁應用程式**：專案總覽的齒輪 →「Project settings」→ 下方「Your apps」點 `</>` 圖示，
   隨便取個名字（不用勾 Hosting），完成後會看到一段 `firebaseConfig`。

## 二、修改 index.html

打開 `index.html`，找到最上面的設定區，把剛才的 `firebaseConfig` 各欄位貼進 `FIREBASE_CONFIG`，
並把 `OWNER_EMAIL` 改成你的 Google 帳號（和規則裡的一樣）。

> Firebase 的 apiKey 本來就是公開的，放在 GitHub 上沒關係；真正的權限是由 Firestore 規則控管。

## 三、發佈到 GitHub Pages

1. 在 GitHub 建立新的 repository（例如 `ff14-static`），設為 Public。
2. 上傳 `index.html`（`firestore.rules` 和 `README.md` 可一起放，不影響網頁）。
3. repository 的「Settings → Pages」→ Source 選「Deploy from a branch」→ Branch 選 `main`、資料夾 `/ (root)` → Save。
4. 等一兩分鐘，網址會是 `https://你的帳號.github.io/ff14-static/`。

## 四、把 GitHub 網域加進 Firebase 授權網域（團長登入需要）

Firebase「Authentication → Settings → Authorized domains」→「Add domain」→ 輸入 `你的帳號.github.io`。

## 使用方式

- 團長：打開網址，頁面最下方「用 Google 登入」→ 出現「發起與管理調查」分頁 → 發起調查，把網址傳到群組。
- 團員：打開網址，選自己的名字，勾時間，按「儲存我的時間」。
- 團長可以截止填寫、重新開放、清除某人的回覆、刪除整份調查，也能用「複製連結」取得某份調查的專屬網址。

## 要改團員名單時

`index.html` 的 `MEMBERS` 和 `firestore.rules` 的 `isMember` 兩邊都要改，`k` 只能用英數字。
