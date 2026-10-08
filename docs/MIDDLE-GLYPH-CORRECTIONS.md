# Bounded middle-kanji topology corrections

## Scope and provenance

`family/proofread_middle_corrections.py` supplies original 24-unit centerline
paths for exactly 18 new-family glyphs. `apply(glyphs)` replaces present targets,
returns their set, and is idempotent. It does not change legacy dictionaries,
shared components, or recursively-derived glyphs. The parent integration must
call it from the data loader; this module does not alter that loader.

Changed records use `source=original:family.proofread_middle_corrections` and
`status=structure-reviewed-large-size`. Prior source/status and existing notes,
flags and metrics are retained. This status explicitly does **not** mean that
all small bitmap strikes are readable.

Noto Sans CJK Regular TTC face 0 (JP) was viewed only to establish components
and topology. No reference outlines, coordinates, or pixels were traced,
imported, converted, or reused in glyph geometry.

## Individually rechecked findings

All findings were independently rechecked against the paired 200px reference
and distributed-font images, before drawing replacements.

| Code points | Characters | Structural finding and correction |
|---|---|---|
| U+622A | 截 | 隹 overlapped the descending 戈. Reserve lower-left 隹 and right 戈. |
| U+65ED U+6636 | 旭 昶 | 九/永 crossed 日. Separate left components and right 日. |
| U+66C6 | 曆 | 秝 and 日 were superimposed inside 厂. Give them upper/lower regions. |
| U+6BE7 U+6BEC U+6BEF U+6BF1 U+6C0A | 毧 毬 毯 毱 氊 | Full-width 毛 crossed its right component. Shorten left bars and reserve a right region; 氊 specifically contains 亶. |
| U+6C24 U+6C33 | 氤 氳 | 气 crossed enclosed 因/昷. Reserve a separate lower interior; U+6C33 uses 囚 above 皿, not U+6C32. |
| U+722C U+74DE | 爬 瓞 | 爪/瓜 crossed 巴/失. Give each its own left/right region. |
| U+74F0 U+74F1 U+74F2 U+74F8 U+7505 | 瓰 瓱 瓲 瓸 甅 | Full-width 瓦 crossed 分/毛/屯/百/厘. Separate the left 瓦 from the right components. |

These are unintended component crossings/placement errors, not differences in
stroke weight, serif shape, or the Noto design aesthetic.

## Evidence and validation

Generated proof root: `build/full-proofread/middle-corrections/`.

- `before-after-0.png` through `before-after-2.png`: all 18 glyphs, Noto / before / after at 200px.
- `<style>.ttf`: 18-glyph small TTFs for all eight styles; no full-family rebuild.
- `large-<style>.png`, `sizes-<style>.png`: 200px and 24/48/96px TTF proofs.
- `distribution-sizes-<style>.png`: actual 16/18/24/32px TTF and matching direct bitmap, displayed with nearest-neighbour 2x enlargement. Every eight-style sheet was viewed.
- `bitmaps/<style>-<size>.sjpb`, `.png`, `.json`: 16/18/24/32/48/96/200px binary fonts and manifests.
- `review-status.json`: per-character/style/distribution-size review states.

Run `.venv/bin/python -m pytest -q tests/test_proofread_middle_corrections.py`.
Tests check exact targets, coordinate bounds, independent path storage, bounded
nonmutation, metadata/provenance, idempotence, TTF coverage, nonempty rendering,
bitmap clipping guards, and exact SJPB decode/raster equality for all eight
styles and seven sizes. Render/exact-decode tests are mechanical checks, not
claims of small-size legibility.

## Remaining small-size limits

At 200px all 18 have the intended separate component regions. The former
large-geometry overlaps are removed. At actual distribution sizes, additional
raster-specific uncertainty remains:

- 16/18px reduced subscript/superscript: too few pixels for reliable per-stroke
  identification; do not certify.
- Dense 曆, 氊, 氳, 甅: interior counters and short strokes can merge, particularly
  in 1-bit non-singleline styles. Italian has especially heavy horizontal joins.
- Several 24/32px non-singleline bitmap strokes still merge after thresholding;
  even when the TTF is recognizable, that does not validate the binary strike.

The per-cell ledger conservatively retains uncertain results rather than
labeling every generated strike as a pass. No renderer/hinting or legacy-asset
changes were made to conceal these limits.
