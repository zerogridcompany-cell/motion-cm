#!/usr/bin/env python3
"""人の切り抜き（写真→透過PNG）。cutout.py in.png out.png
mediapipe selfie segmentation（無料・手元）。背景が無地の暗い写真で実測きれい（2026-10-12 Lucky H1/H3/A1）。"""
import sys, cv2, numpy as np, mediapipe as mp
src, dst = sys.argv[1], sys.argv[2]
im = cv2.imread(src)
seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=0)
m = seg.process(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).segmentation_mask
m = cv2.GaussianBlur((m > 0.5).astype(np.float32), (0, 0), 2)
cv2.imwrite(dst, np.dstack([im, (np.clip(m, 0, 1) * 255).astype(np.uint8)]))
print("ok", dst, "人の面積", round(float(m.mean()), 3))
