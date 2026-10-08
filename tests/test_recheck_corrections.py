"""Local invariants for the high-resolution recheck repairs."""
import copy
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from family.proofread_recheck_corrections import TARGETS,correction_paths,apply_corrections
from family.kanji import validate_glyph,geometry_fingerprint,build_kanji
from family.model import Glyph


def test_target_inventory_validity_and_uniqueness():
    p,n=correction_paths()
    assert len(TARGETS)==38 and set(p)==set(n)==TARGETS
    assert '鑭' not in TARGETS and '欄' not in TARGETS
    for paths in p.values():validate_glyph(paths)
    assert len({geometry_fingerprint(paths) for paths in p.values()})==38


def test_does_not_add_missing_targets_or_mutate_sources():
    from glyphs.kanji import GLYPHS
    legacy=copy.deepcopy(GLYPHS)
    g={'聽':Glyph('聽',[[(0,0),(1,1)]],advance=876),'鑭':Glyph('鑭',[[(2,2),(4,4)]])}
    old=copy.deepcopy(g);apply_corrections(g)
    assert set(g)==set(old) and g['鑭']==old['鑭']
    assert g['聽'].advance==876 and GLYPHS==legacy
    once=copy.deepcopy(g);apply_corrections(g);assert g==once
    g['聽'].paths[0][0]=(0,0);assert correction_paths()[0]['聽'][0][0]!=(0,0)


def test_two_crosses_do_not_share_the_same_vertical():
    p,_=correction_paths()
    verticals=[line for line in p['𠥼'] if line[0][0]==line[-1][0]]
    assert len(verticals)==2 and {line[0][0] for line in verticals}=={6,17}


def test_gate_added_parts_are_below_top_boxes():
    p,_=correction_paths()
    for c in '𨴐𨵱𨷻':
        assert min(y for line in p[c][5:] for x,y in line)>=11


def test_every_generated_style_strike_ttf_sjpb_has_ink(tmp_path):
    from family.styles import STYLES
    from family.font_builder import build_font
    from family.bitmap import build_bitmaps
    from family.bitmap_reader import BitmapFont
    from PIL import ImageFont
    old,_=build_kanji(TARGETS)
    glyphs=apply_corrections({c:Glyph(c,old[c],category='kanji') for c in sorted(TARGETS)})
    count=0
    for key,style in STYLES.items():
        path=tmp_path/f'{key}.ttf';build_font(glyphs,style,path)
        for size in (16,18,24,32):
            build_bitmaps(glyphs,style,size,tmp_path)
            b=BitmapFont(tmp_path/f'{key}-{size}.sjpb');f=ImageFont.truetype(str(path),size)
            for c in glyphs:
                assert b.bitmap(c).any() and f.getmask(c,mode='1').getbbox()
                count+=2
    assert count==2432
