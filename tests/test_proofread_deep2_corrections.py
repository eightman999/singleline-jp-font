"""Regressions for the 44-glyph primary J-source deep review, group 2."""
import copy
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from family.model import Glyph
from family.kanji import build_kanji,validate_glyph,geometry_fingerprint
from family.proofread_deep2_corrections import TARGETS,correction_paths,apply_corrections

REVIEW=frozenset('甗癱矚籌籑籖籭籯籰粛纎纒纖纛臟艷葼虁讖軈釁鐡鐵鑄鑞鑭鑲鑿靨顰饟驌驪驫髓鬈鬌鬐鬒鬖鬟鬠鬢鬣')


def test_exact_inventory_and_valid_unique_paths():
    p,n=correction_paths()
    assert len(REVIEW)==44 and len(TARGETS)==23 and set(p)==set(n)==TARGETS
    for paths in p.values():validate_glyph(paths)
    assert len({geometry_fingerprint(paths) for paths in p.values()})==23


def test_only_verified_targets_change_and_legacy_stays_intact():
    from glyphs.kanji import GLYPHS
    legacy=copy.deepcopy(GLYPHS)
    old,_=build_kanji(REVIEW)
    g={c:Glyph(c,old[c],advance=913) for c in REVIEW};before=copy.deepcopy(g)
    apply_corrections(g)
    assert {c for c in REVIEW if g[c].paths!=before[c].paths}==TARGETS
    assert set(g)==REVIEW and all(x.advance==913 for x in g.values())
    assert GLYPHS==legacy
    once=copy.deepcopy(g);apply_corrections(g);assert once==g


def test_absent_targets_not_inserted_and_cached_paths_not_aliased():
    g={'纒':Glyph('纒',[[(1,1),(2,2)]])};apply_corrections(g)
    assert set(g)=={'纒'}
    g['纒'].paths[0][0]=(0,0)
    assert correction_paths()[0]['纒'][0][0]!=(0,0)


def test_japanese_black_adjustment_is_only_the_internal_middle_bar():
    original,_=build_kanji({'纒'});after=correction_paths()[0]['纒']
    assert after[:8]==original['纒'][:8]
    assert after[9:]==original['纒'][10:]
    assert len(after)==len(original['纒'])-1
    assert after[8][0][1]==after[8][1][1]


def test_gate_internal_component_clears_top_box_ink_width():
    p=correction_paths()[0]['鑭']
    assert min(y for line in p[13:] for x,y in line)>=10.5
    assert (10.5-9)*35>20


def test_compact_bamboo_leaves_real_room_for_dense_body():
    p=correction_paths()[0]
    for c in '籌籖籭籰':
        assert max(y for line in p[c][:6] for x,y in line)<=4
        assert min(y for line in p[c][6:] for x,y in line)>=6


def test_nan_top_component_has_its_lower_edge():
    p=correction_paths()[0]['癱']
    assert any(len(line)==4 and line[0][1]==line[-1][1] and line[1][1]==line[2][1] and line[1][1]>line[0][1] for line in p)


def test_all_styles_four_sizes_ttf_and_sjpb_nonblank(tmp_path):
    from family.styles import STYLES
    from family.font_builder import build_font
    from family.bitmap import build_bitmaps
    from family.bitmap_reader import BitmapFont
    from PIL import ImageFont
    old,_=build_kanji(TARGETS)
    g=apply_corrections({c:Glyph(c,old[c],category='kanji') for c in sorted(TARGETS)})
    rendered=0
    for key,style in STYLES.items():
        path=tmp_path/f'{key}.ttf';build_font(g,style,path)
        for size in (16,18,24,32):
            build_bitmaps(g,style,size,tmp_path);b=BitmapFont(tmp_path/f'{key}-{size}.sjpb');f=ImageFont.truetype(str(path),size)
            for c in g:
                assert b.bitmap(c).any() and f.getmask(c,mode='1').getbbox()
                rendered+=2
    assert rendered==1472
