"""Exact platform-independent source geometry, not hash-only normalization."""
import gzip
import hashlib
import importlib
import json
import math
from pathlib import Path
from unittest.mock import patch

from family import jis_symbols
from family.data_loader import load_glyphs

ROOT = Path(__file__).resolve().parents[1]
CHARACTERS = '◉◐◑◒◓☎⦿'


def digest(paths):
    return hashlib.sha256(json.dumps(paths, separators=(',', ':')).encode()).hexdigest()


def test_frozen_paths_match_original_full_precision_provenance():
    provenance = json.loads(gzip.decompress((ROOT / 'build/family/glyph-provenance.json.gz').read_bytes()))
    glyphs, _ = load_glyphs()
    for char in CHARACTERS:
        assert digest(glyphs[char].paths) == provenance[char]['centerline_sha256']
        assert glyphs[char].paths == jis_symbols.fixed_circle_paths(char)


def test_jis_module_does_not_depend_on_platform_trigonometry():
    before = {c: digest(jis_symbols.GLYPHS[c]) for c in CHARACTERS}
    with patch('math.sin', side_effect=AssertionError('platform sin used')), \
         patch('math.cos', side_effect=AssertionError('platform cos used')):
        importlib.reload(jis_symbols)
        assert {c: digest(jis_symbols.GLYPHS[c]) for c in CHARACTERS} == before


def test_fixed_paths_are_copied_not_shared():
    paths = jis_symbols.fixed_circle_paths('◉')
    paths[0][0] = (0, 0)
    assert jis_symbols.fixed_circle_paths('◉')[0][0] != (0, 0)


def test_circles_keep_intended_geometry_and_empty_counters():
    for char, inner in [('◉', 8.5), ('⦿', 8.5), ('◐', 9), ('◑', 9), ('◒', 9), ('◓', 9)]:
        paths = jis_symbols.fixed_circle_paths(char)
        assert len(paths) == 33
        for quad in paths[:32]:
            assert len(quad) == 5 and quad[0] == quad[-1]
            for point, radius in zip(quad[:4], [10, 10, inner, inner]):
                assert abs(math.hypot(point[0]-12, point[1]-12)-radius) < 1e-12
    for char, axis, direction in [('◐',0,-1), ('◑',0,1), ('◒',1,1), ('◓',1,-1)]:
        assert all(direction*(p[axis]-12) >= -1e-12 for p in jis_symbols.fixed_circle_paths(char)[-1])
