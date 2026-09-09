"""Pi-side bitmap composition only: no SVG, font rasterization, or resizing."""
from functools import lru_cache
import json
from pathlib import Path
import unicodedata

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent / "assets/fonts"


def glyph_units(text):
    """Resolve decomposed kana for drawing only; never rewrite the source text."""
    i = 0
    while i < len(text):
        if i+1 < len(text) and text[i+1] in '\u3099\u309a':
            composed = unicodedata.normalize('NFC', text[i:i+2])
            if len(composed) == 1:
                yield composed
                i += 2
                continue
        yield text[i]
        i += 1


class DotFont:
    def __init__(self, japanese="custom-jp-24", latin="custom-ascii-24"):
        self.atlases = []
        # Latin first: ASCII always uses the custom Latin atlas, including spaces/punctuation.
        for name in (latin, japanese):
            meta = json.loads((ROOT / f"{name}.json").read_text())
            with Image.open(ROOT / meta["image"]) as image:
                pixels = np.array(image.convert("L")) != 0
            self.atlases.append((meta["glyphs"], pixels))
        self.height = max(g["height"] for entries, _ in self.atlases for g in entries.values())

    def missing(self, text):
        return sorted({char for char in glyph_units(text) if not any(char in entries for entries, _ in self.atlases)})

    @lru_cache(maxsize=16)
    def mask(self, text):
        pieces = []
        for char in glyph_units(text):
            found = next(((entries[char], atlas) for entries, atlas in self.atlases if char in entries), None)
            if found is None:
                raise ValueError(f"Missing bitmap glyph U+{ord(char):04X} ({char!r})")
            pieces.append(found)
        trailing = pieces[-1][0]["advance"] - pieces[-1][0]["width"] if pieces else 0
        width = max(1, sum(g["advance"] for g, _ in pieces) - trailing)
        result = np.zeros((self.height, width), dtype=bool)
        x = 0
        for g, atlas in pieces:
            top = (self.height - g["height"]) // 2
            result[top:top+g["height"], x:x+g["width"]] = atlas[g["y"]:g["y"]+g["height"], g["x"]:g["x"]+g["width"]]
            x += g["advance"]
        result.flags.writeable = False
        return result

    def draw(self, frame, text, x, y, color, black):
        """Blit a cached line with opaque black gaps; colors are palette indices."""
        mask = self.mask(text)
        left, top = max(0, x), max(0, y)
        right, bottom = min(frame.shape[1], x + mask.shape[1]), min(frame.shape[0], y + mask.shape[0])
        if left < right and top < bottom:
            frame[top:bottom, left:right] = np.where(mask[top-y:bottom-y, left-x:right-x], color, black)
