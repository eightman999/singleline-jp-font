import copy
import pytest
from PIL import ImageFont
from fontTools.ttLib import TTFont
from family.model import Glyph
from family.proofread_deep3_corrections import apply,correction_paths,CORRECTED_CHARACTERS
from family.font_builder import build_font
from family.bitmap import raster,build_bitmaps
from family.bitmap_reader import BitmapFont
import numpy as np
from family.styles import STYLES


def test_exact_targets_finite_grid_and_no_aliasing():
    p=correction_paths()
    assert set(p)==set('鱜鱥黌鼇鼈齏蘒𠠇𡑮𡿺𢦏𥧔𦥯')
    assert len(p)==13
    for paths in p.values():
        assert paths
        for path in paths:
            assert len(path)>=2
            for x,y in path:assert 0<=x<=24 and 0<=y<=24
    p['鱜'][0][0]=(-1,-1)
    assert correction_paths()['鱜'][0][0]!=(-1,-1)


def test_apply_bounded_nonmutating_idempotent():
    target=Glyph('鱜',[[(0,0),(1,1)]],advance=923,width_factor=.9,notes={'keep':17})
    untouched=Glyph('明',[[(1,2),(3,4)]])
    original=copy.deepcopy(target)
    g={'鱜':target,'明':untouched}
    assert apply(g)=={'鱜'}
    assert target==original and g['明'] is untouched
    for k in ('advance','width_factor','filled','category'):assert getattr(g['鱜'],k)==getattr(original,k)
    assert g['鱜'].notes['keep']==17
    assert g['鱜'].source=='original:family.proofread_deep3_corrections'
    assert g['鱜'].status=='structure-reviewed-large-size'
    assert g['鱜'].notes['previous_source']==original.source
    assert g['鱜'].notes['previous_status']==original.status
    once=copy.deepcopy(g);apply(g);assert once==g


@pytest.mark.parametrize('key',STYLES)
def test_all_styles_ttf_and_four_bitmap_sizes(tmp_path,key):
    glyphs={c:Glyph(c,p,category='kanji') for c,p in correction_paths().items()}
    path=tmp_path/(key+'.ttf');build_font(glyphs,STYLES[key],path)
    font=TTFont(path);assert set(map(ord,glyphs))<=set(font.getBestCmap())
    for size in (16,18,24,32,48,96,200):
        result=build_bitmaps(glyphs,STYLES[key],size,tmp_path)
        decoded=BitmapFont(result['binary'])
        pil=ImageFont.truetype(str(path),size)
        for c,g in glyphs.items():
            assert pil.getmask(c).getbbox() is not None
            mask,advance,left,baseline=raster(g,STYLES[key],size)
            assert mask.any() and advance>0
            assert np.array_equal(decoded.bitmap(c),mask>0)
            assert not mask[0].any() and not mask[-1].any()


def test_retained_crowns_keep_both_crossing_tap_strokes():
    from family.proofread_deep3_corrections import _AO_CROWN,_BIE_CROWN
    assert len(_AO_CROWN)==11 and len(_BIE_CROWN)==10
    for crown in (_AO_CROWN,_BIE_CROWN):
        # The final original 攵 path goes down-right; the preceding one
        # goes down-left. Neither may disappear when the lower 黽 changes.
        assert crown[-1][0][0] < crown[-1][-1][0]
        assert crown[-2][0][0] > crown[-2][-1][0]


def test_compatibility_identity_not_normalized(tmp_path):
    target=Glyph('蘒', [[(1,1),(2,2)]],category='kanji')
    unified=Glyph('蘒', [[(3,3),(4,4)]],category='kanji')
    g={'蘒':target,'蘒':unified}
    assert apply(g)=={'蘒'}
    assert g['蘒'] is unified
    p=tmp_path/'compat.ttf';build_font(g,STYLES['singleline'],p)
    f=TTFont(p)
    tables=[t for t in f['cmap'].tables if t.format==14]
    assert any((0x8612,'uFA20') in t.uvsDict.get(0xFE00,[]) for t in tables)
    result=build_bitmaps(g,STYLES['singleline'],32,tmp_path)
    decoded=BitmapFont(result['binary'])
    assert np.array_equal(decoded.bitmap('蘒\ufe00'),decoded.bitmap('蘒'))
