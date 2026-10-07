# TTFのインストール・更新・削除

対象: V2配布準備版 `2.0.0-rc.1`。以下は導入手順で、実機試験の合格記録ではありません。macOS/CoreText、Windows/DirectWrite、Linuxのフォント管理、アプリごとの表示は別途確認が必要です。

## Pythonなしで使う

1. 通常のアプリで使うなら `SinglelineJPLab-2.0.0-rc.1-static.zip` を選びます。可変軸を操作できるアプリでは `…-variable.zip` も選べます。
2. ZIPを展開します。ZIP内のファイルを直接開くのではなく、展開先の `singleline-jp-font/` を開き、静的版は `build/family/static/`、可変版は `build/family/variable/` 内の `.ttf` を使います。リポジトリでも同じ相対パスです。
3. 下のOS別手順で必要な書体だけをインストールし、使うアプリを開き直します。
4. フォントメニューの `Singleline JP Lab …` を選び、実際の利用サイズで確認します。テスト文: `己已巳 未末 土士 高髙 吉𠮷 日本語 ABC 123`。

フォント利用・OSインストール・同梱HTML見本の閲覧に、Python、NumPy、Pillow、OpenCVは不要です。Pythonと依存パッケージが必要なのは、再生成、検証スクリプト、Python製ビットマップ描画器を使う場合です。PNG/JSON/SJPBやSVG/SVGZはOSにインストールするフォントではありません。

## macOS

- Finderで展開済みTTFをダブルクリックし、Font Bookでインストールします。Font Bookへファイルをドラッグして追加する方法もあります。
- Font Bookの検証結果と重複警告を確認します。警告・失敗が出た場合は、そのまま合格とせず詳細を記録します。
- 削除する場合はFont Bookで対象の `Singleline JP Lab …` を選び、削除します。比較のため一時的に使わない場合は、無効化して後で戻せます。OS付属フォントは操作しないでください。

操作名はOSの版で変わります。[Apple: インストール・検証](https://support.apple.com/guide/font-book/install-and-validate-fonts-fntbk1000/mac)、[削除・無効化](https://support.apple.com/guide/font-book/remove-deactivate-or-activate-fonts-fntb2bcb512d/mac)を参照してください。

## Windows

- 展開済みTTFを右クリックし、「インストール」を選びます。通常は自分のユーザー向けの導入で足ります。全ユーザー向けの導入は必要な場合だけ選びます。
- 確認・削除は「設定 → 個人用設定 → フォント」で対象の `Singleline JP Lab …` を探し、アンインストールします。
- 一つのアプリで表示されないときは別のアプリでも確認します。独自フォントや可変軸への対応はアプリによって異なります。

[Microsoft: Windowsでのフォント管理](https://support.microsoft.com/en-us/windows/experience/personalization/manage-fonts-in-windows)に導入・削除手順があります。

## Linux（Fontconfigを使う環境）

デスクトップ環境のフォント表示アプリでTTFを開いて、ユーザー向けにインストールできます。コマンドを使う場合は、ユーザーのフォントディレクトリへ必要なTTFだけを置きます。展開先の `singleline-jp-font/` をカレントディレクトリにした、静的版の一般的な構成例です。

```sh
font_dir="${XDG_DATA_HOME:-$HOME/.local/share}/fonts/SinglelineJPLab-2.0.0-rc.1"
mkdir -p "$font_dir"
cp build/family/static/*.ttf "$font_dir/"
fc-cache -f "$font_dir"
fc-list | grep 'Singleline JP Lab'
```

可変版ならコピー元を `build/family/variable/*.ttf` に置き換えます。

削除時は、自分で作った上記ディレクトリ内の対象TTFだけをファイルマネージャーで削除して `fc-cache -f` を実行し、アプリを開き直します。別版やシステムフォントをまとめて削除しないでください。読み込みディレクトリはディストリビューションやアプリの構成によります。[Fontconfigの設定資料](https://fontconfig.pages.freedesktop.org/fontconfig/fontconfig-user.html)と、その環境の設定を確認してください。

## 名前・旧版との共存

| 資産 | フォントメニューの名前例 | 内部版 |
| --- | --- | --- |
| 従来のピクセルTTF | Singleline JP Full 24、Singleline JP ASCII 18 | 1.000 |
| 新しい静的TTF | Singleline JP Lab Gothic、Singleline JP Lab Serif | 0.201 |
| 新しい可変TTF | Singleline JP Lab Gothic Variable、Singleline JP Lab Serif Variable | 0.201 |

新旧・静的/可変はフォント名とPostScript名を区別しています。新旧を選び分ける設計ですが、実際の同時導入はOS/アプリでの確認が必要です。従来版2,584文字を使う文書を自動的にLabへ切り替えないでください。

以前のLab 0.201と今回のLabは同じ内部名を使います。ファイル名だけ変えても別フォントにはなりません。既存Labを更新するときは使っているアプリを閉じ、元ファイルを保存した上でFont BookやWindowsのフォント設定などから対象Labだけを無効化/削除し、今回のTTFを導入します。旧Labと新Labのどちらが選択されるかを版番号だけに任せないでください。

V2は配布構成の世代名です。Labの0.201と従来版の1.000は別系統なので、数字の大小で新旧を判断しません。正確なバイナリは各ZIPの `PACKAGE-SHA256.json` で確認できます。

## 可変フォント・小サイズの注意

可変版はGothicとSerifだけです。対応アプリで `wght` 200–700、`slnt` −12–0を操作できます。アプリが軸を公開しない場合は、静的版を使ってください。表示ができたことだけでは全軸・全字形の合格にはなりません。

16/18pxの一部ビットマップでは `己已巳` の区別が失われます。TTFとSJPBは異なる描画経路です。今回のFreeType結果を、macOS/CoreTextやWindows/DirectWriteの結果として扱うことはできません。[優先字形QA](PRIORITY-GLYPH-QA.md)を確認し、人名・重要な識別文字を使う場合は実際の出力を校正してください。
