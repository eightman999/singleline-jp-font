"""Reproduce small actual-TTF/SJPB priority before/after proofs, not a release build."""
from pathlib import Path
import argparse
import json
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from family.data_loader import load_glyphs
from family.font_builder import build_font
from family.bitmap import build_bitmaps
from family.styles import STYLES
from family.model import Glyph
from family.tools.priority_glyph_qa import CHARACTERS,SIZES,audit


def build_pilot(output, include_before=True):
    output=Path(output)
    loaded,_=load_glyphs()
    after={c:loaded[c] for c in CHARACTERS}
    groups={'after':after}
    if include_before:
        from glyphs.kanji import GLYPHS as legacy
        from family.kanji import build_kanji
        expanded,_=build_kanji(set(CHARACTERS))
        groups={'before':{c:Glyph(c,legacy.get(c,expanded.get(c)),category='kanji') for c in CHARACTERS},**groups}
    summaries={}
    for label,glyphs in groups.items():
        for style in STYLES.values():
            build_font(glyphs,style,output/label/'static'/f'SinglelineJPLab-{style.key}.ttf')
            for size in SIZES:build_bitmaps(glyphs,style,size,output/label/'bitmaps')
        summaries[label]=audit(output/label)['summary']
    return summaries


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'build/pilot-priority-corrections')
    print(json.dumps(build_pilot(p.parse_args().output),ensure_ascii=False,indent=2))
