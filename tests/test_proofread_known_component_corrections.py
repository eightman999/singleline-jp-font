import copy
import pytest
import numpy as np
from PIL import ImageFont
from family.model import Glyph
from family.kanji import build_kanji,validate_glyph
from family.proofread_known_component_corrections import apply,correction_paths,turtle_paths,CORRECTED_CHARACTERS
from family.font_builder import build_font
from family.bitmap import build_bitmaps,raster
from family.bitmap_reader import BitmapFont
from family.styles import STYLES


def test_bounded_nonmutating_idempotent():
    source,_=build_kanji(set(CORRECTED_CHARACTERS)|{'明'})
    snapshot=copy.deepcopy(source)
    g={c:Glyph(c,p,category='kanji') for c,p in source.items()};untouched=g['明']
    assert apply(g)==set(CORRECTED_CHARACTERS)
    assert source==snapshot and g['明'] is untouched
    once=copy.deepcopy(g);apply(g);assert once==g
    for c,p in correction_paths().items():validate_glyph(p)
    p=correction_paths();p['難'][0][0]=(24,24)
    assert correction_paths()['難'][0][0]!=(24,24)


def test_modern_and_traditional_nan_crowns_differ():
    p=correction_paths();base,_=build_kanji({'難'})
    assert len(p['難'])==len(base['難'])+1
    assert [(0.5,16.0),(11.5,16.0)] in p['難']
    assert [(3.5,7.0),(8.5,7.0)] not in p['難']
    for c,n in [('儺',2),('攤',3),('灘',3)]:assert len(p[c])==n+len(p['難'])+1


def test_turtle_six_comb_levels_and_extended_middle_bars():
    p=turtle_paths();levels=set()
    for path in p:
        for (x,y),(xx,yy) in zip(path,path[1:]):
            if y==yy and min(x,xx)<=1 and max(x,xx)>=7 and y>=11:levels.add(y)
    assert levels=={11,13,15,17,19.5,22}
    assert [(0.0,13.0),(22.0,13.0)] in p
    assert [(0.0,19.5),(22.0,19.5)] in p
    assert [(16.0,14.5),(20.0,18.0)] in p
    assert [(20.0,14.5),(16.0,18.0)] in p


@pytest.mark.parametrize('key',STYLES)
def test_all_styles_three_sizes(tmp_path,key):
    gs={c:Glyph(c,p,category='kanji') for c,p in correction_paths().items()}
    path=tmp_path/(key+'.ttf');build_font(gs,STYLES[key],path)
    for size in (32,64,200):
        bf=BitmapFont(build_bitmaps(gs,STYLES[key],size,tmp_path)['binary'])
        font=ImageFont.truetype(str(path),size)
        for c,g in gs.items():
            assert font.getmask(c).getbbox()
            mask,*_=raster(g,STYLES[key],size)
            assert mask.any() and np.array_equal(bf.bitmap(c),mask>0)


def test_compatibility_identity_and_unrelated_turtle_stay_untouched(tmp_path):
    from fontTools.ttLib import TTFont
    g={'蘒':Glyph('蘒',[[(0,0),(1,1)]]),'蘒':Glyph('蘒',[[(2,2),(3,3)]]),'亀':Glyph('亀',[[(4,4),(5,5)]])}
    saved={c:g[c] for c in ('蘒','亀')};assert apply(g)=={'蘒'}
    assert all(g[c] is saved[c] for c in saved)
    path=tmp_path/'compat.ttf';build_font(g,STYLES['singleline'],path)
    f=TTFont(path)
    assert any((0x8612,'uFA20') in t.uvsDict.get(0xFE00,[]) for t in f['cmap'].tables if t.format==14)


def test_turtle_has_no_duplicate_segments_or_upper_mouth_extra_bar():
    p=turtle_paths();segments=[]
    for path in p:
        segments.extend(tuple(sorted((a,b))) for a,b in zip(path,path[1:]))
    assert len(segments)==len(set(segments))
    assert not any(a[1]==b[1]==8 for a,b in segments)
