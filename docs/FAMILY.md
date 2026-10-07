# Singleline JP Lab, experimental family 0.201

Added 2026-10-06; expanded to16/18/24/32px in the same-day recheck. This is a separate, editable family generator. Existing
`assets/fonts/custom-*` PNG/JSON, original `fonts/*.ttf`, and canonical `glyphs/`
are unchanged. Their hashes are locked in `family/data/legacy-sha256.json`.

## What this build means

The build targets the 10,050 Kanji in JIS X 0213:2004 levels 1–4, plus the
864 jinmeiyō entries in Unicode 18.0.0 and separately identified surname extras
髙 and 𠮷. Exact counts, missing characters, per-level coverage and sequence
coverage come from **the generated `build/family/coverage.json`**, not this page.
The 864 jinmeiyō entries are inside the JIS Kanji union and must not be added a
second time when counting unique characters.

The source repository has 2,141 Kanji geometries, including all 2,136 Jōyō
Kanji, among its 2,584 original encoded characters. Existing outlines are
preserved. Additional Kanji use project-authored components and CJKVI-IDS
character structure. Geometry can be nonblank, unique and correctly encoded
without being good typography. **Every expanded Kanji is a composition/design
draft, not individually proofread or release-certified.** Dense characters at
18/24 pixels can lose strokes, counters and distinguishing details. Overlay
and nested enclosure compositions are especially high-risk. Per-character
provenance, flags and missing reasons are in `glyph-provenance.json.gz` and
`family/data/kanji-coverage-summary.json`.

There are no tofu, random marks, hashes or copied fallback fonts assigned to
missing characters. `.notdef` is the ordinary unencoded missing-glyph indicator.
Legitimate Latin width/diacritic/enclosure variants and pictogram semantic
aliases are explicit derivations. The upstream Kanji duplicates 剝/剥, 塡/填,
頬/頰 are reported as inherited, rather than silently altered.

## Styles

| Output | Definition | Variable version |
|---|---|---|
| Singleline | thin direct expansion of the editable centerline paths | no |
| PC98 Mincho Inspired | original geometric, vertical-heavy Mincho interpretation with triangular terminals; no PC-98 ROM data | no |
| Gothic | uniform-weight strokes | weight + slant |
| Italian Reverse Contrast | **upright** horizontal-heavy reverse-contrast serif interpretation | no |
| Serif | vertical-heavy strokes with terminal serifs | weight + slant |
| Italic | right-leaning serif, with original cursive a/g/f alternatives | no |
| Subscript | reduced scale and lowered baseline for the whole font | no |
| Superscript | reduced scale and raised baseline for the whole font | no |

Italian is deliberately distinct from italic. The word was interpreted as
reverse-contrast Italian display lettering; this interpretation is reversible.
The variable font's slanted named instances are called **Oblique** because
slanting alone is different from the authored Italic alternates.

The two variable TTFs have `fvar`, `STAT` and nonzero `gvar` outline deltas.
Axes: `wght` 200–700 (default 400), `slnt` −12–0 (default 0). Bilinear corner
corrections make combined weight/slant extremes match their source masters.
The other six styles are static. Bitmap files are fixed raster strikes and
do not themselves interpolate.

## Files

- `build/family/static/*.ttf`: eight installable, scalable TrueType families
- `build/family/variable/*-VF.ttf`: Gothic and Serif variable TrueType
- [`build/family/centerlines.svgz`](../build/family/centerlines.svgz): complete,
  losslessly gzip-compressed editable SVG symbol collection, keyed by
  Unicode-derived IDs; **not** an installable SVG-font format
- `build/family/bitmaps/*-16.*`, `*-18.*`, `*-24.*`, `*-32.*`: 1-bit PNG atlases, JSON metrics and
  genuine row-packed binary `.sjpb` files for each style
- `build/family/specimen/index.html`: offline specimen with inventory search,
  style selector and live variable-weight/slant controls; unzip beside fonts
- `build/family/specimen/*.png`: style, dense/close-form Kanji, original
  pictogram and variable-endpoint proof sheets
- `build/family/coverage.json`, `glyph-provenance.json.gz`, `build-summary.json`:
  machine-readable identity coverage, provenance and build hashes

The new TTFs are expanded from original centerlines, **not enlarged pixels**.
They contain polygons around those paths; TrueType does not install open
zero-width pen paths. Paths remain angular wherever the original design is
angular. Overlapping strokes use consistent clockwise winding and the
TrueType overlap flag. The SVG preserves the actual open centerline geometry
for a plotter or subsequent design refinement.

### Editable centerline SVG

Git tracks `centerlines.svgz` because the complete uncompressed SVG exceeds the
publication connector's request limit. No glyph, path, coordinate or metadata
is removed. The generator writes both `centerlines.svg` and deterministic
`centerlines.svgz` (gzip level 9, no embedded filename, timestamp zero).
The raw SVG remains a local editing output. Source ZIPs produced by
`family/tools/package_family.py` include both versions, even from a clean
clone that has only the SVGZ. If both exist, packaging rejects a mismatch.

Extract the editable file without rebuilding any fonts:

```sh
python3 -c "import gzip,pathlib; p=pathlib.Path('build/family/centerlines.svgz'); p.with_suffix('.svg').write_bytes(gzip.decompress(p.read_bytes()))"
```

Full artifact verification reads the tracked SVGZ directly and checks every
symbol identity. When raw SVG is present, it also checks byte/hash equality.
`build-summary.json` retains the prior source hashes for packaging-only source
changes in `packaging_refresh.previous_source_hashes`; current hashes remain
in `source_hashes`. The packaging refresh does not rebuild fonts or alter the
scope/date of earlier test reports. Its separate checks and artifact hashes
are recorded in `build/family/reports/centerlines-packaging.json`.

Negative circled numerals use genuinely filled discs and unioned counter-wound
cutouts, so crossing numeral strokes cannot cancel into black specks. Their
cutout weight is intentionally fixed while variable slant still applies. The
SVG uses masks for those cutouts; binary rasterization uses white foreground
and black cutout strokes. This is explicit drawing behavior, not a substitution
of hollow circles for negative characters.

## Character handling

- Supplementary-plane Kanji and pictograms use `cmap` format 12
- Raw compatibility scalars are retained; no NFC/NFKC folding of Kanji input
- Registered standardized CJK variation sequences use `cmap` format 14
- JIS's 25 multiscalar character identities remain sequences; available forms
  have explicit GSUB `ccmp` glyphs and longest-match binary lookup
- `sups` / `subs` features provide alternate ASCII letters/digits/operators and
  Greek glyphs in normal fonts, in addition to Unicode small-number characters
- Common combining accents have composition glyphs and mark attachment;
  this is not a complete general-purpose IPA/math layout engine
- Math has an explicit supported inventory. Presence of common operators is
  not a claim of all 2,384 Unicode Math-property characters, stretchy operators
  or an OpenType MATH table
- Upright box-drawing glyphs use edge-to-edge cell geometry, rather than
  ordinary text sidebearings; scaled/slanted standalone styles still need
  application-level line-spacing checks
- 64 original retro-mobile pictograms use **new** U+E000–U+E03F mappings with
  explicit semantic Unicode aliases. No DoCoMo artwork was copied, and the
  private mapping is not carrier-compatible. See `family/SYMBOLS_AND_PICTOGRAMS.md`

## Rebuild and test

Python 3.12 was used. From an unpacked source tree:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-family.txt
.venv/bin/python build_family.py
.venv/bin/python -m family.specimen
.venv/bin/python verify_family.py
.venv/bin/python verify.py
.venv/bin/python verify_ttf.py
```

Sources and character identities are bundled, so generation requires no
network. Installing the pinned Python dependencies is the only network step
in a fresh environment. The family builder never regenerates legacy assets.
`--without-kanji-expansion`, `--styles`, `--bitmap-sizes`, `--no-variable` are
development controls; partial builds are explicitly marked and are not a
complete distribution. Fixed font timestamps, ordered character inventories
and deterministic gzip metadata support reproducible binaries.

The test suite checks identity manifests independently, cmap/variation tables,
shaping, nonblank geometry, master topology, real interpolation, small-number
features, 1-bit pack/atlas equivalence, malformed inputs and legacy hashes.
Tests and representative visual sheets do not replace per-glyph proofreading,
OS installation tests or Japanese typographic review. The report distinguishes
passed, failed and unrun checks; missing fonts or skipped artifact checks do
not count as a successful release audit.

## SJPB v1 binary font format

All integers are little-endian. The 32-byte header is `<4sHHIIIIII>`:
magic `SJPB`, version 1, flags 0, entry count, nominal pixels, index offset,
UTF-8 key table offset, pixel table offset, baseline in pixels.

Each 28-byte index entry is `<IIHHhhhHII>`: key offset relative to the key
table, key byte length, bitmap width/height, advance, horizontal bearing,
vertical bearing, flags 0, bitmap offset relative to the pixel table, bitmap
byte length. Each row uses `ceil(width/8)` bytes, most-significant bit first,
with zero padding. 1 is foreground. UTF-8 keys can contain several scalars.
Bitmap bounds and bearing_y retain descenders and crop guards; nominal pixel size is not a clipping rectangle. The header baseline and JSON line_height align glyphs with different bitmap heights. The SJPB v1 byte layout is unchanged.
The Singleline strike uses direct 1-pixel centerlines. Other fixed strikes use
4× coverage sampling followed by a 32/255 coverage threshold. All emit only
0/255. Sparse and dense shapes can
still alias or collide at small sizes.

```python
from family.bitmap_reader import BitmapFont
font = BitmapFont('build/family/bitmaps/singleline-24.sjpb')
pixels = font.mask('日本語 髙𠮷')  # bool ndarray; missing identity raises KeyError
```

## Provenance and redistribution

Code and project-authored coordinates retain the upstream AGPL v3 license.
Historical project component geometry was recovered from the original
project's pinned history; it is not a newly imported third-party font.
CJKVI-IDS supplies structure only and retains its GPL v2 notices. The upstream
project's mixed notices are preserved; this work does not relicense them or
assert a new unrestricted/OFL font grant. Unicode character data carries its
own bundled Unicode license. Review these notices before redistribution or
embedding. Publication status is recorded in docs/UPDATE-16-32.md. No merge, pull request, deployment or remote installation is implied.
