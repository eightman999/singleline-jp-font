# Kanji centerline sources and limits

The canonical 2,141 kanji in `glyphs/kanji.py` are retained byte-for-byte in their
existing source. That set includes 2,136 Jōyō kanji and five additional existing
forms (剥, 填, 栢, 頬, 𠮟); do not describe the 2,141 figure as the official Jōyō count.

`legacy-components.json` snapshots 515 additional, project-authored components
from this repository's `17d6ad0` revision. The source code was originally extracted
from Takemura-hackathon-2026/hackathon-2026; see the root `NOTICE.md` and `LICENSE`
for the existing AGPL-3.0 terms. No external glyph outlines were imported.

`ids-trees.json` contains 10,361 transitive character-structure records selected
from CJKVI-IDS revision `86b4d16159f0079437870408f0ca186e529015db`. This is structure
only: Unicode character relationships, with no stroke positions, curves,
bitmaps, font outlines or font-derived coordinates. Its GPL-2.0 notice and license
remain in `assets/fonts/source/CJKVI-IDS-README.md` and `CJKVI-IDS-COPYING.txt`.
The combination is **not** represented as OFL or unrestricted font licensing.
The pinned URL, content hashes and original source file names are recorded in
`kanji-sources.json`.

New centerline sketches are in `family/kanji_components.py` and
`family/kanji_rare_components.py` and `family/kanji_variant_components.py`. Coordinates were independently authored for
this project. All new glyphs are *design drafts*, even when their structure can
be composed completely. Automatic IDS enclosures and overlays are specifically
flagged; the renderer does not certify Japanese text quality. Existing canonical
glyphs are inherited as-is, not newly declared visually verified.

Unknown numbered IDS placeholders, undefined components, cycles, blank geometry
and repeated new glyph shapes are excluded from claimed coverage. There is no
normalization fallback: compatibility ideographs retain their original scalar.
Textual structural research and identity-only checks are documented in
`kanji-structure-notes.json`; reference outlines/pixels were never imported or
traced. The requested extra surname forms 髙 and 𠮷 have separately authored geometry.

## Reproduction

From the repository root, with a local copy of the pinned structure-only
CJKVI repository and the supplied JIS manifest:

```
python family/tools/import_kanji_sources.py \
  --ids /path/to/cjkvi-ids/ids.txt \
  --targets /path/to/jisx0213-2004.json
python -m unittest family.tests.test_kanji -v
```

Rebuilding the source snapshots needs the repository's first commit in local git
history. Building glyphs does not: it is fully offline using the committed JSON
snapshots and project-authored Python coordinate definitions.

The public `build_kanji(target_chars)` returns `(glyphs, character_report)`.
Every requested scalar has a report, including unsupported targets. A renderer
must not replace missing targets with a repeated kanji to make the count match.

## Final inventory audit

The current source draws all 10,050 JIS level 1–4 kanji, including all 864
jinmeiyo targets, plus two surname extras. Of the 10,050, 2,141 are inherited
canonical glyphs, 320 are component drafts and 7,589 are composition drafts.
No new repeated geometry or blank placeholder is included. This inventory pass
is not a claim of 10,050 visually approved Japanese designs. Three existing
equivalent groups remain inherited: 剝/剥, 塡/填, 頬/頰.

Re-run `python family/tools/audit_kanji.py` for the versioned counts and hashes
in `kanji-coverage-summary.json`, and full per-character provenance in the
build report directory.

## Bounded visual-QA corrections

`kanji_review_corrections.py` and `kanji_dense_corrections.py` independently
redraw eleven noncanonical structures after concrete overlap/placement errors
were identified: 戾魃兩歷癧藶魎㒼鬮籤爨. Shared-component fixes affect 28 targets.
The original 2,141 canonical glyphs remain unchanged. Before/after fingerprints
are in `kanji-review-corrections.json`; this sampled correction work does not
certify the unreviewed remainder of the repertoire.
