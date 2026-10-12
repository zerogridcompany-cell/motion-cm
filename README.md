# motion-cm（モーショングラフィックスCM）
Claude Code のスキル一式。どの商品でも、30秒前後のモーショングラフィックスCM（横16:9・縦9:16・色違い・ブランド別）を作る。入口＝SKILL.md。

## 型は2つ
- 型1＝拍の網目（音楽主導）：BPM×小節で尺ちょうどの網目を作り、場面・文字・効果音を全部同じ式 at(小節,拍) から出す（実例 NyaquaCM2 / LuckyCM / NyasketCM）
- 型2＝声の区切りで割る（網目なし・ナレーション主導）：場面＝1文・着地＝言葉の頭を Forced Alignment で取る（実例 NyaquaCM4N v8・審査 8.5・止まり2%）
- ほかに写真×モーション型（references/photo-motion.md）

## 中身
- scripts/motion_check.py＝止まり率・最長の止まり・hardcut・動きの種類数を測る／sheet.py＝コマ一覧／mix_template.py＝音を1本に混ぜる（型1）／qa_pm.sh・cutout.py＝写真×モーションの検品と切り抜き
- references/ugoki-zukan.md＝動きの図鑑／photo-motion.md／sfx_kotoba.md／cues_example.json
- 字幕は eizo-iitoko の telop_catalog.md と /jimaku-sync に寄せる（このスキルには持たん）

出典は全部未承認（SKILL.md・references の各所に記載）。
🔴 効果音・音楽・動画・大きな画像は再配布NG／重いため入れてへん（目録と置き場所の記載だけ）。実例の tsx・作業場はこのリポの外（~/scratcher-basket/vsl/remotion/）。
