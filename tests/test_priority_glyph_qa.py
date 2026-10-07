"""Small, source-only tests for the priority QA comparison method."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from family.tools.priority_glyph_qa import CHARACTERS, PAIRS, pixel_signature, proof_sheet, record


def test_expected_priority_inventory():
    assert len(CHARACTERS) == 11
    assert len(PAIRS) == 7
    assert ("吉", "𠮷") in PAIRS


def test_crop_padding_does_not_hide_collision():
    plain = np.array([[True, False], [False, True]])
    padded = np.pad(plain, ((2, 1), (3, 1)))
    assert pixel_signature(plain, 1, 5, 16) == pixel_signature(padded, -2, 7, 16)


def test_baseline_origin_advance_and_pixels_remain_significant():
    mask = np.array([[True, False], [False, True]])
    digest = pixel_signature(mask, 0, 2, 16)
    assert digest != pixel_signature(mask, 1, 2, 16)
    assert digest != pixel_signature(mask, 0, 3, 16)
    assert digest != pixel_signature(mask, 0, 2, 17)
    assert digest != pixel_signature(~mask, 0, 2, 16)


def test_svg_proof_embeds_exact_pixels_without_external_font_assets(tmp_path):
    mask = np.array([[True, False], [False, True]])
    masks = {char: mask for char in CHARACTERS}
    records = {char: record(mask, 0, 2, 16) for char in CHARACTERS}
    path = tmp_path / 'proof.svg'
    proof_sheet('test', [('SJPB', 16, records, masks)], path)
    svg = ET.fromstring(path.read_text())
    paths = svg.findall('.//{http://www.w3.org/2000/svg}path')
    assert len(paths) == len(CHARACTERS)
    assert all(p.attrib['d'] == 'M0,0h3v3h-3zM3,3h3v3h-3z' for p in paths)
    assert not svg.findall('.//{http://www.w3.org/2000/svg}image')
    assert all('href' not in key for element in svg.iter() for key in element.attrib)
    assert path.with_suffix('.png').is_file()
