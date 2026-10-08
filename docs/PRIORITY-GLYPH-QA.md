> 2026-10-08 JST追記: 以下は全字校正前の測定履歴です。現在の枝では重点字の中心線修正と異方ペンの修正を行っています。[修正・再確認](PRIORITY-GLYPH-CORRECTIONS.md)および[全字校正](FULL-GLYPH-PROOFREAD.md)を参照してください。再生成されたJSON/SVGは現在の配布字形に対応し、下記の旧測定数を現行値と混同しないでください。

# 優先近似字形の実測と確認

確認日: 2026-10-07 UTC。対象: `己已巳`、`未末`、`土士`、`高髙`、`吉𠮷` の11字。

**8書体×4サイズを実バイナリで測定しました。SJPBでは己已巳に10ペア・条件の完全同形が残ります。その他の画素差やTTF輪郭差を、日本語字体の正確性・見分けやすさの合格とは扱いません。字形は変更していません。**

## 対象と方法

- サイズ: 16 / 18 / 24 / 32px
- 書体: Singleline、PC98 Mincho Inspired、Gothic、Italian Reverse Contrast、Serif、Italic、Subscript、Superscript
- SJPB: 配布する32ファイルを `family.bitmap_reader.BitmapFont` で読み、実際の1bit画素とベアリング・送り幅を使用
- 静的TTF: 配布する8ファイルのcmap/輪郭を読み、Pillow 12.3.0 / FreeType 2.14.3、Linux / Python 3.12.14でモノクロ描画。ベースライン `ls`、BASIC layout
- 704字・描画条件（11字×8書体×4サイズ×2経路）、448ペア・描画条件（7ペア×8×4×2）。己已巳は3つのペアとして数える
- 余白を除いて、ペン原点・ベースラインからのインク位置と送り幅を比較。余白サイズの差だけで「別形」としない
- TTF輪郭の比較は描画命令列とメトリクスの一致検査。命令列が異なることだけで、視覚的に異なると認定しない

[機械可読結果](../build/family/reports/priority-glyph-qa.json)には40入力ファイルのSHA-256、各字の画素数/寸法、ペア別差分画素数、輪郭ハッシュ、生成した8枚のSVG見本のハッシュを記録しています。SJPBとTTFは別の描画経路なので、両者の画素一致を要求していません。

## 数値結果

欠字・空白は0、対象56組のTTF輪郭ペアはすべて異なる記録でした。静的TTFの対象224ペア・サイズ・書体では、今回のFreeTypeモノクロ画素と送り幅の完全一致は0です。

SJPBの完全同形は次の10件です。

| 字形 | サイズ | 書体 | ペア・条件数 |
| --- | --- | --- | --- |
| 已 / 巳 | 16px | Gothic、Italian、Subscript、Superscript | 4 |
| 己 / 已、己 / 巳、已 / 巳 | 18px | Subscript、Superscript | 6 |

`未末・土士・高髙・吉𠮷` は対象の両描画経路/全サイズ/全書体で完全同形ではありませんでした。最小の差分画素数はそれぞれ4、5、14、20です。わずかな画素差があるだけでも機械的には別になるので、この値を安全な最小利用サイズに読み替えないでください。

## 画像で確認した範囲

実ファイルから生成した以下の8枚について、同じ画素配置のローカルPNGを画像表示して確認しました。配布用SVGも同じ実画素を矩形パスとして記録し、外部フォントに依存しません。各図は11字×4サイズ×2経路を並べ、最近傍3倍で表示しています。外部参照フォントの字形は使っていません。これは支援付きサンプル確認で、専門家による全数校正ではありません。

[Singleline](../build/family/proofs/priority-glyphs/singleline.svg) · [PC98 Mincho](../build/family/proofs/priority-glyphs/pc98-mincho.svg) · [Gothic](../build/family/proofs/priority-glyphs/gothic.svg) · [Italian](../build/family/proofs/priority-glyphs/italian.svg) · [Serif](../build/family/proofs/priority-glyphs/serif.svg) · [Italic](../build/family/proofs/priority-glyphs/italic.svg) · [Subscript](../build/family/proofs/priority-glyphs/subscript.svg) · [Superscript](../build/family/proofs/priority-glyphs/superscript.svg)

- 己已巳: 上部の開き方・左画の接続位置が小さい描画でつぶれます。上記SJPBの同形を見本でも確認しました。TTF側も16pxでは微小な隙間への依存があり、完全一致0を可読性保証にはできません。
- 未末・土士: 横画の長さの差は残りますが、縮小書体の16/18pxではその差が少数画素になります。利用実寸での確認が必要です。
- 高髙: 上部の構造に差が残っても、16/18pxの太い/縮小SJPBでは内側の空間が狭く、髙の細部が固まりに見えます。識別可能性と字体の正しさを別途校正します。
- 吉𠮷: 上下横画の長さの差が見本に残っています。下付き/上付き書体は全体が縮むため、人名の識別用途では実アプリの出力を確認します。

32pxや非縮小書体で差が見えやすくなっても、全収録字・全アプリを認定する結果ではありません。

## 未実施と次の判断

- macOS/CoreText、Windows/DirectWrite、OSインストール/削除/共存は未実施。このLinux上のFreeType描画をネイティブOS試験とは呼ばない
- 可変TTFの全軸/中間値は今回の優先字形測定の対象外。既存の可変試験を置き換えない
- 新しい全字目視校正・日本語字体の専門校正は未実施。正式版の視覚品質ゲートを通した扱いにしない
- 既存字形を一括変更して差分を消さない。改善を行う場合は、サイズ/書体別に開口部・画線長・接続位置を設計し、旧2,584文字の保全方針との整合を確認してから別途検証する

再実行:

```sh
python family/tools/priority_glyph_qa.py
python -m pytest tests/test_priority_glyph_qa.py -q
```

スクリプトは欠字/空白/読込失敗をエラーにし、既知の同形は隠さず報告します。終了コード0は測定の完了で、同形解消や視覚品質の合格ではありません。再実行した見本を未確認のまま、この確認日の視覚所見を新しい成果物へ引き継がないでください。
