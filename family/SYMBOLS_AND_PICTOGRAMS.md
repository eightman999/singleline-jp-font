# Original symbol and pictogram design

## Scope and provenance

All new centerlines were authored geometrically for this project on a 24-unit, y-down em. No external font outlines, glyph screenshots, bitmap sets or carrier emoji assets were used. Latin/Greek/Cyrillic homographs, accents, enclosures and small figures may reuse the original ASCII centerlines already in this repository. Unicode names are metadata only. The repository license and existing provenance notices continue to apply.

Neither module changes the canonical legacy glyphs. `family.symbols.GLYPHS` intentionally excludes characters already present in `glyphs/ascii.py` or `glyphs/symbols.py`; the central family loader should merge it additively.

## Symbol API

- `GLYPHS`: character → list of open or explicitly closed polyline paths
- `FILLED`: empty set; all new geometry is stroked, including rings and enclosures
- `CATEGORIES`: character → coverage category
- `NAMES`: character → Unicode name
- `REPERTOIRE`: supported additions, sorted by scalar value
- `SOURCE`: authoring, input and license metadata

### Exact authored coverage

Total: **700 additions**. This is explicit coverage, not a claim that every symbol block is complete.

| Category | Additions |
|---|---:|
| Cyrillic alphabets | 98 |
| Greek and Greek symbol variants | 56 |
| arrows | 23 |
| circled Latin | 52 |
| circled numbers | 21 |
| currency and typography | 35 |
| extended Latin | 185 |
| mathematical double-struck constants | 7 |
| mathematical operators and constants | 156 |
| subscripts | 32 |
| superscripts | 17 |
| vulgar fractions | 18 |

The Cyrillic set covers every scalar U+0400–U+045F plus U+0490/U+0491. Greek covers the 24 uppercase letters, 24 lowercase letters, final sigma, and seven common symbol variants. These are upright geometric forms; language-specific cursive alternates are not claimed. Latin support includes the decomposable one-mark letters of U+00C0–U+017F and explicit nondecomposable letters/ligatures such as Æ/æ, Œ/œ, Ð/ð, Þ/þ, Ł/ł, Ŋ/ŋ and ß.

Precomposed accents reserve space above or below the letter. Existing decompositions are not rewritten. The circled and super/subscript forms are explicit scalar glyphs; OpenType substitution behavior, combining-mark positioning, and the output styles belong to the central family pipeline. Mathematical blackboard-bold support is limited to ℂ ℍ ℕ ℙ ℚ ℝ ℤ.

### Enumerated mathematical additions

∀ ∁ ∂ ∃ ∅ ∆ ∇ ∈ ∋ ∏ ∐ ∑ ∓ ∔ ∕ ∖ ∗ ∘ ∙ √ ∝ ∟ ∠ ∡ ∢ ∣ ∥ ∧ ∨ ∩ ∪ ∫ ∬ ∭ ∮ ∯ ∰ ∴ ∵ ∶ ∷ ∼ ∽ ≃ ≅ ≈ ≊ ≋ ≍ ≐ ≑ ≒ ≓ ≔ ≕ ≖ ≗ ≙ ≜ ≟ ≡ ≤ ≥ ≪ ≫ ≲ ≳ ≶ ≷ ⊂ ⊃ ⊆ ⊇ ⊎ ⊏ ⊐ ⊑ ⊒ ⊓ ⊔ ⊕ ⊖ ⊗ ⊘ ⊙ ⊚ ⊛ ⊞ ⊟ ⊠ ⊡ ⊢ ⊣ ⊤ ⊥ ⊦ ⊧ ⊨ ⊩ ⊪ ⊫ ⊲ ⊳ ⊴ ⊵ ⋀ ⋁ ⋂ ⋃ ⋄ ⋅ ⋆ ⋈ ⋉ ⋊ ⋮ ⋯ ⋰ ⋱ ¬ ‰ ‱ ℓ ℘ ℏ ℧ ∄ ∉ ∌ ∤ ∦ ≁ ≄ ≇ ≉ ≢ ≮ ≯ ≰ ≱ ≴ ≵ ≸ ≹ ⊄ ⊅ ⊈ ⊉ ⊬ ⊭ ⊮ ⊯ ⊊ ⊋ ∛ ∜

Existing ± × ÷ − ∞ ≠ ≦ ≧ and the existing basic arrows are retained from the canonical project source and are not counted again.

## Original retro mobile pictograms

**These 64 designs are original.** They evoke the limited geometry of monochrome mobile displays but do not reproduce DoCoMo glyphs, logos or any carrier-specific mapping. The contiguous U+E000–U+E03F assignment is a new project-private mapping. A PUA code alone has no portable meaning outside a font using this mapping.

- `PUA_GLYPHS`: only the 64 project PUA characters
- `GLYPHS`: the 64 PUA entries plus 62 standard Unicode aliases (126 scalar entries)
- `ALIASES`: standard Unicode character → PUA character
- `NAME_TO_PUA`: stable descriptive English name → PUA character
- `PICTOGRAM_NAMES`: both PUA and alias character → descriptive English name
- `PICTOGRAM_LABELS_JA`: both PUA and alias character → Japanese label
- `PUA_REPERTOIRE` / `REPERTOIRE`: sorted PUA-only / all-character repertoires
- `FILLED`: empty; each design is a centerline drawing with outline contours
- `SOURCE`: design and mapping provenance

Unicode aliases describe the same object or concept; they do not promise color-emoji presentation, carrier compatibility, standardized variation-selector behavior or shape identity with any other font. Information, wireless-signal and leaf deliberately have no alias because a sufficiently exact simple scalar was not selected. Heart has both U+2661 and U+2764 semantic aliases.

| PUA | Name | Japanese label | Unicode aliases |
|---|---|---|---|
| U+E000 | sun | 晴れ・太陽 | ☀ U+2600 |
| U+E001 | cloud | 雲 | ☁ U+2601 |
| U+E002 | rain-cloud | 雨 | 🌧 U+1F327 |
| U+E003 | snowflake | 雪 | ❄ U+2744 |
| U+E004 | lightning | 雷 | ⚡ U+26A1 |
| U+E005 | umbrella | 傘 | ☂ U+2602 |
| U+E006 | crescent-moon | 月 | 🌙 U+1F319 |
| U+E007 | star | 星 | ⭐ U+2B50 |
| U+E008 | telephone-receiver | 受話器 | 📞 U+1F4DE |
| U+E009 | mobile-phone | 携帯電話 | 📱 U+1F4F1 |
| U+E00A | envelope | メール | ✉ U+2709 |
| U+E00B | camera | カメラ | 📷 U+1F4F7 |
| U+E00C | heart | ハート | ♡ U+2661, ❤ U+2764 |
| U+E00D | smiling-face | 笑顔 | ☺ U+263A |
| U+E00E | sad-face | 悲しい顔 | ☹ U+2639 |
| U+E00F | winking-face | ウインク | 😉 U+1F609 |
| U+E010 | train | 電車 | 🚆 U+1F686 |
| U+E011 | bus | バス | 🚌 U+1F68C |
| U+E012 | car | 自動車 | 🚗 U+1F697 |
| U+E013 | bicycle | 自転車 | 🚲 U+1F6B2 |
| U+E014 | airplane | 飛行機 | ✈ U+2708 |
| U+E015 | ship | 船 | 🚢 U+1F6A2 |
| U+E016 | house | 家 | 🏠 U+1F3E0 |
| U+E017 | hospital | 病院 | 🏥 U+1F3E5 |
| U+E018 | bank | 銀行 | 🏦 U+1F3E6 |
| U+E019 | japanese-post-office | 郵便局 | 🏣 U+1F3E3 |
| U+E01A | school | 学校 | 🏫 U+1F3EB |
| U+E01B | nine-oclock | 9時 | 🕘 U+1F558 |
| U+E01C | alarm-clock | 目覚まし時計 | ⏰ U+23F0 |
| U+E01D | hot-drink | 温かい飲み物 | ☕ U+2615 |
| U+E01E | fork-and-knife | 食事 | 🍴 U+1F374 |
| U+E01F | music-note | 音符 | ♪ U+266A |
| U+E020 | music-notes | 連桁付き音符 | ♫ U+266B |
| U+E021 | bell | ベル | 🔔 U+1F514 |
| U+E022 | open-book | 本 | 📖 U+1F4D6 |
| U+E023 | pencil | 鉛筆 | ✎ U+270E |
| U+E024 | magnifying-glass | 虫眼鏡 | 🔍 U+1F50D |
| U+E025 | key | 鍵 | 🔑 U+1F511 |
| U+E026 | locked | 施錠 | 🔒 U+1F512 |
| U+E027 | unlocked | 解錠 | 🔓 U+1F513 |
| U+E028 | scissors | はさみ | ✂ U+2702 |
| U+E029 | gift | プレゼント | 🎁 U+1F381 |
| U+E02A | shopping-cart | 買い物 | 🛒 U+1F6D2 |
| U+E02B | flag | 旗 | ⚐ U+2690 |
| U+E02C | check-mark | チェック | ✓ U+2713 |
| U+E02D | warning | 注意 | ⚠ U+26A0 |
| U+E02E | information | 案内 | None |
| U+E02F | battery | 電池 | 🔋 U+1F50B |
| U+E030 | electric-plug | 電源プラグ | 🔌 U+1F50C |
| U+E031 | wireless-signal | 無線通信 | None |
| U+E032 | satellite-antenna | 衛星アンテナ | 📡 U+1F4E1 |
| U+E033 | laptop-computer | ノートパソコン | 💻 U+1F4BB |
| U+E034 | printer | プリンター | 🖨 U+1F5A8 |
| U+E035 | television | テレビ | 📺 U+1F4FA |
| U+E036 | game-controller | ゲームパッド | 🎮 U+1F3AE |
| U+E037 | soccer-ball | サッカーボール | ⚽ U+26BD |
| U+E038 | baseball | 野球 | ⚾ U+26BE |
| U+E039 | tennis | テニス | 🎾 U+1F3BE |
| U+E03A | leaf | 葉 | None |
| U+E03B | flower | 花 | ❀ U+2740 |
| U+E03C | dog-face | 犬の顔 | 🐶 U+1F436 |
| U+E03D | cat-face | 猫の顔 | 🐱 U+1F431 |
| U+E03E | footprints | 足跡 | 👣 U+1F463 |
| U+E03F | wastebasket | ごみ箱 | 🗑 U+1F5D1 |

## Validation and small-size limits

Every scalar key, finite coordinate, path length, 0–24 bound, category/name record, exact PUA assignment and alias-to-PUA geometry match was checked programmatically. Rasterized contact sheets at 24 pixels were visually reviewed for all pictograms, Greek, Cyrillic, mathematical additions and extended Latin. All glyphs rasterize to nonempty monochrome masks at 18 and 24 pixels. These checks validate the authored centerlines, not installation behavior or the later generated font binaries.

At small raster sizes, close strokes in compound math signs, circles, accents and multi-digit enclosures can merge. The contour set is intentionally compact rather than an optical-size-specific design. The central build should inspect the styled output again at each target size.
