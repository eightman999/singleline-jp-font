# Provenance, historic notices, and upstream licenses

## Ownership and versioned policy

The copyright holder states that the original Singleline JP glyph geometry and original code are owned by **eightman999**. The source code is newly offered under **GPL-2.0-only OR AGPL-3.0-only**; original V1.0.0 font assets have an additional **Apache-2.0** grant; and only **newly issued, explicitly designated** V2+ font products use the proposed proprietary font license.

**The authoritative new scope matrix is [LICENSING.md](LICENSING.md).** This NOTICE records provenance and obligations for independent inputs, not a blanket declaration that every generated font is GPL-licensed.

Previously distributed artifacts (including public V2 laboratory binaries and files with older embedded notices) retain rights granted with those copies. The published V1 archive/tag is historical and immutable; a new license grant is additive.

## Origin of original assets

The font source was extracted from https://github.com/Takemura-hackathon-2026/hackathon-2026 at commit `04fe462d816c025f5c911efa0cea79fced2eeb3e`. Original authored code and original glyph coordinates were historically distributed with GNU AGPL v3 notices. The current rightsholder offers an additional choice for **their own code and V1 original font artwork**, without retracting historical grants.

Original centerline coordinates are project-authored. V2 new glyphs are built using independently designed project stroke paths and algorithmic layouts; **no third-party font glyph outlines, bitmaps, or stroke coordinates are imported**. No ChocoKanji, KanjiVG, Hershey, PC-98 ROM or carrier emoji artwork is incorporated as glyph outlines.

## Third-party source data (not relicensed)

| Data | Location / provenance | License or notice |
| --- | --- | --- |
| CJKVI-IDS / CHISE character decomposition structure (not outlines) | `family/data/ids-trees.json`, `assets/fonts/source/joyo-compositions-source.json`; pinned CJKVI revision `86b4d16159f0079437870408f0ca186e529015db` | Upstream **GPL v2-related terms**, with `assets/fonts/source/CJKVI-IDS-README.md` and `CJKVI-IDS-COPYING.txt`. Preserve for copies/derivatives of those datasets. |
| Unicode identity, property, variation and repertoire data | `family/data/unicode-jinmeiyo.json`, `jis-compatibility-svs.json`, `sources-lock.json` | **Unicode License v3**, `family/data/UNICODE-LICENSE.txt`, © 1991–2026 Unicode, Inc. |
| Official Jōyō index | https://www.bunka.go.jp/seisaku/kokugo_nihongo/kokugo_shisaku/joyokanjihyo_sakuin/index.html | Official repertoire reference; not third-party glyph artwork. |

The CJKVI README distinguishes `ids.txt` (CHISE-derived) from other source files and their upstream terms. This repository contains the source notices to preserve provenance. **Using character structure alone does not establish that a separately authored TTF reproduces upstream copyrighted glyph artwork.** Conversely, the absence of imported outlines does not automatically resolve every possible dependency claim. Review the particular data and output.

## File/artifact boundary

| Material | Policy |
| --- | --- |
| Original generator/runtime program code, tests and scripts | Dual license **GPL-2.0-only OR AGPL-3.0-only**, copyright holder's portions only. Original older AGPL grants remain valid. |
| Original V1.0.0 `fonts/*.ttf`, `assets/fonts/custom-*.png/json` and identical legacy copies | Additional **Apache-2.0** license grant under `V1-APACHE-GRANT.md`. Previous rights remain intact. |
| New V2+ TTF, bitmap output and original new centerline artwork, if expressly issued as commercial | Proposed independent retail license `FONT-LICENSE-V2PLUS.md`. **Not retroactive to historical published files.** |
| Mixed source ZIPs containing CJKVI/Unicode datasets and authored artwork | Each copyrightable component keeps its own terms. A single broad font license must not be applied to all inputs. |
| Archived V2 RC artifacts built with old embedded AGPL/GPL text | Historic grants and actual embedded notices must be honored. Metadata is changed only for a newly generated and checked release. |

The font `fsType=0` OS/2 technical field is **not** a copyright license. The fact that a program is GPL-licensed does not automatically make its generated outputs GPL-licensed; any copyrightable material reproduced from third-party inputs requires separate review.

## Before publishing a new commercial archive

- Check commercial output against `family/data/KANJI-SOURCES.md`, the pinned dataset revisions, and project glyph provenance.
- Exclude third-party raw input datasets from any font-only package unless separately licensed and accompanied by their notices.
- Make TTF name/license tables, version, package documentation and legal terms agree.
- Complete technical and visual release gates: a machine test pass alone does not certify every Japanese glyph.

See [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md) and [FONT-LICENSE-V2PLUS.md](FONT-LICENSE-V2PLUS.md).
