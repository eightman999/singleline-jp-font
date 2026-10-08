"""Independent-direction and mark-presence regressions, not pixel tracing."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from family.data_loader import MARKS,composed,load_glyphs
from family.model import Glyph


def test_grave_and_acute_have_opposite_slopes():
    def slope(mark):
        (x1,y1),(x2,y2)=MARKS[mark][0]
        return (y2-y1)/(x2-x1)
    assert slope('\u0300')>0 and slope('\u0301')<0


def test_above_marks_are_ordered_bottom_to_top_without_intersection():
    base=Glyph('A',[[(1,1),(12,1),(12,23)]])
    paths=composed(base,'\u0302\u0301')
    base_y=min(y for p in paths[:1] for x,y in p)
    lower=[y for x,y in paths[1]];upper=[y for x,y in paths[2]]
    assert max(upper)<min(lower)<max(lower)<base_y
    assert base.paths==[[(1,1),(12,1),(12,23)]]


def test_above_accents_replace_i_j_dot_but_below_preserves_it():
    from glyphs.ascii import GLYPHS
    for char in 'ij':
        base=Glyph(char,GLYPHS[char])
        assert len(composed(base,'\u0301'))==len(base.paths)
        assert len(composed(base,'\u0323'))==len(base.paths)+1
        assert base.paths==GLYPHS[char]


def test_existing_precomposed_legacy_stays_unchanged():
    from glyphs import symbols
    glyphs,_=load_glyphs(expand_kanji=False)
    for char in 'ÀÁàá':
        if char in symbols.GLYPHS:assert glyphs[char].paths==symbols.GLYPHS[char]
    assert glyphs['A\u0300'].paths != glyphs['A\u0301'].paths
    assert glyphs['A\u0302\u0300'].paths != glyphs['A\u0302\u0301'].paths
