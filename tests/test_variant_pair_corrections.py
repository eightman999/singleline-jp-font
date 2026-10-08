from copy import deepcopy
import numpy as np
from PIL import ImageFont
from family.kanji import build_kanji,validate_glyph
from family.model import Glyph
from family.proofread_variant_pair_corrections import TARGETS,PAIRS,apply_corrections,correction_paths
from family.font_builder import build_font
from family.bitmap import build_bitmaps
from family.bitmap_reader import BitmapFont
from family.styles import STYLES

def source():
    p,_=build_kanji('剝剥塡填頰頬一')
    return {c:Glyph(c,v,category='kanji') for c,v in p.items()}

def test_only_three_targets_metrics_legacy_and_counterparts_preserved():
    before=source();old=deepcopy(before);after=apply_corrections(deepcopy(before))
    assert {c for c in before if before[c].paths!=after[c].paths}==TARGETS
    for c in after:
        validate_glyph(after[c].paths)
        assert after[c].advance==before[c].advance
        assert after[c].width_factor==before[c].width_factor
    assert source()==old
    assert apply_corrections(deepcopy(after))==after
    assert apply_corrections({})=={}

def test_exact_structural_regions_and_shared_parts():
    old=source();p,_=correction_paths()
    assert p['剥'][3:]==old['剝'].paths[3:]
    assert p['剥'][0]==[(2.7,1.5),(14.,1.5),(14.,10.5)]
    assert p['填'][:3]==old['塡'].paths[:3]
    assert p['填'][4]==[(16.5,.5),(16.5,7.)]
    assert p['頬'][6:]==old['頰'].paths[7:]
    assert p['頬'][5]==[(.5,13.),(10.5,13.)]

def test_returned_glyphs_do_not_alias_correction_cache():
    g=apply_corrections(source());original=deepcopy(correction_paths()[0])
    g['剥'].paths[0][0]=(99,99)
    assert correction_paths()[0]==original

def test_pairs_distinct_in_all_styles_and_sizes(tmp_path):
    before=source();after=apply_corrections(deepcopy(before))
    for a,b in PAIRS:assert before[a].paths==before[b].paths
    cases=0
    for style in STYLES.values():
        ttf=tmp_path/f'{style.key}.ttf';build_font(after,style,ttf)
        for size in (16,18,24,32):
            build_bitmaps(after,style,size,tmp_path)
            bitmap=BitmapFont(tmp_path/f'{style.key}-{size}.sjpb');font=ImageFont.truetype(str(ttf),size)
            for a,b in PAIRS:
                ma,mb=bitmap.bitmap(a),bitmap.bitmap(b)
                assert ma.any() and mb.any()
                assert not np.array_equal(ma,mb),(style.key,size,a,b,'SJPB')
                aa,bb=font.getmask(a,mode='1'),font.getmask(b,mode='1')
                assert any(aa) and any(bb)
                assert (aa.size,bytes(aa))!=(bb.size,bytes(bb)),(style.key,size,a,b,'TTF')
                cases+=2
    assert cases==192
