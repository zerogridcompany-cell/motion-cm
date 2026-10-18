#!/usr/bin/env python3
"""nouhin_gate.py <完成.mp4> [--work <作業フォルダ>] [--allow-blue-purple "理由"] [--lufs -16] [--vertical auto|yes|no]
納品の門（2026-10-18・huashu-art-motion の film_gate/deliver の考え方＋うちの -16 LUFS）。
赤が1つでもあれば終了コード 2＝見せん・渡さん。黄は「見に行く場所」。緑と黄なら <work>/納品の紙.md を書いて sha256 で封印。

見る物（全部機械）
 1. film_gate（vendor_huashu・MIT・手を入れてない）：中段の空画面 0.3秒以上＝赤／青紫が時間の30%以上＝赤（12%以上＝黄）／快動コマ <0.035 赤・<0.06 黄（20秒未満は黄止まり）
 2. 音が入っとるか（音の流れが無い＝赤）
 3. 頭0.3秒・終わり0.3秒の黒（blackdetect d=0.1 pix_th=0.10）＝赤／途中の黒＝黄
 4. 音量 -16 LUFS ±0.5（外れ＝赤）・真の山 ≤ -1.0 dBTP（超え＝赤）
 5. 他の門の結果ファイル（<work> にある事）：
    moji_check.json（字の切れ・重なり）赤なら赤／無ければ赤
    kakutei.json（同じ絵が出るか）赤なら赤／無ければ黄
    審査/*.md（動画で見た審査・作っとらん係）無ければ赤
    conte_lint.json（絵コンテ表の検査）赤なら赤／無ければ黄
`--verify <納品の紙.md>` で封印の確かめ（事実の段が書き換わってないか）。
"""
import argparse, glob, hashlib, json, os, re, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
FG = os.path.join(HERE, "vendor_huashu", "film_gate.py")


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(p):
    j = json.loads(sh(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", p]).stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    n, d = (v["r_frame_rate"].split("/") if v else ("0", "1"))
    return dict(dur=float(j["format"]["duration"]), w=v and v["width"], h=v and v["height"],
                fps=round(int(n) / int(d), 3), audio=bool(a))


def blacks(p):
    e = sh(["ffmpeg", "-hide_banner", "-i", p, "-vf", "blackdetect=d=0.1:pix_th=0.10", "-an", "-f", "null", "-"]).stderr
    return [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", e)]


def loud(p):
    e = sh(["ffmpeg", "-hide_banner", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    tail = e[e.rfind("Summary:"):]
    I = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    TP = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return (float(I.group(1)) if I else None, float(TP.group(1)) if TP else None)


def seal(text):
    return hashlib.sha256(text.encode()).hexdigest()


def verify(path):
    s = open(path, encoding="utf-8").read()
    m = re.search(r"<!-- 事実ここから -->\n(.*?)<!-- 事実ここまで sha256:([0-9a-f]+) -->", s, re.S)
    if not m:
        print("🔴 封印が見つからん"); sys.exit(2)
    ok = seal(m.group(1)) == m.group(2)
    print("✅ 封印OK（事実の段は書き換わってない）" if ok else "🔴 事実の段が書き換わっとる"); sys.exit(0 if ok else 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4", nargs="?")
    ap.add_argument("--work", default=None)
    ap.add_argument("--allow-blue-purple", default=None)
    ap.add_argument("--lufs", type=float, default=-16.0)
    ap.add_argument("--vertical", default="auto")
    ap.add_argument("--verify", default=None)
    a = ap.parse_args()
    if a.verify:
        verify(a.verify)
    mp4 = os.path.abspath(a.mp4)
    work = os.path.abspath(a.work or os.path.dirname(mp4))
    rows = []  # (灯, 項目, 値)

    def add(c, k, v):
        rows.append((c, k, v))

    p0 = probe(mp4)
    # 1 film_gate
    cmd = ["uv", "run", "-q", FG, mp4, "--json", "--no-template", "--vertical", a.vertical]
    if a.allow_blue_purple:
        cmd += ["--allow-blue-purple", a.allow_blue_purple]
    r = sh(cmd)
    try:
        fg = json.loads(r.stdout[r.stdout.find("{"):])
    except Exception:
        fg = None
    if fg is None:
        add("赤", "film_gate", "読めんかった: " + (r.stderr or r.stdout)[-300:])
    else:
        L = {"red": "赤", "yellow": "黄", "green": "緑"}
        add(L.get(fg.get("gate_light"), "赤"), "film_gate 結論", fg.get("verdict"))
        add("赤" if fg.get("blank_run_s", 0) >= 0.3 else "緑", "中段の空画面（秒）", f"{fg.get('blank_run_s')} {fg.get('blank_runs_s')}")
        bp = fg.get("blue_purple_share", 0) or 0
        add("赤" if bp >= 0.30 and not a.allow_blue_purple else ("黄" if bp >= 0.12 else "緑"), "青紫の時間の割合", bp)
        fr = fg.get("fast_ratio", 0) or 0
        add("黄" if fr < 0.06 else "緑", "快動コマ（作者の基準・うちは未標定＝黄止まり）", fr)
        add("黄" if (fg.get("push_in_per_min") or 0) >= 8 and p0["dur"] >= 30 else "緑", "寄りの回数/分", fg.get("push_in_per_min"))
    # 2〜4
    p = probe(mp4)
    add("緑" if p["audio"] else "赤", "音の流れ", "あり" if p["audio"] else "無い")
    for s, e in blacks(mp4):
        if s <= 0.3 or e >= p["dur"] - 0.3:
            add("赤", "頭・終わりの黒", f"{s:.2f}–{e:.2f}秒")
        else:
            add("黄", "途中の黒", f"{s:.2f}–{e:.2f}秒")
    if p["audio"]:
        I, TP = loud(mp4)
        add("緑" if I is not None and abs(I - a.lufs) <= 0.5 else "赤", "音量 LUFS", I)
        add("緑" if TP is not None and TP <= -1.0 else "赤", "真の山 dBTP", TP)
    # 5 他の門
    def gate_file(name, missing):
        f = os.path.join(work, name)
        if not os.path.exists(f):
            add(missing, name, "無い（道具を回してない）"); return
        j = json.load(open(f, encoding="utf-8"))
        add("赤" if j.get("red") else ("黄" if j.get("yellow") else "緑"), name,
            f"赤{len(j.get('red', []))}・黄{len(j.get('yellow', []))}")
    gate_file("moji_check.json", "赤")
    gate_file("kakutei.json", "黄")
    gate_file("conte_lint.json", "黄")
    rv = sorted(glob.glob(os.path.join(work, "審査", "*.md")))
    add("緑" if rv else "赤", "動画で見た審査（審査/*.md）", ", ".join(os.path.basename(x) for x in rv) or "無い")

    red = [x for x in rows if x[0] == "赤"]
    for c, k, v in rows:
        print({"赤": "🔴", "黄": "🟡", "緑": "🟢"}.get(c, "  "), k, v)
    if red:
        print(f"\n🔴 赤 {len(red)}件＝見せん・渡さん。直して書き出し直す。"); sys.exit(2)
    fact = "\n".join([
        f"- 動画：{mp4}", f"- sha256（動画）：{hashlib.sha256(open(mp4, 'rb').read()).hexdigest()}",
        f"- 尺 {p['dur']:.2f}秒・{p['w']}x{p['h']}・{p['fps']}fps・音 {'あり' if p['audio'] else '無し'}",
        f"- 時刻：{datetime.datetime.now().isoformat(timespec='seconds')}",
    ] + [f"- {c} {k}：{v}" for c, k, v in rows]) + "\n"
    out = os.path.join(work, "納品の紙.md")
    open(out, "w", encoding="utf-8").write(
        "# 納品の紙（nouhin_gate.py）\n\n<!-- 事実ここから -->\n" + fact +
        f"<!-- 事実ここまで sha256:{seal(fact)} -->\n\n## 作った人のメモ（黄の理由をここに1行ずつ）\n")
    print(f"\n✅ 通った（黄 {sum(1 for x in rows if x[0]=='黄')}件）→ {out}")


if __name__ == "__main__":
    main()
