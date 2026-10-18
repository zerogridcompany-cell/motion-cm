#!/usr/bin/env python3
"""shinsa_zairyo.py <完成.mp4> [--work <作業フォルダ>]
動画で見る審査の材料（2026-10-18・huashu「独立审片」の形）。作っとらん係には、この材料と mp4 だけを渡す（台本・設計・会話は渡さん）。
出す物（<work>/審査_材料/）
 - tiles_NN.jpg：0.25秒ごとのコマを4秒ずつ 4x4 に並べた物（左上から時刻順・各コマに秒を焼く＝審査の材料なので ffmpeg で可）
 - ugoki.csv：0.25秒ごとの「前のコマとの違い」（なめらかさ：急に跳ねる所・止まる所が数で見える）
 - oto.csv：音の山の時刻（効果音・声の出だし）と、各山に一番近い絵の切れ目との差（ms）
 - README.md：係への頼み方（references/douga_shinsa.md の文をそのまま）
"""
import argparse, json, os, re, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def run(c):
    return subprocess.run(c, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mp4"); ap.add_argument("--work"); a = ap.parse_args()
    mp4 = os.path.abspath(a.mp4); work = os.path.abspath(a.work or os.path.dirname(mp4))
    d = os.path.join(work, "審査_材料"); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4]).stdout)
    # 0.25秒ごと・4秒で1枚（16コマ）
    vf = ("fps=4,scale=480:-2,drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6,tile=4x4")
    r = run(["ffmpeg", "-loglevel", "error", "-i", mp4, "-vf", vf, os.path.join(d, "tiles_%02d.jpg")])
    if r.returncode:  # drawtext の無い ffmpeg
        run(["ffmpeg", "-loglevel", "error", "-i", mp4, "-vf", "fps=4,scale=480:-2,tile=4x4", os.path.join(d, "tiles_%02d.jpg")])
    # 動きの曲線
    out = run(["ffmpeg", "-hide_banner", "-i", mp4, "-vf", "fps=4,scale=160:-2,format=gray,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"]).stderr
    ys = [float(x) for x in re.findall(r"YAVG=([\d.]+)", out)]
    with open(os.path.join(d, "ugoki.csv"), "w") as f:
        f.write("秒,違い\n")
        for i, y in enumerate(ys): f.write(f"{(i + 1) / 4:.2f},{y:.2f}\n")
    # 絵の切れ目
    sc = run(["ffmpeg", "-hide_banner", "-i", mp4, "-vf", "select='gt(scene,0.3)',metadata=print", "-an", "-f", "null", "-"]).stderr
    cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", sc)]
    # 音の山（20msごとの音の強さが、直前0.1秒の一番小さい所より 6dB 以上跳ねた所＝効果音・声の出だし。BGM が鳴りっぱなしでも拾える）
    sr = 48000
    st = run(["ffmpeg", "-hide_banner", "-i", mp4, "-af", f"aresample={sr},asetnsamples=n={sr//50}:p=0,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level", "-f", "null", "-"]).stderr
    lv = [float(x) if x not in ("-inf", "inf") else -120.0 for x in re.findall(r"RMS_level=(-?[\w.]+)", st)]
    ons, last = [], -1
    for i in range(5, len(lv)):
        if lv[i] > -40 and lv[i] - min(lv[i - 5:i]) >= 6 and i - last > 5:
            ons.append(i / 50); last = i
    # 絵の出来事＝切れ目＋動きの山（前後1秒の中央値の3倍以上）→ 一番近い音の出だしとの差
    ev = [(c, "切れ目") for c in cuts]
    for i, y in enumerate(ys):
        win = sorted(ys[max(0, i - 4):i + 5]); med = win[len(win) // 2]
        if y >= max(3 * med, 2.0) and all(abs((i + 1) / 4 - e) > 0.3 for e, _ in ev):
            ev.append(((i + 1) / 4, "動きの山"))
    with open(os.path.join(d, "oto.csv"), "w") as f:
        f.write("絵の出来事秒,種類,一番近い音の出だし,差ms（+は音が遅い）\n")
        for t, k in sorted(ev):
            o = min(ons, key=lambda x: abs(x - t)) if ons else None
            f.write(f"{t:.3f},{k},{'' if o is None else f'{o:.3f}'},{'' if o is None else round((o - t) * 1000)}\n")
    shutil.copy(os.path.join(os.path.dirname(HERE), "references", "douga_shinsa.md"), os.path.join(d, "README.md"))
    os.makedirs(os.path.join(work, "審査"), exist_ok=True)
    print(json.dumps({"材料": d, "尺": round(dur, 2), "タイル": len([x for x in os.listdir(d) if x.startswith('tiles')]),
                      "切れ目": len(cuts), "音の出だし": len(ons), "審査の置き場": os.path.join(work, "審査")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
