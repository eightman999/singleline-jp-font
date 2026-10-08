# 象系列の欠画追跡

対象は U+8C61 象、U+6A61 橡、U+6F52 潒、U+8C6B 豫の4字。
像は deep1 の修正済み対象であり、このmoduleからは変更しない。

Unicode18 の公式 [CJK chart](https://www.unicode.org/Public/18.0.0/charts/PDF/U4E00.pdf) の
J0-3E5D、J0-464B、J14-6F33、J0-502Eを実画像で照合した。
現字形・Noto Sans CJK JP・色分けした全ソース線分も500pxで確認した。
全4字の象部は同じ9 pathsを基にしており、必要な左払い3本のうち1本が欠けていた。
右長払いも頭部下端から離れていた。参照行の字形差で許容される省略ではない。

`family/proofread_elephant_corrections.py` は自作24-unit中心線の象部10 pathsに置換する。
木・氵・予の従来座標と各字の部品領域は保存する。既存共有部品や旧glyphsを変更しない。
source/statusを更新し、previous_source/status・既存notes・metricsを保存する。

全8 stylesで32/64/200pxのbefore/after、計192セルを実画像確認した。
第三の払いと右長払いの接続を確認し、空白・タイルclipは0。
32pxのsuperscript/subscriptは縮小された払い間隔が狭く、可読性合格とはしない。
16/18/24pxおよび最終全family配布物はこの追跡検査の対象外。

証拠は `build/full-proofread/elephant-evidence/`、字別の参照・全線分対応・
style/size判定・font SHAは `build/full-proofread/reviews/elephant-propagation.json`。
専用testsは13 passed。全familyへの統合・再生成は別工程。
