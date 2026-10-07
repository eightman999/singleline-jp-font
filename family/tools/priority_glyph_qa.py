"""Audit priority near-forms in delivered SJPB and static TTF files.

This records exact geometry/pixel distinctions, not Japanese proofreading.
Run from any directory: python family/tools/priority_glyph_qa.py
"""
import argparse
import hashlib
import html
import itertools
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np
from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version, features
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

from family.bitmap_reader import BitmapFont
from family.styles import STYLES

GROUPS = ("己已巳", "未末", "土士", "高髙", "吉𠮷")
CHARACTERS = "".join(GROUPS)
PAIRS = tuple(pair for group in GROUPS for pair in itertools.combinations(group, 2))
SIZES = (16, 18, 24, 32)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pixel_signature(mask, bearing_x, bearing_y, advance):
    """Ignore crop padding; preserve baseline-relative ink and advance."""
    rows, cols = np.nonzero(mask)
    if not len(rows):
        payload = [float(advance), []]
    else:
        points = sorted((int(x) + bearing_x, int(y) - bearing_y)
                        for y, x in zip(rows, cols))
        payload = [float(advance), points]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()


def record(mask, bx, by, advance):
    return {"width": mask.shape[1], "height": mask.shape[0],
            "bearing_x": bx, "bearing_y": by, "advance": float(advance),
            "ink_pixels": int(mask.sum()),
            "pixel_sha256": pixel_signature(mask, bx, by, advance)}


def aligned_masks(records, masks):
    left = min(0, *(r["bearing_x"] for r in records.values()))
    right = max(r["bearing_x"] + r["width"] for r in records.values())
    top = min(0, *(-r["bearing_y"] for r in records.values()))
    bottom = max(0, *(r["height"] - r["bearing_y"] for r in records.values()))
    aligned = {}
    for char, r in records.items():
        canvas = np.zeros((bottom - top, right - left), dtype=bool)
        x, y = r["bearing_x"] - left, -r["bearing_y"] - top
        canvas[y:y + r["height"], x:x + r["width"]] = masks[char]
        aligned[char] = canvas
    return aligned


def pair_results(records, masks):
    aligned = aligned_masks(records, masks)
    return [{"characters": list(pair),
             "codepoints": [f"U+{ord(c):04X}" for c in pair],
             "same_ink_pixels": bool(np.array_equal(aligned[pair[0]], aligned[pair[1]])),
             "same_advance": records[pair[0]]["advance"] == records[pair[1]]["advance"],
             "indistinguishable": records[pair[0]]["pixel_sha256"] == records[pair[1]]["pixel_sha256"],
             "different_pixels": int(np.count_nonzero(aligned[pair[0]] ^ aligned[pair[1]]))}
            for pair in PAIRS]


def proof_sheet(style, samples, path):
    """ASCII labels only; actual inspected glyphs come from delivered files."""
    cell_width, row_height, margin, scale = 110, 160, 150, 3
    image = Image.new("1", (margin + len(CHARACTERS) * cell_width, 70 + 8 * row_height), 1)
    draw = ImageDraw.Draw(image)
    draw.text((12, 10), f"Priority near-form audit: {style}; nearest-neighbour 3x", fill=0)
    draw.text((12, 27), "Delivered SJPB / static TTF via FreeType; not native OS or full visual certification", fill=0)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{image.width}" height="{image.height}" viewBox="0 0 {image.width} {image.height}">',
           '<title>Priority near-form actual-pixel proof: ' + html.escape(style) + '</title>',
           '<rect width="100%" height="100%" fill="white"/>',
           '<g fill="black" font-family="monospace" font-size="11">',
           f'<text x="12" y="20">Priority near-form audit: {html.escape(style)}; exact pixels at 3x</text>',
           '<text x="12" y="37">Delivered SJPB / static TTF via FreeType; not native OS or full visual certification</text>']
    for i, char in enumerate(CHARACTERS):
        draw.text((margin + i * cell_width, 49), f"U+{ord(char):04X}", fill=0)
        svg.append(f'<text x="{margin + i * cell_width}" y="59">U+{ord(char):04X}</text>')
    for row, (kind, size, records, masks) in enumerate(samples):
        y = 70 + row * row_height
        draw.text((12, y + 10), f"{kind} {size}px", fill=0)
        svg.append(f'<text x="12" y="{y + 20}">{kind} {size}px</text>')
        aligned = aligned_masks(records, masks)
        for i, char in enumerate(CHARACTERS):
            tile = Image.fromarray(~aligned[char]).resize(
                (aligned[char].shape[1] * scale, aligned[char].shape[0] * scale),
                Image.Resampling.NEAREST)
            image.paste(tile, (margin + i * cell_width, y + 25))
            rows, cols = np.nonzero(aligned[char])
            pixels = "".join(f'M{int(x) * scale},{int(r) * scale}h{scale}v{scale}h{-scale}z'
                             for r, x in zip(rows, cols))
            svg.append(f'<path transform="translate({margin + i * cell_width},{y + 25})" d="{pixels}"/>')
    svg.append('</g></svg>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(svg) + "\n")
    # Local visual-inspection aid; SVG is the canonical publishable proof.
    image.save(path.with_suffix('.png'))


def audit(output, report_path=None):
    output = Path(output)
    report_path = Path(report_path) if report_path else output / "reports/priority-glyph-qa.json"
    result = {"schema_version": 1, "groups": list(GROUPS),
              "sizes": list(SIZES), "styles": list(STYLES),
              "scope": "11 scalars; 7 near-form pairs; 8 static TTFs and 32 delivered SJPB strikes",
              "raster_engine": {"pillow": pillow_version, "freetype": features.version_module("freetype2"),
                                "python": platform.python_version(), "platform": platform.system(),
                                "mode": "monochrome, baseline anchor ls, BASIC layout, unscaled pixels"},
              "method": "Exact ink coordinates relative to pen origin/baseline plus advance. Crop padding is ignored. Outline hashes preserve drawing command order and are not a perceptual shape test.",
              "visual_proofreading": "not-certified", "native_os_installation": "not-run",
              "macos_coretext": "not-run", "windows_directwrite": "not-run",
              "variable_fonts": "outside-this-focused-audit",
              "source_sha256": {str(Path(__file__).relative_to(ROOT)): sha(__file__)},
              "artifact_sha256": {}, "outlines": [], "cases": [], "proofs": []}
    for style in STYLES:
        samples = []
        ttf_path = output / "static" / f"SinglelineJPLab-{style}.ttf"
        result["artifact_sha256"][str(ttf_path.relative_to(output))] = sha(ttf_path)
        with TTFont(ttf_path) as ttfont:
            glyphset = ttfont.getGlyphSet()
            cmap = ttfont.getBestCmap()
            outline_records = {}
            for char in CHARACTERS:
                if ord(char) not in cmap:
                    raise ValueError(f"Missing TTF scalar {char!r} in {ttf_path}")
                name = cmap[ord(char)]
                pen = DecomposingRecordingPen(glyphset)
                glyphset[name].draw(pen)
                payload = [pen.value, ttfont["hmtx"][name]]
                outline_records[char] = {"glyph_name": name, "command_count": len(pen.value),
                                        "outline_sha256": hashlib.sha256(json.dumps(payload).encode()).hexdigest()}
            result["outlines"].append({"style": style, "glyphs": outline_records,
                "pairs": [{"characters": list(pair), "same_outline_and_metrics":
                           outline_records[pair[0]]["outline_sha256"] == outline_records[pair[1]]["outline_sha256"]}
                          for pair in PAIRS]})
        for size in SIZES:
            bitmap_path = output / "bitmaps" / f"{style}-{size}.sjpb"
            result["artifact_sha256"][str(bitmap_path.relative_to(output))] = sha(bitmap_path)
            bitmap = BitmapFont(bitmap_path)
            font = ImageFont.truetype(str(ttf_path), size, layout_engine=ImageFont.Layout.BASIC)
            for kind in ("SJPB", "TTF"):
                records, masks = {}, {}
                for char in CHARACTERS:
                    if kind == "SJPB":
                        _, _, advance, bx, by, _, _ = bitmap.glyphs[char]
                        mask = bitmap.bitmap(char)
                    else:
                        core, (bx, top) = font.getmask2(char, mode="1", anchor="ls")
                        mask = np.array(core, dtype=np.uint8).reshape(core.size[1], core.size[0]) != 0
                        by, advance = -top, font.getlength(char)
                    if not mask.any():
                        raise ValueError(f"Blank priority glyph {char!r}: {style} {kind} {size}")
                    masks[char] = mask
                    records[char] = record(mask, bx, by, advance)
                result["cases"].append({"style": style, "kind": kind, "pixels": size,
                                        "glyphs": records, "pairs": pair_results(records, masks)})
                samples.append((kind, size, records, masks))
        proof = output / "proofs" / "priority-glyphs" / f"{style}.svg"
        proof_sheet(style, samples, proof)
        result["proofs"].append({"path": str(proof.relative_to(output)), "sha256": sha(proof),
                                 "scale": 3, "visual_review": "not-recorded-by-this-tool"})
    collisions = [{"style": case["style"], "kind": case["kind"], "pixels": case["pixels"],
                   "characters": pair["characters"]}
                  for case in result["cases"] for pair in case["pairs"] if pair["indistinguishable"]]
    result["summary"] = {"glyph_renders": len(result["cases"]) * len(CHARACTERS),
                         "pair_comparisons": len(result["cases"]) * len(PAIRS),
                         "missing_or_blank": 0,
                         "identical_outline_pairs": sum(p["same_outline_and_metrics"] for s in result["outlines"] for p in s["pairs"]),
                         "indistinguishable_pair_cases": len(collisions), "collisions": collisions,
                         "outcome": "measured-with-collisions" if collisions else "measured-no-exact-collisions",
                         "warning": "A nonzero pixel difference is not proof of perceptible distinction or correct Japanese form. Existing glyphs are not changed."}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/family")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.output, args.report)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
