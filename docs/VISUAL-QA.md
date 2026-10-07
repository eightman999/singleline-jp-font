# Independent Japanese glyph visual QA

Date: 2026-10-06 UTC

## Assessment

**Experimental only. Numeric repertoire completion is not a certification of Japanese glyph correctness or small-size legibility.**

Final result: 190 unique glyphs were independently viewed. Seven concrete structural-finding groups were corrected and independently rechecked. All 190 latest-inspected geometry hashes match the frozen source. The three inherited identical-shape pairs remain unresolved, and dense 18/24 px legibility remains a real limitation. No glyph is promoted to typographically approved by this report.

The historical findings below preserve what was observed before correction. Read the correction status summaries alongside them; the baseline PNGs intentionally still show the defects.

## What was actually inspected

- 184 unique glyphs in 15 pixel-viewed contact sheets
- All 82 glyphs initially carrying `non_japanese_ids_variant`
- 30 deterministic overlay samples; 20 enclosure samples; 20 deep-composition samples
- 37 identity, compatibility, surname-extra and density checks; groups overlap
- Fresh subset fonts built from the inspected project geometry: Singleline 72 px; Gothic 18 and 24 px; PC98-inspired Mincho 24 px
- Small samples enlarged 3× with nearest-neighbour scaling solely for inspection

The baseline group membership, exact codepoints, geometry hashes, source-file hashes and original-only proof hashes are recorded in [`visual-qa.json`](../build/family/reports/visual-qa.json). Every listed glyph was actually viewed. “No additional issue recorded” means only that this screening recorded no additional finding; it is not a pass or a claim of expert proofreading.

The normal `load_glyphs` entry point briefly failed during unrelated concurrent symbol work. The audit therefore directly used `build_kanji(targets() | set("髙𠮷"))` plus the untouched canonical glyph dictionary, yielding the same kanji centreline geometry without editing a glyph or a builder.

## Findings

### VQA-001: Malformed 戶 enclosure and regional selection (high)

Characters: 戾棙淚錑 — U+623E, U+68D9, U+6DDA, U+9311

Initial 戾 uses ⿸户犬[G]. The detached dot and low 尸 body do not form the broad Japanese 戶 enclosure seen in the identity reference. 犬 overprints the displaced enclosure. The same defect is inherited by the three compounds. Visible already at 72 px; worsening at 18/24 px.

Recommended action: Author a Japanese-form 戾 with a coherent roof and left body, place 犬 inside with clear gaps, and regenerate/recheck all dependants. Do not merely remove the provenance flag.

Original proof: [variant-02.png](../build/family/proofs/visual-qa/variant-02.png), [variant-03.png](../build/family/proofs/visual-qa/variant-03.png), [variant-05.png](../build/family/proofs/visual-qa/variant-05.png)

### VQA-002: 魃 enclosure collision (high)

Characters: 魃 — U+9B43

The broad 鬼 head/body overlaps the 犮 component, creating crossings and a compressed pile rather than distinct, readable left and right forms. Visible at 72 px and unreadable in the 18/24 px samples.

Recommended action: Use component-specific placement for 鬼 and 犮, retaining their identities and the intended lower-left enclosure, then recheck at all sizes.

Original proof: [overlay-02.png](../build/family/proofs/visual-qa/overlay-02.png)

### VQA-003: 巾/入 overlay loses the enclosure (high)

Characters: 輛㒼 — U+8F1B, U+34BC

In 輛, the right-side 兩 appears as an isolated top horizontal followed by a small crossed lower cluster: the enclosing 冂 and two internal 入 are not clearly readable. 㒼 has the related generic 巾/入入 overlay problem. This is a rendered topology problem, not a claim that the source list lacks those paths.

Recommended action: Create component-specific 兩/㒼 geometry with a clear outer enclosure and balanced internal 入; test both independent glyphs and compounds.

Original proof: [overlay-01.png](../build/family/proofs/visual-qa/overlay-01.png), [overlay-02.png](../build/family/proofs/visual-qa/overlay-02.png)

### VQA-004: 鬮 enclosure overprint (high)

Characters: 鬮 — U+9B2E

The 鬥 enclosure and internal 龜 occupy overlapping regions. The centre and lower half become a knot even at 72 px, and a dark block at 18/24 px.

Recommended action: Replace generic enclosure placement with hand-balanced 鬥 margins and a separately spaced interior; recheck density in all intended styles.

Original proof: [enclosure-02.png](../build/family/proofs/visual-qa/enclosure-02.png)

### VQA-005: Deep compounds collapse essential structure (high)

Characters: 籤爨 — U+7C64, U+7228

籤 has a severely compressed and crossing lower 韱; 爨 compresses its upper components into overlapping rails and its lower components into crowded horizontal bands. Structure is difficult to recover even at 72 px.

Recommended action: Author bespoke proportions for these dense full glyphs. Uniform recursive boxes are insufficient; do not mark their repertoire entries approved after a numeric coverage check.

Original proof: [enclosure-01.png](../build/family/proofs/visual-qa/enclosure-01.png), [deep-01.png](../build/family/proofs/visual-qa/deep-01.png)

### VQA-006: 歷 interior collapses (high)

Characters: 癧藶 — U+7667, U+85F6

In 癧 and 藶 the inner 歷 is compressed into the lower-right of the enclosing form. The lower 止 is not independently legible and merges with the 禾 pair, including at 72 px. The paths may exist, but the semantic structure is lost in the rendering.

Recommended action: Give 歷 a component-specific design with distinct 厂, 秝 and 止 zones, then recheck these descendants.

Original proof: [deep-01.png](../build/family/proofs/visual-qa/deep-01.png)

### VQA-007: Dense forms close counters at small sizes (medium)

Characters: 櫜藁麤欟纖鑯 — U+6ADC, U+85C1, U+9EA4, U+6B1F, U+7E96, U+946F

櫜 and 藁 form dark horizontal bars in their upper/middle blocks; 麤 and 欟 have dense merged detail; the right component of 纖 and 鑯 darkens markedly. Gothic 18 px is most affected, and several closed regions persist at 24 px. This is a legibility assessment, not a measured reading-accuracy study.

Recommended action: Introduce size-appropriate spacing and stroke simplification/weight control. Recheck actual bitmap exports separately; these sheets use FreeType-rendered outlines.

Original proof: [variant-03.png](../build/family/proofs/visual-qa/variant-03.png), [variant-05.png](../build/family/proofs/visual-qa/variant-05.png), [identity-02.png](../build/family/proofs/visual-qa/identity-02.png), [deep-01.png](../build/family/proofs/visual-qa/deep-01.png), [enclosure-01.png](../build/family/proofs/visual-qa/enclosure-01.png)

### VQA-008: Inherited glyph distinctions are conflated (high)

Characters: 剝剥塡填頬頰 — U+525D, U+5265, U+5861, U+586B, U+982C, U+9830

剝/剥, 塡/填 and 頬/頰 use identical inherited centreline geometry. The proof sheets confirm that the Japanese-form distinctions visible in the reference are not retained. This predates expansion and is already documented by the coverage report. A same-anchor Gothic raster comparison also confirms zero differing pixels at both 18 and 24 px for each of these three pairs.

Recommended action: Keep the aliases explicitly disclosed. If distinct Japanese encoded forms are required, author separate originals and rerun canonical-regression tests under an explicitly revised design policy.

Original proof: [identity-01.png](../build/family/proofs/visual-qa/identity-01.png), [identity-02.png](../build/family/proofs/visual-qa/identity-02.png)

### VQA-009: 己/已/巳 distinction is delicate at 18 px (medium)

Characters: 己已巳 — U+5DF1, U+5DF2, U+5DF3

The opening/vertical-height distinctions exist at 72 px and are visible under pixel enlargement, but 己 versus 已 has a small gap/height difference at 18 px. The sample does not justify claiming robust text-size recognition.

Recommended action: Retain the topology, but tune small-size spacing and check the actual target rendering platforms and bitmap outputs.

Original proof: [identity-01.png](../build/family/proofs/visual-qa/identity-01.png)

## Positive observations and boundaries

- 未/末 and 土/士 retain visible stroke-length distinctions in the inspected sizes.
- 高/髙 and 吉/𠮷 retain distinct original shapes in the sample.
- 斉/斎 and 齊/齋 are distinct source shapes, though density and interior balance still require refinement.
- Compatibility and supplementary samples render as glyphs rather than tofu; this is not blanket Japanese variant certification.

Other styles, variable instances, platform-specific shaping/rendering and actual bitmap-export pixels were not visually audited here. The 18/24-pixel views are outline-font rasterizations, not the exported bitmap font proof. No reader recognition study was performed.

## Reference discipline

Character identity was compared visually against the installed Noto Sans CJK Regular TTC Japanese face (index 0). Only viewing was used: no external outlines or coordinates were imported, traced, or copied into the project. Reference-containing working sheets remain outside the deliverable. All distributed QA PNGs contain project-original font renders plus Latin labels only. A reference font is a cross-check, not an official per-character JIS certification.

## Exact inspected baseline groups

### variant (82)

㖨㥯㸅㺔䀹䐜佾僙冩凊咎嘷囓婬媺嬾寫寬懶戾挈晷柒栾梥棃棙椶槀槩槪橐檃櫜櫽沭洯洴淚澘瀉瀨焈猹獺瑢疰瘛癩癮皶禰穩穵籘籟縢翺肤胅胊臗舄葼蓱蔾薩藁藾蘤蟥讔賴輒酳錑隱髖魲魶鱜齧

U+35A8, U+396F, U+3E05, U+3E94, U+4039, U+441C, U+4F7E, U+50D9, U+51A9, U+51CA, U+548E, U+5637, U+56D3, U+5A6C, U+5ABA, U+5B3E, U+5BEB, U+5BEC, U+61F6, U+623E, U+6308, U+6677, U+67D2, U+683E, U+68A5, U+68C3, U+68D9, U+6936, U+69C0, U+69E9, U+69EA, U+6A50, U+6A83, U+6ADC, U+6AFD, U+6CAD, U+6D2F, U+6D34, U+6DDA, U+6F98, U+7009, U+7028, U+7108, U+7339, U+737A, U+7462, U+75B0, U+761B, U+7669, U+766E, U+76B6, U+79B0, U+7A69, U+7A75, U+7C58, U+7C5F, U+7E22, U+7FFA, U+80A4, U+80C5, U+80CA, U+81D7, U+8204, U+847C, U+84F1, U+853E, U+85A9, U+85C1, U+85FE, U+8624, U+87E5, U+8B94, U+8CF4, U+8F12, U+9173, U+9311, U+96B1, U+9AD6, U+9B72, U+9B76, U+9C5C, U+9F67

### overlay (30)

㒼仭函匁嘷墻尹彈憗斄柹欞涿熯癉磾笋臿芻葱蛦覡豔輛鈸靱魃麨黻𨐌

U+34BC, U+4EED, U+51FD, U+5301, U+5637, U+58BB, U+5C39, U+5F48, U+6197, U+6584, U+67F9, U+6B1E, U+6DBF, U+71AF, U+7649, U+78FE, U+7B0B, U+81FF, U+82BB, U+8471, U+86E6, U+89A1, U+8C54, U+8F1B, U+9238, U+9771, U+9B43, U+9EA8, U+9EFB, U+2840C

### enclosure (20)

㕞咫幗廳暍爛爨瘤籤總纖觸逶釄鑯闖鬮鹽鼷𪎌

U+355E, U+54AB, U+5E57, U+5EF3, U+668D, U+721B, U+7228, U+7624, U+7C64, U+7E3D, U+7E96, U+89F8, U+9036, U+91C4, U+946F, U+95D6, U+9B2E, U+9E7D, U+9F37, U+2A38C

### deep (20)

㯍增憖楹欟濕灩爨癧籤繒藶豔蹣鑯鑿钁靨麬𩩲

U+3BCD, U+589E, U+6196, U+6979, U+6B1F, U+6FD5, U+7069, U+7228, U+7667, U+7C64, U+7E52, U+85F6, U+8C54, U+8E63, U+946F, U+947F, U+9481, U+9768, U+9EAC, U+29A72

### identity (37)

未末土士己已巳斉斎齊齋剝剥塡填頬頰高髙吉𠮷辻葛榊麤欄﨏祥都喝慨海祉穀者謹頻

U+672A, U+672B, U+571F, U+58EB, U+5DF1, U+5DF2, U+5DF3, U+6589, U+658E, U+9F4A, U+9F4B, U+525D, U+5265, U+5861, U+586B, U+982C, U+9830, U+9AD8, U+9AD9, U+5409, U+20BB7, U+8FBB, U+845B, U+698A, U+9EA4, U+F91D, U+FA0F, U+FA1A, U+FA26, U+FA36, U+FA3E, U+FA45, U+FA4D, U+FA54, U+FA5B, U+FA63, U+FA6A

## Correction rechecks

The baseline proofs above intentionally preserve the original defects. Corrected source hashes and independently recompiled sample hashes are recorded separately in the JSON report.

### Recheck 01

Original-only proof: [recheck-01-01.png](../build/family/proofs/visual-qa/recheck-01-01.png)

- VQA-001: the initial 戾/棙/淚/錑 enclosure/regional-form defect is structurally resolved
- VQA-002: the initial 魃 component-placement defect is structurally resolved
- VQA-003: 輛 is structurally repaired; the separately sampled 㒼 remains open
- Related 兩/倆/裲 were additionally inspected; the clear enclosures are improved, with density still evident at small sizes
- New high-severity VQA-010: 魎 U+9B4E is still severely overprinted by generic ⿺鬼兩 placement. Repairing 兩 alone did not fix this compound
- 188 unique glyphs have now been visually inspected including the four additional forms in this recheck

These are findings about the specific initial defects. They do not promote the corrected glyphs or the rest of the font to approved Japanese typography. Subsequent bounded correction rechecks are recorded below.

### Recheck 02

Original-only proof: [recheck-02-01.png](../build/family/proofs/visual-qa/recheck-02-01.png)

The 魎 enclosure collision is structurally resolved. 歷, 癧 and 藶 now have distinct lower 止 bands and separate 禾 pairs, resolving VQA-006. Checked fresh-font pixels at the same 72/18/24 sizes; small-size density still limits the general quality verdict.

Characters: 魎歷癧藶 — U+9B4E, U+6B77, U+7667, U+85F6

189 unique glyphs have now been inspected.

### Recheck 03

Original-only proof: [recheck-03-01.png](../build/family/proofs/visual-qa/recheck-03-01.png)

The initial severe collision/placement failures in 鬮, 籤, 爨 and 㒼 are structurally resolved. Updated 滿 and 蹣 also have clear enclosures. Dense internal details in 鬮/籤/爨 still merge in places at 18 and 24 px; these remain draft drawings, not typographic approvals.

Characters: 鬮籤爨㒼滿蹣 — U+9B2E, U+7C64, U+7228, U+34BC, U+6EFF, U+8E63

190 unique glyphs have now been inspected.

## Final status

- Structurally resolved after independent fresh-font rechecks: VQA-001 through VQA-006, and VQA-010
- Still open: VQA-007 dense small-size rendering, VQA-008 inherited identical-shape pairs, VQA-009 delicate 己/已 distinction
- Corrected 鬮/籤/爨 still show merged fine detail at18/24px; their improved large-size structure does not imply robust small-size reading
- All190 latest-inspected glyph geometry hashes matched frozen current source at final reconciliation; no stale inspected entries remained
- 18 independent original-only proof PNGs are hashed in the machine-readable report; no reference-font image is distributed by this audit

Recommended next gate: keep the release experimental, prioritize remaining small-size spacing and inherited encoded-form distinctions, and arrange systematic Japanese typographer/reader review of the rest of the repertoire. All82 initial non-Japanese-IDS candidates were screened, but this does not validate every Japanese regional/JIS form. Changes after the recorded hashes require another recheck.

### Changed descendants outside correction recheck

The eleven bespoke/component repairs changed28 target glyphs. Nineteen changed forms were independently rechecked in this audit; these nine propagated descendants were not: 壢懣櫪瀝瞞礰蟎轣靂 (U+58E2, U+61E3, U+6AEA, U+701D, U+779E, U+7930, U+87CE, U+8F63, U+9742). Their updated geometry must not be called visually approved on the strength of component repair or automated coverage checks. The before/after hashes for all28 are in `family/data/kanji-review-corrections.json`.
