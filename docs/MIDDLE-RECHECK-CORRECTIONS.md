# Middle uncertain-glyph recheck

99 glyphs retained as uncertain after 64px screening were individually viewed
again at 200px against Noto Sans CJK Regular TTC face 0 (JP). The project IDS,
component provenance and source paths were inspected to distinguish structural
errors from differences in typography. This is a topology review, not a claim
that all Japanese variants or all small-size strikes are certified.

## Results

- 66: no obvious structural defect at 200px; prior screening uncertainty resolved.
- 9: confirmed extra component crossings or collapsed internal structure, repaired
  only in `family/proofread_middle_recheck_corrections.py`.
- 24: still uncertain; no speculative source edits.

The nine targets are 應 U+61C9, 懴 U+61F4, 懺 U+61FA, 斄 U+6584,
曩 U+66E9, 殱 U+6BB1, 殲 U+6BB2, 灋 U+704B, 璺 U+74BA.
Their repair notes are in the module and per-character ledger.

懿 was not changed: path inspection established that 冖 is open below; its
apparent extra box was a viewing misinterpretation. By contrast, 曩 had two
horizontal source centerlines separated by only about 0.30 of the 24-unit grid,
less than the expanded stroke thickness; the merged stroke was visible even
at 200px. This is a spacing/structure defect, not a preference for Noto's style.

Reference images were viewed only for component topology. No external font
contours, coordinates, or pixel-to-path conversion contributed to the repairs.
Only the final named Glyph records change. Shared components and legacy assets
remain unchanged. `apply` preserves metrics and notes, records prior source and
status, and assigns the module's source plus `structure-reviewed-large-size`.

## Evidence

- `build/full-proofread/kanji-middle-recheck/00.png` through `12.png`: 99 original
  paired 200px comparisons. `reference-detail.png` includes a 450px look at 廌,
  灋, and 懿 to settle component interpretations.
- `build/full-proofread/reviews/kanji-middle-recheck.json`: the 99 rechecks.
- `build/full-proofread/reviews/kanji-middle.json`: revised middle ledger, keeping
  its initial screening result and the recheck/remediation separately.
- `build/full-proofread/middle-recheck-corrections/before-after-0.png` and `1.png`:
  Noto / before / after at 200px for nine repairs.
- The same root holds all eight small TTFs, binary bitmap strikes, large proofs,
  and `distribution-sizes-<style>.png` paired actual 16/18/24/32px TTF/bitmap
  sheets. All eight large and all eight distribution-size sheets were viewed.
- `review-status.json` records 288 small-size target/style/size cells. They are
  conservative and do not replace the earlier 18-glyph/576-cell ledger.

## Tests and remaining limitations

`.venv/bin/python -m pytest -q tests/test_proofread_middle_recheck_corrections.py`
passes ten tests, including eight-style TTF coverage and exact SJPB raster
roundtrip at 16/18/24/32/48/96/200px. Nonempty rendering is not a readability pass.
Dense 1-bit shapes still merge, especially 曩/灋, Italian, and reduced sub/super
strikes. These remain uncertain in the independent small-size axis.

Remaining 200px uncertainty: 慶 攀 攩 攪 斸 曦 櫽 欅 欝 欞 氂 氎 灊 灎 灩 爨
爭 爵 牽 犧 獻 璽 甕 甗. These require more authoritative Japanese glyph/variant
verification rather than a guess from stylistic differences. No additional code
edits are implied by this list.
