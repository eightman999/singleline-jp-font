"""Original, topology-aware draft corrections for three dense characters.

The previous generic IDS layouts overprinted these enclosures. These drawings
assign each structural part explicit space in the 24-unit cell. A locally
installed Noto Sans CJK reference was viewed only to confirm character identity
and topology; no outlines, images, points or paths were imported or traced.
All centerline coordinates below are independently project-authored drafts.

These three characters are outside the canonical project repertoire. Call this
extension after generic component expansion and before restoring canonical data.
"""
from __future__ import annotations


def extend(C, strokes, fit):
    """Apply the three per-character corrections; return their actual keys."""
    # The fit argument intentionally is not used: generic enclosure transforms
    # caused the defects these explicitly spaced whole-character paths correct.
    drawings = {
        # 鬥's full-height OUTER uprights flank two short upper bar groups.
        # None of its inner bars extends into the turtle's lower compartment.
        # 龜 keeps its angled head, folded upper shell, comb-like lower left,
        # crossed right shell cell and separate long turning central tail.
        '鬮': (
            '1,1 1,23.5; 23,1 23,22.5 22,23.5 20.5,23.5; '
            '3.5,1.8 10,1.8; 6.8,1.8 6.8,6.5; '
            '3.5,4.1 10,4.1; 3.5,6.5 10,6.5; '
            '14,1.8 20.5,1.8; 17.2,1.8 17.2,6.5; '
            '14,4.1 20.5,4.1; 14,6.5 20.5,6.5; '
            '11,7.5 8.5,10 4,12.5; 9.5,9 16.5,9 13.5,11.5; '
            '5.5,11.5 10,11.5 10,14.5 6,14.5; '
            '5.5,11.5 5.5,13 8,13; '
            '13.5,11.5 19.5,11.5 19.5,14 14,14; '
            '14,11.5 14,21; '
            '8,15.5 8,22; 3.5,16 8,16; 3.5,18 8,18; '
            '3.5,20 8,20; 3.5,22 8,22; '
            '14,15.8 20,15.8 20,20.3 14,20.3; '
            '15.5,17 18.5,19; 18.5,17 15.5,19; '
            '11,11.5 11,21.5 12.5,22.8 18.5,22.8 20,21.5; '
            '8,18 11,18'
        ),
        # Bamboo uses short downward marks, leaving a separate 从 row. The
        # full-width horizontal of 戈 roofs the broad 韭 without slicing it.
        # The lance curves down the far right; its crossing slash stays outside
        # 韭 until below the latter's baseline, where the forms naturally meet.
        '籤': (
            '5,1 3,3.5 1.5,5; 4,3 10.5,3; 6.5,3 7.5,5; '
            '15,1 13,3.5 11.5,5; 14,3 23,3; 18,3 19,5; '
            '6,6 4.5,8 2,9.5; 6,6 8.5,9; '
            '13,6 11.5,8 9,9.5; 13,6 15.5,9; '
            '1,11 23,11; '
            '6,12 6,21.8; 11.5,12 11.5,21.8; '
            '2,13.5 6,13.5; 11.5,13.5 15.5,13.5; '
            '2,16.5 6,16.5; 11.5,16.5 15.5,16.5; '
            '2,19.5 6,19.5; 11.5,19.5 15.5,19.5; '
            '1,22 16,22; '
            '18,6 18.5,13.5 20,20.5 22,23.5 23,20.5; '
            '23,13.5 21.5,18 18,21.5 14.5,23.5; '
            '21,6.5 23,9'
        ),
        # Three upper compartments: left hand, middle folded chamber, right
        # hand. The wide 冖 lies BELOW them; its horizontals never run through
        # the central chamber. 林, 大 and 火 then occupy separate lower bands.
        '爨': (
            '7,1 3,2.2 3,7.3; 3,4 6.5,4; 3,6 6.5,6; '
            '17,1.5 21,1.5 21,7.3; 17.5,4 21,4; 17.5,6 21,6; '
            '9,7.3 9,1.5 15,1.5 15,7.3; '
            '10.5,3.4 13.5,3.4; 10.5,5.1 13.5,5.1 13.5,7 10.5,7; '
            '1.5,10.4 1.5,8.6 22.5,8.6 22.5,10.4; '
            '7,10 7,15; 2,11.5 11,11.5; '
            '7,11.5 4,13.5 1.5,14.5; 7,11.5 10.5,14.4; '
            '17,10 17,15; 13,11.5 22,11.5; '
            '17,11.5 13.5,14.4; 17,11.5 20,13.5 22.5,14.5; '
            '1,16.5 23,16.5; 12,15 10.5,17.5 6,19 1.5,20; '
            '12,17 17,19 23,20; '
            '12,19 12,20.5 8,22.5 1.5,23.5; '
            '12,20.5 16,22.5 23,23.5; '
            '6,20 4,22; 20,20 17,21.5'
        ),
    }
    # Never let a later repertoire update silently replace a canonical glyph.
    from glyphs.kanji import GLYPHS as canonical
    applied = set()
    for char, drawing in drawings.items():
        if char not in canonical:
            C[char] = strokes(drawing)
            applied.add(char)
    return applied
