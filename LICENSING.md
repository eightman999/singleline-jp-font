# Singleline JP — versioned licensing policy
Copyright (c) 2026 eightman999.

This policy applies to works for which eightman999 is the copyright holder. A file extension, repository location, or the mere use of a build script **does not** determine the license of its contents. Where rights are held by others, their licenses are unchanged. See [NOTICE.md](NOTICE.md).

## License selection and scope

| Material | License / grant | Exact scope |
| --- | --- | --- |
| Original program source (generators, runtime, tooling and tests) | **GPL-2.0-only OR AGPL-3.0-only** | Choose either license for author-owned code. [LICENSE-GPL-2.0.txt](LICENSE-GPL-2.0.txt) / [LICENSE](LICENSE) |
| **V1.0.0 original font assets** | **Apache-2.0**, offered as an additional license | The author-owned TTF, bitmap atlases and bitmap metrics/JSON contained in the GitHub `v1.0.0` font release, and byte-identical compatibility copies. [LICENSE-APACHE-2.0.txt](LICENSE-APACHE-2.0.txt) and [V1-APACHE-GRANT.md](V1-APACHE-GRANT.md) |
| **Newly issued V2 and later original font assets** | **Singleline JP Font Commercial License** (proprietary) | Only versions **expressly designated and newly issued** by the rightsholder under [FONT-LICENSE-V2PLUS.md](FONT-LICENSE-V2PLUS.md). Commercial use, modification and integrated game/app/website/webfont use are permitted; **standalone font redistribution is prohibited**. Covers fonts, bitmaps, SVG centerlines and new V2+ authored glyph artwork in that distribution. |
| V1 geometry embedded as authored data in a Python file | **Apache-2.0** grant for the V1 geometry; program portions under the program license | License scope is by copyrightable material, not indiscriminately every byte of a mixed Python file. |
| Third-party source datasets, their copies and notices | Their upstream license; **not relicensed** | CJKVI-IDS / CHISE structural records (GPL v2-related terms), Unicode metadata (Unicode License v3), and any other third-party material. [NOTICE.md](NOTICE.md) |

### GPL-2.0-only OR AGPL-3.0-only

For program portions copyrighted solely by eightman999, you may comply with **either** GNU GPL version 2 **only**, or GNU Affero GPL version 3 **only** (SPDX expression: `GPL-2.0-only OR AGPL-3.0-only`). This is a dual-license **choice**, not a request to combine the two licenses. It does not relicense any third-party code or data. Keep applicable copyright and license notices.

### Version boundary and previously obtained copies

- `v1.0.0` original font assets receive an **additional** Apache-2.0 license grant from the copyright holder. The license rights of earlier recipients are not withdrawn.
- **Proprietary V2+ is prospective.** Adding this policy to the repository does **not** retroactively cancel AGPL/GPL notices or permissions accompanying already-published V2 experimental binaries, archives or other copies.
- The repository currently contains V2 laboratory binaries and font metadata created under the older notice policy. Those are **historical artifacts**; changing the policy document does not change their embedded licenses or automatically create a new commercial release.
- A commercial V2+ distribution must be freshly built, explicitly identified as such, checked for third-party content, and shipped with the corresponding proprietary license. It must not be described as already released merely because this policy exists.
- For a new V3, do not commit proprietary font binaries or newly authored proprietary glyph artwork to the public repository by accident. The dual-licensed code may remain public.

### Commercial V2+ use boundary

The commercial font license permits commercial output, original-content apps and games that include usable font binaries, websites serving webfonts, and private font modifications or format conversions. It bans **standalone redistribution as a font product**, including renamed/converted copies and sham bundles whose real purpose is distributing a reusable font. Webfont delivery and extractable resources inside genuine apps/games are not, by themselves, violations. See [FONT-LICENSE-V2PLUS.md](FONT-LICENSE-V2PLUS.md) Sections 2–4.

These restrictions apply **only** to new V2+ distributions actually issued under that proprietary license: they do not restrict Apache-2.0 V1 assets or previously obtained copies of historic versions.

### Generated outputs and upstream inputs

Using GPL-licensed **program code** to generate an output does not, by itself, make the output GPL-licensed. However, copyrighted **input data/artwork** can carry separate obligations into an output if protected expression is reproduced or adapted. The project uses authored centerline geometry and CJKVI/CHISE character-structure information without importing third-party font outlines. That technical observation alone is **not a legal certification** that every downstream artifact is free of third-party rights. Audit each intended commercial distribution against [NOTICE.md](NOTICE.md).

### Distribution checklist

1. Identify whether the product is the original `v1.0.0` font asset, an existing historic V2 experimental copy, or a **newly issued** V2+/V3 commercial artifact.
2. Separate standalone third-party inputs and notices from author-owned font files; do not put CJKVI or Unicode datasets under the proprietary EULA.
3. Verify required notices and any applicable source-sharing obligations for **distributed program code and datasets**.
4. Regenerate and test installable fonts, check their embedded license metadata and sha256, and complete the platform/visual quality gates before a formal release.
5. Review the retail EULA terms and store listing; no paid BOOTH release has been made by this policy-only change.

For provenance and precise upstream revisions, see [NOTICE.md](NOTICE.md). This is an authored licensing statement, not a substitute for a legal review of any third-party data dependencies.
