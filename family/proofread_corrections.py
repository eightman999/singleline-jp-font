"""Family-only, independently drawn priority near-form corrections.

Noto Sans CJK JP was viewed for topology only, never traced or imported.
Legacy glyphs remain untouched; these explicit 24-unit centerlines replace
only the new family's selected glyphs, preserving all original metrics.
"""
from dataclasses import replace
from copy import deepcopy

CORRECTION_NOTES = {
    '己': 'Left stem starts at the middle bar, leaving the upper-left open.',
    '已': 'Left stem starts between the top and middle bars.',
    '巳': 'Left stem reaches the top bar and closes the upper-left.',
    '未': 'Upper horizontal is shorter than the lower horizontal (14 vs 22 units).',
    '末': 'Upper horizontal is longer than the lower horizontal (22 vs 14 units).',
    '土': 'Upper horizontal is shorter than the bottom horizontal (14 vs 22 units).',
    '士': 'Upper horizontal is longer than the bottom horizontal (22 vs 14 units).',
    '髙': 'Two uprights run from the top horizontal to the lower enclosure, with one middle crossbar; not a comb.',
}

GLYPHS = {}
for char, left_top in [('己', 14), ('已', 9), ('巳', 3)]:
    GLYPHS[char] = [[(3,3),(21,3),(21,14),(3,14)],
                    [(3,left_top),(3,21),(6,23),(21,23),(23,19)]]
for char, upper, lower in [('未',(5,19),(1,23)), ('末',(1,23),(5,19))]:
    GLYPHS[char] = [[(upper[0],6),(upper[1],6)],[(lower[0],12),(lower[1],12)],
                    [(12,1),(12,24)],[(12,12),(6,20),(1,24)],
                    [(12,12),(18,20),(23,24)]]
for char, upper, lower in [('土',(5,19),(1,23)), ('士',(1,23),(5,19))]:
    GLYPHS[char] = [[(upper[0],9),(upper[1],9)],[(12,1),(12,22)],
                    [(lower[0],22),(lower[1],22)]]
GLYPHS['髙'] = [[(12,1),(12,4)],[(1,4),(23,4)],
                [(6,4),(6,14)],[(18,4),(18,14)],[(6,9),(18,9)],
                [(2,24),(2,14),(22,14),(22,24),(19,24)],
                [(7,17),(17,17),(17,22),(7,22),(7,17)]]


def apply_corrections(glyphs):
    """Replace present glyphs only, without mutating shared legacy paths."""
    for char, paths in GLYPHS.items():
        if char not in glyphs:
            continue
        original = glyphs[char]
        glyphs[char] = replace(original, paths=deepcopy(paths),
            source='original:family.proofread_corrections',
            status='priority-structure-reviewed',
            notes={**original.notes, 'proofread_correction': CORRECTION_NOTES[char],
                   'previous_source': original.notes.get('previous_source', original.source),
                   'review_scope': 'priority topology; raster proofs are separate'})
    return glyphs
