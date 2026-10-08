"""Build small, isolated correction proofs; never rebuild the full family."""
import argparse,hashlib,json,sys,unicodedata as ud
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import numpy as np
from PIL import Image,ImageDraw
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from family.data_loader import load_glyphs
from family.font_builder import build_font
from family.bitmap import build_bitmaps
from family.bitmap_reader import BitmapFont
from family.model import glyph_name
from family.styles import STYLES
from family.tools.full_glyph_proofread import DirectFont
SIZES=(16,18,24,32)


def hash_json(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def image_sig(mask):
    im=Image.fromarray(mask.astype('uint8'));box=im.getbbox();a=np.asarray(im.crop(box)) if box else np.zeros((0,0),dtype=np.uint8)
    return hash_json([list(a.shape),a.tolist()])


def build(output,styles=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);g,_=load_glyphs()
    ledger=json.loads((ROOT/'build/pilot-priority-corrections/accent-change-ledger.json').read_text())
    targets=sorted({r['text'] for r in ledger['changes']}|{'ϕ','ɤ'});keys=set(targets);pairs={}
    for t in targets:
        s=ud.normalize('NFD',t)
        if '\u0300' in s:
            a=s.replace('\u0300','\u0301');a=ud.normalize('NFC',a) if len(t)==1 else a
            if a in g:pairs[t]=a;keys.add(a)
        if len(t)>1:
            keys.update(c for c in t if c in g)
        nfc=ud.normalize('NFC',t)
        if nfc in g:keys.add(nfc)
    keys.update(['ψ','γ'])
    subset={t:g[t] for t in sorted(keys)};all_records=[];manifest={'targets':targets,'count':len(targets),'styles':{},'scale':3,'render_scope':'Actual grayscale FreeType TTF and 1-bit SJPB pixels at16/18/24/32; each ink crop enlarged3x nearest-neighbour. Independent ink cropping does not certify baseline or metrics.'}
    for stylekey in (styles or list(STYLES)):
        st=STYLES[stylekey];directory=output/stylekey;directory.mkdir(exist_ok=True)
        ttf=directory/f'{stylekey}.ttf';build_font(subset,st,ttf);direct=DirectFont(TTFont(ttf),{t:glyph_name(t) for t in subset});bitmaps={}
        for size in SIZES:
            build_bitmaps(subset,st,size,directory);bitmaps[size]=BitmapFont(directory/f'{stylekey}-{size}.sjpb')
        masks={};records=[]
        for t in subset:
            for size in SIZES:
                m,offset,advance=direct.mask(t,size);m=np.asarray(m);b=bitmaps[size];w,h,a,bx,by,_,_=b.glyphs[t]
                for kind,mask,bearing,adv in [('ttf',m,list(offset),advance),('sjpb',b.bitmap(t).astype('uint8')*255,[bx,-by],a)]:
                    masks[t,kind,size]=mask
                    if t not in targets:continue
                    records.append({'text':t,'codepoints':[f'U+{ord(c):04X}' for c in t],'style':stylekey,'size':size,'kind':kind,'blank':not bool(np.any(mask)),'bearing':bearing,'advance':adv,'frame':[int(mask.shape[1]),int(mask.shape[0])],'ink_pixels':int(np.count_nonzero(mask)),'pixel_sha256':hash_json(mask.tolist()),'crop_sha256':image_sig(mask),'binarized128_crop_sha256':image_sig(mask>=128),'status':'pending-visual-review'})
        for r in records:
            if r['text'] in pairs:
                peer=pairs[r['text']];mask=masks[peer,r['kind'],r['size']];r['acute_peer']=peer;r['grave_acute_identical']=r['crop_sha256']==image_sig(mask);r['grave_acute_identical_at128']=r['binarized128_crop_sha256']==image_sig(mask>=128)
        for page,start in enumerate(range(0,len(targets),24),1):
            im=Image.new('RGB',(1600,1430),'white');d=ImageDraw.Draw(im);d.text((3,3),f'{stylekey}: native TTF(top)/SJPB(bottom),16/18/24/32 px; each ink crop3x nearest. Page{page}',fill='black')
            for j,t in enumerate(targets[start:start+24]):
                x=j%4*400;y=45+j//4*230;d.rectangle((x,y,x+399,y+229),outline='#ccc');d.text((x+3,y+2),' '.join(f'U+{ord(c):04X}' for c in t),fill='black')
                for row,kind in enumerate(['ttf','sjpb']):
                    for col,size in enumerate(SIZES):
                        tx=x+col*100;ty=y+18+row*104;d.text((tx+2,ty),f'{kind[0].upper()}{size}',fill='#666');mask=masks[t,kind,size];tile=Image.fromarray(mask);box=tile.getbbox()
                        if box:
                            tile=tile.crop(box);tile=Image.eval(tile,lambda p:255-p).resize((tile.width*3,tile.height*3),Image.Resampling.NEAREST);im.paste(tile,(tx+3,ty+13))
                        else:d.text((tx+3,ty+25),'BLANK',fill='red')
                for r in records:
                    if r['text']==t:r['viewed_image']=str(directory/f'{page:02}.png');r['cell']=j
            im.save(directory/f'{page:02}.png')
        f=TTFont(ttf);gs=f.getGlyphSet();outline={}
        for t in targets:
            pen=DecomposingRecordingPen(gs);n=glyph_name(t);gs[n].draw(pen);outline[t]=hash_json([pen.value,f['hmtx'][n]])
        meta={'ttf':str(ttf),'ttf_sha256':hashlib.sha256(ttf.read_bytes()).hexdigest(),'target_outline_metric_sha256':outline,'records':len(records),'pages':10,'blank_records':sum(r['blank'] for r in records),'grave_acute_collisions':sum(r.get('grave_acute_identical',False) for r in records)}
        (directory/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));(directory/'manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));manifest['styles'][stylekey]=meta;all_records.extend(records);print(stylekey,len(records),flush=True)
    (output/'records.json').write_text(json.dumps(all_records,ensure_ascii=False,indent=2));(output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));return manifest

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'build/full-proofread/nonkanji-small-sizes');p.add_argument('--styles',nargs='+');a=p.parse_args();build(a.output,a.styles)
