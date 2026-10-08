"""Real Unicode shaping must not be confused with direct glyph rendering."""
import pytest
from fontTools.ttLib import TTFont
from family.data_loader import load_glyphs
from family.font_builder import build_font
from family.styles import STYLES
from family.tools.verify_sequence_shaping import audit


@pytest.fixture(scope='module')
def glyphs():
    return load_glyphs()[0]


def test_real_canonical_and_svs_paths_preserve_file(tmp_path,glyphs):
    keys={'A','À','Á','\u0300','\u0301','A\u0300','A\u0301','侮','侮'}
    subset={t:glyphs[t] for t in keys}
    path=tmp_path/'probe.ttf';build_font(subset,STYLES['singleline'],path)
    before=path.read_bytes();order=TTFont(path).getGlyphOrder()
    report=audit(path,tmp_path/'report',subset,render=False)
    assert report['summary']['sequence_count']==2
    assert report['summary']['normal_nfc_pixel_equal']==2
    assert report['summary']['normal_missing']==0
    assert report['summary']['svs_count']==1
    assert report['summary']['svs_pass']==1
    assert all(r['normal_glyphs'] for r in report['sequences'])
    assert path.read_bytes()==before
    assert TTFont(path).getGlyphOrder()==order


def test_composition_difference_is_review_candidate_not_proven_defect(tmp_path,glyphs):
    keys={'A','À','\u0300','A\u0300'}
    subset={t:glyphs[t] for t in keys}
    path=tmp_path/'probe.ttf';build_font(subset,STYLES['singleline'],path)
    r=audit(path,tmp_path/'report',subset,render=False)['sequences'][0]
    assert r['normal_equals_nfc_pixels']
    assert r['status'] in {'routing-equivalent','visual-review-required'}
    assert 'Diagnostic only' in r['ccmp_off_note']
