"""Refresh explicit glyphs after a bounded source fix, requiring stable metrics.

This produces the same atlas cells and binary glyph bytes as a full rebuild.
If any geometry change needs a different frame or advance, refuse and rebuild
normally. Always run the exhaustive padded-source audit after this operation.
"""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from PIL import Image
from family.bitmap import raster
from family.bitmap_reader import BitmapFont
from family.data_loader import load_glyphs
from family.styles import STYLES


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--characters',required=True)
    args=parser.parse_args();glyphs,_=load_glyphs();changes=[]
    for style in STYLES.values():
        for size in (16,18,24,32):
            root=ROOT/'build/family/bitmaps';name=f'{style.key}-{size}'
            jp=root/(name+'.json');bp=root/(name+'.sjpb');meta=json.loads(jp.read_text())
            font=BitmapFont(bp);binary=bytearray(font.data)
            with Image.open(root/meta['image']) as im:atlas=np.array(im.convert('L'))
            for c in args.characters:
                mask,a,bx,by=raster(glyphs[c],style,size);w,h,oa,ox,oy,po,pl=font.glyphs[c]
                if (mask.shape[1],mask.shape[0],a,bx,by)!=(w,h,oa,ox,oy):
                    raise SystemExit(f'{name} {c!r}: metrics changed; run a full build')
                packed=np.packbits(mask>0,axis=1,bitorder='big').tobytes();assert len(packed)==pl
                old=hashlib.sha256(binary[po:po+pl]).hexdigest();binary[po:po+pl]=packed
                box=meta['glyphs'][c];atlas[box['y']:box['y']+h,box['x']:box['x']+w]=mask
                changes.append({'strike':name,'character':c,'old_bitmap_sha256':old,'new_bitmap_sha256':hashlib.sha256(packed).hexdigest()})
            Image.fromarray(atlas).convert('1').save(root/meta['image'])
            meta['sha256']=hashlib.sha256((root/meta['image']).read_bytes()).hexdigest()
            bp.write_bytes(binary);jp.write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':'))+'\n')
    report=ROOT/'build/family/reports/bitmap-glyph-refresh.json'
    report.write_text(json.dumps({'characters':args.characters,'metrics_changed':False,'changes':changes},ensure_ascii=False,indent=2)+'\n')
    print(f'Refreshed{len(changes)} glyph instances; exhaustive source audit still required')


if __name__=='__main__':main()
