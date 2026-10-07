# Provenance and licenses

V2 distribution preparation, 2026-10-07: the mapping below documents existing
notices. It does not relicense any source or output, introduce a font-embedding
exception, or certify that a proposed redistribution satisfies all obligations.

Extracted from https://github.com/Takemura-hackathon-2026/hackathon-2026 at `04fe462d816c025f5c911efa0cea79fced2eeb3e` (host font files).
Original code and authored stroke coordinates retain the source repository's GNU AGPL v3 license (LICENSE). No relicensing is implied.

Character decomposition data: CJKVI-IDS / CHISE, GPL v2. The source attribution, pinned revision and license are in assets/fonts/source/CJKVI-IDS-README.md, CJKVI-IDS-COPYING.txt and joyo-compositions-source.json. The Japanese generated assets retain the source project's GPL v2 notice. These licenses are not an unrestricted or OFL font grant.

The centerline coordinates are project-authored; the CJKVI data supplies character structure only. No ChocoKanji, KanjiVG or Hershey outlines are included.
Official repertoire source: https://www.bunka.go.jp/seisaku/kokugo_nihongo/kokugo_shisaku/joyokanjihyo_sakuin/index.html

Categorization update: resolved final coordinates are now canonical in glyphs/. Identical paths are interned without changing geometry. The original composition data is retained for provenance, not executed at build time. TrueType outputs trace lit pixels as closed rectangles and preserve the respective asset notices.

The preceding pixel-tracing description applies to the legacy `fonts/*.ttf`.
The experimental Lab TTFs instead expand authored centerlines into filled
outlines. Their different construction does not remove inherited notices.

## Source-to-notice mapping

| Material | Repository location / evidence | Preserved notice |
| --- | --- | --- |
| Original program code and authored coordinates; subsequent project code and original centerline designs | root Python files, `glyphs/`, `family/*.py`, `family/tools/`, `family/data/legacy-components.json`; provenance in `family/data/KANJI-SOURCES.md` and `kanji-sources.json` | GNU AGPL v3, root `LICENSE`; upstream origin above |
| CJKVI-IDS / CHISE character structures, without imported outlines or stroke positions | `assets/fonts/source/joyo-compositions-source.json`, `family/data/ids-trees.json`; pinned revision `86b4d16159f0079437870408f0ca186e529015db` and hashes in `family/data/kanji-sources.json` | Existing GPL v2-related notices in `assets/fonts/source/CJKVI-IDS-README.md` and full `CJKVI-IDS-COPYING.txt`; keep upstream file-specific wording |
| Unicode character properties, names, variation mappings and identity data | `family/data/unicode-jinmeiyo.json`, `jis-compatibility-svs.json`, Unicode-derived fields in character manifests; inputs and hashes in `family/data/sources-lock.json` | Unicode License V3 in `family/data/UNICODE-LICENSE.txt`; © 1991–2026 Unicode, Inc. |
| Repertoire enumeration and project-authored metadata | `family/data/generate_jis_manifest.py`, `jisx0213-2004.json`, coverage/provenance reports | Retain project notice and applicable Unicode data notice; a character inventory is not a license to another font's outlines |

The CJKVI README distinguishes source files and CHISE derivation. The row above
preserves this repository's existing attribution rather than replacing it with
a new blanket interpretation. Consult the bundled original text for that scope.
No ChocoKanji, KanjiVG, Hershey, PC-98 ROM or carrier emoji artwork is imported.

## Artifact-to-source mapping

| Artifact | Inputs represented | Notices to retain with redistribution |
| --- | --- | --- |
| Legacy ASCII PNG/JSON and `fonts/SinglelineJPASCII*.ttf` | Authored ASCII/symbol coordinates and pixel rendering code | Project AGPL notice and source attribution |
| Legacy Japanese PNG/JSON and `fonts/SinglelineJPFull*.ttf` | Authored coordinates; preserved Japanese-asset provenance | Project AGPL notice plus inherited GPL v2 Japanese-asset/CJKVI notices |
| Lab static and variable TTFs | Authored centerlines and style code, IDS-structured Japanese composition drafts, Unicode identity/variation metadata | Project AGPL, inherited Japanese-asset/CJKVI notices, and Unicode data notice; root NOTICE plus the full referenced texts |
| Lab PNG/JSON/SJPB strikes, centerline SVG/SVGZ and sample proofs | The same Lab glyph sources and metadata in different representations | The same relevant source notices; image/binary conversion is not a new license grant |
| Lab coverage/provenance reports and HTML specimens | Project tooling and metadata; samples of the same glyphs; Unicode-derived identities | Project notice, applicable glyph/source notices and Unicode notice |

All four V2 package categories (static, variable, bitmap and source) carry these
notices and full license texts. Binary packages identify the matching source
package; retain that relationship when redistributing. Splitting ZIPs does not
change the source or notice obligations. Build dependencies listed in
`requirements-family.txt` retain their own licenses; naming or using those tools
does not imply that their code or font designs are bundled in the TTF outputs.

The font metadata's `fsType=0` is a technical embedding-permissions field, not
a replacement for the license notices or an additional unrestricted embedding
grant. This project does not describe the resulting mixed-source family as OFL,
public domain, or unrestricted. For a use needing a single permissive font
license, that condition has not been established here.
