"""Family-only topology and actual-render regression tests for near-forms."""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from family.model import Glyph
from family.proofread_corrections import GLYPHS, apply_corrections


def test_left_stem_levels_and_shared_middle():
    assert [GLYPHS[c][1][0][1] for c in '己已巳'] == [14,9,3]
    assert all(GLYPHS[c][0][-1] == (3,14) for c in '己已巳')


def test_horizontal_length_relations():
    for short_top, long_top, bottom_index in [('未','末',1),('土','士',2)]:
        def width(c,i):return GLYPHS[c][i][-1][0]-GLYPHS[c][i][0][0]
        assert width(short_top,0) < width(short_top,bottom_index)
        assert width(long_top,0) > width(long_top,bottom_index)
        assert abs(width(short_top,0)-width(short_top,bottom_index)) == 8


def test_tall_variant_has_connected_ladder_not_comb():
    paths=GLYPHS['髙']
    assert [(6,4),(6,14)] in paths and [(18,4),(18,14)] in paths
    assert [(6,9),(18,9)] in paths


def test_overrides_copy_paths_preserve_metrics_and_do_not_add_absent_glyphs():
    old=Glyph('己',[[(0,0),(1,1)]],advance=987,width_factor=.9,notes={'audit':'kept'})
    untouched=copy.deepcopy(old)
    glyphs={'己':old}
    apply_corrections(glyphs)
    assert set(glyphs)=={'己'}
    assert old==untouched
    assert glyphs['己'].advance==987 and glyphs['己'].width_factor==.9
    assert glyphs['己'].notes['audit']=='kept'
    glyphs['己'].paths[0][0]=(0,0)
    assert GLYPHS['己'][0][0]==(3,3)


def test_legacy_source_is_not_mutated_by_loader():
    from glyphs.kanji import GLYPHS as legacy
    from family.data_loader import load_glyphs
    before=copy.deepcopy(legacy)
    glyphs,_=load_glyphs(expand_kanji=False)
    assert legacy==before
    assert glyphs['己'].paths != legacy['己']
    assert glyphs['高'].paths == legacy['高']
    assert glyphs['吉'].paths == legacy['吉']


def test_all_styles_all_sizes_ttf_and_sjpb_remain_distinct(tmp_path):
    from family.tools.priority_correction_pilot import build_pilot
    result=build_pilot(tmp_path, include_before=False)
    assert result['after']['glyph_renders']==704
    assert result['after']['pair_comparisons']==448
    assert result['after']['indistinguishable_pair_cases']==0
