#!/usr/bin/env python3
"""conte_lint.py <conte.json> [--work <作業フォルダ>]
絵コンテ表の検査（作る前に機械で止める・2026-10-18・huashu storyboard_lint.py の考え方を日本語のうちの型に直した）。
出力＝<work>/conte_lint.json（nouhin_gate.py が読む）。赤があれば終了コード 2＝Remotion に入らん。

conte.json の形
{
  "style": "写真×モーション／高級MG／バウハウス…",   ← 無ければ赤
  "palette": ["#F4EFE6", "#1F6FB2", ...],             ← 無ければ赤・7色以上は黄・青紫（色相225–300°・彩度0.3以上）は赤（allow_blue_purple に理由を書けば黄）
  "chara": "出る物・人（猫・給水器・手だけ…）",       ← 無ければ赤
  "script": "ナレーション・台本の全文",               ← 画面の数字がここに無ければ赤
  "scenes": [
    {"t0": 0.0, "t1": 3.2, "obj": "給水器", "action": "水が上から落ちて器に広がる", "cam": "push", "text": "水、飲んでる？", "kind": "pic"}
  ]
}
cam の言葉＝static / push（寄る）/ pull（引く）/ pan / tilt / track / orbit / cut-in（ガツンと寄る）
kind＝pic（絵が主役）/ text（字だけ）/ logo（締めの商品とロゴ）

決まり（数字）
- 1場面：8秒超＝赤／6–8秒＝黄（6–8秒が全体の2割超＝赤）／1.2秒未満＝黄（拍の網目の早替えは cues 側で・場面はまとまりで書く）
- 画面の字：1場面 28字超＝赤・16字超＝黄
- 字だけの場面（kind=text）：全体の30%超＝赤／最初の場面が text＝赤（最後は logo なら可・text＝赤）
- 動きが「表示・出現・フェードイン・現れる」だけ＝赤（何がどう動くか書く）
- 同じ action が3場面続く＝黄・同じ cam が3回続く＝黄・push/cut-in が3回続く＝黄
- カメラ（static 以外）の替わりの間 2.6秒未満＝黄・どの15秒にも5回超＝黄・寄り（push/cut-in）1分に8回以上＝黄（30秒以上の時）
- 画面の数字が script に無い＝赤（作った数字を出さん）
"""
import argparse, colorsys, json, os, re, sys

MOJI_ONLY = re.compile(r"^(表示|出現|フェードイン|フェード|現れる|出る|表示する|出す)+$")


def hue_bp(h):
    h = h.lstrip("#")
    if len(h) != 6: return False
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    H, L, S = colorsys.rgb_to_hls(r, g, b)
    return 225 <= H * 360 <= 300 and S >= 0.30 and 0.06 <= L <= 0.90


def nums(s):
    s = s.translate(str.maketrans("０１２３４５６７８９．，", "0123456789.,"))
    return re.findall(r"\d+(?:[.,]\d+)?", s)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("conte"); ap.add_argument("--work"); a = ap.parse_args()
    c = json.load(open(a.conte, encoding="utf-8"))
    work = os.path.abspath(a.work or os.path.dirname(os.path.abspath(a.conte)))
    red, yel = [], []
    R = lambda m: red.append(m); Y = lambda m: yel.append(m)
    for k in ("style", "palette", "chara"):
        if not c.get(k): R(f"{k} が無い（画風・色・出る物の3行は必須）")
    pal = c.get("palette") or []
    if len(pal) > 6: Y(f"色が {len(pal)} 色（6色まで）")
    bp = [p for p in pal if hue_bp(p)]
    if bp: (Y if c.get("allow_blue_purple") else R)(f"青紫の色 {bp}（AIっぽい色。題材で要るなら allow_blue_purple に理由）")
    S = c.get("scenes") or []
    if not S: R("scenes が空")
    script = c.get("script", "")
    total = (S[-1]["t1"] - S[0]["t0"]) if S else 0
    long68 = 0; text_n = 0
    for i, s in enumerate(S):
        d = s["t1"] - s["t0"]; tag = f"場面{i+1}（{s['t0']}–{s['t1']}秒）"
        if d > 8: R(f"{tag} {d:.1f}秒＝長すぎ（8秒まで）")
        elif d >= 6: Y(f"{tag} {d:.1f}秒（6–8秒）"); long68 += d
        elif d < 1.2: Y(f"{tag} {d:.1f}秒＝短い（場面はまとまりで書く）")
        t = re.sub(r"\s", "", s.get("text", ""))
        if len(t) > 28: R(f"{tag} 画面の字 {len(t)}字（28字まで）")
        elif len(t) > 16: Y(f"{tag} 画面の字 {len(t)}字（16字まで）")
        act = re.sub(r"[\s、。]", "", s.get("action", ""))
        if not act or MOJI_ONLY.match(act): R(f"{tag} 動きが「{s.get('action','')}」だけ（何がどう動くか書く）")
        if s.get("kind") == "text": text_n += 1
        for n in nums(s.get("text", "")):
            if n not in nums(script): R(f"{tag} 画面の数字「{n}」が台本に無い")
    if S:
        if S[0].get("kind") == "text": R("最初の場面が字だけ（絵で始める）")
        if S[-1].get("kind") == "text": R("最後の場面が字だけ（商品とロゴ＝kind logo で締める）")
        if text_n / len(S) > 0.30: R(f"字だけの場面が {text_n}/{len(S)}＝30%超")
        if total and long68 / total > 0.2: R(f"6–8秒の場面が全体の {long68/total:.0%}（2割まで）")
        for i in range(len(S) - 2):
            tri = S[i:i + 3]
            if len({x.get("action") for x in tri}) == 1: Y(f"場面{i+1}〜{i+3} 同じ動きが3回")
            cams = [x.get("cam", "static") for x in tri]
            if len(set(cams)) == 1 and cams[0] != "static": Y(f"場面{i+1}〜{i+3} 同じカメラ {cams[0]} が3回")
            if all(x in ("push", "cut-in") for x in cams): Y(f"場面{i+1}〜{i+3} 3回続けて寄る")
        moves = [x["t0"] for x in S if x.get("cam", "static") != "static"]
        for p, q in zip(moves, moves[1:]):
            if q - p < 2.6: Y(f"{p}秒→{q}秒 カメラの替わりが {q-p:.1f}秒（2.6秒以上あける）")
        for m in moves:
            k = sum(1 for x in moves if m <= x < m + 15)
            if k > 5: Y(f"{m}秒からの15秒にカメラが {k}回（5回まで）"); break
        pushes = sum(1 for x in S if x.get("cam") in ("push", "cut-in"))
        if total >= 30 and pushes / (total / 60) >= 8: Y(f"寄りが1分に {pushes/(total/60):.1f}回（8回未満）")
    out = {"conte": os.path.abspath(a.conte), "red": red, "yellow": yel}
    json.dump(out, open(os.path.join(work, "conte_lint.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for m in red: print("🔴", m)
    for m in yel: print("🟡", m)
    print(f"赤 {len(red)}・黄 {len(yel)} → {os.path.join(work, 'conte_lint.json')}")
    sys.exit(2 if red else 0)


if __name__ == "__main__":
    main()
