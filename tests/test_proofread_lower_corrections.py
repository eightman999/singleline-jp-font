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
from family.proofread_lower_corrections import (
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
    assert set(paths) == set('䰗䰠亙儔壔壽囟廸廹廼剋尅匙彪奠奥奧嶴冖宀凾巫') == set(CORRECTION_NOTES)
    assert len({geometry_fingerprint(p) for p in paths.values()}) == 22


def test_apply_only_present_targets_and_preserves_metrics():
    g = Glyph('囟', [[(0,0),(1,1)]], advance=937, width_factor=.9,
              source='existing', status='composition-draft', category='kanji',
              notes={'flags': ['non_japanese_ids_variant'], 'other': 17})
    other = Glyph('未', [[(2,2),(4,4)]])
    original = copy.deepcopy(g)
    glyphs = {'囟': g, '未': other}
    assert apply(glyphs) == {'囟'}
    assert glyphs['未'] is other
    assert g == original
    for key in ('advance','width_factor','filled','category'):
        assert getattr(glyphs['囟'], key) == getattr(g, key)
    assert glyphs['囟'].source == 'original:family.proofread_lower_corrections'
    assert glyphs['囟'].status == 'structure-reviewed-large-size'
    assert glyphs['囟'].notes['previous_source'] == g.source
    assert glyphs['囟'].notes['previous_status'] == g.status
    assert glyphs['囟'].notes['flags'] == g.notes['flags']
    assert glyphs['囟'].notes['other'] == 17
    assert 'proofread_lower_correction' in glyphs['囟'].notes
    once = copy.deepcopy(glyphs)
    assert apply(glyphs) == {'囟'}
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
    # Twenty-two named characters only; absence of other characters is intentional.
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


def test_specific_topology_regressions():
    p = correction_paths()
    # 囟's only outside-box stroke is its leading slant. Both crossing
    # strokes now sit below the box's y=5 top and above its y=24 bottom.
    assert all(5 < y < 24 for line in p['囟'][2:] for x,y in line)
    # 亙's two internal strokes must not regress to horizontal box bars.
    assert all(line[0][1] != line[-1][1] for line in p['亙'][3:5])
    # 廴 and the inside glyph have separate horizontal regions. The second
    # 廴 stroke sweeps below the inside, so it is deliberately excluded.
    for c in '廸廹廼':
        assert max(x for x,y in p[c][0]) <= 7
        assert min(x for line in p[c][2:] for x,y in line) >= 9
    # The intervening 一 must remain separate from 工 and the bottom 口寸.
    assert [(2.0,17.0),(23.0,17.0)] in p['壽']
