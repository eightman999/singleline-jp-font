import copy
import pytest
from PIL import ImageFont
from fontTools.ttLib import TTFont
from family.model import Glyph
from family.proofread_middle_corrections import apply,correction_paths,CORRECTED_CHARACTERS
from family.font_builder import build_font
from family.bitmap import raster,build_bitmaps
from family.bitmap_reader import BitmapFont
import numpy as np
from family.styles import STYLES


def test_exact_targets_finite_grid_and_no_aliasing():
    p=correction_paths()
    assert set(p)==set('截旭昶曆毧毬毯毱氊氤氳爬瓞瓰瓱瓲瓸甅')
    assert len(p)==18
    for paths in p.values():
        assert paths
        for path in paths:
            assert len(path)>=2
            for x,y in path:assert 0<=x<=24 and 0<=y<=24
    p['旭'][0][0]=(-1,-1)
    assert correction_paths()['旭'][0][0]!=(-1,-1)


def test_apply_bounded_nonmutating_idempotent():
    target=Glyph('旭',[[(0,0),(1,1)]],advance=923,width_factor=.9,notes={'keep':17})
    untouched=Glyph('明',[[(1,2),(3,4)]])
    original=copy.deepcopy(target)
    g={'旭':target,'明':untouched}
    assert apply(g)=={'旭'}
    assert target==original and g['明'] is untouched
    for k in ('advance','width_factor','filled','category'):assert getattr(g['旭'],k)==getattr(original,k)
    assert g['旭'].notes['keep']==17
    assert g['旭'].source=='original:family.proofread_middle_corrections'
    assert g['旭'].status=='structure-reviewed-large-size'
    assert g['旭'].notes['previous_source']==original.source
    assert g['旭'].notes['previous_status']==original.status
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
