#!/usr/bin/env python3
# コマ一覧：2秒ごとのコマを並べ、Metaリールの安全域（上14%・下20%）を赤線で引く。
# 使い方: python3 sheet.py <video.mp4> <out.jpg> [間隔秒=2]
import subprocess, sys, tempfile, os, json
from PIL import Image, ImageDraw
v, out = sys.argv[1], sys.argv[2]; step = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
d = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",v]).decode())
tmp = tempfile.mkdtemp(); ims = []
t = 1.0
while t < d - 0.1:   # 30.0秒ちょうどの動画で最後のコマを取りに行って落ちるのを防ぐ（10/12）
    p = os.path.join(tmp, f"{t:.2f}.jpg")
    subprocess.run(["ffmpeg","-y","-v","error","-ss",str(t),"-i",v,"-frames:v","1","-vf","scale=432:-1",p], check=True)
    im = Image.open(p).convert("RGB"); dr = ImageDraw.Draw(im); W, H = im.size
    if H > W:
        for y in (int(H*0.14), int(H*0.80)): dr.line([(0,y),(W,y)], fill=(220,0,0), width=1)
    dr.rectangle([0,0,70,22], fill=(0,0,0)); dr.text((4,4), f"{t:.2f}s", fill=(255,255,0))
    ims.append(im); t += step
cols = 5 if ims[0].height > ims[0].width else 3
W, H = ims[0].size; rows = (len(ims)+cols-1)//cols
sheet = Image.new("RGB", (W*cols, H*rows))
for i, im in enumerate(ims): sheet.paste(im, ((i%cols)*W, (i//cols)*H))
sheet.save(out, quality=88); print(out, len(ims), "コマ")
