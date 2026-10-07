# Font repertoire and format reference, checked 2026-10-06

> Historical reference snapshot checked on 2026-10-06. Its proposed acceptance checklist is not evidence that every item was executed or passed. Current distribution status is in [DISTRIBUTION.md](DISTRIBUTION.md).

These are character-identity reference data, not third-party glyph outlines or designs. All files here were created outside the lead checkout.

## Reproducible coverage

Run `python generate_jis_manifest.py` with the downloaded, hashed Unicode 18.0.0 `Unihan.zip` beside it. The generator uses the CPython EUC-JIS-2004 codec and verifies all 6,356 `kJis0` mappings and all 3,695 `kJIS0213` mappings against Unicode's data. All checks passed. The first number includes an ideograph in the non-kanji region, so it must not be confused with the 6,355 level-1/2 kanji count.

- JIS X 0213:2004 levels 1/2/3/4: 2,965 / 3,390 / 1,259 / 2,436 kanji, total 10,050
- Including 1,183 non-kanji: 11,233 encoded sequences
- 25 sequences contain two Unicode scalars; 11,209 distinct scalars are used by the full repertoire
- 303 single-character JIS entries are outside the BMP
- Current jinmeiyo: 864; all are already inside those 10,050 JIS kanji
- 2026's new jinmeiyo is 勒 U+52D2, JIS 1-80-53, a level-2 character
- 57 jinmeiyo entries are compatibility ideographs; the reference SVS manifest aliases all 57, plus 18 other compatibility entries in the JIS set

The statutory name list is a repertoire authority, not an assertion that every person's legal name can be represented. Common surname variants 髙 U+9AD9 and 𠮷 U+20BB7 are outside this exact set. Add a separately named extra-name profile if needed.

### Codec trap

For plane 2, restrict rows to 1,3,4,5,8,12,13,14,15,78–94. CPython successfully decodes 6,067 additional JIS0212 fallback positions if every possible plane-2 byte pair is tried. Those do not belong in the JIS0213 manifest.

Plane-1 level 1 is rows16–46 plus row47 cells1–51; level2 is rows48–83 plus row84 cells1–6; level3 is the remaining assigned positions in rows14–94. Rows1–13 are classified as non-kanji; plane2 assigned entries are level4.

Preserve Unicode tuples as keys. Do not normalize the repertoire: even NFC folds 神 U+FA19 into 神 U+795E. Use Unicode's StandardizedVariants identities to add supported aliases with cmap14. IVS from the IVD are a separate opt-in set; advertising arbitrary IVS or every registered variant without distinct reviewed glyphs is misleading.

## Optional derivative profiles

The complete Unicode18 `Math` property yields 2,384 code points in `unicode-math-property.json`; category `Sm` alone has 1,005. These are computed from the pinned official data. A broad Math profile is an explicit product choice; mathematical alphabet symbols and holes represented in Letterlike Symbols must not be lost by selecting only the U+1D400 block. There are 997 assigned characters in that block in Unicode18.

`docomo-historical-unicode-mappings.json` records 244 historical DoCoMo round-trip Unicode identities from official EmojiSources.txt, including 11 keycap sequences. This is not a claim to implement every carrier glyph or a 176/252-item catalog, and it contains no carrier artwork. Historical keycaps omit FE0F; modern keycap forms need separate handling. Draw original single-line weather, transport, emotion, communication, food, etc. designs for a documented chosen set. Keep carrier mappings optional and do not imply NTT endorsement.

Define alphabet profiles explicitly (ASCII, selected Latin extensions, combining marks, Greek, etc.). OpenType style variations should leave ordinary text encoded normally; mathematical styled letters have distinct semantic Unicode identities. “Italian” should have a clearly stated design meaning if retained separately from “Italic.”

## Real format distinctions

- Scalable TTF/OTF is built from filled outlines; keep project-authored centerline SVG/JSON paths separately for genuine plotter/stroke use. Simply closing a centerline is not a usable stroked glyph
- The existing project's pixel-outline TTF is scalable pixel geometry, not smooth stroke-derived outlines
- BDF is a text bitmap format. For a requested binary bitmap deliverable provide documented packed 1-bit records, PCF, or EBDT+EBLC as applicable. PNG/JSON alone is an atlas interface, not an embedded bitmap font table
- EBDT+EBLC supports fixed ppem strikes; verify exact designed raster output. Such strikes do not supply continuous interpolation with font axes
- A TrueType variable font needs fvar, STAT and actual gvar data when outlines vary; HVAR/MVAR may be needed when metrics change. Compatible glyph topology across masters is essential. Separate families for structurally different styles are safer than pretending arbitrary styles interpolate
- Use cmap12 for supplementary characters; cmap14 (platform0, encoding5) for variation sequences. JIS combining sequences need shaping via GSUB/GPOS or a sequence-aware renderer; cmap14 cannot replace that
- Use `sups`/`subs` GSUB features and tested alternates for general superscript/subscript. Encoded U+207x/U+208x characters alone are not a complete alphabet
- A math-symbol font is not automatically a full mathematical layout font. Claim MATH typesetting only after implementing and testing MATH constants, italic corrections, accents and extensible constructions

## Acceptance tests

1. Pin source versions and hashes; compare exact sequence sets for each advertised profile, not only raw glyph counts
2. Test every cmap entry and shaping sequence for non-.notdef output; include compatibility forms, SVS, supplementary chars and all 25 JIS sequences
3. Explicitly reject placeholders, wrong radicals, duplicate-codepoint aliases used to conceal missing designs, and near-identical accidental designs. Review duplicate outline and bitmap fingerprints; legitimate equivalences need documented exceptions
4. Human-readable proof sheets for all glyphs, plus dense kanji and near-pairs 未末, 土士, 己已巳, 斉斎齊齋 and JIS2004 variants 辻葛祇祁
5. Render every bitmap strike at designed ppem and compare with source raster. Check row padding, offsets, endianness, advance widths, ascent/descent and clipping
6. Compile/reload/checksum binaries; render in FreeType and shape in HarfBuzz when available. Test variable default, named instances, extrema and intermediate coordinates, and ensure axes cause actual visual changes without point-order failures
7. Check sups/subs baselines, tracking, accents and full math examples. Record tested applications instead of promising universal install/runtime compatibility
8. Preserve the original repo's AGPL/GPL notices and source obligations. Do not silently relicense inherited glyph data as OFL. A catalog/name list licenses no third-party font outlines. New original glyphs should have provenance records

## Primary sources

- Unicode18 version and data: https://www.unicode.org/versions/Unicode18.0.0/ and https://www.unicode.org/Public/18.0.0/ucd/Unihan.zip
- Jinmeiyo property: https://www.unicode.org/reports/tr38/#kJinmeiyoKanji
- 2026 addition decision: https://www.unicode.org/L2/L2026/26151.htm (188-A80/188-A81)
- Japanese Ministry of Justice repertoire: https://www.moj.go.jp/MINJI/minji86.html (search-readable; direct fetch returned403)
- CPython codecs: https://docs.python.org/3/library/codecs.html
- SVS: https://www.unicode.org/Public/18.0.0/ucd/StandardizedVariants.txt
- IVD: https://www.unicode.org/ivd/ (latest dated 2026-08-03)
- Math property: https://www.unicode.org/Public/18.0.0/ucd/DerivedCoreProperties.txt
- Historical carrier identity mappings: https://www.unicode.org/Public/18.0.0/ucd/EmojiSources.txt
- Unicode data license: https://www.unicode.org/license.txt
- OpenType format: https://learn.microsoft.com/en-us/typography/opentype/spec/otff
- OpenType variations: https://learn.microsoft.com/en-us/typography/opentype/spec/otvaroverview
- cmap: https://learn.microsoft.com/en-us/typography/opentype/spec/cmap
- Bitmap tables: https://learn.microsoft.com/en-us/typography/opentype/spec/ebdt and https://learn.microsoft.com/en-us/typography/opentype/spec/eblc
- Script features: https://learn.microsoft.com/en-us/typography/opentype/spec/features_pt
- MATH: https://learn.microsoft.com/en-us/typography/opentype/spec/math
- BDF: https://www.adobe.com/devnet/font/
- Repo provenance: https://github.com/eightman999/singleline-jp-font/blob/main/NOTICE.md
