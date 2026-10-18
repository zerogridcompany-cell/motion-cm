// moji_dom.mjs <CompositionId> [--work <作業フォルダ>] [--per-sec 4] [--root ~/scratcher-basket/vsl/remotion]
// 字の切れ・重なり・字幕の帯（Remotion の中で字の箱を直接測る版・2026-10-18）。
// 1文字だけ切れた「k」も拾う（文字認識の moji_check.py は1文字を読めん）。元の Composition は変えん＝src/probe-index.ts が包む。
// 赤＝0.3秒以上続いた：切れ（箱の10〜90%だけ見えとる）／重なり（別の字同士が小さい方の30%以上）
// 黄＝1回だけの物・字幕の帯（下14.8%）に data-jimaku の無い字
// 出力＝<work>/moji_check.json（nouhin_gate.py が読む。moji_check.py と同じ形）
import fs from "node:fs"; import os from "node:os"; import path from "node:path";
import { createRequire } from "node:module"; import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const id = args[0];
const root = opt("--root", path.join(os.homedir(), "scratcher-basket/vsl/remotion"));
const work = path.resolve(opt("--work", process.cwd()));
const perSec = +opt("--per-sec", 4);
fs.mkdirSync(work, { recursive: true });
const req = createRequire(path.join(root, "package.json"));
const { bundle } = await import(pathToFileURL(req.resolve("@remotion/bundler")).href);
const { renderFrames, selectComposition } = await import(pathToFileURL(req.resolve("@remotion/renderer")).href);

const serveUrl = await bundle({ entryPoint: path.join(root, "src/probe-index.ts") });
const comp = await selectComposition({ serveUrl, id });
const W = comp.width, H = comp.height, fps = comp.fps;
const nth = Math.max(1, Math.round(fps / perSec));
const recs = {};
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "moji-"));
await renderFrames({
  serveUrl, composition: comp, outputDir: tmp, imageFormat: "jpeg", everyNthFrame: nth, concurrency: 4,
  onBrowserLog: (l) => { if (l.text.startsWith("MOJI")) { const j = JSON.parse(l.text.slice(4)); recs[j.f] = j.L; } },
  onStart: () => {}, onFrameUpdate: () => {},
});
fs.rmSync(tmp, { recursive: true, force: true });

const hits = new Map(); const add = (k, f) => { if (!hits.has(k)) hits.set(k, []); hits.get(k).push(f); };
const area = (b) => Math.max(0, b[2] - b[0]) * Math.max(0, b[3] - b[1]);
const inter = (a, b) => [Math.max(a[0], b[0]), Math.max(a[1], b[1]), Math.min(a[2], b[2]), Math.min(a[3], b[3])];
for (const [f, L] of Object.entries(recs)) {
  for (const x of L) {
    const screen = inter(x.b, [0, 0, W, H]); const vis = inter(screen, x.c);
    const r = area(vis) / Math.max(1, area(x.b));
    if (r > 0.1 && r < 0.9) add(`切れ|${x.t}`, +f);
    if (!x.sub && x.b[1] > H * 0.852 && r >= 0.9) add(`字幕の帯に字幕以外|${x.t}`, +f);
  }
  for (let i = 0; i < L.length; i++) for (let j = i + 1; j < L.length; j++) {
    if (L[i].id === L[j].id) continue;
    const o = area(inter(L[i].b, L[j].b)) / Math.max(1, Math.min(area(L[i].b), area(L[j].b)));
    if (o >= 0.3) add(`重なり|${L[i].t} × ${L[j].t}`, +f);
  }
}
const red = [], yellow = [];
for (const [k, fs_] of hits) {
  const [kind, txt] = k.split("|"); const s = [...new Set(fs_)].sort((a, b) => a - b);
  const runs = [[s[0], s[0]]];
  for (const f of s.slice(1)) { if (f - runs.at(-1)[1] <= nth) runs.at(-1)[1] = f; else runs.push([f, f]); }
  for (const [a, b] of runs) {
    const item = { 種類: kind, 字: txt, 秒: [+(a / fps).toFixed(2), +((b + nth) / fps).toFixed(2)] };
    const long = (b + nth - a) / fps >= 0.3;
    (long && kind !== "字幕の帯に字幕以外" ? red : yellow).push(item);
  }
}
const out = { comp: id, size: [W, H], sampled: Object.keys(recs).length, red, yellow, note: "赤＝0.3秒以上の切れ・重なり／黄＝一瞬・字幕の帯（data-jimaku の無い字）" };
fs.writeFileSync(path.join(work, "moji_check.json"), JSON.stringify(out, null, 1));
for (const [c, L] of [["🔴", red], ["🟡", yellow]]) for (const x of L) console.log(c, x.種類, `${x.秒[0]}–${x.秒[1]}秒`, x.字);
console.log(`測ったコマ ${out.sampled}・赤 ${red.length}・黄 ${yellow.length} → ${path.join(work, "moji_check.json")}`);
process.exit(red.length ? 2 : 0);
