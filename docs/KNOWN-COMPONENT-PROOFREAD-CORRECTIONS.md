# Bounded audit of known 難 and 龜 descendants

## Outcome

Eight explicit glyphs are replaced by new family-only centerlines:
難 儺 攤 灘 龜 龝 鬮 蘒. The parent integrates
`family.proofread_known_component_corrections.apply` after deep2/deep3.
Shared legacy glyphs, components, and the historical repair modules are intact.
This is not a recursive component substitution.

All paths were inspected and compared with the exact Japanese-source rows in
local Unicode 18 charts. Reference glyphs were viewed at over 300px; project
before/after images are rendered at 400px. No external font contours or chart
images are included in deliverables. Noto fonts were not used as evidence.

## Primary references and decisions

- 難 U+96E3: J0-4671, U4E00 PDF page 475 (printed 1031). Add the missing second
  independent horizontal below 口. Its Japanese modern crown is 艹-shaped;
  **do not add the traditional 廿 bottom edge**.
- 儺 U+513A: J0-5135, page 23 (579). Add 廿 bottom edge and second lower bar.
- 攤 U+6524: J0-5A3A, page 152 (708). Same two separately verified omissions.
- 灘 U+7058: J0-4667, page 225 (781). Same two separately verified omissions.
- 龜 U+9F9C: J0-737D, page 531 (1087). Replace rectangular grid substitution
  with separate upper/lower three-bar combs and the crossed right compartment.
- 龝 U+9F9D: J0-6354, page 531 (1087). Preserve 禾, repair its 龜.
- 鬮 U+9B2E: J0-722D, page 503 (1059). Existing cross was correct, but four
  comb bars plus a short bridge omit two levels. Restore all six comb bars;
  each group's middle bar continues to the right compartment boundary.
- 蘒 U+FA20: J4-7738, UF900 PDF page 10. Independently verified the same six
  comb levels and connected middle bars; post-deep3 correction removes the
  spurious extra short bar inside the top-left mouth and closes its outline.
  Compatibility identity U+FA20 and 8612 FE00 are retained, never normalized.
- 癱 U+7671: J13-785F, U4E00 PDF page 264. Comparison only: existing deep2
  has the required 廿 edge and two lower bars; no new correction.

Sources: https://www.unicode.org/charts/PDF/U4E00.pdf and
https://www.unicode.org/charts/PDF/UF900.pdf . Glyphs select the stated J row;
other regions' forms are not being declared invalid.

## Verification and limits

- Regression tests: exact target scope, modern/traditional crown distinction,
  six comb levels and two extended middle bars, unchanged source inputs and
  unrelated glyphs, idempotent apply, grid bounds, no duplicate turtle segments,
  compatibility cmap14 mapping, and all eight styles at 32/64/200px.
- 192 TTF glyphs and 192 SJPB glyphs generated. SJPB decoded masks equal the
  raster output. Nonempty rendering is not a readability certification.
- All eight style sheets at 32/64/200px were viewed. Singleline at 400px
  confirms the repaired topology. At 32px dense glyphs remain difficult.
- Italian reverse-contrast horizontal weight still merges or nearly merges
  dense comb gaps, especially inside 鬮 and 蘒 even at 200px. This is a remaining
  style/spacing limitation, not resolved by restoring missing topology.
- Native OS rendering was not tested. No full-family rebuild is claimed here.

Own-font images, individual coordinate/reason JSONs, and a reproducible pilot
are in `build/full-proofread/known-component-review/` and
`family/tools/known_component_correction_pilot.py`. Unicode reference images
remain private temporary inspection assets and are not published.
