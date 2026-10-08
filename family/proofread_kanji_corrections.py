"""Ten bounded, independently drawn centerline repairs for the new family only.

Reference images establish topology, never coordinates or contours. This module
replaces only the named assembled Glyph.paths. It does not mutate legacy glyph
modules or recursively propagate changes to components/other characters.
"""
from dataclasses import replace

CORRECTED_CHARACTERS = tuple('㖨䐜咎嘷晷槩櫜洴籘蓱')


def _p(text):
    return [[tuple(map(float, point.split(','))) for point in line.split()]
            for line in text.split(';') if line.strip()]


def _fit(paths, x, y, w, h):
    return [[(x+a*w/24, y+b*h/24) for a,b in line] for line in paths]


_MOUTH = _p('2,3 22,3 22,22 2,22 2,3')
_DAY = _MOUTH + _p('2,12 22,12')
_MOON = _p('3,1 21,1 21,23 17,23;3,1 3,17 1,24;3,9 21,9;3,16 21,16')
_WOOD = _p('1,7 23,7;12,1 12,24;12,7 8,14 1,21;12,7 17,15 24,21')
_WATER_SIDE = _p('2,2 5,5;1,9 4,12;1,23 6,15')
_GRASS = _p('1,3 23,3;7,0 7,6;17,0 17,6')
_BAMBOO = _p('5,0 2,5;4,3 11,3;7,3 8,6;17,0 14,5;16,3 23,3;19,3 20,6')

# A clear, separated left 夂 and right 人 above the mouth. Do not overlay both
# components in the same box, the cause of the old tangled X-shaped crown.
_BLAME = _p('8,1 3,5;6,3 12,3 9,7 3,11;'
            '5,5 9,9 15,12 23,12;'
            '17,1 16,5 13,8;17,4 21,8') + _fit(_MOUTH,4,14,17,10)

# Japanese 幷 form: two same-direction falling strokes, joined to the two
# upright members, rather than detached opposed 八 above 开.
_MERGE = _p('8,1 5,6;19,1 16,6;'
            '3,6 23,6;1,14 24,14;'
            '8,6 8,17 5,23;19,6 19,24')

# 絭 with deliberately reserved space for 龹 (upper 11 units) and 糸 (lower).
_SILK_ROLL = _p('6,0 8,3;18,0 16,3;4,4 20,4;2,7 22,7;'
                '10,3 8,7 2,11;14,3 17,8 23,11;'
                '11,11 7,15 13,15;16,12 8,19 18,18;16,16 19,20;'
                '13,19 13,24 11,24;8,21 4,24;18,21 22,24')

CORRECTION_NOTES = {
    '㖨': 'Replace the ヨ-like crown with an independently drawn 彑/彔 crown.',
    '䐜': 'Use the Japanese 眞 crown, replacing the 十-headed 真 composition.',
    '咎': 'Separate 夂 from the right-hand 人 above 口; remove accidental overlay.',
    '嘷': 'Replace the radiating 米-like lower part by the Japanese 臯 horizontal/vertical structure.',
    '晷': 'Keep 日 above the newly separated 咎 structure.',
    '槩': 'Redraw the upper-left 皀 with its opening slant, 白 and lower 匕; preserve 木 below.',
    '櫜': 'Reserve separate bands for the top shelter, 咎 and bottom 木.',
    '洴': 'Use the Japanese 幷 structure rather than detached 八 plus 开.',
    '籘': 'Reserve independent areas for 竹, 月, 龹 and 糸, avoiding stacked line collisions.',
    '蓱': 'Use the same Japanese 幷 repair within the whole character below 艹.',
}


def correction_paths():
    """Fresh path lists on the original 24-unit design grid, no source mutation."""
    paths = {}
    paths['㖨'] = _fit(_MOUTH,0,6,8,16) + _p(
        '15,1 12,8 23,8;14,3 22,3 20,8;'
        '17,8 17,23 14,23;11,12 14,15;14,16 9,21;'
        '23,12 20,15;18,15 23,21')
    paths['䐜'] = _fit(_MOON,0,0,8,24) + _p(
        '12,1 12,5 21,5 22,4;12,3 21,1;'
        '12,8 21,8 21,18 12,18 12,8;12,11 21,11;12,14.5 21,14.5;'
        '10,20 23,20;14,21 10,24;19,21 23,24')
    paths['咎'] = _BLAME
    paths['嘷'] = _fit(_MOUTH,0,5,8,17) + _p(
        '17,0 15,3;12,3 23,3 23,12 12,12 12,3;'
        '12,6 23,6;12,9 23,9;'
        '17.5,13 17.5,24;10,21 24,21;'
        '11,15 15,15;20,15 24,15;11,18 15,18;20,18 24,18')
    paths['晷'] = _fit(_DAY,4,0,16,7) + _fit(_BLAME,0,8,24,16)
    white_spoon = _p('7,0 5,3;2,3 10,3 10,10 2,10 2,3;2,6.5 10,6.5;'
                     '3,10 3,15 9,14;3,12 9,10')
    already = _p('13,3 23,3;15,3 12,9 22,9;'
                 '18,9 16,13 12,16;20,9 20,15 23,15 24,13')
    paths['槩'] = white_spoon + already + _fit(_WOOD,0,16,24,8)
    paths['櫜'] = _p('12,0 12,5;4,1 20,1;7,2 17,2 17,5 7,5 7,2;'
                     '2,9 2,6 22,6 22,9') + _fit(_BLAME,2,7,20,10) + _fit(_WOOD,0,17,24,7)
    paths['洴'] = _WATER_SIDE + _fit(_MERGE,8,0,16,24)
    paths['籘'] = _BAMBOO + _fit(_MOON,0,8,8,16) + _fit(_SILK_ROLL,9,7,15,17)
    paths['蓱'] = _GRASS + _fit(paths['洴'],0,6,24,18)
    return {c: [[tuple(point) for point in line] for line in paths[c]]
            for c in CORRECTED_CHARACTERS}


def apply(glyphs):
    """Replace only present target Glyphs, returning the set actually changed.

    Glyph metrics remain intact; original source/status are retained in notes,
    and a bounded repair note is added. No broad visual approval is asserted.
    """
    changed = set()
    for c, paths in correction_paths().items():
        if c not in glyphs:
            continue
        old = glyphs[c]
        notes = dict(old.notes)
        notes.setdefault('previous_source', old.source)
        notes.setdefault('previous_status', old.status)
        notes['proofread_kanji_correction'] = CORRECTION_NOTES[c]
        notes['proofread_kanji_scope'] = 'bounded topology repair; not full typographic certification'
        glyphs[c] = replace(old, paths=paths, notes=notes, source='original:family.proofread_kanji_corrections', status='structure-reviewed-large-size')
        changed.add(c)
    return changed
