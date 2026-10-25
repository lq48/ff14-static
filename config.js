/* ============ 全站共用設定（改這一個檔案就好） ============ */

export const FIREBASE_CONFIG = {
  apiKey: "AIzaSyCkXln7MpkYFzMF9pLl1UP3DYc2X_A365U",
  authDomain: "attendance-4f7a3.firebaseapp.com",
  projectId: "attendance-4f7a3",
  storageBucket: "attendance-4f7a3.firebasestorage.app",
  messagingSenderId: "480792441403",
  appId: "1:480792441403:web:57ea91a8894f75bed9e21e"
};

// 團長：Discord ID（主要）與 Google 帳號（備用登入），要和 firestore.rules 一致
export const OWNER_DISCORD_ID = "886243755051601921";
export const OWNER_EMAIL = "lq0408@gmail.com";

// Cloudflare Worker 網址（Discord 登入、提醒機器人都靠它）
export const WORKER_URL = "https://ff14-notify.lq0408.workers.dev";

// 常用團員通訊錄：Discord ID 對照（alias 是同一人的其他寫法）
export const DIRECTORY = [
  {n:"飛雷虛",did:"390511952625008640"},{n:"諾爾",did:"867669258992222208"},{n:"楓之旋律",did:"488186522663649280"},
  {n:"33",did:"687693387612291102",alias:["三三"]},{n:"Jman",did:"517588902006095883"},{n:"Satoru",did:"886243755051601921"},
  {n:"草八刀",did:"693797650532663326"},{n:"來來",did:"687696892372844623",alias:["來來子"]},{n:"Paku",did:"1243145228962103317"},
  {n:"Cirtus",did:"852141381987074099"},{n:"山壯",did:"513206089303719936"}
];
