"""Offline original ASCII atlas generation with Japanese-style thin strokes."""
from pathlib import Path
import hashlib
import cv2
import numpy as np
from build_dot_fonts import save_atlas
from custom_ascii_strokes import GLYPHS


def ascii_mask(char, size, fullwidth=False):
    width = size if fullwidth else round(size*2/3)
    mask = np.zeros((size,width),np.uint8)
    for line in GLYPHS[char]:
        points=np.rint(np.asarray(line)*[(width-1)/24,(size-1)/24]).astype(np.int32)
        cv2.polylines(mask,[points],False,255,1,cv2.LINE_8)
    return mask


def main():
    source=Path(__file__).parent/'glyphs/ascii.py'
    for size in (18,24):
        save_atlas(f'custom-ascii-{size}',{c:ascii_mask(c,size) for c in GLYPHS},
                   {'name':'Project original geometric ASCII','coordinates':'glyphs/ascii.py',
                    'coordinate_sources': {str(p.relative_to(source.parent.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (source,source.with_name('paths.py'))},
                    'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'opencv':cv2.__version__},
                   dotted=False,advance_gap=2,
                   rasterization={'thickness':1,'line_type':'LINE_8','thinning':None,'coordinate_grid':24})


if __name__=='__main__':
    main()
