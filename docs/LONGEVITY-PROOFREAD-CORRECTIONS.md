# 壽系列の配置不具合追跡

直接参照の15字をUnicode18 J-source、Noto JP、現中心線の全pathsと300px画像で照合した。
嶹幬擣檮濤燾璹疇禱躊隯の11字を限定修正。儔壔籌鑄は先行修正を比較確認し、変更しない。

「中央縦線の欠画」という仮説はソースで否定された。工の縦線は元からある。
問題は上部7 pathsが約6.8 units（燾では約4.54）に集中し、下の一・口寸との空きが
大きくなった非均等な配置。12 pathsの意味を保存したまま、士・折れ・工・一・口寸を
連続した高さ帯へ再配置する。寸の縦画上端は一に接続させる。
左偏と燾の灬は元座標を保存。禱の示/礻差は今回の壽不具合と区別し、示を保持する。
共有components・glyphs・既修正moduleは変更しない。外部輪郭の転用はない。

全15字×8 styles×32/64/200px×before/after、720セルを実画像閲覧。
空白/タイルclipは0。32pxは各細部の可読性を一律合格にしない。
Italianの燾・籌は64/200pxでも太い横画による近接帯域の接触が残るため、
構造上の対応確認と光学的な分離品質を区別し、後者は未認定とした。

専用testsは20 passed。全線分・字別一次出典・font SHA・style/size結果は
`build/full-proofread/reviews/longevity-propagation.json`。
Unicode原表画像は `build/full-proofread/longevity-evidence/` の内部参照用で公開配布しない。
全familyの統合・再生成は別工程。
