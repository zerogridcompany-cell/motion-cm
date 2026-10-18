#!/usr/bin/env python3
"""moji_check.py <完成.mp4> [--work <作業フォルダ>] [--fps 4] [--sub-band 0.148] [--sync sync.json]
字の切れ・重なり・字幕の帯の検査（2026-10-18・huashu qa.py／cth9191 textcheck の考え方を、Remotion でもどの道具でも効くよう「画面の字を読む」形にした）。
0.25秒ごとにコマを抜き、macOS の文字認識（ocr_lines・無料）で1行ずつの箱を取る。初回は `swiftc -O scripts/ocr_lines.swift -o scripts/ocr_lines` で作る。

赤＝0.3秒以上（2コマ続けて）同じ所で起きた物
 - 切れ：字の箱が画面の端から 4px 以内に触れとる（はみ出して切れとる）
 - 重なり：別の字の箱同士が小さい方の30%以上重なる
 - 字幕の帯に字幕以外：下 sub-band（既定 14.8%＝1920高で y>1636・1080高で y>920）に入った字が、--sync の字幕の文と合わん
黄＝1コマだけ（カメラが通り過ぎる一瞬かもしれん）→ 目で見に行く
出力＝<work>/moji_check.json（nouhin_gate.py が読む）＋ <work>/moji_check/ のコマ
"""
import argparse, json, os, subprocess, sys, shutil, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
OCR = os.path.join(HERE, "ocr_lines")


def ov(a, b):
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    s = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return (x1 - x0) * (y1 - y0) / max(s, 1)


def subs_at(sync, t):
    out = []
    for r in sync:
        if r.get("in", 0) - 0.1 <= t <= r.get("out", 0) + 0.1:
            out.append("".join(r.get("rows") or [r.get("text", "")]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4"); ap.add_argument("--work"); ap.add_argument("--fps", type=float, default=4)
    ap.add_argument("--sub-band", type=float, default=0.148); ap.add_argument("--sync")
    a = ap.parse_args()
    mp4 = os.path.abspath(a.mp4); work = os.path.abspath(a.work or os.path.dirname(mp4))
    fd = os.path.join(work, "moji_check"); shutil.rmtree(fd, ignore_errors=True); os.makedirs(fd)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp4, "-vf", f"fps={a.fps}", os.path.join(fd, "f%05d.png")], check=True)
    files = sorted(os.listdir(fd))
    sync = json.load(open(a.sync, encoding="utf-8")) if a.sync else None
    if isinstance(sync, dict):
        sync = sync.get("lines") or sync.get("subs") or []
    hits = {}  # (種類, 字) -> [時刻]
    for i in range(0, len(files), 40):
        r = subprocess.run([OCR] + [os.path.join(fd, f) for f in files[i:i + 40]], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            j = json.loads(line); t = (int(j["f"][1:6]) - 1) / a.fps; W, H = j["w"], j["h"]
            L = [x for x in j["lines"] if (x["b"][3] - x["b"][1]) >= 9 and x["t"].strip()]
            for x in L:
                b = x["b"]
                if b[0] <= 4 or b[1] <= 4 or b[2] >= W - 4 or b[3] >= H - 4:
                    hits.setdefault(("切れ", x["t"]), []).append(t)
                if sync is not None and b[1] > H * (1 - a.sub_band):
                    cand = subs_at(sync, t)
                    if not any(difflib.SequenceMatcher(None, x["t"], c).ratio() > 0.4 or x["t"] in c for c in cand):
                        hits.setdefault(("字幕の帯に字幕以外", x["t"]), []).append(t)
            for m in range(len(L)):
                for n in range(m + 1, len(L)):
                    if ov(L[m]["b"], L[n]["b"]) >= 0.30:
                        hits.setdefault(("重なり", L[m]["t"] + " × " + L[n]["t"]), []).append(t)
    red, yellow = [], []
    step = 1 / a.fps
    for (k, txt), ts in sorted(hits.items(), key=lambda kv: kv[1][0]):
        ts = sorted(set(ts)); runs = [[ts[0], ts[0]]]
        for t in ts[1:]:
            if t - runs[-1][1] <= step + 1e-6: runs[-1][1] = t
            else: runs.append([t, t])
        for s, e in runs:
            item = {"種類": k, "字": txt, "秒": [round(s, 2), round(e + step, 2)]}
            (red if e - s >= step - 1e-6 else yellow).append(item)
    out = {"mp4": mp4, "red": red, "yellow": yellow, "note": "赤＝0.3秒以上続いた・黄＝1コマだけ"}
    json.dump(out, open(os.path.join(work, "moji_check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for c, L in (("🔴", red), ("🟡", yellow)):
        for x in L:
            print(c, x["種類"], f'{x["秒"][0]}–{x["秒"][1]}秒', x["字"][:40])
    print(f"赤 {len(red)}・黄 {len(yellow)} → {os.path.join(work, 'moji_check.json')}")
    sys.exit(2 if red else 0)


if __name__ == "__main__":
    main()
