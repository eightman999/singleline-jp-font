"""Canonical codepoints from the Agency for Cultural Affairs index.

This is character inventory, not imported font geometry. It is used only by
the host-side builder, catalogue, and tests, never by the Pi renderer.
"""
from pathlib import Path

SOURCE = Path(__file__).parent / 'assets/fonts/source'
SOURCE_URL = 'https://www.bunka.go.jp/seisaku/kokugo_nihongo/kokugo_shisaku/joyokanjihyo_sakuin/index.html'
ROWS = [line.split('\t') for line in (SOURCE/'joyo-kanji.txt').read_text().splitlines()
        if line and not line.startswith('#')]
if [int(n) for n, _ in ROWS] != list(range(1, 2137)):
    raise ValueError('Joyo inventory must contain every official index, 1..2136')
JOYO = ''.join(c for _, c in ROWS)
if len(JOYO) != 2136 or len(set(JOYO)) != 2136:
    raise ValueError('Joyo inventory must contain 2136 distinct single codepoints')
ADDITIONS = {i: (SOURCE/f'joyo-additions-{i}.txt').read_text().strip() for i in (1,2,3)}
# Widely used alternate Unicode encodings. Keep input text unchanged and make
# each codepoint explicit in the catalogue rather than normalizing messages.
ALTERNATE_FORMS = {'填':'塡', '剥':'剝', '頬':'頰', '𠮟':'叱'}
