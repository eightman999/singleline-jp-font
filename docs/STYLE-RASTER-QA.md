# 全書体・実出力ピクセル再チェック

確認日: 2026-10-06 UTC

## 結論

**8書体 × 16 / 18 / 24 / 32 px の全32ストライクを、書き出された SJPB の実ピクセルで再確認した。全収録グリフを1字ずつ目視校正したという意味ではない。公開品質の日本語書体としては引き続き実験版。**

今回の目視対象は各ストライク174字、重複を除く5,568字・書体・サイズの組み合わせ。全書体に共通する試験サンプルとして、基本漢字、近似字形、密な漢字、仮名、英字、数式、囲み文字・白抜き数字、上付き・下付き数字、罫線、オリジナル絵文字を確認した。機械監査で見つかった一部の衝突も追加で目視した。

32 pxでは細部がかなり改善する。一方、16/18 pxの画線の密集と字形衝突は明確で、32 pxの縮小書体にも字形衝突が残る。画線・空白・異体字の区別を用途ごとに確認する必要がある。

機械可読のサンプル一覧、実ファイルのSHA-256、個々の寸法とピクセル数、比較結果は [style-raster-qa.json](../build/family/reports/style-raster-qa.json) に保存した。

## 確認方法と範囲

- SJPB: `family.bitmap_reader.BitmapFont` で実ファイルを読み、`bitmap` で実データを取り出し、`mask` で書き出し済みの水平・垂直ベアリングを反映。再生成した中心線や別のTTF描画で代用していない
- 対象書体: Singleline、PC98 Mincho Inspired、Gothic、Italian Reverse Contrast、Serif、Italic、Subscript、Superscript
- 対象サイズ: 16 / 18 / 24 / 32 px。48枚のSJPB見本を目視
- 静的TTF: 実際の8ファイルから基本36字ずつを48 pxで描画し、3枚の比較見本を目視。修正された2つのドットは16 / 32 / 48 pxの追加3枚で目視
- 可変TTF: Gothic / Serifの両方で、`wght=200/700` と `slnt=0/-12` の4端点を16 / 32 / 64 pxで描画。各インスタンスの基本17字を3枚の比較見本で目視。修正された2つのドットも同じ端点・サイズの追加3枚で目視
- TTFの描画はPillow/FreeTypeのネイティブなモノクロモード。これはSJPBストライクとは別の描画経路であり、両者のピクセル一致を要求する試験ではない
- 配布する60枚のPNGはすべて1-bit、ピクセル値は0/255のみ。拡大には最近傍を使用
- 配布画像はプロジェクト独自のグリフとASCIIラベルのみ。外部参照フォントのグリフ画像は含めていない

SJPBの174字サンプルでは、全32ストライクを通して予期しない空白グリフ0、実ビットマップ枠へのインク接触0。空白文字 U+0020 / U+00A0 / U+3000 は全32ストライクで空白として保持されていた。これはサンプルの結果であり、全グリフの欠け検査は別の [full-tests.json](../build/family/reports/full-tests.json) を参照。

## 未解決の所見

### SQA-001: 異なる字形が同一の小サイズビットマップになる

重要度: 高。ピクセルと送り幅の一致を確認した具体例:

- 已 U+5DF2 / 巳 U+5DF3: 16 pxのGothic、Italian、Subscript、Superscriptで同一
- 己 U+5DF1 / 已 U+5DF2 / 巳 U+5DF3: 18 pxのSubscript、Superscriptで3字とも同一
- 煮 U+716E / 煮 U+FA48: 32 pxでもSubscript、Superscriptで同一。小さいサイズにも衝突がある
- 欄 U+6B04 / 欄 U+F91D: 16 pxのSinglelineで同一

比較では空白の余白を除き、ベアリングに基づくベースラインと送り幅をそろえた。上記は目視サンプル中の例で、全漢字の機械比較にはさらに別の衝突がある。互換漢字の扱いを含め、コードポイントが別であることと表示形が別に保たれることは分けて評価する。

対処: 各サイズ・書体に合わせた画線位置と開口部の光学調整を行うか、用途別の最小サイズを明記する。収録率の表記変更だけで解決扱いにしない。

### SQA-002: 密な漢字の内部空間が閉じる

重要度: 高。例: 鬮、籤、爨、癧、藶、麤、欟、纖、鑯、櫜、藁。

16/18 pxでは、太さのある書体、とくにSubscript / Superscriptで画線が黒い塊に合流する。32 pxでもItalianの爨・麤・櫜や、太さのある鬮などには細部の密集が残る。Singleline 32 pxは比較的構造が見やすいが、それ自体は日本語字体の正確性の認定ではない。

対処: 部品間隔・画線幅・サイズ別の形状を個別に調整する。過去に修正された高解像度の構造が元に戻ったことを示す所見ではなく、実際の小サイズで残る可読性の問題。

### SQA-003: 囲み数字と二重に縮小された数字が窮屈になる

重要度: 中。例: ⑩ U+2469、⑳ U+2473、❿ U+277F、⓴ U+24F4、および上付き・下付きの0/6/8/9。

16/18 pxの縮小書体では、2桁の囲み数字の内部が密集する。すでに小さいUnicode上付き・下付き数字へ縮小書体を適用すると、さらに縮小され、16 pxでは数ピクセルの高さになる例がある。確認した白抜き数字には切り抜きのピクセルが残っており、全面的な黒塗りへの置き換わりではないが、判読性は十分ではない。

対処: 小サイズ用の数字と内部空間を別途調整する。縮小書体を密な本文や、すでに縮小されたUnicode文字へ使う場合は実寸で校正する。

### SQA-004: 小さな絵文字の意味を担う細部がつぶれる

重要度: 中。例: 雪 U+E003、病院 U+E017、郵便局 U+E019、鍵 U+E025、カート U+E02A。

16/18 pxでは、鍵の歯、建物上部の標識、雪の枝、カートの細部が合流する。縮小書体で特に顕著。32 pxでは多くが改善するが、太さのある書体の建物標識などはまだ窮屈になる。

対処: 小サイズ用の簡略化を行い、意味を担う部分を意図的に残す。PUAと対応するUnicode別名の双方で確認する。

### SQA-005: 継承済みの3組の同形字

重要度: 高、既知・未解決。剝/剥、塡/填、頬/頰は全32ストライクで同一ピクセル・同一送り幅。これはサイズ追加以前の中心線形状に由来する。

対処: 制約を引き続き明記する。表示上の区別が必要なら、別々の独自字形を設計して改めて確認する。

## 追加修正の限定再確認: SQA-006（修正済み）

全件機械監査により、初回の172字サンプルに含まれていなかった中点 · U+00B7 と上ドット ˙ U+02D9 が、16 pxのSubscript / Superscriptで空白になる不具合が見つかった。ビルド担当がこの2字の独自ドット線分だけを0.7から1.6グリッド単位へ広げた。汎用の空白グリフ代替処理は追加していない。

- 修正後の2字を全32ストライク、64ケースで実ピクセル目視。すべて非空白で、上下の位置も区別できる
- 問題があった16 pxの両縮小書体では、中点が3ピクセル、上ドットが2ピクセルのインクを保持
- 再生成された静的8書体と可変2書体はすべてVersion 0.201。追加TTF見本96ケースでも2字とも非空白
- 初回に確認した5,504組のSJPBピクセルハッシュ・寸法・送り幅・ベアリングは全件一致。初回50枚のSJPB / TTF見本画像も再描画後にバイト単位で一致
- 変更のない字を再びすべて目視したとは扱わず、上記の同一性検証と、2字分の追加見本10枚の目視を記録した

最終レポートのサンプル数は174字、5,568字・書体・サイズの組み合わせ。初回サンプルで空白がなかったことは、サンプル外の欠けを否定しなかった点にも注意する。

## 最終メタデータの整合確認

2026-10-06 17:39:49 UTCのビルド担当による最終更新で、全10 TTFの`head.fontRevision`をname ID 5のVersion 0.201とそろえた。保存時は`recalcTimestamp=False`。字形・ラスタライズ・可変軸の変更は報告されていない。

独立確認では、全10ファイルのname ID 5と`head.fontRevision`が一致することを確認した。`head.fontRevision`の実格納値は固定小数点精度により0.2010040283203125となり、0.201と整合する。10ファイルのSHA-256を最終値へ更新し、既存のTTF見本12枚を機械的に再描画して全画像のハッシュ一致を確認した。新たな目視確認を行ったとは記録していない。

## TTFと可変端点の所見

- 静的8書体を実ファイルから読み込んで描画できた。Italicのa/g/fには、単なる機械的な斜体化とは異なる形が見える
- 可変2書体の4端点では太さと傾斜の変化を目視できた。斜体側の端点はObliqueであり、静的Italicの筆記的な代替字形とは別
- 16 pxの太い端点や32/64 pxの密な漢字でも、内部空間の合流は残る。端点が描画できることは、全軸位置・全プラットフォームの品質認定ではない
- フォントファイルの構造・補間・全グリフの機械テストは別の全件監査を参照

## サンプル一覧と見本

各SJPB見本の行は、上からSingleline、PC98 Mincho Inspired、Gothic、Italian、Serif、Italic、Subscript、Superscript。サンプルごとにコードポイントを記載した。PUAの名称は [SYMBOLS_AND_PICTOGRAMS.md](../family/SYMBOLS_AND_PICTOGRAMS.md) を参照。

### simple

一二三人口日月田山水木永日本語

[16 px](../build/family/specimen/new-style-proof-simple-16.png) / [18 px](../build/family/specimen/new-style-proof-simple-18.png) / [24 px](../build/family/specimen/new-style-proof-simple-24.png) / [32 px](../build/family/specimen/new-style-proof-simple-32.png)

### close

未末土士己已巳高髙吉𠮷斉斎齊齋葛剝剥塡填頬頰

[16 px](../build/family/specimen/new-style-proof-close-16.png) / [18 px](../build/family/specimen/new-style-proof-close-18.png) / [24 px](../build/family/specimen/new-style-proof-close-24.png) / [32 px](../build/family/specimen/new-style-proof-close-32.png)

### dense

戾棙淚錑魃魎㒼兩輛鬮籤爨癧藶麤欟纖鑯櫜藁

[16 px](../build/family/specimen/new-style-proof-dense-16.png) / [18 px](../build/family/specimen/new-style-proof-dense-18.png) / [24 px](../build/family/specimen/new-style-proof-dense-24.png) / [32 px](../build/family/specimen/new-style-proof-dense-32.png)

### collision-followup

已巳煮煮欄欄

[16 px](../build/family/specimen/new-style-proof-collision-followup-16.png) / [18 px](../build/family/specimen/new-style-proof-collision-followup-18.png) / [24 px](../build/family/specimen/new-style-proof-collision-followup-24.png) / [32 px](../build/family/specimen/new-style-proof-collision-followup-32.png)

### spacing-dots

·˙

[16 px](../build/family/specimen/new-style-proof-spacing-dots-16.png) / [18 px](../build/family/specimen/new-style-proof-spacing-dots-18.png) / [24 px](../build/family/specimen/new-style-proof-spacing-dots-24.png) / [32 px](../build/family/specimen/new-style-proof-spacing-dots-32.png)

### bounds

─━│┃┌┏└┗┘┛┼╋

[16 px](../build/family/specimen/new-style-proof-bounds-16.png) / [18 px](../build/family/specimen/new-style-proof-bounds-18.png) / [24 px](../build/family/specimen/new-style-proof-bounds-24.png) / [32 px](../build/family/specimen/new-style-proof-bounds-32.png)

### kana

あいうえおかがぱアカガパッャー・

[16 px](../build/family/specimen/new-style-proof-kana-16.png) / [18 px](../build/family/specimen/new-style-proof-kana-18.png) / [24 px](../build/family/specimen/new-style-proof-kana-24.png) / [32 px](../build/family/specimen/new-style-proof-kana-32.png)

### latin

ABEIOQSXafgijpqy019

[16 px](../build/family/specimen/new-style-proof-latin-16.png) / [18 px](../build/family/specimen/new-style-proof-latin-18.png) / [24 px](../build/family/specimen/new-style-proof-latin-24.png) / [32 px](../build/family/specimen/new-style-proof-latin-32.png)

### math

∑∫∮√∞≈≠≤≥±×÷∂∇∈∉⊂⊄

[16 px](../build/family/specimen/new-style-proof-math-16.png) / [18 px](../build/family/specimen/new-style-proof-math-18.png) / [24 px](../build/family/specimen/new-style-proof-math-24.png) / [32 px](../build/family/specimen/new-style-proof-math-32.png)

### counter

①⑨⑩⑳❶❾❿⓫⓴ⓐⓩ

[16 px](../build/family/specimen/new-style-proof-counter-16.png) / [18 px](../build/family/specimen/new-style-proof-counter-18.png) / [24 px](../build/family/specimen/new-style-proof-counter-24.png) / [32 px](../build/family/specimen/new-style-proof-counter-32.png)

### small-numbers

⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉

[16 px](../build/family/specimen/new-style-proof-small-numbers-16.png) / [18 px](../build/family/specimen/new-style-proof-small-numbers-18.png) / [24 px](../build/family/specimen/new-style-proof-small-numbers-24.png) / [32 px](../build/family/specimen/new-style-proof-small-numbers-32.png)

### pictograms

U+E000, U+E003, U+E007, U+E00C, U+E010, U+E012, U+E014, U+E017, U+E019, U+E01B, U+E025, U+E026, U+E027, U+E02A, U+E02D, U+E03F

[16 px](../build/family/specimen/new-style-proof-pictograms-16.png) / [18 px](../build/family/specimen/new-style-proof-pictograms-18.png) / [24 px](../build/family/specimen/new-style-proof-pictograms-24.png) / [32 px](../build/family/specimen/new-style-proof-pictograms-32.png)

### 静的TTF・可変TTF

- 静的TTF 48 px: [漢字](../build/family/specimen/new-style-proof-static-kanji-48.png)、[英字・記号](../build/family/specimen/new-style-proof-static-symbols-48.png)、[小数字・絵文字](../build/family/specimen/new-style-proof-static-details-48.png)
- 可変端点: [16 px](../build/family/specimen/new-style-proof-variable-endpoints-16.png)、[32 px](../build/family/specimen/new-style-proof-variable-endpoints-32.png)、[64 px](../build/family/specimen/new-style-proof-variable-endpoints-64.png)

### 修正ドットの追加TTF見本

- 静的8書体: [16 px](../build/family/specimen/new-style-proof-static-spacing-dots-16.png)、[32 px](../build/family/specimen/new-style-proof-static-spacing-dots-32.png)、[48 px](../build/family/specimen/new-style-proof-static-spacing-dots-48.png)
- 可変2書体の4端点: [16 px](../build/family/specimen/new-style-proof-variable-spacing-dots-16.png)、[32 px](../build/family/specimen/new-style-proof-variable-spacing-dots-32.png)、[64 px](../build/family/specimen/new-style-proof-variable-spacing-dots-64.png)

## 引き続き残る確認範囲

過去の [VISUAL-QA.md](VISUAL-QA.md) では190字を目視している。今回の174字と重複があるため、単純に合計して確認字数としない。

拡張漢字は依然として組版・設計上の草案。既存の由来レポートには地域的字体78、重ね合わせ239、囲み1177、深い合成434の要確認フラグがある。フラグの件数は今回の目視合格数ではなく、フラグがある字が必ず誤りであるという意味でもない。

全収録字の日本語字体校正、各OS・アプリでのシェーピング検証、読者による認識率試験は未実施。このレビューでは、字形ソース、ジェネレーター、既存の正本資産、フォントファイルには変更を加えていない。
