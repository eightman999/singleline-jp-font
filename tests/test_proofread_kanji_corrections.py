"""Regression tests for the bounded new-family-only Japanese topology repairs."""
import copy
from dataclasses import asdict
from pathlib import Path

import pytest
from PIL import ImageFont
from fontTools.ttLib import TTFont

from family.data_loader import load_glyphs
from family.font_builder import build_font
from family.kanji import geometry_fingerprint, validate_glyph
from family.model import Glyph
from family.proofread_kanji_corrections import (
    CORRECTED_CHARACTERS, CORRECTION_NOTES, apply, correction_paths,
)
from family.styles import STYLES
from glyphs.kanji import GLYPHS as LEGACY


@pytest.mark.parametrize('char', CORRECTED_CHARACTERS)
def test_paths_are_valid_and_independent(char):
    a = correction_paths()
    validate_glyph(a[char])
    assert a[char]
    a[char][0][0] = (-100, -100)
    validate_glyph(correction_paths()[char])


def test_exact_target_set_no_duplicate_shapes():
    paths = correction_paths()
    assert set(paths) == set('㖨䐜咎嘷晷槩櫜洴籘蓱') == set(CORRECTION_NOTES)
    assert len({geometry_fingerprint(p) for p in paths.values()}) == 10


def test_apply_only_present_targets_and_preserves_metrics():
    g = Glyph('咎', [[(0,0),(1,1)]], advance=937, width_factor=.9,
              source='existing', status='composition-draft', category='kanji',
              notes={'flags': ['non_japanese_ids_variant'], 'other': 17})
    other = Glyph('未', [[(2,2),(4,4)]])
    original = copy.deepcopy(g)
    glyphs = {'咎': g, '未': other}
    assert apply(glyphs) == {'咎'}
    assert glyphs['未'] is other
    assert g == original
    for key in ('advance','width_factor','filled','category'):
        assert getattr(glyphs['咎'], key) == getattr(g, key)
    assert glyphs['咎'].source == 'original:family.proofread_kanji_corrections'
    assert glyphs['咎'].status == 'structure-reviewed-large-size'
    assert glyphs['咎'].notes['previous_source'] == g.source
    assert glyphs['咎'].notes['previous_status'] == g.status
    assert glyphs['咎'].notes['flags'] == g.notes['flags']
    assert glyphs['咎'].notes['other'] == 17
    assert 'proofread_kanji_correction' in glyphs['咎'].notes
    once = copy.deepcopy(glyphs)
    assert apply(glyphs) == {'咎'}
    assert glyphs == once


def test_legacy_dictionary_unchanged():
    old = copy.deepcopy(LEGACY)
    g, _ = load_glyphs()
    untreated = {c: geometry_fingerprint(v.paths) for c,v in g.items()
                 if c not in CORRECTED_CHARACTERS}
    apply(g)
    assert LEGACY == old
    assert all(geometry_fingerprint(g[c].paths) == fp for c,fp in untreated.items())


@pytest.mark.parametrize('style_key', STYLES)
def test_subset_font_reloads_and_renders_every_size(style_key, tmp_path):
    # Ten named characters only; absence of other characters is intentional.
    glyphs = {c: Glyph(c, p, category='kanji') for c,p in correction_paths().items()}
    path = tmp_path / (style_key + '.ttf')
    build_font(glyphs, STYLES[style_key], path)
    font = TTFont(path)
    assert set(font.getBestCmap()) == {ord(c) for c in CORRECTED_CHARACTERS}
    for size in (16,18,24,32):
        pil = ImageFont.truetype(str(path), size)
        for c in CORRECTED_CHARACTERS:
            assert pil.getmask(c).getbbox() is not None
            assert font['glyf'][font.getBestCmap()[ord(c)]].numberOfContours > 0
