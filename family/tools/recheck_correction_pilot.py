"""Small target-only upper-kanji before/after TTF/SJPB build and pixel proofs."""
from pathlib import Path
import sys,json,hashlib
from copy import deepcopy
import argparse
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from family.kanji import build_kanji
from family.model import Glyph
from family.proofread_recheck_corrections import TARGETS,apply_corrections
from family.font_builder import build_font
from family.bitmap import build_bitmaps
from family.bitmap_reader import BitmapFont
from family.styles import STYLES


def build_pilot(root):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    original,_=build_kanji(TARGETS)
    before={c:Glyph(c,original[c],category='kanji') for c in sorted(TARGETS)}
    after=apply_corrections(deepcopy(before));chars=list(before)
    for label,source in [('before',before),('after',after)]:
        for style in STYLES.values():
            build_font(source,style,root/label/'static'/f'{style.key}.ttf')
            for size in (16,18,24,32):build_bitmaps(source,style,size,root/label/'bitmaps')
    ref=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',160,index=0)
    fonts=[ref,*[ImageFont.truetype(str(root/label/'static/singleline.ttf'),160) for label in ('before','after')]]
    for start in range(0,len(chars),5):
        im=Image.new('RGB',(900,1100),'white');d=ImageDraw.Draw(im)
        d.text((10,5),'160px: Noto CJK JP / before / after; self-authored geometry, topology comparison',fill='black')
        for row,c in enumerate(chars[start:start+5]):
            y=row*210+30;d.text((10,y+40),f'U+{ord(c):04X}',fill='black')
            for col,f in enumerate(fonts):d.text((150+col*240,y),c,font=f,fill='black')
        im.save(root/f'comparison-160-{start//5:02}.png')
    cases=[]
    for key in STYLES:
        rows=[]
        for size in (16,18,24,32):
            font=ImageFont.truetype(str(root/'after/static'/f'{key}.ttf'),size)
            bitmap=BitmapFont(root/'after/bitmaps'/f'{key}-{size}.sjpb')
            for kind in ('SJPB','TTF'):
                masks=[]
                for c in chars:
                    if kind=='SJPB':mask=bitmap.bitmap(c)
                    else:
                        core=font.getmask(c,mode='1');mask=np.array(core).reshape(core.size[1],core.size[0])!=0
                    if not mask.any():raise AssertionError((key,size,kind,c,'blank'))
                    masks.append(mask)
                rows.append((kind,size,masks));cases.append({'style':key,'size':size,'format':kind,'glyphs':len(chars),'blank':0})
        for start in range(0,len(chars),13):
            im=Image.new('RGB',(1430,1060),'white');d=ImageDraw.Draw(im)
            d.text((5,5),f'{key}: actual pixels at nearest-neighbour 3x; structure remains difficult at low ppem',fill='black')
            for col,c in enumerate(chars[start:start+13]):d.text((110+col*100,25),f'{ord(c):04X}',fill='black')
            for row,(kind,size,masks) in enumerate(rows):
                y=50+row*125;d.text((5,y+10),f'{kind} {size}px',fill='black')
                for col,m in enumerate(masks[start:start+13]):
                    tile=Image.fromarray((~m.astype(bool)*255).astype('uint8')).resize((m.shape[1]*3,m.shape[0]*3),Image.Resampling.NEAREST)
                    im.paste(tile,(110+col*100,y))
            im.save(root/f'{key}-small-{start//13}.png')
    ledger=[{'character':c,'codepoint':f'U+{ord(c):04X}','before_sha256':hashlib.sha256(json.dumps(before[c].paths).encode()).hexdigest(),'after_sha256':hashlib.sha256(json.dumps(after[c].paths).encode()).hexdigest(),'reason':after[c].notes['proofread_correction']} for c in chars]
    result={'changed_count':len(chars),'glyph_renders':len(cases)*len(chars),'cases':cases,'changes':ledger,'native_os':'not-run','visual_certification':'not asserted; separate review required'}
    (root/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/pilot-recheck-corrections');a=p.parse_args()
    r=build_pilot(a.output);print(r['changed_count'],r['glyph_renders'])
