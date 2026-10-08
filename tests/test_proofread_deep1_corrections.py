import copy
import pytest
from PIL import ImageFont
from fontTools.ttLib import TTFont
from family.model import Glyph
from family.kanji import validate_glyph,geometry_fingerprint
from family.styles import STYLES
from family.font_builder import build_font
from family.proofread_deep1_corrections import CORRECTED_CHARACTERS,CORRECTION_NOTES,correction_spec,correction_paths,apply
from glyphs.kanji import GLYPHS as LEGACY

TARGETS=set('㟴傀嵬廆䀹䆴乘嵊像亂亹劘嚢屬囑斸埀夔奭孅峯椶攩攪欞氂牽獻')

@pytest.mark.parametrize('char',CORRECTED_CHARACTERS)
def test_deep1_geometry_and_semantic_coverage(char):
    parts=correction_spec()[char]
    paths=correction_paths()[char]
    validate_glyph(paths)
    assert all(role and group for role,group in parts)
    assert sum(len(group) for role,group in parts)==len(paths)
    assert [line for role,group in parts for line in group]==paths
    assert CORRECTION_NOTES[char]
    paths[0][0]=(-99,-99)
    validate_glyph(correction_paths()[char])


def test_deep1_exact_keys_unique_and_idempotent():
    assert set(CORRECTED_CHARACTERS)==TARGETS==set(CORRECTION_NOTES)
    assert len({geometry_fingerprint(p) for p in correction_paths().values()})==28
    old_legacy=copy.deepcopy(LEGACY)
    g={c:Glyph(c,[[(0,0),(1,1)]],source='before',status='legacy-existing',category='kanji',notes={'flags':['test']}) for c in TARGETS|{'未','爨'}}
    previous=copy.deepcopy(g)
    assert apply(g)==TARGETS
    for c in ('未','爨'):assert g[c]==previous[c]
    for c in TARGETS:
        assert g[c].source=='original:family.proofread_deep1_corrections'
        assert g[c].status=='structure-reviewed-large-size'
        assert g[c].notes['previous_source']=='before'
        assert g[c].notes['previous_status']=='legacy-existing'
        assert g[c].notes['flags']==['test']
        assert g[c].advance==previous[c].advance
    once=copy.deepcopy(g);apply(g);assert g==once
    assert LEGACY==old_legacy


def test_deep1_specific_topology_constraints():
    sp=correction_spec()
    elephant=sp['像'][2][1]
    assert len(elephant)==6
    # Three distinct left sweeps, not the former two.
    assert [p[-1] for p in elephant[:3]]==[(8.,17.),(8.,21.),(8.,24.)]
    # 毛 remains entirely below the 厂 top at y12.
    assert min(y for p in sp['氂'][-1][1] for x,y in p)>=14
    # Both 百 boxes stop at y16, above the crossing legs of 大.
    assert max(y for role,ps in sp['奭'][1:] for p in ps for x,y in p)<=16
    # Both small 人 in 巫 stop inside its horizontal bars.
    witch=sp['欞'][-1][1]
    assert all(14<y<24 for p in witch[3:] for x,y in p)
    # No new cross-character replacement can be triggered by a missing key.
    assert apply({})==set()

@pytest.mark.parametrize('style',STYLES)
def test_deep1_compiles_reloads_and_renders(style,tmp_path):
    g={c:Glyph(c,p,category='kanji') for c,p in correction_paths().items()}
    path=tmp_path/f'{style}.ttf';build_font(g,STYLES[style],path)
    t=TTFont(path);assert set(t.getBestCmap())==set(map(ord,TARGETS))
    for size in [16,18,24,32,200]:
        f=ImageFont.truetype(str(path),size)
        assert all(f.getmask(c).getbbox() for c in TARGETS)
