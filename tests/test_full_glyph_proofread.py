"""Proof inventory invariants, without certifying letterform correctness."""
from family.model import Glyph
from family.tools.full_glyph_proofread import collision_groups, expected_blank, identity, source_inventory


def test_blank_requires_semantics_not_empty_paths():
    assert expected_blank(' ', Glyph(' ', []))
    assert not expected_blank('字', Glyph('字', []))


def test_sequence_identity_and_review_pending():
    rows = source_inventory({'a\u0301': Glyph('a\u0301', [[(1,2),(2,3)]])})
    assert rows[0]['id'] == 'U+0061+U+0301'
    assert rows[0]['kind'] == 'sequence'
    assert rows[0]['visual_review'] == 'pending'
    assert len(rows[0]['source_sha256']) == 64


def test_blank_and_missing_are_not_collisions():
    rows = [dict(id=c, exists=True, empty=False, signature='same') for c in 'ab']
    rows += [dict(id='space',exists=True,empty=True,signature='same'),dict(id='missing',exists=False,signature='same')]
    assert collision_groups(rows,'signature') == {'same':['a','b']}


def test_source_hash_changes_with_geometry():
    a = source_inventory({'a':Glyph('a',[[(1,2),(2,3)]])})[0]
    b = source_inventory({'a':Glyph('a',[[(1,2),(3,3)]])})[0]
    assert a['source_sha256'] != b['source_sha256']
    assert identity('𠮷') == 'U+20BB7'


def test_direct_sequence_render_selects_one_glyph():
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from family.tools.full_glyph_proofread import DirectFont
    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder(['.notdef', 'a', 'sequence'])
    glyphs = {}
    for name, width in [('.notdef',0),('a',100),('sequence',700)]:
        pen = TTGlyphPen(None)
        if width:
            pen.moveTo((0,0));pen.lineTo((width,0));pen.lineTo((width,700));pen.lineTo((0,700));pen.closePath()
        glyphs[name] = pen.glyph()
    builder.setupCharacterMap({97:'a'})
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics({n:(800,0) for n in glyphs})
    builder.setupHorizontalHeader(ascent=800,descent=-200)
    builder.setupNameTable({'familyName':'Test','styleName':'Regular','psName':'Test-Regular'})
    builder.setupOS2(sTypoAscender=800,sTypoDescender=-200,usWinAscent=800,usWinDescent=200)
    builder.setupPost();builder.setupMaxp()
    direct = DirectFont(builder.font, {'a':'a','aa':'sequence'})
    scalar = direct.mask('a', 64)
    sequence = direct.mask('aa', 64)
    assert sequence[0].getbbox()[2] > scalar[0].getbbox()[2] * 4
    assert sequence[2] == scalar[2]  # one selected glyph, not two scalar advances
    assert direct.mask('missing',64) is None


def test_variable_grid_discrete_points_and_numeric_checks():
    from family.tools.full_glyph_proofread import VARIABLE_GRID, outline_issues
    assert len(VARIABLE_GRID)==9
    assert {p['wght'] for p in VARIABLE_GRID}=={200,400,700}
    assert {p['slnt'] for p in VARIABLE_GRID}=={0,-6,-12}
    assert outline_issues([('lineTo',((10,20),))],(0,0,10,20),1000,1000)==[]
    assert 'non-finite-coordinate-or-metric' in outline_issues([('lineTo',((float('nan'),0),))],None,1000,1000)
    assert 'zero-or-negative-ink-bbox-area' in outline_issues([], (0,0,0,20),0,1000)
    assert 'negative-advance' in outline_issues([],None,-1,1000)
    assert 'bbox-beyond-8-em-review-flag' in outline_issues([],(0,0,9000,20),1000,1000)
