# ニャスケット30秒CMの音（ドラム＋効果音を1本に）。2026-10-12。
# 網目＝src/nyasket_cm_cues.json（96BPM・12小節＝30.000秒・裏の8分を swing=0.6 に跳ねさせる）。
# NyaquaCM2 は効果音を Remotion のコマ単位で置いて最大15.8msずれた → ここでは全部サンプル単位で置く。
# 置き方：各音の「山（いちばん大きい所）」を実測して、山が拍ちょうどに来るように前へずらす。
# 出力：public/nyasket_cm/mix_raw.wav（48kHz・ステレオ・32bit float）と specs/nyasket_cm/placed.json（置いた時刻の控え）
import json, os
import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "../..")
cues = json.load(open(os.path.join(ROOT, "src/nyasket_cm_cues.json")))
SR = 48000; BPM = cues["bpm"]; BEAT = 60 / BPM; TOTAL = cues["bars"] * 4 * BEAT; SW = cues["swing"]
FPS = 30
at = lambda bar, beat=0: (bar * 4 + beat) * BEAT
assert abs(TOTAL - 30.0) < 1e-9

cache = {}
def load(n):
    if n in cache: return cache[n]
    sr, x = wavfile.read(os.path.join(ROOT, f"public/sfx_premium/{n}.wav"))
    if x.dtype == np.int16: x = x.astype(np.float32) / 32768
    elif x.dtype == np.int32: x = x.astype(np.float32) / 2147483648
    else: x = x.astype(np.float32)
    if x.ndim == 1: x = np.stack([x, x], 1)
    assert sr == SR, (n, sr)
    env = np.abs(x).max(1)
    k = int(0.004 * SR); sm = np.convolve(env, np.ones(k) / k, "same")
    pk = int(np.argmax(sm))
    cache[n] = (x, pk); return cache[n]

out = np.zeros((int(TOTAL * SR) + SR * 3, 2), np.float32)
placed = []
def put(n, t, g, why="", align_peak=True, maxdur=None):
    x, pk = load(n)
    if maxdur: x = x[: int(maxdur * SR)]
    st = int(round(t * SR)) - (pk if align_peak else 0)
    a = max(0, -st); st = max(0, st)
    seg = x[a:]; m = min(len(seg), len(out) - st)
    out[st:st + m] += seg[:m] * g
    placed.append({"f": n, "t": round(t, 5), "peak_at": round((st + pk - a) / SR if align_peak else t, 5), "why": why})

# ---- ドラム（ブームバップ・裏が跳ねる）----
K, C, H = "selfsynth_drum_kick_02", "selfsynth_drum_snare_03", "selfsynth_drum_hat_02"
for bar in range(cues["bars"]):
    full = 1 <= bar <= 9
    for b in range(4):
        if full:
            if b == 0: put(K, at(bar, 0), 0.62, "kick 1拍目")
            if b == 2 and not (bar == 9): put(K, at(bar, 2 + SW), 0.50, "kick 3拍目の裏（跳ね）")
            if b in (1, 3) and not (bar == 9 and b == 3): put(C, at(bar, b), 0.34, "snare 2・4拍")
            put(H, at(bar, b), 0.10, "hat 表"); put(H, at(bar, b + SW), 0.065, "hat 裏（跳ね）")
    if bar == 3: put(K, at(3, 2), 0.50, "kick 0 の着地")
    if bar == 9:
        for i, g in enumerate((0.16, 0.2, 0.25, 0.32)): put(C, at(9, 3 + i * 0.25), g, "snare フィル（締めへ）")
    if bar == 10:
        put(K, at(10, 0), 0.62, "kick 締めの頭")
        for b in range(4): put(H, at(10, b + SW), 0.05, "hat 裏だけ")
    if bar == 11: put(K, at(11, 0), 0.62, "kick ボタンと同時・最後")

# ---- 効果音 ----
for bar, beat, f, vol, why in cues["hits"]:
    put(f, at(bar, beat), vol, why)

# ---- サイズの数字の刻み（TSX の sizeVal と同じ式・値が変わるコマに tick・1秒12発まで）----
ROLL = 0.3
def size_val(s):
    prev = 0
    for bar, beat, _, v in cues["sizes"]:
        t = at(bar, beat)
        if s < t - ROLL: return prev
        if s < t: return int(prev + (v - prev) * (s - (t - ROLL)) / ROLL)
        prev = v
    return prev
last_v, last_t = None, -9
for fr in range(int(at(6, 0) * FPS), int(at(7, 0) * FPS)):
    s = fr / FPS; v = size_val(s)
    if last_v is not None and v != last_v and s - last_t >= 1 / 12 - 1e-6:
        put("kenney_tick_01", s, 0.16, "数字の刻み（上がるだけ）"); last_t = s
    last_v = v

out = out[: int(TOTAL * SR)]
# 最後の 0.4 秒で静かに消す（ブツ切りを防ぐ）
n = int(0.4 * SR); out[-n:] *= np.linspace(1, 0, n)[:, None]
wavfile.write(os.path.join(ROOT, "public/nyasket_cm/mix_raw.wav"), SR, out.astype(np.float32))
json.dump(placed, open(os.path.join(HERE, "placed.json"), "w"), ensure_ascii=False, indent=0)
err = max(abs(p["peak_at"] - p["t"]) for p in placed)
print("placed", len(placed), "peak", float(np.abs(out).max()), "max peak-vs-grid error ms", round(err * 1000, 3))
