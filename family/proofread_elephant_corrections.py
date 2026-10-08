"""Exact-key repairs for the four remaining deficient 象 descendants.

Independently laid out on the 24-unit grid after inspecting Unicode 18 J-source
rows and Noto JP. No reference outlines or shared glyph components are used.
像 is deliberately absent: its frozen deep1 correction already restores this.
"""
from dataclasses import replace

CORRECTED_CHARACTERS = tuple('象橡潒豫')
J_SOURCES = dict(zip(CORRECTED_CHARACTERS, ('J0-3E5D', 'J0-464B', 'J14-6F33', 'J0-502E')))


def _elephant():
    return [
        [(9, 1), (3, 6)],
        [(7, 3), (19, 3), (14, 7)],
        [(4, 7), (21, 7), (21, 13), (4, 13), (4, 7)],
        [(13, 7), (13, 13)],
        [(10, 13), (5, 16), (1, 17)],
        [(12, 16), (7, 19), (1, 21)],
        [(14, 19), (8, 22), (1, 24)],
        [(10, 13), (12, 16), (14, 19), (15, 21), (14, 24), (10, 24), (8, 23)],
        [(22, 14), (17, 19)],
        [(13, 13), (17, 19), (20, 22), (24, 24)],
    ]


def _fit(paths, left, width):
    return [[(left + x * width / 24, y) for x, y in path] for path in paths]


def correction_spec():
    tree = [[(2, 8), (22, 8)], [(12, 1), (12, 23)],
            [(12, 8), (7, 15), (1, 21)], [(12, 8), (17, 15), (23, 21)]]
    water = [[(5, 2), (12, 5)], [(3, 10), (10, 13)], [(5, 22), (15, 15)]]
    yo = [[(4, 2), (21, 2), (13, 8)], [(8, 5), (14, 9)],
          [(1, 10), (23, 10), (19, 15)], [(13, 10), (13, 23), (8, 23)]]
    return {
        '象': [('象', _elephant())],
        '橡': [('木', _fit(tree, 0, 10)), ('象', _fit(_elephant(), 11, 13))],
        '潒': [('氵', _fit(water, 0, 8)), ('象', _fit(_elephant(), 9, 15))],
        '豫': [('予', _fit(yo, 0, 11)), ('象', _fit(_elephant(), 12, 12))],
    }


def correction_paths():
    return {c: [path for _, group in parts for path in group]
            for c, parts in correction_spec().items()}


def apply(glyphs):
    changed = set()
    for c, paths in correction_paths().items():
        if c not in glyphs:
            continue
        old = glyphs[c]
        notes = dict(old.notes)
        notes.setdefault('previous_source', old.source)
        notes.setdefault('previous_status', old.status)
        notes['proofread_elephant_correction'] = (
            f'{J_SOURCES[c]}: restore three separate left sweeps of 象 and '
            'connect the long right limb to the head baseline; independently laid out.')
        notes['proofread_elephant_scope'] = 'four exact keys; no recursive propagation or small-size approval'
        glyphs[c] = replace(old, paths=paths,
                            source='original:family.proofread_elephant_corrections',
                            status='structure-reviewed-large-size', notes=notes)
        changed.add(c)
    return changed
