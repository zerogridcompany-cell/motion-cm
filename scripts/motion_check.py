#!/usr/bin/env python3
"""motion_check.py — 書き出した mp4 の「止まり率」と、cues.json の「動きの種類数」を測る。

使い方:
  python3 motion_check.py out.mp4                 # 止まりだけ
  python3 motion_check.py out.mp4 cues.json       # ＋動きの種類数（scenes[].motion の名前）

測り方（cm3 / cm4n で使ったのと同じ）:
  15fps・96×96・白黒に落として、前のコマとの差の平均（0〜255）を取る。
  差 < 0.15 ＝ 止まり／差 > 25 ＝ 大きな飛び（hardcut）／明るさ平均 < 12 ＝ 暗転。
  閾値の根拠＝cm3/cm4n の実物で「目で止まって見えた所」と合わせた値（2026-10-12）。
  🔴 ゆっくりのカメラ（Ken Burns 等）は止まりに数えられやすい。各場面に一方向の動きを足すと下がる（cm4n v1 15% → 2〜3%）。

合格の目安（SKILL.md 手順7）: 止まり 30秒あたり1秒以下（≒3%以下）・0.6秒超の止め無し・動きの種類5以上。
終了コード: 目安を外れたら 1。
"""
import json, re, subprocess, sys
import numpy as np

FPS, W, H = 15, 96, 96
STILL, CUT, DARK = 0.15, 25.0, 12.0


def frames(path):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", path,
                          "-vf", f"fps={FPS},scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)


def runs(mask):
    out, start = [], None
    for i, s in enumerate(list(mask) + [False]):
        if s and start is None:
            start = i
        elif not s and start is not None:
            out.append((start, i)); start = None
    return out


def motion_names(cues_path):
    c = json.load(open(cues_path))
    names = set()
    for sc in c.get("scenes", []):
        ms = sc.get("motion", [])
        if isinstance(ms, str):
            ms = [ms]
        for m in ms:
            mm = re.match(r"([A-Za-z][A-Za-z\- ]+?)(?: \d|（|＝|$)", str(m))
            if mm:
                names.add(mm.group(1).strip())
    return names


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    a = frames(sys.argv[1])
    d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
    dur = len(a) / FPS
    still = d < STILL
    sr = [(s / FPS, e / FPS) for s, e in runs(still)]
    longest = max([e - s for s, e in sr] or [0])
    long_stops = [(s, e) for s, e in sr if e - s > 0.6]
    cuts = [round(float(i + 1) / FPS, 2) for i in np.where(d > CUT)[0]]
    dark = float((a.mean(axis=(1, 2)) < DARK).sum() / FPS)
    still_s = float(still.sum() / FPS)
    per30 = still_s / dur * 30 if dur else 0

    print(f"長さ {dur:.1f}秒 ／ 止まり {still.mean()*100:.1f}%（{still_s:.1f}秒・30秒あたり {per30:.2f}秒）")
    print(f"最長の止まり {longest:.2f}秒 ／ 0.6秒超の止め {len(long_stops)}か所 ／ 暗転 {dark:.1f}秒 ／ 動きの平均 {d.mean():.2f}")
    for s, e in long_stops:
        print(f"   止め {s:.2f}〜{e:.2f}秒（{e-s:.2f}秒）")
    print(f"大きな飛び（hardcut） {len(cuts)}回: {cuts[:30]}")

    ng = []
    if per30 > 1.0:
        ng.append(f"止まりが30秒あたり {per30:.2f}秒 > 1秒")
    if long_stops:
        ng.append(f"0.6秒超の止めが {len(long_stops)}か所")
    if len(sys.argv) > 2:
        names = motion_names(sys.argv[2])
        print(f"動きの種類 {len(names)}: {sorted(names)}")
        if len(names) < 5:
            ng.append(f"動きの種類 {len(names)} < 5")
    print("NG", len(ng)); [print("  NG", x) for x in ng]
    sys.exit(1 if ng else 0)


if __name__ == "__main__":
    main()
