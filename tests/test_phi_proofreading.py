"""Closed phi-symbol loop, kept distinct from open psi arms."""
from family.symbols import GLYPHS


def test_phi_symbol_has_closed_loop_and_vertical_stem():
    stem, loop = GLYPHS['ϕ']
    assert loop[0] == loop[-1]
    assert stem == [(12, 1), (12, 24)]
    assert min(x for x,y in loop) < 12 < max(x for x,y in loop)
    assert min(y for x,y in loop) > 1
    assert max(y for x,y in loop) < 24
