"""Independent structural QA for the experimental family.

Run quick source/sample tests:
  python -m pytest tests/test_family.py -k 'not TestFullArtifacts'
Run release verification (missing outputs are failures, never successes):
  python verify_family.py

These tests establish encoding, binary integrity and actual variation, not
legibility or suitability for names/legal documents. Composition drafts remain
unreviewed, even when every test passes.
"""
from collections import Counter
from functools import lru_cache
from dataclasses import replace
import gzip
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import pytest
from PIL import Image, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from family.bitmap import BitmapFont, HEADER, INDEX, build_bitmaps, raster
from family.data_loader import load_glyphs
from family.font_builder import build_font, feature_glyphs, standard_variants
from family.geometry import centerlines, contours, make_glyph
from family.model import Glyph, glyph_name
from family.styles import STYLES, variable_style
from build_family import compress_centerlines, write_centerlines
from family.tools.package_family import editable_centerlines

DATA = ROOT / 'family' / 'data'
OUTPUT = Path(os.environ.get('FAMILY_OUTPUT', ROOT / 'build' / 'family'))
STYLE_KEYS = ('singleline', 'pc98-mincho', 'gothic', 'italian', 'serif', 'italic', 'subscript', 'superscript')
STRIKE_SIZES = (16, 18, 24, 32)
EXPECTED_LEVELS = {0: 1183, 1: 2965, 2: 3390, 3: 1259, 4: 2436}
SAMPLES = ('A', 'a', 'g', '2', '+', '日', '語', '高', '髙', '𠮷', '∑', '☀')


def json_read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def required_artifacts():
    return [*(Path('static') / f'SinglelineJPLab-{s}.ttf' for s in STYLE_KEYS),
            *(Path('variable') / f'SinglelineJPLab-{s}-VF.ttf' for s in ('gothic', 'serif')),
            *(Path('bitmaps') / f'{s}-{size}.{ext}' for s in STYLE_KEYS for size in STRIKE_SIZES for ext in ('sjpb', 'json', 'png')),
            *(Path(p) for p in ('coverage.json', 'centerlines.svgz', 'glyph-provenance.json.gz', 'build-summary.json'))]


def artifact(relative):
    p = OUTPUT / relative
    if not p.is_file():
        message = f'INCOMPLETE BUILD: missing {p}'
        if os.environ.get('FAMILY_REQUIRE_OUTPUTS') == '1':
            pytest.fail(message)
        pytest.skip(message)
    return p


def static_path(key):
    return artifact(Path('static') / f'SinglelineJPLab-{key}.ttf')


def coords(g):
    return np.asarray(g.coordinates, dtype=float)


def topology(g):
    return g.numberOfContours, tuple(getattr(g, 'endPtsOfContours', ())), len(getattr(g, 'coordinates', ()))


@lru_cache(maxsize=32)
def _hb_font(path, mtime_ns):
    font = hb.Font(hb.Face(Path(path).read_bytes()))
    font.scale = (1000, 1000)
    hb.ot_font_set_funcs(font)
    return font


def shape(path, text, features=None, *, preserve=False):
    path = Path(path)
    font = _hb_font(str(path.resolve()), path.stat().st_mtime_ns)
    buf = hb.Buffer()
    if preserve:
        buf.flags = hb.BufferFlags.PRESERVE_DEFAULT_IGNORABLES | hb.BufferFlags.DO_NOT_INSERT_DOTTED_CIRCLE
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {})
    return [i.codepoint for i in buf.glyph_infos], list(buf.glyph_positions)


def source_entries(source):
    entries = {glyph_name(c): (g, None) for c, g in source.items()}
    for c in feature_glyphs(source):
        for tag in ('sups', 'subs'):
            entries[glyph_name(c) + '.' + tag] = (source[c], tag)
    return entries


def assert_font_vertical_bounds(font):
    failures = []
    for name in font.getGlyphOrder():
        g = font['glyf'][name]
        if not g.numberOfContours:
            continue
        g.recalcBounds(font['glyf'])
        limits = {
            'OS/2 Win': (-font['OS/2'].usWinDescent, font['OS/2'].usWinAscent),
            'OS/2 typo': (font['OS/2'].sTypoDescender, font['OS/2'].sTypoAscender),
            'hhea': (font['hhea'].descent, font['hhea'].ascent),
        }
        for kind, (bottom, top) in limits.items():
            if g.yMin < bottom or g.yMax > top:
                failures.append((name, kind, g.yMin, g.yMax, bottom, top))
    assert not failures, f'Outline exceeds advertised vertical metrics: {failures[:40]} ({len(failures)} failures)'


def assert_unclipped_bitmap(glyph, style, size, mask, bx, by):
    """Compare with a generously padded reference in the SAME pixel phase.

    The reference uses source polygons/centerlines and never clips them to the
    exported bitmap frame. This detects ink cut off at any edge, including
    below-baseline subscript strokes. Touching an edge alone is not failure.
    """
    import cv2
    polygons = contours(glyph, style)
    points = [p for path in polygons for p in path]
    scale = size / 1000
    h, w = mask.shape
    outside = [4]
    for x, y in points:
        px, py = x * scale - bx, by - y * scale
        outside.extend((-px, px - w + 1, -py, py - h + 1))
    pad = int(np.ceil(max(outside))) + 4
    if style.key == 'singleline':
        reference = np.zeros((h + 2 * pad, w + 2 * pad), np.uint8)
        for i, path in enumerate(centerlines(glyph, style)):
            p = np.rint([(x * scale - bx, by - y * scale) for x, y in path]).astype(np.int32) + pad
            if not len(p):
                continue
            if glyph.notes.get('negative'):
                if i == 0:
                    cv2.fillPoly(reference, [p], 255, lineType=cv2.LINE_8)
                else:
                    cv2.polylines(reference, [p], False, 0, 1, cv2.LINE_8)
            elif glyph.filled:
                cv2.fillPoly(reference, [p], 255, lineType=cv2.LINE_8)
            else:
                cv2.polylines(reference, [p], False, 255, 1, cv2.LINE_8)
    else:
        ss = 4
        high = np.zeros(((h + 2 * pad) * ss, (w + 2 * pad) * ss), np.uint8)
        cutouts = np.zeros_like(high) if glyph.notes.get('negative') else None
        for i, path in enumerate(polygons):
            p = np.rint([((x * scale - bx) * ss, (by - y * scale) * ss) for x, y in path]).astype(np.int32) + pad * ss
            if len(set(map(tuple, p))) < 3:
                continue
            area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(path, path[1:] + path[:1]))
            cut = glyph.notes.get('negative') and area > 0
            cv2.fillPoly(high, [p], 0 if cut else 255, lineType=cv2.LINE_8)
            if cutouts is not None and i > 0:
                cv2.fillPoly(cutouts, [p], 255 if cut else 0, lineType=cv2.LINE_8)
        coverage = cv2.resize(high, (w + 2 * pad, h + 2 * pad), interpolation=cv2.INTER_AREA)
        reference = np.where(coverage >= 32, 255, 0).astype(np.uint8)
        if cutouts is not None:
            white = cv2.resize(cutouts, (w + 2 * pad, h + 2 * pad), interpolation=cv2.INTER_AREA)
            reference[white >= 32] = 0
    center = reference[pad:pad + h, pad:pad + w].astype(bool)
    assert np.array_equal(center, mask.astype(bool)), f'Bitmap differs from source raster: {style.key}/{size} {glyph.text!r}'
    reference[pad:pad + h, pad:pad + w] = 0
    assert not reference.any(), f'Clipped bitmap ink: {style.key}/{size} {glyph.text!r} bearing=({bx},{by}) frame=({w},{h}) lost_pixels={np.count_nonzero(reference)}'


def assert_bitmap_composition_alignment(font, text):
    units = list(font.units(text))
    rendered = font.mask(text)
    positions = []
    pen = 0
    for c in units:
        positions.append((c, pen))
        pen += font.glyphs[c][2]
    left = min([0] + [pen_x + font.glyphs[c][3] for c, pen_x in positions])
    right = max([1, pen] + [pen_x + font.glyphs[c][3] + font.glyphs[c][0] for c, pen_x in positions])
    assert rendered.shape == (font.height, right - left)
    expected = np.zeros_like(rendered)
    for c, pen_x in positions:
        w, h, advance, bx, by, _, _ = font.glyphs[c]
        x, y = pen_x + bx - left, font.baseline - by
        assert x >= 0 and y >= 0
        assert x + w <= rendered.shape[1] and y + h <= rendered.shape[0]
        expected[y:y + h, x:x + w] |= font.bitmap(c)
    np.testing.assert_array_equal(rendered, expected, err_msg=repr(text))


@pytest.fixture(scope='session')
def source():
    return load_glyphs()[0]


@pytest.fixture(scope='session')
def manifests():
    return json_read(DATA / 'jisx0213-2004.json'), json_read(DATA / 'unicode-jinmeiyo.json')


@pytest.fixture(scope='session')
def small_source(source, manifests):
    keep = set(SAMPLES) | set('0123456789xéかカ゚') | set('⓫❽│─·˙') | {' ', '\u0301', 'a\u0301', 'か\u309a', 'カ\u309a', '\U0002000b', '侮', '侮'}
    for entry in manifests[0]['entries']:
        if len(entry['text']) > 1:
            keep.add(entry['text'])
            keep.update(entry['text'])
    missing = keep - source.keys()
    assert not missing, f'Representative source glyphs missing: {sorted(missing)}'
    return {c: source[c] for c in sorted(keep)}


@pytest.fixture(scope='session')
def sample_fonts(tmp_path_factory, small_source):
    directory = tmp_path_factory.mktemp('family-sample-fonts')
    paths = {}
    for key in ('gothic', 'serif'):
        paths[key] = directory / f'{key}.ttf'
        build_font(small_source, STYLES[key], paths[key], variable=True)
    return paths


def test_legacy_original_files_byte_identical():
    manifest = json_read(DATA / 'legacy-sha256.json')
    assert manifest
    assert any(p.startswith('glyphs/') for p in manifest)
    assert any(p.endswith('.png') for p in manifest)
    assert any(p.endswith('.ttf') for p in manifest)
    failures = [p for p, digest in manifest.items() if not (ROOT / p).is_file() or sha(ROOT / p) != digest]
    assert not failures, f'Original legacy files changed: {failures}'


def test_centerlines_exports_deterministic_lossless_svgz(tmp_path, small_source):
    first=tmp_path/'centerlines.svg'
    second=tmp_path/'different-name.svg'
    write_centerlines(small_source,first)
    write_centerlines(small_source,second)
    raw=first.read_bytes()
    compressed=first.with_suffix('.svgz').read_bytes()
    assert gzip.decompress(compressed)==raw==second.read_bytes()
    assert compressed==second.with_suffix('.svgz').read_bytes()==compress_centerlines(raw)
    assert compressed[3]==0 and compressed[4:8]==b'\0'*4 and compressed[9]==255
    symbols=ET.fromstring(raw).findall('.//{http://www.w3.org/2000/svg}symbol')
    assert len(symbols)==len(small_source)
    assert {s.attrib['id'] for s in symbols}=={glyph_name(c) for c in small_source}


@pytest.mark.parametrize('raw_present', [False, True])
def test_editable_svg_from_compressed_source(tmp_path, raw_present):
    raw='<svg xmlns="http://www.w3.org/2000/svg"><title>日本語</title></svg>\n'.encode()
    compressed=compress_centerlines(raw)
    (tmp_path/'centerlines.svgz').write_bytes(compressed)
    if raw_present:(tmp_path/'centerlines.svg').write_bytes(raw)
    assert editable_centerlines(tmp_path)==raw
    assert (tmp_path/'centerlines.svg').exists()==raw_present


def test_package_rejects_stale_raw_centerlines(tmp_path):
    (tmp_path/'centerlines.svgz').write_bytes(compress_centerlines(b'<svg/>\n'))
    (tmp_path/'centerlines.svg').write_bytes(b'<svg>stale</svg>\n')
    with pytest.raises(ValueError,match='disagree'):
        editable_centerlines(tmp_path)


def test_jis_manifest_exact_identities_and_level_counts(manifests):
    jis, _ = manifests
    entries = jis['entries']
    assert len(entries) == len({e['text'] for e in entries}) == 11233
    assert len({e['jis'] for e in entries}) == 11233
    assert Counter(e['level'] for e in entries) == EXPECTED_LEVELS
    assert sum(len(e['text']) > 1 for e in entries) == 25
    assert len({c for e in entries for c in e['text']}) == 11209
    # Reconstruct independently of the project's manifest generator. Restrict
    # plane 2; the codec also decodes out-of-scope JIS X 0212 positions.
    actual = {}
    allowed_rows = {1, 3, 4, 5, 8, 12, 13, 14, 15, *range(78, 95)}
    for plane in (1, 2):
        for row in range(1, 95):
            if plane == 2 and row not in allowed_rows:
                continue
            for cell in range(1, 95):
                encoded = (b'\x8f' if plane == 2 else b'') + bytes([row + 160, cell + 160])
                try:
                    text = encoded.decode('euc_jis_2004', errors='strict')
                except UnicodeDecodeError:
                    continue
                level = 4 if plane == 2 else (1 if 1601 <= row * 100 + cell <= 4751 else
                         2 if 4801 <= row * 100 + cell <= 8406 else 3 if row >= 14 else 0)
                actual[f'{plane}-{row:02d}-{cell:02d}'] = (text, level)
    assert {e['jis']: (e['text'], e['level']) for e in entries} == actual
    for entry in entries:
        assert entry['unicode'] == [f'U+{ord(c):04X}' for c in entry['text']]


def test_jinmeiyo_raw_property_identity_counts(manifests):
    jis, jin = manifests
    entries = jin['entries']
    assert jin['unicode_version'] == '18.0.0'
    assert len(entries) == len({e['text'] for e in entries}) == 864
    assert Counter(e['property'].split(':')[0] for e in entries) == {'2010': 861, '2015': 1, '2017': 1, '2026': 1}
    assert [e['text'] for e in entries if e['property'].startswith('2026')] == ['勒']
    assert {e['text'] for e in entries} <= {e['text'] for e in jis['entries'] if e['level'] > 0}
    for e in entries:
        assert len(e['text']) == 1 and e['unicode'] == f'U+{ord(e["text"]):04X}'
    lock = json_read(DATA / 'sources-lock.json')
    unihan = next(e for e in lock['files'] if e['file'] == 'Unihan.zip')
    assert jin['source_sha256'] == unihan['sha256']


def test_all_kanji_target_identities_are_present(source, manifests):
    jis, jin = manifests
    required = {e['text'] for e in jis['entries'] if e['level']} | {e['text'] for e in jin['entries']}
    assert not required - source.keys(), f'Incomplete Kanji repertoire: {sorted(required - source.keys())}'



def test_all_jis_identities_including_nonkanji_and_sequences_are_present(source, manifests):
    jis, _ = manifests
    required = {e['text'] for e in jis['entries']}
    assert len(required) == 11233
    assert not required - source.keys(), f'Incomplete JIS repertoire: {sorted(required - source.keys())}'


def test_missing_characters_are_not_synthetic_coverage(source):
    assert '\U0010ffff' not in source
    assert '\U0003134a' not in source
    for text, glyph in source.items():
        assert text == glyph.text
        if text.isspace():
            continue
        assert glyph.paths and any(p for p in glyph.paths), f'Blank source counts as coverage: {text!r}'
        assert not any(word in glyph.source.lower() for word in ('placeholder', 'fallback', 'tofu'))
        if glyph.source == 'project-component-composition':
            assert glyph.status in {'component-draft', 'composition-draft'}
            assert not glyph.notes.get('visually_reviewed', False)


@pytest.mark.parametrize('key', STYLE_KEYS)
def test_sample_outlines_have_ink_and_valid_metrics(source, key):
    for c in SAMPLES:
        glyph, metrics = make_glyph(source[c], STYLES[key])
        assert glyph.numberOfContours > 0, (key, c)
        assert len(glyph.coordinates) >= 3
        assert metrics[0] > 0
        glyph.recalcBounds(None)
        assert glyph.xMax > glyph.xMin and glyph.yMax > glyph.yMin


@pytest.mark.parametrize('key', ('gothic', 'serif'))
def test_master_compatibility_and_actual_two_axis_interpolation(source, sample_fonts, key):
    with TTFont(sample_fonts[key]) as font:
        assert {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in font['fvar'].axes} == {
            'wght': (200, 400, 700), 'slnt': (-12, 0, 0)}
        assert {a.AxisTag for a in font['STAT'].table.DesignAxisRecord.Axis} == {'wght', 'slnt'}
        assert 'gvar' in font and font['gvar'].variations
        masters = {}
        for weight in (200, 400, 700):
            for slant in (0, -12):
                instance = instantiateVariableFont(font, {'wght': weight, 'slnt': slant}, inplace=False)
                for c in SAMPLES:
                    expected, _ = make_glyph(source[c], variable_style(STYLES[key], weight, slant))
                    actual = instance['glyf'][glyph_name(c)]
                    assert topology(actual) == topology(expected)
                    np.testing.assert_allclose(coords(actual), coords(expected), atol=0.01, err_msg=f'{key} {c} {weight} {slant}')
                    masters[c, weight, slant] = coords(actual)
                instance.close()
        for c in SAMPLES:
            assert not np.array_equal(masters[c, 200, 0], masters[c, 700, 0]), (key, c, 'ineffective weight')
            assert not np.array_equal(masters[c, 400, 0], masters[c, 400, -12]), (key, c, 'ineffective slant')
        # Interior instances are the bilinear interpolation of four authored
        # corner masters. This tests both axis interactions, not only metadata.
        for weight, low, high in ((300, 200, 400), (550, 400, 700)):
            instance = instantiateVariableFont(font, {'wght': weight, 'slnt': -6}, inplace=False)
            for c in SAMPLES:
                expected = sum(masters[c, w, s] for w in (low, high) for s in (0, -12)) / 4
                np.testing.assert_allclose(coords(instance['glyf'][glyph_name(c)]), expected, atol=1.0)
            instance.close()




def test_sample_font_shapes_all_25_jis_sequences(sample_fonts, manifests):
    path = sample_fonts['gothic']
    with TTFont(path) as font:
        for entry in manifests[0]['entries']:
            sequence = entry['text']
            if len(sequence) <= 1:
                continue
            gids, _ = shape(path, sequence)
            assert gids == [font.getGlyphID(glyph_name(sequence))], repr(sequence)


def test_opentype_super_sub_have_smaller_raised_lowered_outlines(sample_fonts):
    with TTFont(sample_fonts['gothic']) as font:
        base_name = glyph_name('2')
        base = font['glyf'][base_name]
        base.recalcBounds(font['glyf'])
        sup, sub = (font['glyf'][base_name + '.' + tag] for tag in ('sups', 'subs'))
        for glyph in (sup, sub):
            glyph.recalcBounds(font['glyf'])
            assert 0 < glyph.yMax - glyph.yMin < base.yMax - base.yMin
        assert sup.yMin > base.yMin
        assert sub.yMax < base.yMax
        for tag in ('sups', 'subs'):
            assert 0 < font['hmtx'][base_name + '.' + tag][0] < font['hmtx'][base_name][0]


def test_italic_authored_a_g_differ_from_shear(source):
    italic = STYLES['italic']
    oblique = replace(italic, italic=False)
    for c in ('a', 'g'):
        assert centerlines(source[c], italic) != centerlines(source[c], oblique)
        a, _ = make_glyph(source[c], italic)
        b, _ = make_glyph(source[c], oblique)
        assert topology(a) != topology(b) or not np.array_equal(coords(a), coords(b))


def test_italian_is_upright_reverse_contrast():
    italian, serif = STYLES['italian'], STYLES['serif']
    assert italian.slant == 0 and not italian.italic
    assert italian.horizontal > italian.vertical
    assert serif.vertical > serif.horizontal
    horizontal = Glyph('h', [[(4, 12), (20, 12)]])
    vertical = Glyph('v', [[(12, 4), (12, 20)]])
    h, _ = make_glyph(horizontal, replace(italian, serif=0))
    v, _ = make_glyph(vertical, replace(italian, serif=0))
    h.recalcBounds(None); v.recalcBounds(None)
    assert h.yMax - h.yMin > v.xMax - v.xMin



def test_negative_enclosures_have_real_outline_and_bitmap_counters(source):
    negative = [glyph for glyph in source.values() if glyph.notes.get('negative')]
    assert len(negative) >= 20
    for glyph in negative:
        shapes = contours(glyph, STYLES['gothic'])
        signed_areas = [sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p, p[1:] + p[:1])) for p in shapes]
        assert signed_areas[0] < 0
        assert any(a > 0 for a in signed_areas[1:]), glyph.text
        solid = replace(glyph, paths=glyph.paths[:1], notes={}, filled=True)
        for key in STYLE_KEYS:
            for size in (*STRIKE_SIZES, 96):
                cut, *_ = raster(glyph, STYLES[key], size)
                disc, *_ = raster(solid, STYLES[key], size)
                assert cut.shape == disc.shape
                assert cut.any() and (disc.astype(bool) & ~cut.astype(bool)).any(), (glyph.text, key, size)
                assert not (cut.astype(bool) & ~disc.astype(bool)).any(), (glyph.text, key, size)
        masters = [make_glyph(glyph, variable_style(STYLES['gothic'], weight, slant))[0]
                   for weight in (200, 400, 700) for slant in (0, -12)]
        assert len({topology(g) for g in masters}) == 1, glyph.text


def test_negative_enclosure_font_renders_white_counters(sample_fonts):
    # FreeType/Pillow reads the serialized TTF. Background islands inside ink
    # prove these are actual counters rather than dark lines on a solid disc.
    import cv2
    font = ImageFont.truetype(str(sample_fonts['gothic']), 192)
    for c in ('⓫', '❽'):
        rendered = font.getmask(c, mode='L')
        image = np.asarray(rendered, dtype=np.uint8).reshape(rendered.size[1], rendered.size[0])
        ink = image > 127
        padded = np.pad(ink, 1, constant_values=False)
        count, labels = cv2.connectedComponents((~padded).astype(np.uint8), connectivity=4)
        background = labels[0, 0]
        islands = [label for label in range(1, count) if label != background]
        assert islands, f'No white counters in serialized TTF for {c}'
        assert sum((labels == label).sum() for label in islands) > 10


@pytest.mark.parametrize('key', ('gothic', 'serif'))
def test_sample_font_build_is_byte_deterministic(tmp_path, small_source, key):
    for variable in (False, True):
        one, two = tmp_path / 'one.ttf', tmp_path / 'two.ttf'
        build_font(small_source, STYLES[key], one, variable=variable)
        build_font(small_source, STYLES[key], two, variable=variable)
        assert one.read_bytes() == two.read_bytes(), (key, variable)


@pytest.fixture(scope='session')
def sample_bitmap(tmp_path_factory, small_source):
    directory = tmp_path_factory.mktemp('family-sample-bitmaps')
    build_bitmaps(small_source, STYLES['italic'], 24, directory)
    return directory / 'italic-24'


def check_bitmap_triplet(base, *, all_glyphs=False):
    base = Path(base)
    font = BitmapFont(base.with_suffix('.sjpb'))
    manifest = json_read(base.with_suffix('.json'))
    assert manifest['sha256'] == sha(base.with_suffix('.png'))
    with Image.open(base.with_suffix('.png')) as image:
        assert image.mode == '1', 'PNG must be lossless 1-bit, not grayscale or RGB'
        atlas = np.asarray(image, dtype=bool)
    assert set(font.glyphs) == set(manifest['glyphs'])
    keys = sorted(font.glyphs)
    chosen = set(keys if all_glyphs else keys[::max(1, len(keys) // 64)])
    chosen |= {c for c in font.glyphs if len(c) > 1}
    chosen |= (set(SAMPLES) | set('⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴❶❷❸❹❺❻❼❽❾❿')) & font.glyphs.keys()
    for key in chosen:
        m = manifest['glyphs'][key]
        mask = font.bitmap(key)
        np.testing.assert_array_equal(mask, atlas[m['y']:m['y'] + m['height'], m['x']:m['x'] + m['width']], err_msg=repr(key))
        assert font.glyphs[key][:5] == (m['width'], m['height'], m['advance'], m['bearing_x'], m['bearing_y'])
        assert list(font.units(key)) == [key]
    with pytest.raises(KeyError):
        font.bitmap('\U0010ffff')
    with pytest.raises(KeyError):
        list(font.units('A\U0010ffff'))
    return font


def test_sample_bitmap_exact_png_roundtrip_and_sequences(sample_bitmap):
    font = check_bitmap_triplet(sample_bitmap, all_glyphs=True)
    assert 'か\u309a' in font.glyphs and '侮\ufe00' in font.glyphs
    assert list(font.units('Aか\u309a侮\ufe002')) == ['A', 'か\u309a', '侮\ufe00', '2']
    assert font.mask('Aか\u309a侮\ufe002').any()



@pytest.mark.parametrize('key', STYLE_KEYS)
def test_sample_all_sizes_are_unclipped_and_baseline_aligned(tmp_path, small_source, key):
    for size in STRIKE_SIZES:
        build_bitmaps(small_source, STYLES[key], size, tmp_path)
        base = tmp_path / f'{key}-{size}'
        font = check_bitmap_triplet(base, all_glyphs=True)
        metadata = json_read(base.with_suffix('.json'))
        assert font.baseline == metadata['baseline'] == max(g[4] for g in font.glyphs.values())
        assert font.height == metadata['line_height']
        assert_bitmap_composition_alignment(font, 'A│日か\u309a𠮷g')
        assert_bitmap_composition_alignment(font, '')
        for c, glyph in small_source.items():
            mask = font.bitmap(c)
            if not c.isspace():
                assert mask.any(), (key, size, c)
            _, _, _, bx, by, _, _ = font.glyphs[c]
            assert_unclipped_bitmap(glyph, STYLES[key], size, mask, bx, by)


@pytest.mark.parametrize('mutation', ['short_header', 'bad_magic', 'version', 'header_flags', 'index_out_of_bounds', 'payload_truncated', 'record_flags', 'empty_key', 'zero_size', 'duplicate_key', 'index_overlap', 'invalid_baseline', 'negative_advance'])
def test_malformed_bitmap_pack_is_rejected(sample_bitmap, tmp_path, mutation):
    data = bytearray(sample_bitmap.with_suffix('.sjpb').read_bytes())
    header = list(HEADER.unpack_from(data))
    index, keys, pixels = header[5:8]
    record = list(INDEX.unpack_from(data, index))
    if mutation == 'short_header':
        data = data[:10]
    elif mutation == 'bad_magic':
        data[:4] = b'NOPE'
    elif mutation in ('version', 'header_flags', 'zero_size'):
        header[{'version': 1, 'header_flags': 2, 'zero_size': 4}[mutation]] = 0 if mutation == 'zero_size' else 99
        HEADER.pack_into(data, 0, *header)
    elif mutation == 'index_out_of_bounds':
        header[5] = len(data) + 1
        HEADER.pack_into(data, 0, *header)
    elif mutation == 'payload_truncated':
        data = data[:-1]
    elif mutation == 'record_flags':
        record[7] = 1
        INDEX.pack_into(data, index, *record)
    elif mutation == 'empty_key':
        record[1] = 0
        INDEX.pack_into(data, index, *record)
    elif mutation == 'duplicate_key':
        second = list(INDEX.unpack_from(data, index + INDEX.size))
        second[:2] = record[:2]
        INDEX.pack_into(data, index + INDEX.size, *second)
    elif mutation == 'invalid_baseline':
        header[8] = 0
        HEADER.pack_into(data, 0, *header)
    elif mutation == 'negative_advance':
        record[4] = -1
        INDEX.pack_into(data, index, *record)
    elif mutation == 'index_overlap':
        # Index payload starts after the declared key section. All offsets are
        # individually in bounds; the parser must validate the whole table.
        header[6] = index
        HEADER.pack_into(data, 0, *header)
    path = tmp_path / f'{mutation}.sjpb'
    path.write_bytes(data)
    with pytest.raises((ValueError, struct.error, UnicodeError, OverflowError)):
        BitmapFont(path)


class TestFullArtifacts:
    """Final-build integration tests. Missing artifacts never count as passes."""

    def test_inventory_complete(self):
        missing = [str(p) for p in required_artifacts() if not (OUTPUT / p).is_file()]
        if missing and os.environ.get('FAMILY_REQUIRE_OUTPUTS') != '1':
            pytest.skip('INCOMPLETE BUILD: ' + ', '.join(missing))
        assert not missing, f'INCOMPLETE BUILD: {missing}'

    def test_coverage_exactly_matches_encoded_font_and_provenance(self, source, manifests):
        coverage = json_read(artifact('coverage.json'))
        with gzip.open(artifact('glyph-provenance.json.gz'), 'rt') as f:
            provenance = json.load(f)
        identities = {k for k in provenance if k != '_kanji_expansion'}
        assert identities == set(source), 'Stale provenance or source mismatch; rebuild final outputs'
        assert 'draft' in coverage['warning'].lower()
        assert 'not individually proofread' in coverage['warning'].lower()
        assert coverage['development_without_expansion'] is False
        jis, jin = manifests
        groups = {f'jis_level_{i}': {e['text'] for e in jis['entries'] if e['level'] == i} for i in range(1, 5)}
        groups.update(jinmeiyo={e['text'] for e in jin['entries']},
                      jis_nonkanji={e['text'] for e in jis['entries'] if e['level'] == 0},
                      jis_multiscalar={e['text'] for e in jis['entries'] if len(e['text']) > 1})
        with TTFont(static_path('gothic')) as font:
            cmap = font.getBestCmap()
            assert set(cmap) == {ord(c) for c in identities if len(c) == 1}
            assert coverage['scalar_cmap_count'] == len(cmap)
            assert coverage['sequence_glyph_count'] == sum(len(c) > 1 for c in identities)
            for name, target in groups.items():
                encoded = {c for c in target if (ord(c) in cmap if len(c) == 1 else glyph_name(c) in font.getGlyphOrder())}
                record = coverage['groups'][name]
                assert record['target'] == len(target)
                assert record['present'] == len(encoded)
                assert set(record['missing']) == target - encoded
                assert record['missing_count'] == len(target - encoded)
                assert record['complete_encoding'] == (encoded == target)
                assert encoded == target, f'{name} remains incomplete: {sorted(target - encoded)}'
                for c in record['missing']:
                    assert glyph_name(c) not in font.getGlyphOrder()
        assert coverage['status_counts'] == dict(Counter(provenance[c]['status'] for c in identities))
        for c in identities:
            assert provenance[c]['centerline_sha256'] == hashlib.sha256(json.dumps(source[c].paths, separators=(',', ':')).encode()).hexdigest()

    @pytest.mark.parametrize('key', STYLE_KEYS)
    def test_static_cmap_outlines_names_and_notdef(self, key, source):
        with TTFont(static_path(key)) as font:
            cmap = font.getBestCmap()
            assert set(cmap) == {ord(c) for c in source if len(c) == 1}
            assert 0x10FFFF not in cmap and 0x3134A not in cmap
            assert any(t.format == 12 for t in font['cmap'].tables)
            assert cmap[ord('𠮷')] == glyph_name('𠮷')
            assert 'EXPERIMENTAL' in font['name'].getDebugName(5)
            assert 'composition drafts' in font['name'].getDebugName(10)
            assert font['glyf']['.notdef'].numberOfContours > 0
            tags = {f.FeatureTag for f in font['GSUB'].table.FeatureList.FeatureRecord}
            assert {'ccmp', 'sups', 'subs'} <= tags
            for name, (src, feature) in source_entries(source).items():
                expected, metrics = make_glyph(src, STYLES[key], feature=feature)
                actual = font['glyf'][name]
                assert topology(actual) == topology(expected), (key, name)
                if actual.numberOfContours:
                    np.testing.assert_array_equal(coords(actual), coords(expected), err_msg=f'{key} {name}')
                assert font['hmtx'][name] == metrics, (key, name)
            assert_font_vertical_bounds(font)
            bad = []
            for c, src in source.items():
                glyph = font['glyf'][glyph_name(c)]
                if c.isspace():
                    continue
                if glyph.numberOfContours <= 0:
                    bad.append(c)
                    continue
                glyph.recalcBounds(font['glyf'])
                if glyph.xMax <= glyph.xMin or glyph.yMax <= glyph.yMin:
                    bad.append(c)
            assert not bad, f'Blank encoded outlines in {key}: {bad}'
            gids, _ = shape(static_path(key), '\U0010ffff')
            assert gids == [0]

    @pytest.mark.parametrize('key', STYLE_KEYS)
    def test_svs_format14_keeps_compatibility_identity(self, source, key):
        variants = json_read(DATA / 'jis-compatibility-svs.json')['entries']
        assert len(variants) == 75
        with TTFont(static_path(key)) as font:
            tables = [t for t in font['cmap'].tables if t.format == 14]
            assert len(tables) == 1
            actual = {(base, selector): name for selector, pairs in tables[0].uvsDict.items() for base, name in pairs}
            expected = {(int(e['sequence'][0][2:], 16), int(e['sequence'][1][2:], 16)):
                        glyph_name(chr(int(e['compatibility_target'][2:], 16))) for e in variants
                        if chr(int(e['compatibility_target'][2:], 16)) in source}
            assert actual == expected
            for (base, selector), name in expected.items():
                gids, _ = shape(static_path(key), chr(base) + chr(selector))
                assert gids == [font.getGlyphID(name)]

    @pytest.mark.parametrize('key', STYLE_KEYS)
    def test_gsub_and_harfbuzz_latin_math_japanese(self, source, key):
        path = static_path(key)
        with TTFont(path) as font:
            tags = {f.FeatureTag for f in font['GSUB'].table.FeatureList.FeatureRecord}
            assert {'ccmp', 'sups', 'subs'} <= tags
            for text in ('Hello 123', 'x2+α=∑∞≤≠', '日本語髙𠮷', '☀☕☺'):
                gids, _ = shape(path, text)
                assert gids and 0 not in gids, repr(text)
            for feature in ('sups', 'subs'):
                text = 'x2+α'
                gids, positions = shape(path, text, {feature: 1})
                assert gids == [font.getGlyphID(glyph_name(c) + '.' + feature) for c in text]
                assert all(p.x_advance > 0 for p in positions)
            for sequence in ('a\u0301', 'か\u309a', 'カ\u309a'):
                assert sequence in source
                gids, _ = shape(path, sequence)
                assert len(gids) == 1 and gids[0] != 0, repr(sequence)
                if sequence[0] in 'かカ':
                    assert gids[0] == font.getGlyphID(glyph_name(sequence))
            # A mark combination outside the explicit ccmp inventory must
            # remain shapeable and carry a zero-advance mark attachment.
            gids, pos = shape(path, 'x\u0301')
            assert 0 not in gids
            if len(gids) == 2:
                assert pos[1].x_advance == 0
                assert pos[1].x_offset or pos[1].y_offset

    @pytest.mark.parametrize('key', STYLE_KEYS)
    def test_each_encoded_jis_multiscalar_identity_shapes_exactly(self, source, manifests, key):
        jis, _ = manifests
        path = static_path(key)
        with TTFont(path) as font:
            sequences = [e['text'] for e in jis['entries'] if len(e['text']) > 1]
            assert len(sequences) == 25
            for sequence in sequences:
                if sequence not in source:
                    # An openly reported missing identity is checked by the
                    # coverage test, and must never become fake coverage.
                    assert glyph_name(sequence) not in font.getGlyphOrder()
                    continue
                gids, _ = shape(path, sequence)
                assert gids == [font.getGlyphID(glyph_name(sequence))], repr(sequence)

    @pytest.mark.parametrize('key', STYLE_KEYS)
    def test_every_encoded_identity_shapes_without_missing_glyphs(self, key, source):
        path = static_path(key)
        with TTFont(path) as font:
            nominal = _hb_font(str(path.resolve()), path.stat().st_mtime_ns)
            for c in source:
                if len(c) == 1:
                    assert nominal.get_nominal_glyph(ord(c)) == font.getGlyphID(glyph_name(c)), (key, c)
                gids, positions = shape(path, c, preserve=True)
                assert gids and 0 not in gids, (key, c, gids)
                assert all(p.x_advance >= 0 for p in positions), (key, c)

    @pytest.mark.parametrize('key', ('gothic', 'serif'))
    def test_full_variable_tables_and_real_endpoint_instances(self, key, source):
        path = artifact(Path('variable') / f'SinglelineJPLab-{key}-VF.ttf')
        with TTFont(path) as font:
            assert {a.axisTag for a in font['fvar'].axes} == {'wght', 'slnt'}
            assert {'gvar', 'STAT'} <= set(font.keys())
            assert len(font.getBestCmap()) == sum(len(c) == 1 for c in source)
            assert len(font['gvar'].variations) > 10000
            for weight, slant in ((200, 0), (700, 0), (200, -12), (700, -12)):
                instance = instantiateVariableFont(font, {'wght': weight, 'slnt': slant}, inplace=False)
                for name, (src, feature) in source_entries(source).items():
                    expected, metrics = make_glyph(src, variable_style(STYLES[key], weight, slant), feature=feature)
                    actual = instance['glyf'][name]
                    assert topology(actual) == topology(expected), (key, name, weight, slant)
                    if actual.numberOfContours:
                        np.testing.assert_allclose(coords(actual), coords(expected), atol=0.01, err_msg=f'{key} {name} {weight} {slant}')
                    assert instance['hmtx'][name] == metrics, (key, name, weight, slant)
                assert_font_vertical_bounds(instance)
                instance.close()

    @pytest.mark.parametrize('key', STYLE_KEYS)
    @pytest.mark.parametrize('size', STRIKE_SIZES)
    def test_full_bitmap_pack_png_exactness(self, key, size, source):
        relative = Path('bitmaps') / f'{key}-{size}'
        for ext in ('.sjpb', '.json', '.png'):
            artifact(relative.with_suffix(ext))
        font = check_bitmap_triplet(OUTPUT / relative, all_glyphs=True)
        assert set(source) <= font.glyphs.keys()
        assert font.size == size
        manifest = json_read((OUTPUT / relative).with_suffix('.json'))
        assert font.baseline == manifest['baseline'] == max(g[4] for g in font.glyphs.values())
        expected_line_height = font.baseline + max(g[1] - g[4] for g in font.glyphs.values())
        assert manifest['line_height'] == expected_line_height
        assert font.height == expected_line_height
        assert_bitmap_composition_alignment(font, 'A│日か\u309a𠮷g')
        assert_bitmap_composition_alignment(font, 'gA')
        assert_bitmap_composition_alignment(font, '')
        assert list(font.units('日本語か\u309a髙𠮷')) == ['日', '本', '語', 'か\u309a', '髙', '𠮷']
        assert font.mask('日本語か\u309a髙𠮷').any()
        entries = dict(source)
        entries.update({sequence: source[target] for sequence, target in standard_variants(source)})
        assert set(font.glyphs) == set(entries)
        blanks = []
        for c, glyph in entries.items():
            mask = font.bitmap(c)
            if not c.isspace() and not mask.any():
                blanks.append(c)
            w, h, advance, bx, by, _, _ = font.glyphs[c]
            assert mask.shape == (h, w)
            assert advance == round(glyph.advance * STYLES[key].scale * size / 1000), (key, size, c)
            assert_unclipped_bitmap(glyph, STYLES[key], size, mask, bx, by)
        assert not blanks, f'Blank encoded bitmaps: {key}/{size}: {blanks}'

    def test_centerlines_svg_and_build_provenance(self, source):
        compressed = artifact('centerlines.svgz').read_bytes()
        svg = gzip.decompress(compressed)
        assert compress_centerlines(svg) == compressed, 'SVGZ must use deterministic gzip packaging'
        raw = OUTPUT / 'centerlines.svg'
        if raw.is_file():
            assert svg == raw.read_bytes(), 'Compressed centerlines must preserve every original SVG byte'
            assert hashlib.sha256(svg).hexdigest() == sha(raw)
        root = ET.fromstring(svg)
        symbols = root.findall('.//{http://www.w3.org/2000/svg}symbol')
        assert len(symbols) == len(source)
        assert {s.attrib['id'] for s in symbols} == {glyph_name(c) for c in source}
        assert {s.find('{http://www.w3.org/2000/svg}title').text for s in symbols} == set(source)
        summary = json_read(artifact('build-summary.json'))
        assert summary['experimental'] is True
        assert summary['legacy']['unchanged'] and summary['legacy_after']['unchanged']
        assert len(summary['fonts']) == 10 and len(summary['bitmaps']) == len(STYLE_KEYS) * len(STRIKE_SIZES)
        assert summary['source_hashes']
        for relative, digest in summary['source_hashes'].items():
            assert sha(ROOT / relative) == digest, f'Stale build source hash: {relative}'
