"""Standalone single-line atlas writer, extracted from the source project."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent / "assets/fonts"

def save_atlas(name, masks, source, *, dotted=False, rasterization=None, advance_gap=None):
    if dotted:
        raise ValueError("Only single-line atlases are supported")
    glyphs = [(char, mask)
              for char, mask in sorted(masks.items())]
    cell_w = max(mask.shape[1] for _, mask in glyphs)
    cell_h = max(mask.shape[0] for _, mask in glyphs)
    columns = 32
    atlas = np.zeros(((len(glyphs) + columns - 1) // columns * cell_h, columns * cell_w), np.uint8)
    entries = {}
    for index, (char, mask) in enumerate(glyphs):
        x, y = index % columns * cell_w, index // columns * cell_h
        h, w = mask.shape
        atlas[y:y+h, x:x+w] = mask
        gap = (3 if dotted else 0) if advance_gap is None else advance_gap
        entries[char] = {"x": x, "y": y, "width": w, "height": h, "advance": w + gap}
    png = ROOT / f"{name}.png"
    Image.fromarray(atlas).convert("1").save(png)
    manifest = {"version": 1, "image": png.name, "sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
                "style": "dots" if dotted else "single-line",
                "dot_size": 2 if dotted else None, "gap": 1 if dotted else 0, "pitch": 3 if dotted else 1,
                "rasterization": rasterization or ({"coverage_threshold": 32, "thinning": "Zhang-Suen with component preservation"}
                                  if dotted else {"coverage_threshold_exclusive": 96, "thickness": 1, "line_type": "LINE_AA", "thinning": None}),
                "source": source, "glyphs": entries}
    (ROOT / f"{name}.json").write_text(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"{name}: {len(entries)} glyphs, {atlas.shape[1]}x{atlas.shape[0]}px, {png.stat().st_size} bytes")

