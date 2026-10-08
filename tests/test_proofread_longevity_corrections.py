import copy
import pytest
from PIL import Image, ImageDraw, ImageChops, ImageFont
from fontTools.ttLib import TTFont
from family.model import Glyph
from family.kanji import validate_glyph
from family.styles import STYLES
from family.font_builder import build_font
from family.proofread_longevity_corrections import correction_spec, correction_paths, apply, CORRECTED_CHARACTERS
from glyphs.kanji import GLYPHS as LEGACY


def test_exact_targets_metadata_and_no_propagation():
    assert set(CORRECTED_CHARACTERS) == set('嶹幬擣檮濤燾璹疇禱躊隯')
    legacy = copy.deepcopy(LEGACY)
    gs = {c: Glyph(c, [[(1, 1), (2, 2)]], advance=913, width_factor=.8,
                  source='before', status='old', notes={'flags': ['retained']})
          for c in '嶹幬擣檮濤燾璹疇禱躊隯儔壔籌鑄'}
    old = copy.deepcopy(gs)
    assert apply(gs) == set('嶹幬擣檮濤燾璹疇禱躊隯')
    assert all(gs[c] == old[c] for c in '儔壔籌鑄')
    for c in CORRECTED_CHARACTERS:
        assert gs[c].source == 'original:family.proofread_longevity_corrections'
        assert gs[c].status == 'structure-reviewed-large-size'
        assert gs[c].notes['previous_source'] == 'before'
        assert gs[c].notes['previous_status'] == 'old'
        assert gs[c].notes['flags'] == ['retained']
        assert (gs[c].advance, gs[c].width_factor) == (913, .8)
    once = copy.deepcopy(gs)
    apply(gs)
    assert gs == once
    assert LEGACY == legacy
    assert apply({}) == set()


@pytest.mark.parametrize('char', CORRECTED_CHARACTERS)
def test_twelve_paths_spaced_bands_and_connections(char):
    parts = correction_spec()[char]
    shou = next(ps for role, ps in parts if role == '壽')
    assert len(shou) == 12
    factor = 19/24 if char == '燾' else 1
    assert shou[5][0][1] == pytest.approx(11*factor)
    assert shou[5][-1][1] == pytest.approx(14*factor)
    assert shou[10][0][1] == shou[7][0][1]
    assert shou[0][0][1] < shou[2][0][1] < shou[3][0][1] < shou[4][0][1] < shou[6][0][1] < shou[7][0][1] < shou[8][0][1]
    validate_glyph(correction_paths()[char])
    damaged = correction_paths()[char]
    damaged[0][0] = (-99, -99)
    validate_glyph(correction_paths()[char])


@pytest.mark.parametrize('style', STYLES)
def test_all_styles_compile_and_raster_bounds(style, tmp_path):
    gs = {c: Glyph(c, p, category='kanji') for c, p in correction_paths().items()}
    fp = tmp_path / f'{style}.ttf'
    build_font(gs, STYLES[style], fp)
    with TTFont(fp) as font:
        assert all(ord(c) in font.getBestCmap() for c in CORRECTED_CHARACTERS)
    for size in [32, 64, 200]:
        font = ImageFont.truetype(str(fp), size)
        for c in CORRECTED_CHARACTERS:
            tile = Image.new('L', (size + 40, size + 40), 255)
            ImageDraw.Draw(tile).text((20, 20), c, font=font, fill=0, anchor='lt')
            bbox = ImageChops.invert(tile).getbbox()
            assert bbox and min(bbox[:2]) > 0
            assert max(bbox[2:]) < size + 40
