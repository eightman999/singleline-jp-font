# Original JIS non-Kanji additions

`jis_symbols.py` adds 409 genuine source glyph identities, including 23 new
combining marks and 20 negative circled numbers. Together with the existing
project geometry and loader's explicit canonical/width derivations, the
repertoire covers all 1,183 JIS X 0213:2004 non-Kanji identities and all 25
multi-scalar sequences. Coverage counts are identity/geometry coverage, not
a claim that every glyph has production-quality typographic review.

## Provenance

All paths are authored geometric centerlines or explicit transformations of
this project's owned ASCII, kana, or Kanji. There is no font-outline import,
bitmap tracing, substitution of unrelated shapes, or arbitrary repeated
placeholder. Semantic shared forms are explained in `DERIVATIONS`:
turned/reversed IPA letters, white/black figure pairs, circled digits/kana,
parenthesized Kanji, Roman numerals, era ligatures, and square units.

Unicode names and decompositions establish character identities. The
[Unicode mathematics report](https://unicode.org/L2/L2003/03165-tr25-6d7.pdf)
was used to verify the textual meaning of projective/perspective: a bar or
double bar above a wedge. No source graphic was traced or copied.

## Integration contracts

- Merge `MARKS` before canonical composition and give these marks zero advance
- Respect `CATEGORIES`, `ADVANCES`, and `WIDTH_FACTORS`
- Keep explicit multi-scalar keys, especially rising/falling contour tones
- Use `FILLED` only for genuine solid geometry
- `NEGATIVE` keys have a closed solid outer contour first, then numeral
  centerlines that must become white cutouts. They are not in `FILLED`.
  Raster/SVG renderers should use a white mask; outline renderers need real
  counter geometry and correct treatment of overlapping white strokes
- Annular filled symbols use a union of hole-free solid quadrilaterals, so
  their empty central counters remain empty even in an all-filled-path API
- Classify phonetic marks by Unicode combining class, not codepoint ranges:
  several below marks have codepoints earlier than U+0320
- Box-drawing geometry reaches source-cell boundaries. A consumer that
  promises continuous rules across cells must give category `box-drawing`
  edge-to-edge metrics rather than ordinary text sidebearings

## Design status and limits

The source grid is x/y-down 0..24; below marks can reach y=25. The alphabet is
intentionally angular. Six generated source contact sheets were visually
inspected and concrete orientation/equality/junction defects corrected.
This is source review, not expert IPA review or a complete pixel-size audit.
Small enclosed forms and dense square units can lose detail at bitmap sizes;
they should be checked at the actual requested ppem and weight.

Run `python -m unittest family.tests.test_jis_symbols` for focused source,
coverage, sequence, mark-metric, fill-semantics, and negative-protocol checks.
