"""Original, unreviewed centerlines for difficult historical CJK components.

These are independently drawn skeletons in the project's 24-unit design cell.
No outline font, KanjiVG path, traced image, or external stroke geometry is used.
Related forms share only an explicitly drawn structural part where appropriate:
專/惠 use 叀, 鼠/巤 use the long-tailed lower element, and 與 uses 𦥑.
The drawings deliberately retain the visible distinctions of 亞/亜, 帶/帯,
烏/鳥, 虛/虚, 黑/黒, and 與/与. All additions remain design drafts.
"""
from __future__ import annotations


def extend(C, strokes, fit):
    """Add absent components to ``C`` and return exactly the newly added keys.

    ``strokes`` parses semicolon-separated polylines; ``fit`` uses the existing
    project's 24-unit coordinate convention. Existing definitions are preserved.
    """
    added = set()

    def put(char, paths):
        if char not in C:
            C[char] = [[tuple(point) for point in line] for line in paths]
            added.add(char)

    # Stepped side walls are essential here: the interior is not 亜's grid.
    put('亞', strokes(
        '2,2 22,2; 8,2 8,8; 8,8 3,8 3,16 8,16; 8,16 8,22; '
        '16,2 16,8; 16,8 21,8 21,16 16,16; 16,16 16,22; 2,22 22,22'))

    # 婁 has the old pierced upper body, separate from the female lower part.
    lou_top = strokes(
        '12,1 12,13; 5,3 19,3 19,8; 5,3 5,8; 5,5.5 19,5.5; '
        '5,8 19,8; 2,10.5 22,10.5; 7,8 7,13; 17,8 17,13')
    put('婁', lou_top + strokes(
        '10,12.5 6,18 13,20 21,23; 2,16 22,16; '
        '18,16 15,20 9,22 2,23'))

    # 叀: a pierced field and the small bent/dotted lower element.  In particular
    # these are not copies of modern 専 or 恵 with the historical detail omitted.
    zhuan_top = strokes(
        '3,2 21,2; 5,5 19,5 19,10.5 5,10.5 5,5; '
        '5,7.7 19,7.7; 12,1 12,10.5; '
        '12,10.5 8,14 18,14; 16.5,11.5 20,14.5')
    put('專', zhuan_top + strokes(
        '2,17 22,17; 16,15 16,22.5 12,23; 6,19 9,21.5'))
    put('惠', zhuan_top + strokes(
        '3,18 1.5,22; 7,17 7,21.5 9,23 18,23 20,21; '
        '11,16 14,18.5; 19,17.5 22,21'))

    # Old 帶 has interlocking upright tips and a hooked right-hand top, above
    # the cover and hanging cloth. The shape is visibly different from 帯.
    put('帶', strokes(
        '1.5,4.5 22,4.5; 5,1 5,8.5 9,8.5 9,1; '
        '12.5,1 12.5,8.5; 17,1 17,8.5 21,8.5 23,6.5; '
        '2,15 2,11.5 22,11.5 22,15; '
        '5.5,22.5 5.5,16.5 18.5,16.5 18.5,22.5 16,22.5; '
        '12,12.5 12,23'))

    # The empty head of 烏 deliberately has no bird's inner eye bar.
    put('烏', strokes(
        '12,1 9,4; 6,4 19,4 19,10 6,10; '
        '6,4 6,16 22,16 20,23 17.5,23; 6,13 21,13; '
        '4,19 2,23; 8.5,19 9.5,22.5; 13,19 15,22.5'))
    put('焉', strokes(
        '3,2 21,2; 12,2 12,9.5; 12,5.5 20,5.5; '
        '6,5 6,9.5; 2,9.5 22,9.5; 6,12 22,12; '
        '7,12 6,16 22,16 20,23 17.5,23; '
        '4,19 2,23; 8,19 9,22; 12,19 13.5,22; 16,19 17.5,21.5'))

    # 虍's outer stroke preserves the left shelter. The lower four upright
    # corners are intentionally articulated instead of 虚's two diagonal dots.
    put('虛', strokes(
        '11,1 11,7; 11,3.8 21.5,3.8; '
        '22.5,7 4,7 4,15 3,19 1,23; '
        '8,11 20,9.5; 11,8 11,12.5 13,14 20,14 22,12; '
        '10,16 10,22; 17,16 17,22; '
        '7,16 7,19 10,19; 21,16 21,19 17,19; '
        '10,16 13,16; 6,22 23,22'))

    # 隹 above the indented, double-shouldered lower enclosure of 雋.
    put('雋', strokes(
        '7,1 5,5 1.5,8; 5.5,4.5 5.5,13; '
        '14,1 16,2.8; 5.5,4 22,4; 5.5,7 21,7; '
        '5.5,10 21,10; 5.5,13 22.5,13; 14,4 14,13; '
        '3,16 3,23; 3,16 9,16 9,20; '
        '9,20 15,20 15,16; 15,16 21,16 21,22.5 18.5,23'))

    # 黑's enclosed diagonal pair is retained; replacing it with 田 makes 黒.
    put('黑', strokes(
        '5,2 19,2 19,11 5,11 5,2; 8,5 10,8; 16,5 14,8; '
        '12,11 12,18; 5,14.5 19,14.5; 2,18 22,18; '
        '4,20 2,23; 9,20 10,23; 14,20 15.5,23; 19,20 22,23'))

    # Eye-shaped vessel and the two distinct folded leg frameworks of 鼎.
    put('鼎', strokes(
        '8,2 16,2 16,12 8,12 8,2; 8,5.3 16,5.3; 8,8.7 16,8.7; '
        '4,7 4,15 10,15 10,23; 7,15 7,19; 2,19 7,19 7,23; '
        '20,7 20,15 14,15 14,23; 14,19 21,19 21,23'))

    # The complete original tail module is shared only by its actual relatives.
    mouse_tail = strokes(
        '4,1 4,22 8,19; 5.8,7 8,9; 5.8,13 8,15; '
        '10.5,1 10.5,22 14.5,19; 12.3,7 14.5,9; 12.3,13 14.5,15; '
        '17,1 17.5,13 19.5,20 22,23 23,18')
    put('鼠', strokes(
        '10,1 4,3.5; 4,3.5 4,9; 4,6 9,6; '
        '15,2 20,2 20,9; 15,6 20,6; 4,9 20,9')
        + fit(mouse_tail, 0, 10.5, 24, 13))

    # 齊 keeps the central fork and flanking blades under its cap; the lower
    # paired crossbars sit between the descending side strokes.
    put('齊', strokes(
        '11,1 13,3; 2,4 22,4; '
        '3,6.5 9,6.5 8,12.5 6.5,13; 6,6.5 5,10.5 2,14; '
        '10.5,6.3 12,8.5; 13.7,6.3 12,8.5 12,13.5; '
        '19,5.8 17,8 15,9.5; 15.5,6.5 18,10 22,12; 20.5,7 20.5,14; '
        '5,15.5 5,20 3,23; 20,15.5 20,23; '
        '7.5,17 17.5,17; 7,21 18,21'))

    hands = strokes(
        '9,1 3,4; 3,4 3,23; 3,10 8,10; 3,17 8,17; '
        '16,2 21,2 21,23; 16,10 21,10; 16,17 21,17')
    put('𦥑', hands)
    put('與', fit(hands, 0, 0, 24, 17.5) + strokes(
        '11,1 9.5,9 16,9 15,16 12,16; 10,4.5 16,4.5; '
        '7.5,12.5 15.5,12.5; 1,18 23,18; '
        '7,20.5 2,23; 17,20.5 22,23'))

    put('巤', strokes(
        '7,1 4,3.2 7,5; 13,1 10,3.2 13,5; 19,1 16,3.2 19,5; '
        '5,6.5 19,6.5 19,11 5,11 5,6.5; '
        '9,7.5 15,10; 15,7.5 9,10')
        + fit(mouse_tail, 0, 12, 24, 11.5))

    # The old left upper blade of 劉, then 刀, then 金; the tall right knife
    # remains separate. This cannot be manufactured from simplified 刘.
    put('劉', strokes(
        '8,1 3,3; 3,3 3,8 6,6.5; 7.5,3.5 7,8.5; '
        '10,2 17,2 16,8.5 13.5,8.5; 13,2 12,6 9,9; '
        '9,10 5,13 1.5,15; 9,10 13,13 17,15; '
        '5,15 13,15; 2,18 16,18; 9,15 9,23; '
        '4,19.5 6,21.5; 14,19.5 12,21.5; 1,23 17,23; '
        '19.5,5 19.5,17; 23,1 23,22 20.5,23'))

    # 羲: capped sheep body above 禾 and the bent 丂, crossed by a long lance.
    put('羲', strokes(
        '6,1 8,3; 18,1 16,3; 3,3 21,3; 5,5.5 19,5.5; '
        '1,8 23,8; 12,3 12,8; '
        '13,9.5 5,11; 3,13.5 15,13.5; 9,10.3 9,17; '
        '9,13.5 3,17.5; 9,13.5 14,16.5; '
        '3,18.5 13,18.5; 7,18.5 6,21.5 12,21.5 11,23.5 8,23.5; '
        '16.5,9.5 17.5,17 20,22 22,23.5 23,20; '
        '22,14 18,19 13,23; 20,10 22,12'))

    # 田 is crossed by a continuous stem, with the double upright crosspiece
    # below it. The lower centre descender is not the simplified 毕 structure.
    put('畢', strokes(
        '5,2 19,2 19,10 5,10 5,2; 5,6 19,6; '
        '12,2 12,23; 6,12 6,19; 18,12 18,19; '
        '2,14 22,14; 3,19 21,19'))

    # 亙 retains the oblique moon-like interior, unlike the upright 日 of 亘.
    put('亙', strokes(
        '2,2 22,2; 10,5 8,12 5,20; 10,5 19,5 15,20; '
        '9,10 17.5,10; 7.5,15 16,15; 1,22 23,22'))

    # Shared jar lid; modern 壷 has the through-grid, historical 壺 the stepped
    # chamber. Neither is substituted with the unrelated lower part of 壱.
    jar_lid = strokes(
        '2,3.5 22,3.5; 12,1 12,7; 6,7 18,7; '
        '2,13 2,10 22,10 22,13')
    put('壷', jar_lid + strokes(
        '5,14 19,14 19,19 5,19 5,14; '
        '9,11.5 9,23; 15,11.5 15,23; 2,23 22,23'))
    put('壺', jar_lid + strokes(
        '9,11.5 9,14; 9,14 5,14 5,19 9,19; 9,19 9,23; '
        '15,11.5 15,14; 15,14 19,14 19,19 15,19; '
        '15,19 15,23; 2,23 22,23'))

    # Bird framework with NO fire-dot base. Its outer tail shelters the actual
    # 木 / 衣 / 几 lower part in these three characters, rather than stacking an
    # entire 鳥 above a second complete glyph.
    bird_framework = strokes(
        '12,1 9,3.5; 5,3.5 18,3.5 18,9 5,9; '
        '5,6.2 18,6.2; 5,3.5 5,14 22,14 20,23 18,23; '
        '5,11.5 21,11.5')
    put('梟', bird_framework + strokes(
        '1,18 17,18; 9,14.7 9,23; 9,18 5,21 1,23; '
        '9,18 12,20.5 17,23'))
    put('裊', bird_framework + strokes(
        '8,14.7 10,16; 1,17 17,17; 9,17 5.5,20 1,21; '
        '5.5,20 5.5,23 10,21.5; 10,18 13,21 17,23; '
        '17,18 13,20'))
    put('鳬', bird_framework + strokes(
        '2,23 5,20.5 5,16.5 13,16.5 13,21.5 14.5,23 17,23 18,21'))

    # 兎 uses the single top slant and pierced body. It is not 兔's 免 head.
    put('兎', strokes(
        '17,1 6,4; 4,6 20,6 20,13 4,13 4,6; '
        '12,4 12,13 8,20 1,23; '
        '16,13 16,21 18,23 22,23 23,19; 18.5,15 21,18'))

    # The right side of 派: descending shelter, inner rising hook, and branch.
    put('𠂢', strokes(
        '21,1 5,5 5,15 4,19 1,23; '
        '10,7 10,23 15,19; 21,8 14,13; '
        '13,8 17,18 23,23'))

    # Structural cross-checks only (no imported stroke coordinates):
    # https://github.com/chise/ids/blob/master/IDS-UCS-Basic.txt
    # https://github.com/chise/ids/blob/master/IDS-UCS-Ext-A.txt
    # https://github.com/chise/ids/blob/master/IDS-UCS-Ext-B-2.txt
    # CDP-88C8 is shared by 其/甚/䑓; CDP-89CC by 囬 and 𣘺;
    # CDP-8CAC is 印's left part and 襃's internal left part.
    # These relationships inform whole-character drawings, not placeholder keys.
    put('䑓', strokes(
        '2,3 22,3; 6,1 6,7.5; 18,1 18,7.5; '
        '6,5.2 18,5.2; 2,7.5 22,7.5; '
        '2,12 2,10 22,10 22,12; '
        '4,13.5 20,13.5; 11,13.5 6,17 19,16.5; '
        '17,14.5 21,18; 4,20 20,20; 12,17.5 12,23; 2,23 22,23'))

    # 囬 is the gridded lower body of 面, not the single inner box of 回.
    put('廽', strokes(
        '1,3 6,3 2,9 6,9 5,15 2,20; '
        '1,13 3,18 8,21.5 14,23 23,23; '
        '9,2 22,2 22,19 9,19 9,2; '
        '13,2 13,19; 18,2 18,19; 13,7.5 18,7.5; 13,13.5 18,13.5'))

    # 戞 retains the covering 冖 below the white head, unlike 戛's 自 head.
    put('戞', strokes(
        '2,1.5 22,1.5; 12,1.5 9.5,4; '
        '6,4 18,4 18,9.5 6,9.5 6,4; 6,6.8 18,6.8; '
        '2,14 2,12 22,12 22,14; '
        '1,17 22,15.5; 13,13.5 14,18 18,22 22,23.5 23,20; '
        '21,17.5 15,21 7,23.5; 18,13.5 20.5,15'))

    # CHISE supplies 並 directly for these words. It is also the Unicode
    # compatibility decomposition of CJK compatibility character U+FA70.
    parallel_body = strokes(
        '6,1 9,5; 18,1 15,5; 2,6 22,6; '
        '8,6 8,23; 16,6 16,23; 2,11 5,19; 22,11 19,19; 1,23 23,23')
    put('掽', strokes(
        '1,8 8,8; 5,1 5,22 2.5,23; 1,16 8,12')
        + fit(parallel_body, 9, 0, 15, 24))
    put('碰', strokes(
        '1,4 9,4; 6,4 4,11 1,16; 3.5,12 8.5,12 8.5,22 3.5,22 3.5,12')
        + fit(parallel_body, 10, 0, 14, 24))

    # 斵 uses the same upper pair of blade forms as 劉, over 亞, beside 斤.
    put('斵', strokes(
        '6,1 2,2.5; 2,2.5 2,7.5 5,6; 6,3 5.5,8; '
        '8,1.8 14,1.8 13,7.5 11,7.5; 10.5,1.8 10,5.5 7,8; '
        '23,1 17,4 17,15 15,22.5; 17,9 24,9; 21,9 21,23')
        + fit(C['亞'], 0, 9, 14, 15))

    # Old 襃 has the 印-like open hand within the split 衣 frame. This
    # additional inner stroke distinguishes it from modern 褒's person radical.
    put('襃', strokes(
        '11,1 13,3; 2,4 22,4; '
        '8,5.5 3,7; 3,7 3,15 8,13.5; 3,10.5 8,10.5; '
        '11,6 21,6 21,10 11,10 11,6; '
        '10,12 23,12; 16,10 16,16; 16,12 12,14.5 9,16; '
        '16,12 19,14.5 23,16; '
        '12,16.5 7,19 1,20.5; 7,19 7,23 13,21; '
        '13,18 17,21 23,23; 22,17.5 17,20'))

    # U+FA32 has the folded knife head recorded in the Japanese IDS source,
    # followed by the familiar pierced body and legs. No arbitrary accent dot.
    put('免', strokes(
        '6,2 20,2 18,8 15.5,8; 12,2 9,6 4,9; '
        '4,10 20,10 20,16 4,16 4,10; '
        '12,9 12,16 8,21 1,23; '
        '16,16 16,21 18,23 22,23 23,20'))

    # Bridge-name variant: the four-stroke frame found inside 囬 is above
    # 冋. This keeps the actual structure rather than duplicating ordinary 橋.
    put('𣘺', strokes(
        '1,8 9,8; 5,1 5,23; 5,8 3,14 1,18; 5,9 8,14; '
        '15,1 12,5; 14,3 22,3; '
        '14,5 14,12; 21,5 21,12; 14,7.5 21,7.5; 14,10.5 21,10.5; '
        '11,23 11,14 23,14 23,23 21,23; '
        '15,17 20,17 20,21 15,21 15,17'))

    return added
