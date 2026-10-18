// kakutei.mjs <CompositionId> [--work <作業フォルダ>] [--n 4] [--root ~/scratcher-basket/vsl/remotion]
// 同じ絵が出るかの検査（2026-10-18・huashu qa.py の「冷/温の2回描画」＝MIT の考え方）。
// 散らばった n コマを「順に1回目→逆順で2回目」と2回描いて、画素が1つでも違えば赤。
// 原因はたいてい Math.random()（→ remotion の random("種")）か、前のコマの状態・時計（Date.now）に頼っとる所。
// 1コマの描き時間も出す（150ms/コマ超えは黄＝書き出しが重い）。出力＝<work>/kakutei.json
import fs from "node:fs"; import os from "node:os"; import path from "node:path"; import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module"; import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const id = args[0];
const root = opt("--root", path.join(os.homedir(), "scratcher-basket/vsl/remotion"));
const work = path.resolve(opt("--work", process.cwd()));
const n = +opt("--n", 4);
fs.mkdirSync(work, { recursive: true });
process.chdir(root); // ブラウザの控え（.remotion）を Remotion の作業フォルダに置く
const req = createRequire(path.join(root, "package.json"));
const { bundle } = await import(pathToFileURL(req.resolve("@remotion/bundler")).href);
const { renderStill, selectComposition } = await import(pathToFileURL(req.resolve("@remotion/renderer")).href);

const serveUrl = await bundle({ entryPoint: path.join(root, "src/index.ts") });
const comp = await selectComposition({ serveUrl, id });
const frames = Array.from({ length: n }, (_, i) => Math.round((comp.durationInFrames - 1) * (i + 0.5) / n));
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "kakutei-"));
const shot = async (f, tag) => {
  const out = path.join(tmp, `${tag}_${f}.png`); const t = Date.now();
  await renderStill({ serveUrl, composition: comp, frame: f, output: out, imageFormat: "png" });
  return { out, ms: Date.now() - t, md5: crypto.createHash("md5").update(fs.readFileSync(out)).digest("hex") };
};
const A = {}, B = {};
for (const f of frames) A[f] = await shot(f, "a");
for (const f of [...frames].reverse()) B[f] = await shot(f, "b");
const red = [], yellow = [];
for (const f of frames) {
  if (A[f].md5 !== B[f].md5) {
    let psnr = "?";
    try { psnr = execFileSync("ffmpeg", ["-hide_banner", "-i", A[f].out, "-i", B[f].out, "-lavfi", "psnr", "-f", "null", "-"], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }); } catch (e) { psnr = String(e.stderr || ""); }
    const m = /average:([\w.]+)/.exec(psnr);
    red.push({ コマ: f, 秒: +(f / comp.fps).toFixed(2), 違い_PSNR: m ? m[1] : "?" });
    fs.copyFileSync(A[f].out, path.join(work, `kakutei_${f}_1回目.png`)); fs.copyFileSync(B[f].out, path.join(work, `kakutei_${f}_2回目.png`));
  }
}
const ms = frames.map(f => B[f].ms); const avg = ms.reduce((a, b) => a + b, 0) / ms.length;
if (avg > 150 * 4) yellow.push({ 描き時間: `${avg.toFixed(0)}ms/コマ（1枚ずつの静止画の値・目安は書き出しで150ms/コマ）` });
fs.rmSync(tmp, { recursive: true, force: true });
const out = { comp: id, frames, red, yellow, ms_per_still: Math.round(avg) };
fs.writeFileSync(path.join(work, "kakutei.json"), JSON.stringify(out, null, 1));
for (const x of red) console.log("🔴 2回描いたら違う絵", x);
for (const x of yellow) console.log("🟡", x);
console.log(`コマ ${frames.join(",")}・赤 ${red.length} → ${path.join(work, "kakutei.json")}`);
process.exit(red.length ? 2 : 0);
