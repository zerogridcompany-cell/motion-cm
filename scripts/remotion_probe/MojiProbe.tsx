// 各コマで画面の字（テキストノード）の箱を測って console に出す（motion-cm moji_dom.mjs が拾う）。
// Root の全 Composition をそのまま包むだけ＝元のファイルは変えん。
import React, { useEffect } from "react";
import { Composition, continueRender, delayRender, useCurrentFrame } from "remotion";
import { Root } from "../Root";

const vis = (el: Element | null): number => {
  let o = 1;
  for (let e = el; e && e !== document.body; e = e.parentElement) {
    const s = getComputedStyle(e);
    if (s.display === "none" || s.visibility === "hidden") return 0;
    o *= parseFloat(s.opacity || "1");
  }
  return o;
};
const clip = (el: Element | null) => {
  let c = { x0: -1e9, y0: -1e9, x1: 1e9, y1: 1e9 };
  for (let e = el?.parentElement; e && e !== document.body; e = e.parentElement) {
    const s = getComputedStyle(e);
    if (s.overflow !== "visible" || s.clipPath !== "none") {
      const r = e.getBoundingClientRect();
      c = { x0: Math.max(c.x0, r.left), y0: Math.max(c.y0, r.top), x1: Math.min(c.x1, r.right), y1: Math.min(c.y1, r.bottom) };
    }
  }
  return c;
};

const Probe: React.FC = () => {
  const frame = useCurrentFrame();
  useEffect(() => {
    const h = delayRender("moji");
    requestAnimationFrame(() => {
      const out: any[] = [];
      const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let n: Node | null; let id = 0;
      while ((n = w.nextNode())) {
        const t = (n.textContent || "").trim();
        if (!t) continue;
        const el = n.parentElement; const o = vis(el);
        if (o < 0.05) continue;
        const c = clip(el); const r = document.createRange(); r.selectNodeContents(n);
        const sub = !!el?.closest("[data-jimaku]");
        for (const b of Array.from(r.getClientRects())) {
          if (b.width < 1 || b.height < 9) continue;
          out.push({ id, t: t.slice(0, 30), o: +o.toFixed(2), sub, b: [b.left, b.top, b.right, b.bottom].map(Math.round), c: [c.x0, c.y0, c.x1, c.y1].map(Math.round) });
        }
        id++;
      }
      console.log("MOJI" + JSON.stringify({ f: frame, L: out }));
      continueRender(h);
    });
  }, [frame]);
  return null;
};

const wrap = (C: any) => (p: any) => (<><C {...p} /><Probe /></>);

export const ProbeRoot: React.FC = () => {
  const tree: any = (Root as any)();
  const map = (ch: any): any => React.Children.map(ch, (el: any) => {
    if (!React.isValidElement(el)) return el;
    const e: any = el;
    if (e.type === Composition && e.props.component) return React.cloneElement(e, { component: wrap(e.props.component) });
    if (e.props?.children) return React.cloneElement(e, {}, map(e.props.children));
    return e;
  });
  return <>{map(tree.props.children)}</>;
};
