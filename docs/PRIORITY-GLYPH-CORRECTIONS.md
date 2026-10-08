# Priority near-form proofreading: family-only corrections

## Scope and reference

Eleven glyphs were compared visually with installed **Noto Sans CJK JP Regular**
(`/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`, collection face 0).
The face name was verified from its name table; reference glyphs were actually
rendered and viewed at 90 px. Reference outlines/pixels were not converted,
traced, or imported. All replacements are independently authored centerlines
on the project's 24-unit grid.

The original delivered `build/family/proofs/priority-glyphs/singleline.png`
was viewed before editing. The focused before/after build is reproducible with:

```sh
.venv/bin/python family/tools/priority_correction_pilot.py
.venv/bin/python -m pytest -q tests/test_proofread_corrections.py tests/test_priority_glyph_qa.py
```

Outputs are under `build/pilot-priority-corrections/{before,after}/` with actual
static TTFs, four SJPB sizes per style, PNG/SVG proofs and JSON measurements.
These are deliberately small 11-glyph pilot fonts, not the release family.

## Findings and changes

| Glyphs | Before | Family-only correction |
|---|---|---|
| 己・已・巳 | 己's left stem rose above its middle bar, resembling 已. Several small-size renders merged two or all three forms. | Common top/middle bars at y=3/14; left stem begins at y=14/9/3. The left opening distinguishes all three. |
| 未・末 | Correct short/long ordering, but weak length separation at small sizes. | Upper/lower bars are 14/22 units for 未, 22/14 for 末. |
| 土・士 | Correct ordering, but 土's upper bar was 18 units against its 22-unit bottom. | Upper/bottom bars are 14/22 for 土, 22/14 for 士, with shared y positions. |
| 髙 | The center was an open-top horizontal comb with extra vertical divisions. | Two verticals connect the top bar to the lower enclosure, with a middle crossbar. |
| 高 | Upper 口 and lower enclosure structure matches the reference's character topology. | Kept unchanged. The short diagonal top dot is a stylistic centerline choice. |
| 吉・𠮷 | Upper 士/土 horizontal-length distinction was already present. | Kept unchanged; independently checked in every pilot proof. |

The common y=14 middle bar for 己已巳 leaves sufficient space for the intermediate
left-stem start in the reduced 0.65-scale subscript/superscript designs. This is
an optical simplification, not a claim that Noto has these exact proportions.

## Verification and limits

All eight final style sheets were actually viewed: singleline, gothic, serif,
pc98-mincho, italian, italic, subscript and superscript. Each sheet contains
both SJPB and FreeType monochrome TTF rendering at 16, 18, 24 and 32 px.

- 704 glyph renders, 448 within-group pair comparisons per before/after build.
- Before: 10 exactly indistinguishable pixel cases, all among 己已巳.
- After: zero exact collisions, zero blank/missing priority glyphs.
- Ten focused regression tests passed, including a fresh all-style raster build.
- Small SJPB counters remain heavy, especially high/髙 and reduced styles at
  16–18 px. Exact pixel distinction is not a readability certification.
- Native CoreText/DirectWrite, actual installation, variable-font instances and
  every non-priority character are outside this focused verification.

## Compatibility boundary

No `glyphs/*.py` compatibility source was changed. `family/data_loader.py`
applies `family.proofread_corrections.apply_corrections()` at its final stage.
Only the eight explicitly listed replacement glyphs are overridden; metrics
and all other glyphs are preserved. Legacy generators retain the old designs.
The family glyph notes record the previous source, correction reason and narrow
review scope. This does not certify the full family's Japanese proofreading.

## Related combining-accent corrections

The non-Kanji review identified three concrete composition errors. Its actual
before sheets `build/full-proofread/nonkanji-sheets/001.png` and `006.png` were
viewed, then an independent before/after TTF proof was built and viewed at
`build/pilot-priority-corrections/accent-before-after.png`.

1. U+0300 grave and U+0301 acute previously described the same geometric segment
   in opposite path order. Grave is now `(9,0) → (14,3)`, while acute keeps its
   opposite slope. This changes the family combining mark and its generated
   derivatives, not existing precomposed legacy designs such as À.
2. Multiple above marks previously shared the same y-band. They now occupy
   successive 4-unit bands in canonical order, first mark nearest the base.
   The base is compressed downward to reserve space while retaining its bottom.
3. Above accents on i/j replace their audited legacy dot path; below-only marks
   retain the dot. Input geometry is never mutated.

The comparison reference for Latin accents is installed **Noto Sans Regular**,
not Noto CJK: the latter lacks some required mark coverage. Proof-only PUA aliases
address the generated family sequence outlines directly; this proof does not
claim to test application GSUB shaping. The proof shows grave/acute direction,
separate mark presence/order, removed i/j dot and retained below-only dot.
Its design is not intended to match Noto pixels or Noto's side-offset Vietnamese
mark positioning.

`build/pilot-priority-corrections/accent-change-ledger.json` records every changed
identity, source and before/after geometry hash: **217 identities** changed from
the state immediately after the eight Kanji corrections. The full-family
regeneration must include these changes. Four extra accent regressions bring
focused tests to **14 passed**. The unreconstructed old full build produced
83 passed / 44 failed in `tests/test_family.py`; failures were stale source,
outline, variable-outline and bitmap comparisons and must be rerun after the
parent's full integrated build. No existing artifacts were certified from that
stale run.

### High-resolution confirmation

After the initial small-size audit, **160 px** reference and actual before/after
TTF glyphs were rendered and all six PNGs were opened and visually inspected:
`priority-160-{1,2,3}.png` and `accent-160-{1,2,3}.png` under the pilot directory.
They confirm the left-opening distinction, 髙's connected ladder, opposite
accent slopes, separate multi-mark levels, i/j dot removal and below-only dot
retention. The 未末/土士 length changes are readability improvements to already
correct topology, not claims that different proportions were spelling errors.

Source/sample regression run (excluding stale full-artifact comparisons):
**64 passed, 77 deselected**. The accent identity ledger was passed to the
non-Kanji reviewer for independent full-repertoire rechecking.
