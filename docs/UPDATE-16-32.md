# 16/32px追加と全書体再検査

2026-10-06の追加依頼に対応する試作更新です。「16,32ビット」は16/32pxの文字サイズとして実装し、各画素は従来どおり1bitの白黒データを維持しています。16/18/24/32px × 8書体、計32ストライクを生成します。

## 修正

- Version0.201:16pxのSubscript/Superscriptで消えていた中黒「·」と上点「˙」について、独自の点の線分を0.7→1.6グリッド単位に拡大。任意の欠字を点に置き換える処理ではありません

- Subscriptの罫線文字23字が従来の固定1.25emフレームより下へ伸び、下端を切っていた問題を修正
- 字ごとの上下限とbearing_yを保存し、フォント全体の共通ベースラインで合成。SJPB v1のバイナリ構造は変更なし
- すべての書体・サイズのJIS漢字10,050字について、同じ原点・ベースラインに揃えて画素衝突を再計測。余白や切り出しサイズの違いで衝突を隠さない
- すべての静的TTF、符号化済み文字・シーケンス、可変軸の端点、PNG/SJPBストライクを再検査

## 再生成

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-family.txt
.venv/bin/python build_family.py
.venv/bin/python -m family.specimen
.venv/bin/python family/tools/audit_bitmap_collisions.py
.venv/bin/python render_bitmap_proof.py
.venv/bin/python verify_family.py --report build/family/reports/full-tests.json
.venv/bin/python -m unittest family.tests.test_kanji family.tests.test_jis_symbols -v
.venv/bin/python verify.py
.venv/bin/python verify_ttf.py
```

## 検査範囲

数値検査は全収録字・全書体を対象にします。全12,000字以上を1字ずつ人が目視校正したという意味ではありません。抽出字の実画素による再確認は`docs/STYLE-RASTER-QA.md`、機械検査の結果は`build/family/reports/full-tests.json`、全ストライクの衝突一覧は`build/family/reports/bitmap-collisions.json`に記録します。

特に16px、Subscript/Superscriptの縮小字、密度の高い漢字では線・空白の消失や字形衝突が残り得ます。符号化収録の完了と、日本語字形・可読性の完成は区別します。従来の50個の固定資産は変更していません。

## GitHub

公開対象は`eightman999/singleline-jp-font`の専用ブランチ`codex/font-family-16-32px`です。作業開始時にremote mainが`c1f5774a51d38fe33670c067e19314f6fc706370`であることを確認しました。mainへのマージ・デプロイ・PR作成はこの更新に含めません。公開結果は実際のリモートコミットを照合して報告します。`build-summary.json`の`source_commit`は元の取得元コミットを指し、改修後の実際の生成ソースは同ファイルの`source_hashes`で固定しています。

HTML見本は生成しますが、ownVMのブラウザー起動制限により、検索や可変軸UIのブラウザー操作確認は未実施です。FreeType/HarfBuzzとフォント・バイナリの検査とは別の制限です。
