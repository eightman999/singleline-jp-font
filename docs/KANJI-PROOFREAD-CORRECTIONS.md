# Bounded Japanese-form repairs (10 glyphs)

The new family has independently authored centerline repairs for
**㖨 䐜 咎 嘷 晷 槩 櫜 洴 籘 蓱**. These address concrete topology or
component-placement defects identified in the 78-character non-Japanese-IDS
review. They are not a blanket certification of these characters at all sizes,
or of the rest of the family.

## Scope and integration

`family/proofread_kanji_corrections.py` exposes `apply(glyphs)`. Call it after
assembling the new family's glyph dictionary. It replaces only existing entries
for the ten named characters and returns their set. It preserves metrics and prior flags. It labels the new source module and
`structure-reviewed-large-size` status, retaining original source/status in
`notes.previous_source` / `notes.previous_status` with an explicit repair note.
`glyphs/`, shared components, recursive IDS data, and legacy products are not
changed. The module is idempotent and does not propagate repairs to other words
or descendants. Its paths are original 24-unit-grid drawings, not sampled,
traced, converted or extracted from any reference font or PDF.

## Evidence and changes

- 㖨: restore a 彑/彔-style crown instead of the previous ヨ-like crown.
- 䐜: replace a 十-headed 真 composition with a 眞-style crown.
- 咎: give the upper 夂 and right 人 separate placement above 口.
- 嘷: replace the radiating 米-like lower part with the Japanese 臯 structure.
- 晷: preserve 日 and use the separated 咎 structure below it.
- 槩: redraw the 皀 component, including its leading slant and lower 匕.
- 櫜: allocate separate vertical bands for the shelter, 咎 and 木.
- 洴: use the Japanese 幷 structure, rather than detached 八 above 开.
- 籘: reserve distinct space for 竹, 月, 龹 and 糸.
- 蓱: retain 艹 and use the Japanese 幷 structure in 洴 below it.

Reference comparisons use installed **Noto Sans CJK JP 2.004, TTC face 0**.
The flagged forms were also checked by viewing the Japanese-source glyphs in
Unicode 18.0 charts. The entry-level record gives PDF pages and J-source IDs:

- [Extension A](https://www.unicode.org/Public/18.0.0/charts/PDF/U3400.pdf):
  㖨 page 11, J4-2426; 䐜 page 110, J4-754C.
- [Unified ideographs](https://www.unicode.org/Public/18.0.0/charts/PDF/U4E00.pdf):
  咎 page 44/J0-5268; 嘷 page 55/J14-2441; 晷 page 161/J13-7540;
  槩 page 183/J3-7623; 櫜 page 189/J14-2F67; 洴 page 204/J4-6E65;
  籘 page 303/J0-645C; 蓱 page 359/J14-7662.

These are PDF file page numbers, not the printed Unicode book page numbers.
[Unicode chart font data has its own restrictions](https://www.unicode.org/charts/fonts.html);
no embedded font or outline data was extracted.

## Verification actually performed

Ten-character before/after subset TTFs were built in all eight styles. Every
subset was reloaded and rasterized at 16, 18, 24 and 32 px. There are **320 after
renders and 320 before renders**, with no blank output or tile clipping. The
640-render count is not 640 separate characters.

The reviewer actually viewed:

- `build/full-proofread/reviews/kanji-corrections/comparison-160px.png`, containing
  all ten before/after/reference comparisons at 160 px.
- All eight `small-sizes-<style>.png` sheets in the same directory, displaying
  native 16/18/24/32 px TTF rasters enlarged 3× with nearest-neighbour sampling.

The reported large-size topology defects are corrected in those comparisons.
**Small-size readability remains limited**, especially the dense 櫜 and 籘,
heavy horizontal Italian styling, and reduced super/subscript styles. Several
16/18 px interiors fuse or become too faint to distinguish reliably. Raster
presence and absence of clipping do not certify readability. The native small
rasters were inspected, but are not marked as a universal typographic pass.

This verification concerns generated outline-TTF subsets, not every full-family
bitmap strike, variable-axis instance, browser, operating system, or shaping
engine. Full-family regeneration and integration checks are separate work.
The original 78-entry review still has 32 uncertain entries; they were not
silently promoted to approved status.

## Tests and records

Run `python -m pytest tests/test_proofread_kanji_corrections.py -q` from the repo
root. Tests cover bounded scope, idempotence, finite in-cell paths, independent
path lists, preserved metadata, untouched legacy data, unique geometry, font
reload and nonblank rendering for all eight styles and four sizes.

The original review and appended repair/recheck details are in
`build/full-proofread/reviews/non-japanese-ids.json`. Raster presence/clipping
measurements are in `build/full-proofread/reviews/kanji-corrections/raster-checks.json`.

## Independent lower-range follow-up

A second reviewer actually viewed every character on the ten 180 px detail
sheets enumerated by `build/full-proofread/kanji-lower-detail/index.json`:
**160 distinct codepoints**, not a claim to independently repeat the full
2,500-glyph first screening. The resulting second-look record is
`build/full-proofread/reviews/kanji-lower-recheck.json`.

The following **22 exact-key repairs** are implemented independently in
`family/proofread_lower_corrections.py`:
䰗䰠亙儔壔壽囟廸廹廼剋尅匙彪奠奥奧嶴冖宀凾巫.
The previously repaired 咎 is recorded but is not duplicated. U+4F96 is 侖;
comparison to 傘 is explicitly rejected as a codepoint misidentification.
建 and 廽 have narrower original 廴 geometry than 廸/廹/廼 and were not
changed merely because they look similar.

The confirmed coordinate defects include overlapping 鬥/interior regions,
overlapping 鬼 and 申 heads, 乂 extending above 囟's enclosing box, 廴 crossing
into its inner glyph, overlaid 克/刂 and 是/匕, an excessively compressed 酉,
and 米/釆 extending above 奥/奧's upper frame. Per-character reasons cite the
original coordinates. These repairs are not propagated recursively.

All 22 before/after/reference images at 160 px were viewed. All eight
small-size sheets were viewed at native 16/18/24/32 px (3× nearest-neighbour
presentation); **704 after rasters** were nonblank and unclipped. Dense 壽,
䰗 and 嶴 remain limited at small sizes, especially Italian reverse contrast
and the scaled subscript/superscript styles. These tests establish bounded
structural improvements, not universal readability.

Both apply functions label changed Glyphs as
`source='original:family.<module>'` and
`status='structure-reviewed-large-size'`. Original source/status are retained
in notes; they do not continue to falsely label repaired paths as untouched
legacy drawings. Existing notes, flags and metrics remain intact. Tests are
in `tests/test_proofread_lower_corrections.py` as well as the ten-glyph test
module above.

## Primary-source resolution pass and 13 additional repairs

The 54 lower-range and 32 non-Japanese-IDS uncertainties contain one duplicate,
㺔. A further pass viewed the **Unicode 18 J-source rows for all 85 distinct
scalars**, beside the delivered design and Noto JP. These are primary-source
row views, not repeated guesses from the same Noto comparison. Source IDS
identities and selected original coordinate layouts were also checked.

The consolidated, per-codepoint result is
`build/full-proofread/reviews/kanji-uncertain-resolution.json`:

- 48 structural/regional suspicions resolved with **no change**.
- 24 remain **uncertain**, with a specific open layout or stroke-correspondence
  question for each. They are not approved as harmless variants.
- 13 exact-codepoint defects repaired in
  `family/proofread_additional_kanji_corrections.py`.

Important no-change distinctions include 氵+覇 in 㶚 (not 霸), 口+粛 in 嘨
(not 嘯), 女+㐮 in 嬢 (not 孃), and heartless 檃 versus heart-bearing 櫽.
瑢's Japanese 宂/人/口 structure does not require adding another 八. The
four inner 人 groups of 齧/囓 are present, despite their thin wave-like
appearance. These decisions settle the stated structural suspicion, not all
small-size typography.

### Approved additional exact keys

兠 劃 厴 哉 唐 嚳 壚 廬 彧 翺 亟 焈 魲.

The first ten repair component overlap, a severed central stem, surplus bars,
or the Japanese 臯 form. Primary Japanese source IDs are respectively
J4-2326, J0-3344, J14-2358, J0-3A48, J0-4562, J13-2F3E, J13-2F64,
J0-572A, J13-743F and J13-7A43.

Three later confirmations were explicitly added to this module:

- 亟 U+4E9F: J0-5034 connects the 丂 fold to the top horizontal. The original
  paths placed the next horizontal/fold at y=6, detached from the top y=2.
- 焈 U+7108: J4-6F6E has the connected/sloping 戶 crown. The original design
  used a detached-dot 户 crown, corresponding to another source column.
- 魲 U+9B72: J3-7E43 likewise has the connected/sloping 戶 crown. The Unicode
  row distinguishes it visibly from the detached-dot G/KP source forms.

The latter two are Japanese-source choices for the same encoded scalars,
not a claim that other regional glyphs are universally incorrect. No
normalization, cmap remapping, or IVS conflation is performed.

Every repair has a 160 px before/after/reference comparison, actually viewed,
in `build/full-proofread/reviews/additional-corrections/`. Before-state subsets
were generated with this exact repair temporarily disabled in memory; they do
not accidentally show already-repaired source data. All eight native-size
sheets were viewed at 16/18/24/32 px, with 3× nearest-neighbour presentation.
**416 after renders** are nonblank and unclipped in 48×40 raster tiles.
An initial 40 px tile clipped the right edge of 32 px Italic 劃; widening the
inspection tile established that this was a proof-tile limit rather than
clipping within the font. Dense small forms, reverse-contrast and scaled
subscript/superscript styles retain readability limitations.

The 10-, 22- and 13-glyph module test suites together passed **79 tests**.
The additional module uses the same bounded apply/source-history contract.
All three modules were frozen after the final image review for integrated
regeneration. No uncertain character was changed merely to reduce the count.

### Specific unresolved work

The remaining 24 are:
㟴 䀹 䆴 乘 亂 亹 傀 像 劉 劘 嚢 囑 埀 夔 奭 孅 屬 峯 嵊 嵬 廆 椶 葼 鱜.

The record distinguishes exact issues: extremely compressed inner boxes in
屬/囑 and 夔; crowded 林/非 in 劘; 大 legs approaching/crossing the 百 boxes
in 奭; shallow bands in 嚢 and 亹; and specific 鬼, 乘, 㚇 or 鄕 constituent
questions. Matching a component name or an IDS operator does not resolve the
optical layout. These need independent, bounded follow-up instead of blanket
acceptance or recursive component replacement.
