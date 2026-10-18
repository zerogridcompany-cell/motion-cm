// 字の位置を測る入口（motion-cm moji_dom.mjs 専用・2026-10-18）。本番の書き出しは index.ts のまま。
import { registerRoot } from "remotion";
import { ProbeRoot } from "./kit/MojiProbe";
registerRoot(ProbeRoot);
