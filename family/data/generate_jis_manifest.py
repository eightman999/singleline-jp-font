#!/usr/bin/env python3
"""Create JIS X 0213:2004 repertoire records, including sequences.

No glyph artwork is downloaded or reused. CPython's EUC-JIS-2004 codec is
cross-checked against Unicode 18 Unihan kJis0 + kJIS0213 data supplied locally.
Do not enumerate every decodable plane-2 byte pair: the codec accepts JIS0212
fallback positions outside the JIS0213 repertoire.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
P2_ROWS = {1, 3, 4, 5, 8, 12, 13, 14, 15, *range(78, 95)}


def build():
    entries = []
    for plane in (1, 2):
        for row in range(1, 95):
            if plane == 2 and row not in P2_ROWS:
                continue
            for cell in range(1, 95):
                encoded = (b'\x8f' if plane == 2 else b'') + bytes((0xA0 + row, 0xA0 + cell))
                try:
                    text = encoded.decode('euc_jis_2004', errors='strict')
                except UnicodeDecodeError:
                    continue
                if plane == 2:
                    level = 4
                elif 16 <= row <= 46 or row == 47 and cell <= 51:
                    level = 1
                elif 48 <= row <= 83 or row == 84 and cell <= 6:
                    level = 2
                elif row >= 14:
                    level = 3
                else:
                    level = 0
                entries.append(dict(jis=f'{plane}-{row:02d}-{cell:02d}', level=level,
                                    text=text, unicode=[f'U+{ord(c):04X}' for c in text]))
    assert Counter(x['level'] for x in entries) == {0: 1183, 1: 2965, 2: 3390, 3: 1259, 4: 2436}
    assert len(entries) == len({x['text'] for x in entries}) == 11233
    assert sum(len(x['text']) > 1 for x in entries) == 25
    assert len({c for x in entries for c in x['text']}) == 11209
    return entries


def verify_with_unihan(entries, zip_path):
    by_jis = {tuple(map(int, x['jis'].split('-'))): x['unicode'] for x in entries}
    checked = Counter()
    names = []
    with ZipFile(zip_path) as archive:
        for filename in archive.namelist():
            if not filename.endswith('.txt'):
                continue
            for line in archive.read(filename).decode('utf-8').splitlines():
                if not line or line.startswith('#'):
                    continue
                code, prop, value = line.split('\t')
                if prop == 'kJis0':
                    key = (1, int(value[:2]), int(value[2:]))
                elif prop == 'kJIS0213':
                    key = tuple(map(int, value.split(',')))
                else:
                    if prop == 'kJinmeiyoKanji':
                        names.append(dict(unicode=code, text=chr(int(code[2:], 16)), property=value))
                    continue
                assert by_jis[key] == [code], (key, code, by_jis.get(key))
                checked[prop] += 1
    assert checked == {'kJis0': 6356, 'kJIS0213': 3695}
    assert len(names) == 864
    assert {x['text'] for x in names} <= {x['text'] for x in entries if x['level']}
    assert [x['unicode'] for x in names if x['property'].startswith('2026')] == ['U+52D2']
    return names, checked


if __name__ == '__main__':
    entries = build()
    zip_path = HERE / 'Unihan.zip'
    names, checked = verify_with_unihan(entries, zip_path)
    (HERE / 'jisx0213-2004.json').write_text(json.dumps({
        'source': f'CPython {sys.version.split()[0]} euc_jis_2004 with exact plane-2 row filter',
        'cross_check': dict(checked), 'entries': entries}, ensure_ascii=False, indent=2) + '\n')
    (HERE / 'unicode-jinmeiyo.json').write_text(json.dumps({
        'source': 'https://www.unicode.org/Public/18.0.0/ucd/Unihan.zip',
        'source_sha256': hashlib.sha256(zip_path.read_bytes()).hexdigest(),
        'unicode_version': '18.0.0', 'entries': names}, ensure_ascii=False, indent=2) + '\n')
    print('Verified 11,233 JIS sequences and 864 jinmeiyo; zero Unihan mismatches')
