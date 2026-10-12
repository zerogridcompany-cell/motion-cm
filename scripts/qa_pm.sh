#!/bin/bash
# 写真×モーションCMの検品（書き出した後に毎回）。qa_pm.sh <CM.tsx> <完成.mp4> <混ぜた音.wav>
# 全部 OK でなければ Eugene に見せん。
T=$1; V=$2; M=$3; NG=0
a=$(grep -c "<Audio" "$T"); [ "$a" = 1 ] && echo "OK 音は1本（<Audio>=1）" || { echo "NG <Audio> が $a 本＝声が二重になる（10/12 実測）"; NG=1; }
c=$(grep -c "<Telop" "$T"); [ "$c" -le 1 ] && echo "OK 字幕の重ね書きなし" || { echo "NG <Telop> が $c 本"; NG=1; }
L=$(ffmpeg -hide_banner -i "$V" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
python3 -c "import sys; sys.exit(0 if abs($L+16)<=0.6 else 1)" && echo "OK 音量 $L LUFS" || { echo "NG 音量 $L LUFS（-16 に）"; NG=1; }
B=$(ffmpeg -hide_banner -i "$V" -vf "blackdetect=d=0.1:pix_th=0.06" -an -f null - 2>&1 | grep -c black_start)
[ "$B" = 0 ] && echo "OK 真っ黒なつなぎ 0か所" || { echo "NG 真っ黒が0.1秒以上 $B か所（場面の入りを whip/up＝透明の地に）"; NG=1; }
ffmpeg -hide_banner -loglevel error -y -i "$V" -ac 1 -ar 16000 /tmp/qa_r.wav; ffmpeg -hide_banner -loglevel error -y -i "$M" -ac 1 -ar 16000 /tmp/qa_m.wav
R=$(python3 -c "
from scipy.io import wavfile;from scipy.signal import fftconvolve;import numpy as np
_,r=wavfile.read('/tmp/qa_r.wav');_,m=wavfile.read('/tmp/qa_m.wav');r=r.astype(np.float64);m=m.astype(np.float64);n=min(len(r),len(m));r=r[:n];m=m[:n]
c=fftconvolve(r,m[::-1]);lag=int(np.argmax(c))-(n-1);a=r[max(0,lag):n+min(0,lag)];b=m[max(0,-lag):n-max(0,lag)];g=np.sum(a*b)/np.sum(b*b);res=a-g*b
print(round(10*np.log10(np.sum(res*res)/np.sum(a*a)),1))")
python3 -c "import sys; sys.exit(0 if $R < -12 else 1)" && echo "OK 動画の音＝混ぜた音だけ（残り $R dB）" || { echo "NG 動画の音に別の音が混ざっとる（残り $R dB）"; NG=1; }
S=${V%.mp4}_コマ一覧.jpg; ffmpeg -hide_banner -loglevel error -y -i "$V" -vf "fps=2,scale=180:320,tile=12x8" -frames:v 1 "/tmp/qa_sheet.jpg" && echo "コマ一覧＝/tmp/qa_sheet.jpg（0.5秒ごと）→ 別の係の審査に渡す"
[ $NG = 0 ] && echo "== 全部OK ==" || echo "== NG あり：直してから見せる =="
exit $NG
