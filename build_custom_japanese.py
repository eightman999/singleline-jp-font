"""Build only the original Japanese subset; no ChocoKanji input or Pi work."""
import hashlib
from pathlib import Path

import cv2
import numpy as np

from build_dot_fonts import save_atlas
from build_custom_ascii import ascii_mask
from custom_japanese_strokes import GLYPHS, PHRASES, FULLWIDTH_ALIASES
from custom_symbol_strokes import FILLED


def glyph_mask(lines, size, filled=False):
    mask = np.zeros((size, size), np.uint8)
    for line in lines:
        points = np.rint(np.asarray(line) * ((size-1)/24)).astype(np.int32)
        if filled:
            cv2.fillPoly(mask, [points], 255, lineType=cv2.LINE_8)
        else:
            cv2.polylines(mask, [points], False, 255, 1, cv2.LINE_8)
    return mask


def main():
    source = Path(__file__).with_name("custom_japanese_strokes.py")
    sources = [source, source.with_name('custom_symbol_strokes.py'),
               *sorted(source.parent.glob('education_strokes_*.py')),
               *[source.with_name(name) for name in ('joyo_composer.py', 'joyo_components.py',
                                                     'joyo_primitive_strokes.py', 'joyo_repertoire.py')]]
    for size in (18, 24):
        masks = {c: glyph_mask(lines, size, filled=c in FILLED) for c, lines in GLYPHS.items()}
        for char, ascii_char in FULLWIDTH_ALIASES.items():
            masks[char] = ascii_mask(ascii_char, size, fullwidth=True)
        save_atlas(f"custom-jp-{size}", masks,
                   {"name": "Project original geometric Japanese single-line subset",
                    "coordinates": source.name, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    "coordinate_sources": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                    "composition_data": {name: hashlib.sha256((source.parent/'assets/fonts/source'/name).read_bytes()).hexdigest()
                                         for name in ('joyo-compositions.json', 'joyo-kanji.txt')},
                    "composition_reference": "CJKVI-IDS / CHISE (character structure only)",
                    "composition_license": "GPL-2.0",
                    "phrases": PHRASES, "opencv": cv2.__version__,
                    "fullwidth_ascii": "Project original geometric ASCII",
                    "ascii_sha256": hashlib.sha256(source.with_name("custom_ascii_strokes.py").read_bytes()).hexdigest()}, dotted=False, advance_gap=2,
                   rasterization={"thickness": 1, "line_type": "LINE_8", "thinning": None,
                                  "filled_symbols": sorted(FILLED),
                                  "coordinate_grid": 24, "cell_size": size})


if __name__ == "__main__":
    main()
