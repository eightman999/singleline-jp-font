# Singleline JP Font

小さな画面向けの独自単線ビットマップ文字セット。18px / 24px、計2,584文字。常用漢字2,136字、ひらがな・カタカナ、ASCII、全角英数字、記号を収録します。★●▲▼■は塗りつぶしです。

[全収録文字](assets/fonts/CHARACTERS.md) · [検索可能なカタログ](assets/fonts/catalog.html) · [出典とライセンス](NOTICE.md)
カタログはダウンロードしてブラウザで開いてください。[インストール用TTF](fonts/)も同梱します。複雑な字の18px表示や実機LEDの可読性は保証しません。

## すぐ使う

PNG/JSONだけで利用可能です。`assets/fonts/custom-jp-24.*` と `custom-ascii-24.*` を組で使います。JSONの `glyphs` は文字をキーとし、`x/y/width/height` がPNG内の矩形、`advance` が送り幅です。白が点灯、黒が背景です。18px版も同じ形式です。

```sh
git clone https://github.com/eightman999/singleline-jp-font.git
cd singleline-jp-font
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python render.py '日本語 ABC 123 ％ ★' --scale 4 -o output.png
```

```python
from dot_font import DotFont
font = DotFont()
print(font.missing('寿帝差弔彙挿'))  # 未収録文字の一覧
pixels = font.mask('日本語 ABC')   # NumPy bool配列
```

実行時はNumPyとPillowのみ。OpenCVや字形ソースの読み込みは不要です。改行は行ごとに処理してください。欠字は自動置換せず例外になります。

## 再生成

```sh
.venv/bin/pip install -r requirements-build.txt
.venv/bin/python build_custom_ascii.py
.venv/bin/python build_custom_japanese.py
.venv/bin/python build_font_catalog.py
.venv/bin/python verify.py
```

線分は24単位の座標から1px幅・アンチエイリアスなしで生成します。`glyphs/kanji.py`・`hiragana.py`・`katakana.py`・`ascii.py`が字種別の正本、`symbols.py`が記号です。同一の線分は`paths.py`で共有します。旧部品合成器と重複した字形・後勝ちの修正定義を除去し、確定済みの全座標とPNGを維持しています。`custom_*_strokes.py`は既存利用者向けの薄い入口です。生成物のJSONに出典とハッシュを記録します。

コード・独自線分は元プロジェクトのAGPL v3、外部構成データと日本語生成物の扱いは[NOTICE.md](NOTICE.md)を参照してください。ゲーム、通信、Pi制御、旧フォント資産は含みません。

## インストール用 TrueType

| 版 | 18px設計 | 24px設計 | 収録 |
|---|---|---|---|
| ASCII | [TTF](fonts/SinglelineJPASCII18-Regular.ttf) | [TTF](fonts/SinglelineJPASCII24-Regular.ttf) | ASCII 95字＋° |
| 全字 | [TTF](fonts/SinglelineJPFull18-Regular.ttf) | [TTF](fonts/SinglelineJPFull24-Regular.ttf) | 2,584字 |

ダウンロードしたTTFをOSのフォント管理機能でインストールできます。フォント名は `Singleline JP Full 24` などです。いずれもRegular。既存の点灯画素を閉じた輪郭にしたピクセル形状のフォントで、筆記用の単線パスや滑らかなアウトラインへの変換ではありません。設計サイズの整数倍を推奨します。ASCII版に日本語は含まれません。

```sh
.venv/bin/python build_ttf.py
.venv/bin/python verify_ttf.py
```

全字のcmap、送り幅、FreeTypeによる設計サイズでの表示とPNGとの一致を検証します。OSへのインストールや個別アプリの表示は別途確認してください。新旧構成の移行でも全字の座標と4枚のPNGが完全一致することを検証済みです。

TTF生成は[fontTools FontBuilder](https://github.com/fonttools/fonttools/blob/main/Lib/fontTools/fontBuilder.py)を使用します。TTFにも既存の出典・ライセンス条件を引き継ぎます。

![TTF preview](fonts/preview.png)
