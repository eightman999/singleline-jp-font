"""Exact-key 壽 layout repair; no shared component or legacy mutation.

All twelve original semantic paths existed. Their upper seven paths were
compressed into 6.8 units (4.54 in 燾), followed by oversized vertical gaps.
This fixes that layout, not a falsely claimed missing 工 vertical stroke.
"""
from copy import deepcopy
from dataclasses import replace

CORRECTED_CHARACTERS = tuple('嶹幬擣檮濤燾璹疇禱躊隯')
# Frozen pre-existing non-壽 constituent paths; preserved without shared lookup.
_OTHER = {'嶹': [[[1.375, 7.0], [1.375, 22.0], [9.625, 22.0], [9.625, 7.0]], [[5.5, 1.0], [5.5, 22.0]]],
 '幬': [[[1.375, 22.0], [1.375, 6.0], [9.625, 6.0], [9.625, 22.0], [7.791666666666667, 22.0]],
       [[5.5, 1.0], [5.5, 24.0]]],
 '擣': [[[0.6666666666666666, 7.0], [7.0, 7.0]],
       [[4.0, 1.0], [4.0, 22.0], [2.3333333333333335, 23.0]],
       [[0.6666666666666666, 15.0], [7.333333333333333, 11.0]]],
 '檮': [[[0.8333333333333334, 8.0], [9.166666666666666, 8.0]],
       [[5.0, 1.0], [5.0, 23.0]],
       [[5.0, 8.0], [2.9166666666666665, 15.0], [0.4166666666666667, 21.0]],
       [[5.0, 8.0], [7.083333333333333, 15.0], [9.583333333333334, 21.0]]],
 '濤': [[[1.6666666666666667, 2.0], [4.0, 5.0]],
       [[1.0, 10.0], [3.3333333333333335, 13.0]],
       [[1.6666666666666667, 22.0], [5.0, 15.0]]],
 '燾': [[[3.0, 21.958333333333332], [1.0, 23.708333333333332]],
       [[9.0, 21.958333333333332], [10.0, 23.708333333333332]],
       [[15.0, 21.958333333333332], [17.0, 23.708333333333332]],
       [[21.0, 21.958333333333332], [24.0, 23.708333333333332]]],
 '璹': [[[0.8333333333333334, 3.0], [9.166666666666666, 3.0]],
       [[1.6666666666666667, 12.0], [8.333333333333334, 12.0]],
       [[0.4166666666666667, 22.0], [9.583333333333334, 22.0]],
       [[5.0, 3.0], [5.0, 22.0]]],
 '疇': [[[0.9166666666666666, 3.0],
        [10.083333333333334, 3.0],
        [10.083333333333334, 22.0],
        [0.9166666666666666, 22.0],
        [0.9166666666666666, 3.0]],
       [[5.5, 3.0], [5.5, 22.0]],
       [[0.9166666666666666, 12.0], [10.083333333333334, 12.0]]],
 '禱': [[[1.8333333333333333, 1.6666666666666667], [9.166666666666666, 1.6666666666666667]],
       [[0.4583333333333333, 7.0], [10.541666666666666, 7.0]],
       [[5.5, 9.625], [5.5, 23.375], [3.6666666666666665, 23.375]],
       [[2.2916666666666665, 13.375], [0.4583333333333333, 19.625]],
       [[8.708333333333334, 13.375], [10.541666666666666, 19.625]]],
 '躊': [[[1.375, 1.375], [9.625, 1.375], [9.625, 9.625], [1.375, 9.625], [1.375, 1.375]],
       [[5.5, 12.5], [5.5, 23.0]],
       [[5.5, 16.0], [10.083333333333334, 16.0]],
       [[2.2916666666666665, 16.5], [2.2916666666666665, 23.0]],
       [[0.4583333333333333, 23.0], [10.541666666666666, 23.0]]],
 '隯': [[[1.0, 24.0],
        [1.0, 2.0],
        [7.0, 2.0],
        [4.666666666666667, 9.0],
        [6.666666666666667, 15.0],
        [6.666666666666667, 19.0],
        [5.0, 21.0],
        [2.3333333333333335, 19.0]]]}
_RIGHT_LEFT = {'嶹':12, '幬':12, '擣':9, '檮':11, '濤':9,
               '璹':11, '疇':12, '禱':12, '躊':12, '隯':9}


def _shou():
    # 士, folded bar, 工, separator, 口 and 寸, independently spaced.
    return [[(1,3),(23,3)], [(12,0),(12,6)], [(4,6),(20,6)],
            [(2,8),(22,8),(19,10)], [(3,11),(21,11)],
            [(12,11),(12,14)], [(1,14),(23,14)], [(1,17),(23,17)],
            [(2,19),(10,19),(10,24),(2,24),(2,19)],
            [(13,20),(24,20)], [(21,17),(21,24),(18,24)],
            [(14,21),(16,23)]]


def correction_spec():
    result = {}
    for c in CORRECTED_CHARACTERS:
        if c == '燾':
            shou = [[(x, y*19/24) for x,y in p] for p in _shou()]
            result[c] = [('壽', shou), ('灬', deepcopy(_OTHER[c]))]
        else:
            left = _RIGHT_LEFT[c]
            shou = [[(left+x*(24-left)/24, y) for x,y in p] for p in _shou()]
            result[c] = [('unchanged left constituent', deepcopy(_OTHER[c])), ('壽', shou)]
    return result


def correction_paths():
    return {c:[p for _,part in parts for p in part] for c,parts in correction_spec().items()}


def apply(glyphs):
    changed = set()
    for c,paths in correction_paths().items():
        if c not in glyphs:
            continue
        old = glyphs[c]
        notes = dict(old.notes)
        notes.setdefault('previous_source', old.source)
        notes.setdefault('previous_status', old.status)
        notes['proofread_longevity_correction'] = 'Redistribute the existing twelve 壽 paths into consecutive legible levels; 工 vertical already existed, no added stroke.'
        notes['proofread_longevity_scope'] = 'eleven exact keys; no recursive propagation or small-size approval'
        glyphs[c] = replace(old, paths=paths, source='original:family.proofread_longevity_corrections',
                            status='structure-reviewed-large-size', notes=notes)
        changed.add(c)
    return changed
