/* 站位圖播放器：把 xivplan 的場景直接畫在網站裡（不用跳到 xivplan）
   - xpMount(el, entries, opts)：entries＝[{label,url}]（火／雷…），opts＝{me:"H2", job:slot=>"WHM"|"" , jobImg:job=>url}
   - 支援的物件：場地（圓／方、格線、刻度）、場地標記、隊員、王、扇形、圓形、甜甜圈、矩形、直線、箭頭、文字
     其他物件不畫，並在下面提示「到 xivplan 看完整內容」
   - 座標：xivplan 以場地中心為 (0,0)、y 朝北；旋轉 0＝北、順時針。SVG 的 y 朝下，所以 y 取負號
   - 隊員在步驟之間用動畫移動（有開「減少動態效果」就直接跳） */
import { xpDecode, xpSlotOf, xpArrowOwners } from "./xivplan.js?v=2";

const NS = "http://www.w3.org/2000/svg";
const ROLE_OF = { MT: "t", ST: "t", H1: "h", H2: "h", D1: "d", D2: "d", D3: "d", D4: "d" };
const ROLE_COLOR = { t: "#3b6fd6", h: "#2e9150", d: "#c4422e", x: "#6b7385" };
const ME_RING = "#ffd84a";
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const num = (v, d = 0) => { const n = +v; return Number.isFinite(n) ? n : d; };
/* 顏色只接受 #rgb / #rrggbb，其他一律換成預設，避免把奇怪的字串塞進 SVG */
const col = (c, d = "#ff8a3d") => /^#[0-9a-f]{3}([0-9a-f]{3})?$/i.test(String(c || "")) ? c : d;
const op = o => Math.max(0, Math.min(1, num(o?.opacity, 100) / 100));
const rad = d => d * Math.PI / 180;
const dir = (b, r) => [r * Math.sin(rad(b)), -r * Math.cos(rad(b))];
const SUPPORTED = new Set(["party", "marker", "enemy", "cone", "circle", "donut", "rect", "line", "arrow", "text"]);
const MARK_COLOR = { A: "#e8485f", B: "#e3c93c", C: "#4aa3e8", D: "#c77de0", 1: "#e8485f", 2: "#e3c93c", 3: "#4aa3e8", 4: "#c77de0" };

function arenaInfo(sc) {
  const a = sc.arena || {}, w = num(a.width, 600), h = num(a.height, 600);
  return { a, w, h, circle: (a.shape || "circle") === "circle", R: Math.min(w, h) / 2 };
}
/* 文字物件落在畫面框外面的，當成這一步的說明（用網頁文字顯示，比畫在圖裡清楚）；上面的是標題、下面的是補充 */
const isCap = (o, vb) => o.type === "text" && (num(o.x) < vb[0] || num(o.x) > vb[0] + vb[2] || -num(o.y) < vb[1] || -num(o.y) > vb[1] + vb[3]);
function captions(sc, step) {
  const vb = viewBox(sc), out = [];
  (step.objects || []).forEach(o => { if (o && isCap(o, vb)) out.push({ y: num(o.y), t: String(o.text || "").trim() }); });
  out.sort((a, b) => b.y - a.y);
  return out.map(x => x.t).filter(Boolean);
}
export function stepLabel(sc, i) {
  const c = captions(sc, sc.steps[i] || {}), m = (c[0] || "").match(/^(\d{1,2}:\d{2})/);
  return m ? m[1] : "第 " + (i + 1) + " 步";
}
/* 視窗：把所有步驟裡的人、標記、王都框進來，四周留一點空間；整份圖用同一個框，換步驟時畫面不會跳 */
const VB = new WeakMap();
function viewBox(sc) { if (!VB.has(sc)) VB.set(sc, viewBox0(sc)); return VB.get(sc); }
function viewBox0(sc) {
  const { w, h, a } = arenaInfo(sc), pad = num(a.padding, 0);
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  const add = (x, y, r) => { x0 = Math.min(x0, x - r); x1 = Math.max(x1, x + r); y0 = Math.min(y0, -y - r); y1 = Math.max(y1, -y + r); };
  sc.steps.forEach(st => (st.objects || []).forEach(o => {
    if (o.type === "party" || o.type === "marker") add(num(o.x), num(o.y), 26);
    else if (o.type === "enemy") add(num(o.x), num(o.y), Math.min(num(o.radius, 40), 60) + 8);
    else if ((o.type === "circle") && num(o.radius) < 90) add(num(o.x), num(o.y), num(o.radius));
  }));
  if (x0 > x1) { x0 = -w / 2; x1 = w / 2; y0 = -h / 2; y1 = h / 2; }
  const m = 34, cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  let s = Math.max(x1 - x0, y1 - y0) + m * 2;
  s = Math.max(s, 300); s = Math.min(s, Math.max(w, h) + pad * 2);
  const lim = (c, half) => Math.max(-(Math.max(w, h) / 2 + pad) + half, Math.min((Math.max(w, h) / 2 + pad) - half, c));
  const half = s / 2;
  return [lim(cx, half) - half, lim(cy, half) - half, s, s];
}
function floorSVG(sc) {
  const { a, w, h, circle, R } = arenaInfo(sc), g = a.grid || {}, t = a.ticks || {};
  let s = '<g class="xpv-floor">';
  if (circle) s += `<circle r="${R}" class="xf"/>`;
  else s += `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="6" class="xf"/>`;
  if (g.type === "radial" && circle) {
    const n = Math.min(num(g.angularDivs, 0), 36), rr = Math.min(num(g.radialDivs, 0), 8);
    for (let i = 0; i < n; i++) { const [x, y] = dir(i * 360 / n + num(g.startAngle, 0), R); s += `<line x1="0" y1="0" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" class="xg"/>`; }
    for (let i = 1; i <= rr; i++) s += `<circle r="${(R * i / (rr + 1)).toFixed(1)}" class="xg"/>`;
  } else if (g.type === "rectangular") {
    const rows = Math.min(num(g.rows, 0), 20), cols = Math.min(num(g.columns, 0), 20);
    for (let i = 1; i < cols; i++) { const x = -w / 2 + w * i / cols; s += `<line x1="${x}" y1="${-h / 2}" x2="${x}" y2="${h / 2}" class="xg"/>`; }
    for (let i = 1; i < rows; i++) { const y = -h / 2 + h * i / rows; s += `<line x1="${-w / 2}" y1="${y}" x2="${w / 2}" y2="${y}" class="xg"/>`; }
  }
  if (t.type === "radial" && circle) {
    const mc = Math.min(num(t.minorCount, 0), 360), Mc = Math.min(num(t.majorCount, 0), 36);
    for (let i = 0; i < mc; i++) { const b = num(t.minorStart, 0) + i * 360 / mc, [x1, y1] = dir(b, R), [x2, y2] = dir(b, R + 7); s += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" class="xt"/>`; }
    for (let i = 0; i < Mc; i++) { const b = num(t.majorStart, 0) + i * 360 / Mc, [x1, y1] = dir(b, R), [x2, y2] = dir(b, R + 14); s += `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" class="xt xT"/>`; }
  }
  if (circle) s += `<circle r="${R}" class="xrim"/>`;
  else s += `<rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="6" class="xrim"/>`;
  return s + "</g>";
}
/* 攻擊範圍：填色淡、邊線清楚 */
function zone(o) {
  const x = num(o.x), y = -num(o.y), c = col(o.color), a = op(o), hol = !!o.hollow;
  const st = hol ? `fill="none" stroke="${c}" stroke-width="4" opacity="${a}"` : `fill="${c}" fill-opacity="${(a * .55).toFixed(2)}" stroke="${c}" stroke-opacity="${Math.min(.8, a * 1.3).toFixed(2)}" stroke-width="1.5"`;
  if (o.type === "circle") return `<circle cx="${x}" cy="${y}" r="${Math.max(1, num(o.radius, 20))}" ${st}/>`;
  if (o.type === "cone") {
    const r = num(o.radius, 100), ang = Math.max(1, Math.min(360, num(o.coneAngle, 90))), b = num(o.rotation);
    if (ang >= 360) return `<circle cx="${x}" cy="${y}" r="${r}" ${st}/>`;
    const [ax, ay] = dir(b - ang / 2, r), [bx, by] = dir(b + ang / 2, r);
    return `<path d="M${x} ${y}L${(x + ax).toFixed(1)} ${(y + ay).toFixed(1)}A${r} ${r} 0 ${ang > 180 ? 1 : 0} 1 ${(x + bx).toFixed(1)} ${(y + by).toFixed(1)}Z" ${st} stroke-linejoin="round"/>`;
  }
  if (o.type === "donut") {
    const r = num(o.radius, 100), ri = Math.min(num(o.innerRadius, r / 2), r - 1);
    return `<path fill-rule="evenodd" d="M${x - r} ${y}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0ZM${x - ri} ${y}a${ri} ${ri} 0 1 0 ${2 * ri} 0a${ri} ${ri} 0 1 0 ${-2 * ri} 0Z" ${st}/>`;
  }
  if (o.type === "rect") {
    const w = num(o.width, 50), h = num(o.height, 50);
    return `<rect x="${x - w / 2}" y="${y - h / 2}" width="${w}" height="${h}" transform="rotate(${num(o.rotation)} ${x} ${y})" ${st}/>`;
  }
  if (o.type === "line") {
    const L = num(o.length, 100), w = num(o.width, 20);
    return `<rect x="${x - w / 2}" y="${y - L}" width="${w}" height="${L}" transform="rotate(${num(o.rotation)} ${x} ${y})" ${st}/>`;
  }
  return "";
}
function arrowSVG(o, mine) {
  /* 箭頭終點通常就是隊員現在的位置，會被圖示蓋住：終點縮到圖示邊緣；自己的箭頭起點畫一個虛線圈（上一步站的地方） */
  const x = num(o.x), y = -num(o.y), L0 = Math.max(4, num(o.length, 40)), b = num(o.rotation), L = L0 > 34 ? L0 - 19 : L0;
  const [dx, dy] = dir(b, L), w = mine ? 7 : 4.5, c = mine ? ME_RING : col(o.color, "#ffffff"), hd = w * 2.6;
  const [ux, uy] = dir(b, 1), ex = x + dx, ey = y + dy, bx = ex - ux * hd, by = ey - uy * hd, px = -uy, py = ux;
  return `<g class="xa${mine ? " me" : ""}" opacity="${mine ? 1 : Math.max(.55, op(o))}">` + (mine ? `<circle cx="${x}" cy="${y}" r="17" fill="${ME_RING}" fill-opacity=".12" stroke="${ME_RING}" stroke-width="2.5" stroke-dasharray="5 4"/>` : "") +
    `<line x1="${x}" y1="${y}" x2="${bx.toFixed(1)}" y2="${by.toFixed(1)}" stroke="#0d1220" stroke-width="${w + 3}" stroke-linecap="round"/>` +
    `<line x1="${x}" y1="${y}" x2="${bx.toFixed(1)}" y2="${by.toFixed(1)}" stroke="${c}" stroke-width="${w}" stroke-linecap="round"/>` +
    `<path d="M${ex.toFixed(1)} ${ey.toFixed(1)}L${(bx + px * hd * .62).toFixed(1)} ${(by + py * hd * .62).toFixed(1)}L${(bx - px * hd * .62).toFixed(1)} ${(by - py * hd * .62).toFixed(1)}Z" fill="${c}" stroke="#0d1220" stroke-width="1.5" stroke-linejoin="round"/></g>`;
}
function markerSVG(o) {
  const x = num(o.x), y = -num(o.y), n = String(o.name || "").trim().slice(0, 2), c = col(o.color, MARK_COLOR[n] || "#cccccc"), s = 30, sq = o.shape === "square";
  return `<g class="xm" transform="translate(${x} ${y})">` + (sq ? `<rect x="${-s / 2}" y="${-s / 2}" width="${s}" height="${s}" rx="4" fill="${c}" fill-opacity=".22" stroke="${c}" stroke-width="2.5"/>` : `<circle r="${s / 2}" fill="${c}" fill-opacity=".22" stroke="${c}" stroke-width="2.5"/>`) +
    `<text y="6.5" fill="${c}">${esc(n)}</text></g>`;
}
function enemySVG(o) {
  const x = num(o.x), y = -num(o.y), r = Math.max(8, Math.min(num(o.radius, 40), 200)), c = col(o.color, "#e0384a"), b = num(o.rotation);
  let s = `<g class="xe"><circle cx="${x}" cy="${y}" r="${r}" fill="${c}" fill-opacity=".16" stroke="${c}" stroke-width="2.5" stroke-opacity=".85"/>`;
  if (o.ring && o.ring !== "omni") { const [fx, fy] = dir(b, r + 2), [lx, ly] = dir(b - 14, r - 12), [rx, ry] = dir(b + 14, r - 12); s += `<path d="M${x + fx} ${y + fy}L${x + lx} ${y + ly}L${x + rx} ${y + ry}Z" fill="${c}"/>`; }
  return s + `<circle cx="${x}" cy="${y}" r="5" fill="${c}"/></g>`;
}
function textSVG(o) {
  const x = num(o.x), y = -num(o.y), fs = Math.max(10, Math.min(num(o.fontSize, 18), 40));
  return `<text class="xx" x="${x}" y="${y + fs * .35}" font-size="${fs}" fill="${col(o.color, "#ffffff")}" text-anchor="middle">${esc(String(o.text || "").slice(0, 60))}</text>`;
}
/* 隊員圖示：有設定職業就用職業圖示，沒有就用位置文字（坦藍、補綠、輸出紅） */
function tokenInner(slot, name, opts) {
  const j = slot && opts.job ? opts.job(slot) : "", src = j && opts.jobImg ? opts.jobImg(j) : "";
  const S = 34;
  if (src) return `<rect x="${-S / 2 - 1.5}" y="${-S / 2 - 1.5}" width="${S + 3}" height="${S + 3}" rx="7" fill="#0d1220"/><image href="${esc(src)}" x="${-S / 2}" y="${-S / 2}" width="${S}" height="${S}"/>`;
  const c = ROLE_COLOR[ROLE_OF[slot] || "x"], t = slot || String(name || "").slice(0, 3);
  return `<circle r="${S / 2}" fill="${c}" stroke="#0d1220" stroke-width="2.5"/><circle r="${S / 2 - 2.5}" fill="none" stroke="#ffffff" stroke-opacity=".35" stroke-width="1.2"/><text y="5.2" class="xpt">${esc(t)}</text>`;
}

export function xpUnsupported(sc) {
  const s = new Set();
  sc.steps.forEach(st => (st.objects || []).forEach(o => { if (o && !SUPPORTED.has(o.type)) s.add(o.type); }));
  return [...s];
}

/* 一個步驟的「靜態層」：範圍、標記、王、箭頭、場內文字（隊員另外畫，才能做移動動畫） */
function layerSVG(sc, i, me, owners) {
  const st = sc.steps[i] || { objects: [] }, vb = viewBox(sc), objs = st.objects || [];
  let z = "", mk = "", en = "", ar = "", tx = "";
  objs.forEach(o => {
    if (!o) return;
    if (o.type === "circle" && o.hollow && /^#ffe14a$/i.test(o.color || "")) return; // 舊版「只看自己」連結裡的黃圈：交給播放器畫
    if (["circle", "cone", "donut", "rect", "line"].includes(o.type)) z += zone(o);
    else if (o.type === "marker") mk += markerSVG(o);
    else if (o.type === "enemy") en += enemySVG(o);
    else if (o.type === "arrow") {
      const k = owners.get(o) || "";
      if (me && k && k !== me) return;
      ar += arrowSVG(o, !!me && k === me);
    } else if (o.type === "text" && !isCap(o, vb)) tx += textSVG(o);
  });
  return z + mk + en + ar + tx;
}
function partyOf(st) {
  const m = new Map();
  (st.objects || []).forEach(o => { if (o && o.type === "party") { const k = xpSlotOf(o.name) || ("#" + o.id); if (!m.has(k)) m.set(k, o); } });
  return m;
}

const CSS = `.xpv{display:grid;gap:8px}
.xpv-top{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.xpv-seg{display:inline-flex;background:var(--surface2,#eee);border-radius:999px;padding:3px;gap:2px}
.xpv-seg button{border:0;background:transparent;font:inherit;font-weight:700;font-size:14px;min-height:36px;min-width:52px;padding:0 14px;border-radius:999px;color:var(--muted,#666);cursor:pointer}
.xpv-seg button[aria-pressed=true]{background:var(--surface,#fff);color:var(--ink,#222);box-shadow:0 1px 3px rgba(0,0,0,.18)}
.xpv-me{margin-left:auto;display:inline-flex;align-items:center;gap:6px;font-size:13.5px;font-weight:700;color:var(--muted,#666);cursor:pointer;min-height:36px}
.xpv-me input{width:18px;height:18px;accent-color:#c9a400;margin:0}
.xpv-stage{position:relative;border-radius:14px;overflow:hidden;background:#11161f;aspect-ratio:1;touch-action:pan-y}
.xpv-stage svg{display:block;width:100%;height:100%}
.xpv .xf{fill:#1d2533}.xpv .xg{stroke:#fff;stroke-opacity:.07;stroke-width:1.5;fill:none}.xpv .xt{stroke:#9fb0d0;stroke-opacity:.35;stroke-width:1.5}.xpv .xT{stroke-opacity:.7;stroke-width:2.5}
.xpv .xrim{fill:none;stroke:#5d6f93;stroke-width:3}
.xpv .xm text{font:900 17px system-ui,sans-serif;text-anchor:middle;paint-order:stroke;stroke:#0d1220;stroke-width:3px}
.xpv .xx{font-weight:800;font-family:system-ui,sans-serif;paint-order:stroke;stroke:#0d1220;stroke-width:4px}
.xpv .xpt{font:900 13px system-ui,sans-serif;fill:#fff;text-anchor:middle;letter-spacing:.02em}
.xpv .tok{transition:transform .45s cubic-bezier(.3,.7,.2,1),opacity .3s}
.xpv .lay{animation:xpvIn .3s ease-out}
@keyframes xpvIn{from{opacity:0}to{opacity:1}}
@media (prefers-reduced-motion:reduce){.xpv .tok{transition:none}.xpv .lay{animation:none}}
.xpv-cap{margin:0;min-height:1.6em;font-size:15px;line-height:1.55;font-weight:700}
.xpv-cap small{display:block;font-weight:400;color:var(--muted,#666);font-size:13.5px}
.xpv-nav{display:flex;gap:6px;align-items:center}
.xpv-nav .xpv-steps{display:flex;gap:4px;flex:1;min-width:0}
.xpv-nav .xpv-steps button{flex:1;min-width:0;min-height:40px;border:1px solid var(--line,#ddd);background:var(--surface,#fff);border-radius:10px;font:inherit;font-size:13.5px;font-weight:700;color:var(--muted,#666);cursor:pointer;font-variant-numeric:tabular-nums;padding:0 4px}
.xpv-nav .xpv-steps button[aria-current=step]{background:var(--ink,#222);border-color:var(--ink,#222);color:var(--surface,#fff)}
.xpv-nav .xpv-arr{width:40px;min-height:40px;border:1px solid var(--line,#ddd);background:var(--surface,#fff);border-radius:10px;cursor:pointer;color:var(--ink,#222);font-size:18px;line-height:1;flex:none}
.xpv-nav button:focus-visible,.xpv-seg button:focus-visible{outline:3px solid var(--accent,#c55);outline-offset:2px}
.xpv-foot{display:flex;justify-content:space-between;gap:8px;font-size:13px;color:var(--muted,#666);flex-wrap:wrap}
.xpv-foot a{color:inherit;text-decoration:underline;text-underline-offset:2px}
.xpv-err{padding:14px;border-radius:12px;background:var(--surface2,#eee);color:var(--muted,#666);font-size:14px}`;
let cssDone = false;
function css() { if (cssDone) return; cssDone = true; const s = document.createElement("style"); s.textContent = CSS; document.head.appendChild(s); }

/* 掛上播放器。回傳 {destroy} */
export function xpMount(el, entries, opts = {}) {
  css();
  const st = { v: Math.min(opts.v || 0, entries.length - 1), i: opts.i || 0, mine: opts.mine !== false, sc: null, owners: null, gen: 0 };
  el.classList.add("xpv");
  el.innerHTML = '<div class="xpv-err">站位圖載入中…</div>';
  async function load() {
    const g = ++st.gen, e = entries[st.v];
    try {
      const sc = await xpDecode(e.url);
      if (g !== st.gen) return;
      st.sc = sc; st.owners = xpArrowOwners(sc); st.i = Math.min(st.i, sc.steps.length - 1);
      build();
    } catch (err) { console.warn("xivplan", err); if (g === st.gen) el.innerHTML = '<div class="xpv-err">這張站位圖讀不出來，<a href="' + esc(e.url) + '" target="_blank" rel="noopener noreferrer">到 xivplan 看</a>。</div>'; }
  }
  function build() {
    const sc = st.sc, vb = viewBox(sc), n = sc.steps.length;
    const slots = new Set(); sc.steps.forEach(s => partyOf(s).forEach((o, k) => { if (!k.startsWith("#")) slots.add(k); }));
    const me = opts.me && slots.has(opts.me) ? opts.me : "";
    const un = xpUnsupported(sc);
    let h = '<div class="xpv-top">';
    if (entries.length > 1) h += '<div class="xpv-seg" role="group" aria-label="版本">' + entries.map((e, k) => '<button type="button" data-xv="' + k + '" aria-pressed="' + (k === st.v) + '">' + esc(e.label || "站位圖") + '</button>').join("") + '</div>';
    if (me) h += '<label class="xpv-me"><input type="checkbox" data-xme' + (st.mine ? " checked" : "") + '>只看我（' + esc(me) + '）</label>';
    h += '</div><div class="xpv-stage"><svg xmlns="' + NS + '" viewBox="' + vb.map(v => v.toFixed(1)).join(" ") + '" role="img" aria-label="站位圖"><g class="flr">' + floorSVG(sc) + '</g><g class="lay"></g><g class="pty"></g></svg></div>';
    h += '<p class="xpv-cap" aria-live="polite"></p>';
    if (n > 1) h += '<div class="xpv-nav"><button type="button" class="xpv-arr" data-xs="-1" aria-label="上一步">‹</button><div class="xpv-steps">' + sc.steps.map((s, k) => '<button type="button" data-xi="' + k + '">' + esc(stepLabel(sc, k)) + '</button>').join("") + '</div><button type="button" class="xpv-arr" data-xs="1" aria-label="下一步">›</button></div>';
    h += '<div class="xpv-foot"><span>' + (un.length ? "有部分內容這裡沒畫出來，" : "") + '</span><a href="' + esc(entries[st.v].url) + '" target="_blank" rel="noopener noreferrer">在 xivplan 開啟</a></div>';
    el.innerHTML = h; st.me = me; st.tok = new Map();
    draw(true);
  }
  function draw(first) {
    const sc = st.sc, step = sc.steps[st.i], me = st.mine ? st.me : "", svg = el.querySelector("svg");
    const lay = svg.querySelector(".lay"), nl = document.createElementNS(NS, "g");
    nl.setAttribute("class", "lay"); nl.innerHTML = layerSVG(sc, st.i, me, st.owners); lay.replaceWith(nl);
    const pty = svg.querySelector(".pty"), P = partyOf(step), seen = new Set();
    /* 自己畫在最上面 */
    const order = [...P.keys()].sort((a, b) => (a === st.me) - (b === st.me));
    order.forEach(k => {
      const o = P.get(k), slot = k.startsWith("#") ? "" : k; seen.add(k);
      let g = st.tok.get(k);
      if (!g) { g = document.createElementNS(NS, "g"); g.setAttribute("class", "tok"); g.innerHTML = '<circle class="ring" r="23" fill="none" stroke="' + ME_RING + '" stroke-width="4.5"/>' + tokenInner(slot, o.name, opts); st.tok.set(k, g); if (first) g.style.transition = "none"; }
      pty.appendChild(g);
      g.style.transform = `translate(${num(o.x)}px,${-num(o.y)}px)`;
      const isMe = !!st.me && k === st.me;
      g.querySelector(".ring").style.display = isMe && st.mine ? "" : "none";
      g.style.opacity = me && !isMe ? .32 : op(o);
      g.setAttribute("aria-label", slot || "");
    });
    st.tok.forEach((g, k) => { if (!seen.has(k)) g.style.opacity = 0; });
    if (first) requestAnimationFrame(() => st.tok.forEach(g => { g.style.transition = ""; }));
    const c = captions(sc, step), cap = el.querySelector(".xpv-cap");
    cap.innerHTML = c.length ? esc(c[0]) + (c[1] ? "<small>" + esc(c[1]) + "</small>" : "") : (sc.steps.length > 1 ? esc(stepLabel(sc, st.i)) : "");
    el.querySelectorAll("[data-xi]").forEach(b => { if (+b.dataset.xi === st.i) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current"); });
    const a = el.querySelectorAll("[data-xs]"); if (a.length) { a[0].disabled = st.i === 0; a[1].disabled = st.i === sc.steps.length - 1; }
  }
  const go = i => { if (!st.sc) return; i = Math.max(0, Math.min(st.sc.steps.length - 1, i)); if (i === st.i) return; st.i = i; opts.onStep && opts.onStep(i); draw(false); };
  function onClick(e) {
    const b = e.target.closest("button,input"); if (!b || !el.contains(b)) return;
    if (b.dataset.xv != null) { const v = +b.dataset.xv; if (v !== st.v) { st.v = v; opts.onVersion && opts.onVersion(v); load(); } }
    else if (b.dataset.xi != null) go(+b.dataset.xi);
    else if (b.dataset.xs != null) go(st.i + +b.dataset.xs);
    else if (b.hasAttribute("data-xme")) { st.mine = b.checked; opts.onMine && opts.onMine(st.mine); draw(false); }
  }
  function onKey(e) { if (e.target.closest("input,textarea")) return; if (e.key === "ArrowRight") { go(st.i + 1); e.preventDefault(); } else if (e.key === "ArrowLeft") { go(st.i - 1); e.preventDefault(); } }
  let sx = null;
  const td = e => { sx = e.touches[0].clientX; }, te = e => { if (sx == null) return; const dx = e.changedTouches[0].clientX - sx; sx = null; if (Math.abs(dx) > 40) go(st.i + (dx < 0 ? 1 : -1)); };
  el.addEventListener("click", onClick); el.addEventListener("keydown", onKey);
  el.addEventListener("touchstart", td, { passive: true }); el.addEventListener("touchend", te);
  load();
  return { destroy() { st.gen++; el.removeEventListener("click", onClick); el.removeEventListener("keydown", onKey); el.removeEventListener("touchstart", td); el.removeEventListener("touchend", te); } };
}

/* 清單用的小縮圖（第一步、只看自己），點了再開完整播放器 */
export async function xpThumb(url, opts = {}) {
  const sc = await xpDecode(url), vb = viewBox(sc), st = sc.steps[0] || { objects: [] }, owners = xpArrowOwners(sc), me = opts.me || "";
  let p = "";
  const P = partyOf(st), order = [...P.keys()].sort((a, b) => (a === me) - (b === me));
  order.forEach(k => { const o = P.get(k), slot = k.startsWith("#") ? "" : k, isMe = me && k === me;
    p += `<g transform="translate(${num(o.x)} ${-num(o.y)})" opacity="${me && !isMe ? .32 : 1}">${isMe ? `<circle r="23" fill="none" stroke="${ME_RING}" stroke-width="4.5"/>` : ""}${tokenInner(slot, o.name, opts)}</g>`; });
  css();
  return `<svg class="xpv xpth" xmlns="${NS}" viewBox="${vb.map(v => v.toFixed(1)).join(" ")}" aria-hidden="true">${floorSVG(sc)}${layerSVG(sc, 0, me, owners)}${p}</svg>`;
}
