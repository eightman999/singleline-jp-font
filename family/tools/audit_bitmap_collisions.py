"""Measure actual delivered 1-bit Kanji collisions, without hiding aliases."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from family.bitmap_reader import BitmapFont
from family.repertoire import targets
from family.styles import STYLES
import numpy as np


def main():
    output=ROOT/'build/family/reports/bitmap-collisions.json'
    result={'schema_version':2,'scope':'All eight styles,16/18/24/32px;10,050 JIS Kanji per strike',
            'normalization':'Common pen origin and baseline canvas; crop padding cannot hide identical visible pixels.',
            'styles':{}}
    for style in STYLES:
        result['styles'][style]={}
        for size in (16,18,24,32):
            font=BitmapFont(ROOT/f'build/family/bitmaps/{style}-{size}.sjpb')
            glyphs=[font.glyphs[c] for c in targets()]
            left=min(0,min(g[3] for g in glyphs));right=max(g[0]+g[3] for g in glyphs)
            groups={}
            for c in sorted(targets()):
                mask=np.zeros((font.height,right-left),bool)
                w,h,a,bx,by,_,_=font.glyphs[c]
                mask[font.baseline-by:font.baseline-by+h,bx-left:bx-left+w]=font.bitmap(c)
                key=hashlib.sha256(mask.tobytes()+str(a).encode()).hexdigest()
                groups.setdefault(key,[]).append(c)
            duplicate=[v for v in groups.values() if len(v)>1]
            result['styles'][style][str(size)]={'glyph_count':len(targets()),'unique_bitmap_count':len(groups),
                'collision_group_count':len(duplicate),'characters_in_collisions':sum(map(len,duplicate)),
                'collision_groups':duplicate,
                'warning':'Actual raster collisions are unresolved small-size distinctions, not proof of unique or correct typography. Three original legacy pairs remain unchanged.'}
            print(style,size,'px:',len(groups),'distinct bitmaps;',len(duplicate),'collision groups',flush=True)
    output.parent.mkdir(exist_ok=True,parents=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
