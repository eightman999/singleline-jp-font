# Upper-codepoint kanji: 37 local structural corrections

## Evidence and scope

The 37 confirmed-defect entries in
`build/full-proofread/reviews/kanji-upper.json` were independently checked by
actually opening all three 200 px confirmation sheets. No entries were rejected
as false positives: the specific reported crossings, overlaps and disconnected
crown strokes were visible at that resolution.

`family/proofread_upper_corrections.py` applies only to the following identities:

舞 賡 贋 赳 趁 趄 趨 閘 閴 颫 颰 颱 颶 颷 颸 颺 颼 飂 飃 鬧 鬨 鬩 鬪 鬫 魁 魋 魍 魘 麨 麩 麪 麭 麯 麴 麵 麾 齎

All replacement layouts are independently authored on the project grid, using
existing project-authored component paths where appropriate. Noto Sans CJK JP
Regular (TTC face 0) was used as a visual topology reference, never as a source
of contours or coordinates. This work does not require pixel/proportion equality
with Noto. Other accepted glyph conventions and style differences are preserved.

## Structural changes

- 舞: four continuous verticals connect all three crown horizontals; 舛 occupies
  the lower compartment.
- 賡, 贋, 魘, 麾: reserve separate upper and lower contents under 广/厂. The
  respective 貝, 鬼 and 毛 no longer cross the upper contents.
- 赳, 趁, 趄, 趨: narrow 走's upper-left structure; place the right component in
  a separate region above its bottom sweep.
- 閘, 閴: place 甲/貝 below the two closed top compartments of 門.
- Ten 風 derivatives: wind head/body at left, added component at upper right;
  only the intended lower sweep passes beneath the right component.
- Five 鬥 derivatives: short crown halves end at y=8, enclosed component begins
  at y=10 and remains inside the two outer verticals.
- 魁, 魋, 魍: compact left 鬼 head, legs and curl; distinct upper-right component
  above the long lower leg.
- Seven 麥 derivatives: narrow independently redrawn 來/夂 structure at left,
  added component at right, and only the lower descending sweep spans the cell.
  A separate 240 px Noto reference for 麥/來/麩 was opened to confirm the left
  element's internal topology; lateral small 人 strokes begin below the top
  horizontal rather than protruding above it.
- 齎: complete 齊 crown above a separate 貝, between the two lower outer stems.

No `glyphs/*.py`, shared components or non-target glyphs were edited. Applying
these overrides preserves the existing advance, width factor and other metrics.
The data loader integration is handled by the full-build coordinator.

## Reproduce the focused build

```sh
.venv/bin/python family/tools/upper_correction_pilot.py
.venv/bin/python -m pytest -q tests/test_upper_corrections.py
```

The proof tool reconstructs the old project geometry directly using `build_kanji`
so its before/after comparison remains valid after loader integration.

Outputs in `build/pilot-upper-corrections/`:

- `comparison-160-00.png` through `comparison-160-07.png`: Noto / before / after.
  All eight sheets were opened and visually reviewed, including regenerated
  wheat sheets after the final geometry adjustment.
- `{style}-small-{0,1,2}.png`: actual after TTF/SJPB pixels at 3× nearest-neighbor.
  All 24 sheets were opened and visually reviewed.
- `before/` and `after/`: 8 static TTFs and 32 SJPB strikes each, 37 glyphs only.
- `report.json`: exact changed identities, before/after geometry hashes,
  per-character reasons and all 64 render-case combinations.

Ten focused tests passed, including actual serialization and rendering of
**2,368 after glyph cases** (37 × 8 styles × 4 sizes × 2 formats), no blanks,
finite in-grid geometry, target-only mutation, idempotence, original source
preservation and reserved component regions.

## Remaining limitations

The high-resolution review confirms removal of the reported structural
interference. It is not a blanket typographic certification of every component.
At 16–18 px, many dense counters remain filled or hard to distinguish, especially
in thick SJPB and subscript/superscript styles; Italian's heavier horizontals also
reduce counter clarity. These outcomes were observed, not marked as visual
passes. A nonblank-render test is not a readability test.

The focused proof does not cover installed CoreText/DirectWrite, variable-font
instances, full-family release packaging or final integrated artifact parity.
Those checks require the coordinator's full regeneration and final tests.
