"""Target-only upper-kanji layout regressions with native generated artifacts."""
import copy
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from family.proofread_upper_corrections import TARGETS,WIND,FIGHT,GHOST,WHEAT,WALK,correction_paths,apply_corrections
from family.kanji import validate_glyph,geometry_fingerprint,build_kanji
from family.model import Glyph


def bbox(paths):
    points=[p for line in paths for p in line]
    return min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)


def test_exact_target_inventory_and_distinct_valid_geometry():
    paths,notes=correction_paths()
    assert len(paths)==37 and set(paths)==set(TARGETS)==set(notes)
    assert len({geometry_fingerprint(p) for p in paths.values()})==37
    for p in paths.values():validate_glyph(p)


def test_local_application_does_not_mutate_legacy_or_other_glyphs():
    from glyphs.kanji import GLYPHS
    legacy=copy.deepcopy(GLYPHS)
    originals={c:Glyph(c,[[(0,0),(24,24)]],advance=901) for c in TARGETS|{'木'}}
    snapshot=copy.deepcopy(originals);apply_corrections(originals)
    assert originals['木']==snapshot['木'] and GLYPHS==legacy
    assert set(originals)==set(snapshot)
    assert all(originals[c].advance==901 for c in TARGETS)
    originals['舞'].paths[0][0]=(0,0)
    assert correction_paths()[0]['舞'][0][0]!=(0,0)


def test_missing_targets_are_not_inserted_and_apply_is_idempotent():
    g={'舞':Glyph('舞',[[(0,0),(1,1)]])};apply_corrections(g)
    once=copy.deepcopy(g);apply_corrections(g)
    assert g==once and set(g)=={'舞'}


@pytest.mark.parametrize('group,prefix,left,top,right,bottom',[
    (WIND,6,13,2,23,19),(FIGHT,10,4,10,20,23),
    (GHOST,8,14,2,23,19),(WHEAT,11,13,2,23,22),(WALK,7,13,1,23,20)])
def test_added_components_stay_in_reserved_regions(group,prefix,left,top,right,bottom):
    paths,_=correction_paths()
    for c in group:
        x0,y0,x1,y1=bbox(paths[c][prefix:])
        assert x0>=left-1e-8 and y0>=top-1e-8
        assert x1<=right+1e-8 and y1<=bottom+1e-8


def test_gate_interiors_and_dance_crown_are_separated():
    paths,_=correction_paths()
    for c in '閘閴':assert bbox(paths[c][5:])[1]>=11
    crown=paths['舞'][:8]
    assert [line for line in crown if line[0][0]==line[-1][0]]==[
        [(5.,4.),(5.,12.)],[(10.,4.),(10.,12.)],[(15.,4.),(15.,12.)],[(20.,4.),(20.,12.)]]
    assert bbox(paths['舞'][8:])[1]>=14


def test_all_styles_strikes_generated_ttf_and_sjpb_are_nonblank(tmp_path):
    from family.styles import STYLES
    from family.font_builder import build_font
    from family.bitmap import build_bitmaps
    from family.bitmap_reader import BitmapFont
    from PIL import ImageFont
    original,_=build_kanji(TARGETS)
    glyphs=apply_corrections({c:Glyph(c,original[c],category='kanji') for c in sorted(TARGETS)})
    count=0
    for key,style in STYLES.items():
        ttf=tmp_path/f'{key}.ttf';build_font(glyphs,style,ttf)
        for size in (16,18,24,32):
            build_bitmaps(glyphs,style,size,tmp_path)
            bitmap=BitmapFont(tmp_path/f'{key}-{size}.sjpb')
            ft=ImageFont.truetype(str(ttf),size)
            for c in glyphs:
                assert bitmap.bitmap(c).any()
                assert ft.getmask(c,mode='1').getbbox() is not None
                count+=2
    assert count==2368
