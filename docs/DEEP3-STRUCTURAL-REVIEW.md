# Deep structural review, group 3

## Scope and outcome

All 45 assigned identities were compared individually using:

1. The exact Japanese-source glyph raster in the official Unicode 18 chart.
2. Noto Sans CJK Regular TTC face 0 (JP), for corroboration only.
3. The actual pre-deep-rebuild distributed singleline TTF at 220px.
4. Every project source path and the available IDS/provenance records.

Outcome: **32 structurally normal with design/size limits kept separate;
13 confirmed errors repaired in local source; no unresolved identity/topology
question remains in this particular group.** This is not an all-style or
small-size readability certification.

The 45 per-character reasons, source-coordinate snapshots, exact J-source IDs,
PDF page links, image hashes, old artifact hashes, and repair verification are in
`build/full-proofread/reviews/deep-structural-group-3.json`. The old screening and
recheck reports are not overwritten by this report.

## Primary references

- [Unicode CJK Unified Ideographs chart](https://www.unicode.org/charts/PDF/U4E00.pdf)
- [Unicode CJK Compatibility Ideographs chart](https://www.unicode.org/charts/PDF/UF900.pdf)
- [Unicode CJK Extension B chart](https://www.unicode.org/charts/PDF/U20000.pdf)

The local PDF versions identify themselves as Unicode 18. Japanese source
labels, rather than an arbitrary G/T/H glyph from the same row, select the
reference. Each cropped source image retains its J label. The references were
used to identify components, enclosure boundaries, and variants, never to trace
or extract reference contours or coordinates.

## Bounded repairs

`family/proofread_deep3_corrections.py` modifies only:

鱜 鱥 黌 鼇 鼈 齏 蘒 𠠇 𡑮 𡿺 𢦏 𥧔 𦥯

- 鱜: restore the 鄕-family middle 白＋匕 required by J14-7D6C.
- 鱥: remove the 歲 interior crossbar/point collisions.
- 黌 / 𦥯: keep both 爻 crosses above 冖; also separate 黃's compressed interior.
- 鼇 / 鼈: remove extra vertical partitions inside the lower 黽 compartments,
  retaining both original 攵 diagonals in each crown.
- 齏: relocate 韭 from the 齊 crown into the lower interior.
- 蘒: retain traditional 龜's comb-like left side and crossed right compartment.
- 𠠇: restore the upper inner point and 刀 falling stroke, retaining 亞 and 刂.
- 𡑮: separate the compressed 塞 crown bars and uprights.
- 𡿺: enclose the 囟 cross rather than letting it project above its box.
- 𢦏: place 十 at the upper left of 戈 rather than over its central stem.
- 𥧔: separate 气 and the enclosed 米 below 穴.

The module returns the changed target set, keeps glyph metrics and existing
notes/flags, stores prior provenance, and assigns its own source plus
`structure-reviewed-large-size`. It does not modify shared components or legacy
source dictionaries. `apply` requires parent data-loader integration; a full
family rebuild is intentionally not performed by this review worker.

## Compatibility and supplementary identities

All six compatibility glyphs retain their own code points. The old distributed
cmap14 was checked for these exact mappings:

- 6B04 FE00 → F91D
- 8612 FE00 → FA20
- 5840 FE00 → FA39
- 722B FE00 → FA49
- 7A40 FE00 → FA54
- 8CD3 FE00 → FA64

Each mapped to the same glyph name as its direct compatibility code point.
The repaired FA20 also has a dedicated regression test for cmap14 and SJPB
sequence identity. FA20's traditional 龜 must not be conflated with U+26FF7's
J-source 亀. The 20 Extension-B identities were checked directly against their
own J-source rows; none was normalized into a convenient BMP character.

## Proofs and retained limitations

Evidence root: `build/full-proofread/deep3/`.

- `primary-references.json`: URLs, PDF pages, clip locations, J labels and hashes.
- `compare-00.png` through `compare-11.png`: all 45 original three-way comparisons.
- `source-paths.json`: pre-repair paths and IDS/provenance for every assigned glyph.
- `repaired/compare-after-00.png` through `03.png`: official / old / repaired at 220px.
- `repaired/large-<style>.png`: all 13 repaired glyphs in eight styles at 220px.
- `repaired/distribution-sizes-<style>.png`: actual 16/18/24/32px TTF and direct
  bitmap views, displayed at nearest-neighbour 2x. All eight sheets were viewed.
- `repaired/review-status.json`: 416 distinct repaired-character/style/size cases.
- `repaired/grass-all8-160-32.png`: all-eight-style 160px/32px TTF/bitmap checks
  after lengthening FA20's grass uprights so heavy horizontals cannot hide them.
- `repaired-pre-grass-fix/`: prior proofs retained without overwriting history.
- `evidence-sha256.json`: evidence hashes, including the new strikes.

The grass correction preserves both uprights and separation from the body in
all eight styles at 160px and 32px. That does not certify the dense 龜 interior
at 32px. Italian heavy horizontals can still close dense counters even at large
sizes (notably 黌/鼇/鼈), and many 1-bit or reduced sub/super strikes remain
uncertain. The small ledger conservatively records 396 TTF and 412 bitmap cases
as uncertain; these are separate from resolving the 45 character identities and
source-structure questions.

## Tests and integration

`.venv/bin/python -m pytest -q tests/test_proofread_deep3_corrections.py`

Result: **12 passed**. Coverage includes exact targets, coordinate bounds,
independent path storage, bounded/idempotent replacement, provenance retention,
TTF coverage and nonempty masks, bitmap clipping guards, exact SJPB roundtrip
for all eight styles at seven sizes, retained crown diagonals, and compatibility
identity. Mechanical rendering tests are not used as a visual quality pass.

Source and tests are frozen after the grass fix. The final distributed artifact
hash and post-integration result must be rebound by the parent after its full
family build; this report deliberately marks that step pending.
