/* 減傷軸：血量檢查（純計算，不碰畫面和資料庫，方便單獨測試）

   資料（全部選填，舊資料照常可用）
   - 機制 row.aoe：all 全體｜tank 單坦（死刑）｜tanks 雙坦分攤｜share 分攤｜spread 分散｜single 單體（非坦）
       沒填時依 row.tag 推：死刑→tank、全體AOE→all、分攤→share、分散→spread；都沒有就當全體
   - 每段傷害 hit：dtype（phys／magic／true）、dmg（文字，例「92,000」「9.2萬」「80k」）、n（次數）、off（距第一段幾秒）
       dot（持續傷害每跳，文字）、tk（跳數）、iv（每跳間隔秒數，預設 3）
       傷害數值一律是「每個人實際吃到的量」（分攤要先除好，和日文減傷表的 Hit 欄一樣）
   - 副本 duty.hp：{tank, ranged, caster}；duty.chain：連段秒數（預設 5）

   判斷誰最危險（團隊的排軸習慣）
   - 死刑、雙坦分攤 → 看坦克
   - 其他物理 → 看法系；魔法 → 看遠敏；真實／不確定 → 兩者取剩比較少的
   連段：前一下和這一下相隔不超過 chain 秒，就當作中間沒補血，傷害累加；隔太久就重新算
   補血不列入（看的是最壞情況） */

export const HP_DEF = { tank: 225800, ranged: 142000, caster: 142000 };
export const CHAIN_DEF = 5;
export const AOE = { all: "全體", tank: "死刑", tanks: "雙坦分攤", share: "分攤", spread: "分散", single: "單體" };
export const ROLE_N = { tank: "坦克", ranged: "遠敏", caster: "法系" };
const TAG_AOE = { "死刑": "tank", "全體AOE": "all", "分攤": "share", "分散": "spread" };

/* 「92,000」「9.2萬」「80k」「1.2m」「800000」→ 數字；看不懂回 0 */
export function parseDmg(s) {
  if (s == null) return 0;
  if (typeof s === "number") return Number.isFinite(s) && s > 0 ? s : 0;
  const m = String(s).replace(/[,，\s]/g, "").match(/^(\d+(?:\.\d+)?)(萬|万|w|k|m)?$/i);
  if (!m) return 0;
  const v = parseFloat(m[1]) * ({ "萬": 1e4, "万": 1e4, w: 1e4, k: 1e3, m: 1e6 }[(m[2] || "").toLowerCase()] || 1);
  return v > 0 && v < 1e8 ? Math.round(v) : 0;
}
export const fmtN = v => Math.round(v).toLocaleString("en-US");
export const aoeOf = r => (r.aoe && AOE[r.aoe]) ? r.aoe : (TAG_AOE[r.tag] || "");
const posNum = (v, d) => { const n = +v; return Number.isFinite(n) && n > 0 ? n : d; };
export function hpCfg(duty) {
  const h = (duty && duty.hp) || {};
  return {
    hp: { tank: posNum(h.tank, HP_DEF.tank), ranged: posNum(h.ranged, HP_DEF.ranged), caster: posNum(h.caster, HP_DEF.caster) },
    chain: Math.min(30, posNum(duty && duty.chain, CHAIN_DEF))
  };
}

/* rows：同一個階段的機制（含段落列）；times：每列的秒數（可以是推估），和 rows 一樣長
   回傳 { [rowId]: 結果 }，只有有傷害數值的列才有 */
export function hpCheck(rows, times, cfg) {
  const ev = [];
  rows.forEach((r, i) => {
    if (!r || r.virt || r.kind === "head") return;
    const T = times[i]; if (T == null) return;
    const aoe = aoeOf(r), tankOnly = aoe === "tank" || aoe === "tanks";
    (r.hits || []).forEach(h => {
      const off = posNum(h.off, 0), d = parseDmg(h.dmg), n = Math.max(1, Math.floor(posNum(h.n, 1)));
      if (d) ev.push({ t: T + off, d: d * n, dt: h.dtype || "", r, tankOnly, dot: false });
      const dv = parseDmg(h.dot), tk = Math.floor(posNum(h.tk, 0)), iv = posNum(h.iv, 3);
      if (dv && tk) for (let k = 1; k <= Math.min(tk, 60); k++) ev.push({ t: T + off + iv * k, d: dv, dt: h.dtype || "", r, tankOnly, dot: true });
    });
  });
  ev.sort((a, b) => a.t - b.t);
  const st = { tank: { last: -1e9, sum: 0, from: null }, ranged: { last: -1e9, sum: 0, from: null }, caster: { last: -1e9, sum: 0, from: null } };
  const out = {};
  ev.forEach(e => {
    const who = e.tankOnly ? ["tank"] : ["tank", "ranged", "caster"];
    who.forEach(k => {
      const s = st[k];
      if (e.t - s.last > cfg.chain) { s.sum = 0; s.from = e.r; }
      s.sum += e.d; s.last = e.t;
    });
    const o = out[e.r.id] || (out[e.r.id] = { raw: 0, dot: 0, dotN: 0, dt: e.dt, tankOnly: e.tankOnly, after: null, dotAfter: null, chainFrom: null });
    const snap = { tank: st.tank.sum, ranged: st.ranged.sum, caster: st.caster.sum };
    if (e.dot) { o.dot = o.dot || e.d; o.dotN++; o.dotAfter = snap; }
    else {
      o.raw += e.d; o.after = snap;
      if (!o.dt) o.dt = e.dt;
      const k = e.tankOnly ? "tank" : e.dt === "phys" ? "caster" : "ranged";
      o.chainFrom = st[k].from && st[k].from !== e.r ? st[k].from : null;
    }
  });
  Object.values(out).forEach(o => {
    const left = sums => sums ? {
      tank: cfg.hp.tank - sums.tank, ranged: cfg.hp.ranged - sums.ranged, caster: cfg.hp.caster - sums.caster
    } : null;
    const L = left(o.after), LD = left(o.dotAfter);
    let role;
    if (o.tankOnly) role = "tank";
    else if (o.dt === "phys") role = "caster";
    else if (o.dt === "magic") role = "ranged";
    else role = (L || LD) && (L || LD).caster < (L || LD).ranged ? "caster" : "ranged";
    o.role = role; o.hp = cfg.hp[role];
    o.left = L ? L[role] : null;          // 這一下打完剩多少（只有持續傷害的列是 null）
    o.dotLeft = LD ? LD[role] : null;     // 持續傷害全部跳完剩多少
    o.chain = !!(o.after && (o.after[role] > o.raw + 0.5));  // 這一下之前還有沒補回來的傷害
    const worst = o.dotLeft != null ? Math.min(o.left == null ? Infinity : o.left, o.dotLeft) : o.left;
    o.worst = worst;
    o.level = worst <= 0 ? "dead" : worst < o.hp * 0.2 ? "warn" : "ok";
    delete o.after; delete o.dotAfter;
  });
  return out;
}
