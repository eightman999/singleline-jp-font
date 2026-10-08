"""Regression for the independently authored rams-horn lower loop."""
from family.data_loader import load_glyphs
from family.jis_symbols import IPA


def test_rams_horn_has_closed_lower_loop_and_two_upper_horns():
    paths = IPA['ɤ']
    assert len(paths) == 1
    path = paths[0]
    junction = (12.0, 15.0)
    hits = [i for i, p in enumerate(path) if p == junction]
    assert len(hits) == 2
    loop = path[hits[0]:hits[1] + 1]
    assert loop[0] == loop[-1]
    assert max(y for x, y in loop) > junction[1]
    assert min(x for x, y in loop) < junction[0] < max(x for x, y in loop)
    assert path[0][0] < junction[0] < path[-1][0]
    assert path[0][1] < junction[1] and path[-1][1] < junction[1]


def test_rams_horn_family_uses_repaired_geometry():
    glyphs, _ = load_glyphs()
    assert glyphs['ɤ'].paths == IPA['ɤ']
    assert glyphs['ɤ'].category == 'alphabet'
