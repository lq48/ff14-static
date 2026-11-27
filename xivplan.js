/* xivplan（https://xivplan.netlify.app/）站位圖連結的小工具
   分享連結＝ #/plan/ 後面接「場景 JSON → zlib 壓縮 → base64url」（格式見 xivplan 原始碼 src/file.ts）
   - xpIs(url)：是不是 xivplan 的分享連結
   - xpPersonal(url, slot)：產生「只看自己」的版本：自己放大加黃圈、其他人變淡、只留自己的移動箭頭
   全部在瀏覽器裡算，不經過任何伺服器 */

const HOST = "https://xivplan.netlify.app/";
const PREFIX = HOST + "#/plan/";
export const xpIs = u => typeof u === "string" && u.startsWith(PREFIX) && u.length < 60000 && /^[A-Za-z0-9_\-%]+$/.test(u.slice(PREFIX.length));

/* 隊員名字 → 位置。認我們產生的 MT～D4，也認 xivplan 內建的 Tank 1、Healer 1、Melee 1… */
const NAME_SLOT = {
  "MT": "MT", "ST": "ST", "H1": "H1", "H2": "H2", "D1": "D1", "D2": "D2", "D3": "D3", "D4": "D4",
  "Tank 1": "MT", "Tank 2": "ST", "Healer 1": "H1", "Healer 2": "H2",
  "Melee DPS 1": "D1", "Melee DPS 2": "D2", "Ranged DPS 1": "D3", "Ranged DPS 2": "D4",
  "DPS 1": "D1", "DPS 2": "D2", "DPS 3": "D3", "DPS 4": "D4"
};
export const xpSlotOf = name => NAME_SLOT[String(name || "").trim()] || "";

const b64u = {
  dec(s) { s = s.replace(/-/g, "+").replace(/_/g, "/"); s += "=".repeat((4 - s.length % 4) % 4); const b = atob(s), a = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); return a; },
  enc(a) { let s = ""; for (let i = 0; i < a.length; i += 0x8000) s += String.fromCharCode.apply(null, a.subarray(i, i + 0x8000)); return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); }
};
async function pipe(bytes, stream) { const r = new Blob([bytes]).stream().pipeThrough(stream); return new Uint8Array(await new Response(r).arrayBuffer()); }
export async function xpDecode(url) {
  if (!xpIs(url)) throw new Error("不是 xivplan 連結");
  const raw = await pipe(b64u.dec(decodeURIComponent(url.slice(PREFIX.length))), new DecompressionStream("deflate"));
  const sc = JSON.parse(new TextDecoder().decode(raw));
  if (!sc || !Array.isArray(sc.steps)) throw new Error("場景格式不對");
  return sc;
}
export async function xpEncode(sc) {
  const z = await pipe(new TextEncoder().encode(JSON.stringify(sc)), new CompressionStream("deflate"));
  return PREFIX + b64u.enc(z);
}

/* 這張圖裡有哪些位置（給畫面判斷要不要顯示「看自己的」按鈕） */
export async function xpSlots(url) {
  const sc = await xpDecode(url), s = new Set();
  sc.steps.forEach(st => (st.objects || []).forEach(o => { if (o.type === "party") { const k = xpSlotOf(o.name); if (k) s.add(k); } }));
  return [...s];
}

/* 只看自己：
   - 自己：放大一點、外面加黃圈；箭頭變黃色加粗
   - 其他人：透明度 30%；他們的箭頭拿掉（箭頭終點最靠近誰就是誰的）
   - 沒認出是誰的箭頭（例如王的移動）保留 */
export function xpPersonalScene(sc, slot) {
  sc = JSON.parse(JSON.stringify(sc));
  let next = Math.max(sc.nextId || 1, 1), prev = {};
  sc.steps.forEach(st => {
    const objs = st.objects || [], cur = {};
    objs.forEach(o => { if (o.type === "party") { const k = xpSlotOf(o.name); if (k) cur[k] = o; } });
    /* 箭頭是誰的：終點靠近他這一步的位置，起點靠近他上一步的位置（兩人分攤站同一點時靠起點分辨） */
    const owner = a => {
      const r = (a.rotation || 0) * Math.PI / 180, ex = a.x + (a.length || 0) * Math.sin(r), ey = a.y + (a.length || 0) * Math.cos(r);
      let best = "", bs = 1e9;
      Object.entries(cur).forEach(([k, p]) => {
        const de = Math.hypot(p.x - ex, p.y - ey); if (de > 30) return;
        const q = prev[k], ds = q ? Math.hypot(q.x - a.x, q.y - a.y) : 0, sc2 = de + ds;
        if (sc2 < bs) { bs = sc2; best = k; }
      });
      return best;
    };
    const out = [];
    objs.forEach(o => {
      if (o.type === "arrow") {
        const k = owner(o);
        if (k && k !== slot) return;
        if (k === slot) { o.color = "#ffe14a"; o.width = Math.max(o.width || 8, 14); o.opacity = 100; }
        out.push(o); return;
      }
      if (o.type === "party" && xpSlotOf(o.name)) {
        if (xpSlotOf(o.name) === slot) {
          o.width = Math.max(o.width || 32, 34); o.height = Math.max(o.height || 32, 34); o.opacity = 100;
          out.push({ type: "circle", id: next++, x: o.x, y: o.y, radius: 24, color: "#ffe14a", opacity: 100, hollow: true });
        } else o.opacity = 30;
      }
      out.push(o);
    });
    st.objects = out;
    Object.entries(cur).forEach(([k, p]) => { prev[k] = { x: p.x, y: p.y }; });
  });
  sc.nextId = next;
  return sc;
}
const cache = new Map();
export async function xpPersonal(url, slot) {
  const k = slot + "|" + url;
  if (!cache.has(k)) cache.set(k, xpDecode(url).then(sc => xpEncode(xpPersonalScene(sc, slot))));
  return cache.get(k);
}
