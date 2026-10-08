# Recheck of 794 previously uncertain upper kanji

## What was actually reviewed

All **794** identities marked uncertain in the original
`build/full-proofread/reviews/kanji-upper.json` were rendered against Noto Sans
CJK JP, face 0, at **160 px**. All **67** sheets under
`build/full-proofread/upper-recheck-160/` were physically opened and inspected.
The manifest records the original delivered TTF hash and the reference identity;
all 794 had reference cmap coverage. The original review remains unchanged.

Separate history: `build/full-proofread/reviews/kanji-upper-recheck.json`.

- 668: no obvious structural defect found at this resolution
- 88: still uncertain; not silently approved or changed
- 38: confirmed structural defects, checked against exact Unicode identity,
  local IDS descriptions and the complete source centerlines as well as images

"No obvious defect" is narrower than a full glyph-design certification. Stroke
style, proportions, polygonal approximation and differences from Noto alone
were not grounds for calling a glyph wrong. In particular, **鑭 U+946D and
欄 U+F91D were downgraded from tentative candidates to uncertain**: their center
stem passes through the open gap between gate boxes, and their inner top bar is
0.5 units below the box baseline. This may cause weight/raster-dependent contact,
but it is not an unequivocal centerline crossing.

## 38 target-only repairs

`family/proofread_recheck_corrections.py` changes exactly:

翹 聽 艫 蘼 趯 躙 躪 釄 鑪 靡 顱 飇 飈 飋 馗 鬜 鬭 鬱 鱸 鷹 鸕 鼯 鼷 鼹 虜 勉 𠠺 𠥼 𢌞 𣆶 𤄃 𤭖 𤭯 𧄍 𨴐 𨵱 𨷻 𪎌

The changes reserve separate regions for components previously overlaid:

- 堯/羽, 走/翟, 風/right components, 鼠/right components, 瓦/right components,
  免/right components, 元/力, 九/首 and 麦/来
- 林 above 非 beneath 广, and its individually checked derivatives
- 虍's short inner curl above 田/皿, preserving the five checked 盧 derivatives
- The explicitly checked U+F936 uses 毌 plus 力, not an automatic substitution
  of generic 男/田
- Gate interiors moved below the two top boxes; 鬜 is **U+9B1C, 髟+閒**, not 髜
- 鬥's crown shortened before placing 斲 below it
- 耳 above 壬 in the left side of 聽
- 木/缶/木 assigned disjoint crown regions in 鬱
- 鷹's 亻隹 and 鳥 stacked below 广
- U+2097C's two distinct cross stems restored instead of merging both at x=12
- 廴 turns kept left of 囘, with only the bottom sweep extending below it

Only named targets are overridden. Shared components and `glyphs/*.py` remain
unchanged. No external outline was imported or traced. Reused geometry belongs
to the project; new strokes/layouts were authored on its 24-unit grid. The
original 37 repairs are not modified by this module. Integration into the
loader belongs to the coordinator.

## Verification and artifacts

```sh
.venv/bin/python family/tools/recheck_correction_pilot.py
.venv/bin/python -m pytest -q tests/test_recheck_corrections.py
```

`build/pilot-recheck-corrections/` contains:

- Eight 160 px Noto / before / after sheets, all actually viewed
- 24 small-size after sheets, all actually viewed
- Before/after 38-glyph pilot TTFs for all eight styles and 32 SJPB strikes
- `report.json`: all 38 geometry differences, hashes and correction reasons

Five focused tests passed, including **2,432 actual nonblank TTF/SJPB renders**
(38 × 8 styles × 4 sizes × 2 formats), source validity/uniqueness, target-only
mutation, metric preservation, idempotence and original geometry protection.
High-resolution after status is recorded separately in
`build/full-proofread/reviews/kanji-upper-recheck-after.json`.

The tests do not prove all-size readability. Actual small-size inspection still
shows merged counters and difficult dense forms, particularly thick SJPB,
Italian and reduced subscript/superscript at 16–18 px. These remain a separate
unresolved raster/readability status. Native OS installation, variable instances
and full integrated artifact parity are not covered by the pilot.
