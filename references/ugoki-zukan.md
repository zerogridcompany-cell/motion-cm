# 動きの図鑑（2026-10-12・全部未承認）＝動きを「名前＋ミリ秒＋曲線」で決める

元：
- @VibeEverything「Motion Reference」583個の動きの見本サイト（x.com/VibeEverything/status/2109293698836205573・2026-10-11・634いいね）。動画は `~/research/x-posts-20261012/media/vibe_mg_library.mp4`
  - サイトの住所は取れんかった（投稿にも返信にも無い）。中身は動画のコマから読んだ
- X調べ B/C/D：`~/.claude/ad-mimawari/調査_生データ/2026-10-12_MG凝った表現/`（00_総まとめ.md・見せる_手本20本/）

🔴 なぜ要る：うちの MG は動きの曲線が1種類だけやった（spring 0回・潰れ/遅れ/揺れ戻し無し・CM2は出揃った後50%止まっとる＝A_genjo）。
任天堂っぽい「気持ちいい」は絵より**動きの物理**。

---

## 使い方（場面を作る前に）
1. 場面ごとに「気分」を1つ選ぶ：**なめらか／キビキビ／やわらか／重い／弾む**（図鑑の Feeling と同じ5つ）
2. 下の表から動きの**名前**を選び、cues.json に `motion:"Overshoot 600ms easeOutBack"` のように書く。**1本の中で最低5種類**
3. 出揃ったら止めん：止まりは30秒あたり1秒以下・0.6秒を超える止めは無し（D：everestchris6）。読ませる文字の間は「Breathing Scale」「Focus Halo」など小さく動かし続ける
4. 書き出したら `motion.txt` の止まり率で検算（A_genjo の測り方）

## 図鑑（動画のコマから読めた分・名前／種類／長さ／曲線／何が起きる）

### 跳ね・反応（Bounce & Reaction）＝任天堂っぽさの核
| 名前 | 長さ | 曲線 | 動き |
|---|---|---|---|
| Overshoot | 600ms | easeOutBack | 目標を少し行き過ぎて、短く戻る |
| Bounce Landing | 700ms | easeOutBounce | 跳ね返りが段々低く短くなって着地 |
| Spring Follow | 1800ms | spring(1,80,10) | 先頭1つ＋後ろ3つが順に行き過ぎて集まる |
| Rubber Band | 900ms | easeOutElastic | 引っぱられる方へ伸び→中立を越えて縮む→戻る |
| Recoil | 520ms | easeOutQuart | 強く前へ→小さく引き戻し→止まる |
| Double Bounce | 820ms | easeOutBounce | 大きい跳ね1回＋小さい跳ね1回で「完了」 |
| Snap Back | 560ms | easeOutElastic | 伸びた形がパチンと戻って中立を越える |
| After Shake | 720ms | easeOutElastic | 当たった後、左右の揺れが減りながら止まる |
| Impact Squash | 620ms | easeOutBack | 当たった瞬間に縦に潰れ横に広がって戻る |

### 大きさ（Scale）
Pop Scale（小→大で現れる）／Breathing Scale（ゆっくり膨らみ縮み＝待ちの間）／Elastic Scale（行き過ぎて戻る）／Axis Stretch（進む方向に伸びる）／Focus Pulse 680ms easeOutCubic（物は止まり輪だけ広がって消える）／Depth Zoom 740ms easeInOutQuint（ぼけた物が手前へ）／Soft Shrink 600ms easeInCubic（縮んで消える）

### 回転（Rotation）
Simple Turn 2200ms（両端ゆっくり180°）／Spin Stop（速く回って狙った角度にぴたっ）／Pendulum Wobble（振り子が揺れて止まる）／Card Flip 760ms easeInOutCubic（90°で表が消え裏が出る）／Tilt Reaction（触れた方へ少し傾いて戻る）／Tumble In 820ms（位置が先に着き、回転が少し遅れて着く）／Counter Rotation 1000ms（外と内が逆に回る）

### 並び（List & Grid）
Staggered List 760ms／Cascade List 820ms easeOutQuad（上から順に降りる）／Alternating List（左右から交互）／Row Expand 720ms easeOutBack／Grid Wave 900ms（左上→右下へ・遅れ＝(行+列)×55ms）／Center-out Grid 860ms easeOutBack（真ん中から輪で広がる）／Row Sweep Grid 800ms（1行ずつ）／Shuffle to Grid 980ms（散らばりから整列）

### 目を引く（Attention & Emphasis）
Nudge 520ms（ちょい横に動いて戻る）／Attention Bounce 620ms（1回ぴょん）／Badge Pop（数字の玉だけ弾む）／Focus Halo 900ms（輪が広がる・本体は止まる）／Highlight Sweep 820ms（光の帯が1回なめる）／Border Chase 1000ms（枠を光が回る）／Press Feedback 420ms（押すと97%に縮んで影が減る）／Jelly Emphasis 760ms easeOutElastic（X・Yが交互に潰れる）

### 光（Light & Glow）
Rim Glow 1000ms（縁だけ光る）／Energy Charge 1200ms easeInCubic（ためて光る）／Light Trail 900ms（先頭が一番明るい尾）／Scan Line 1100ms（横線が一定速度で降りる）／Neon Flicker（点いたり消えたりして安定）／Light Sweep 950ms（斜めの帯が通る）／Bloom Reveal 780ms（白い光から形が出る）

### 効果・切り替え（Effects & Transitions）
Blur Zoom 720ms（大きさ・ぼかし・透明度が同時に揃う）／Chromatic Split 900ms（赤と青のずれが段階で重なる）／Glitch In 650ms（最初だけ崩れる）／Pixel Dissolve 900ms（マスが別々の時刻に出て隙間なく揃う）／Particle Burst 820ms（芯が反応した直後に粒が全方向）／Ripple Reveal 950ms（触れた所から波が2重に）／Slice Reveal 840ms（横に切った板が別々に動いて揃う）／Noise Resolve 1000ms（ざらつきが消えて形が残る）

### 画面の移り（Layout & Navigation）
Shared Element 850ms（同じ色の形が位置・大きさ・角丸を変えて次の画面へ＝1つの物を持ち回る）／View Crossfade 520ms（古い1→0と新しい0→1を重ねて空白を作らん）／FLIP Reorder／Modal Morph（小さいカードが真ん中で本当の大きさに育つ）／Tab Indicator 520ms（下線が次へ伸びてから縮む）／Filter Reflow（消えた所を残りが詰める）／Page Wipe 780ms（幕が画面を覆ってから中身が替わる）

### 文字（Text）
Kinetic Emphasis／Letter Wave／Blur Resolve／Split & Assemble／Staggered Letters／Tracking Open（字間が開いて落ち着く）／Line Mask Up（行が下から覗く）／Word Swap

## X調べの数値（B 動きの細部・D 作り方）
- 速さで伸びる：動く間だけ横に最大1.8〜2.5倍＋ぼかし0→3px、止まりで約17%行き過ぎて1.0秒で落ち着く＝`spring({mass:1, stiffness:100, damping:10})`（gabriell_lab）
- ため→伸び→頂点で0.17秒止め→着地1コマで高さ−22%→0.4秒で戻る。**面積は一定**（actionplannet）
- 文字の入れ替え：ぼける2コマ→替わる→戻る2コマ（約0.13秒・6px）（jakubkrehel）
- 押した4段（約0.8秒）：枠が光る→縮んで中から育つ→115%→100%→粒が2重の輪（yui540）
- 吊り札の数字：上から下へ0.13秒でめくれ±5°揺れ・桁ごと0.2秒ずらし（yui540）
- スタンプ：1.4→1.0倍を3コマ・当たりで白く光って−3°・0.5秒で戻る（takayuP4）
- 色の帯6〜8本で0.4秒ワイプ→部品が2〜3コマで一斉に着地→光が走る（takayuP4）
- 文字の出：1文字0.9秒・0.025秒ずらし・下から16px・ぼかし12→0・曲線(0.22,1,0.36,1)／消え0.6秒(0.64,0,0.78,0)（alex_barashkov）
- 速さは3種だけ：普通33/33・ためて止まる80/80・飛び出して滑り込む100/0。動く前に一度引く（ymrun_jp）
- 仕上げは層：配置→小物→光と色→額縁→白フラッシュ（Snowwwball）／多角形マスク3〜4枚をずらして0.75〜1秒（crnacura）

## 見た目の型（C）＝場面に合わせて選ぶ
ちぎり紙コラージュ（暮らし・時間）／リソグラフ2〜3色＋版ずれ1〜2px（比較）／作字＝1字を物に（「水」「爪」）／太さが変わる数字＋色タイル（30dB・2.2L・値段）／実写に平らなキャラを貼る（雑菌）／黄黒白3色＋赤1点（フック）／すりガラスの立体（水・清潔）

## 奥行き（E 取り直し・2026-10-12）
- **横の視差**：手前・真ん中・奥を 1 : 0.5 : 0.05 の速さで流す（Kurzgesagt）。ドット絵なら6〜7層（danfessler）
- **前へ進む（Z）**：1枚絵をただ寄せると月まで大きくなって平たい（失敗）。板に分けて、拡大率＝1/(板の距離−カメラの進み)。**手前が先に外へ抜け、一番奥は大きさを変えん**（Disney マルチプレーン・WDFMuseum／timsoret）
- **形が溶けて変わる**：ボタン→こぶ→液体が全面を塗る→場面替わり（0.75秒・60fpsdesign）／丸→くびれ→カード（0.5秒・メタボール＝ぼかし＋しきい値・learnframer）／カードが島へ台形に吸い込まれ少し行き過ぎ（jmtrivedi）
- **弾む UI**：選択肢が小→大へ少し行き過ぎ・叫ぶ字は1.6倍で出て0.25秒で戻る（adamgryu）／獲得演出＝光の放射→白く大きく出て0.15秒で戻る→光の帯（takayuP4）／基礎6つ（伸び縮み・予備動作・追従・行き過ぎ・残像・緩急＝muscat_dot）
