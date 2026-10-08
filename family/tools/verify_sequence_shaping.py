"""Real HarfBuzz input-path checks, separate from direct-glyph proofing.

A raster difference against the explicit sequence glyph is a review candidate,
not proof of a wrong letterform. Canonical equivalence and SVS routing are
checked independently. ccmp-off is diagnostic only. Never edits the input font.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import unicodedata as ud

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from PIL import Image,ImageDraw
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb
from family.data_loader import load_glyphs
from family.model import glyph_name
from family.font_builder import standard_variants
from family.tools.full_glyph_proofread import DirectFont


def shape(font,text,features=None,language=None):
    buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties()
    if language:buf.language=language
    hb.shape(font,buf,features or {})
    return [{'gid':i.codepoint,'cluster':i.cluster,'x_advance':p.x_advance,'y_advance':p.y_advance,'x_offset':p.x_offset,'y_offset':p.y_offset} for i,p in zip(buf.glyph_infos,buf.glyph_positions)]


def run_key(run):
    return [(r['gid'],r['x_advance'],r['y_advance'],r['x_offset'],r['y_offset']) for r in run]


def draw_run(direct,order,run,size=160):
    # Fixed pen origin/baseline: no independent crop or centering that could
    # hide mark-positioning defects. Allow multiple-advance tone contours.
    im=Image.new('L',(size*4,size*3),0);x=y=0
    for r in run:
        mask,offset,advance=direct.mask(order[r['gid']],size)
        bx=round(size+(x+r['x_offset'])*size/1000)+offset[0]
        by=round(size*2-(y+r['y_offset'])*size/1000)+offset[1]
        if mask.width and mask.height:im.paste(Image.fromarray(np.maximum(np.asarray(im.crop((bx,by,bx+mask.width,by+mask.height))),np.asarray(mask))),(bx,by))
        x+=r['x_advance'];y+=r['y_advance']
    return im


def outline_key(tt,order,run):
    gs=tt.getGlyphSet();x=y=0;parts=[];upem=tt['head'].unitsPerEm
    for r in run:
        pen=DecomposingRecordingPen(gs)
        gs[order[r['gid']]].draw(TransformPen(pen,(1000/upem,0,0,1000/upem,x+r['x_offset'],y+r['y_offset'])))
        parts.extend(pen.value);x+=r['x_advance'];y+=r['y_advance']
    return json.dumps([parts,x,y],sort_keys=True,separators=(',',':'))


def audit(font_path,output,glyphs=None,render=True):
    font_path=Path(font_path);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    glyphs=load_glyphs()[0] if glyphs is None else glyphs
    data=font_path.read_bytes();tt=TTFont(font_path);order=tt.getGlyphOrder();order_before=list(order);upem=tt['head'].unitsPerEm
    face=hb.Face(data);font=hb.Font(face);font.scale=(1000,1000);hb.ot_font_set_funcs(font)
    # DirectFont mutates only this independent in-memory TTFont.
    direct=DirectFont(TTFont(font_path),{n:n for n in order})
    records=[];images=[];cmap=tt.getBestCmap();names=set(order)
    for text in sorted(t for t in glyphs if len(t)>1):
        nfc=ud.normalize('NFC',text);lang='ja' if any(0x3000<=ord(c)<=0x30ff for c in text) else ('el' if 'GREEK' in ud.name(text[0],'') else 'ru' if 'CYRILLIC' in ud.name(text[0],'') else 'en')
        normal=shape(font,text,language=lang);nfc_run=shape(font,nfc,language=lang);off=shape(font,text,{'ccmp':False},lang)
        explicit_name=glyph_name(text);exists=explicit_name in names
        explicit=[{'gid':tt.getGlyphID(explicit_name),'cluster':0,'x_advance':round(tt['hmtx'][explicit_name][0]*1000/upem),'y_advance':0,'x_offset':0,'y_offset':0}] if exists else []
        actual=draw_run(direct,order,normal);wanted=draw_run(direct,order,explicit) if exists else Image.new('L',actual.size)
        nfc_image=draw_run(direct,order,nfc_run)
        equal=bool(np.array_equal(np.asarray(actual),np.asarray(wanted))) and sum(r['x_advance'] for r in normal)==sum(r['x_advance'] for r in explicit)
        canon_equal=bool(np.array_equal(np.asarray(actual),np.asarray(nfc_image))) and sum(r['x_advance'] for r in normal)==sum(r['x_advance'] for r in nfc_run)
        record={'text':text,'codepoints':[f'U+{ord(c):04X}' for c in text],'nfc':nfc,'language':lang,'normal_run':normal,'normal_glyphs':[order[r['gid']] for r in normal],'nfc_run':nfc_run,'explicit_glyph':explicit_name,'explicit_exists':exists,'normal_equals_explicit_outline':outline_key(tt,order,normal)==outline_key(tt,order,explicit),'normal_equals_explicit_pixels':equal,'normal_equals_nfc_pixels':canon_equal,'normal_missing_glyph':any(r['gid']==0 for r in normal),'ccmp_off_run':off,'ccmp_off_note':'Diagnostic only; differences are not failures. Normalization may still compose to a precomposed scalar.','status':'routing-equivalent' if equal or outline_key(tt,order,normal)==outline_key(tt,order,explicit) else 'visual-review-required'}
        # Canonical reordering must retain identity for differing CCC marks.
        tail=list(text[1:])
        if len(tail)>1 and all(ud.combining(c)>0 for c in tail) and len({ud.combining(c) for c in tail})>1:
            reordered=text[0]+''.join(sorted(tail,key=ud.combining,reverse=True));rr=shape(font,reordered,language=lang)
            record['reordered_input']=reordered;record['canonical_reordering_equal']=run_key(rr)==run_key(normal)
        records.append(record);images.append((actual,wanted,nfc_image))
    svs=[]
    for text,target in standard_variants(glyphs):
        run=shape(font,text,language='ja');expected=cmap.get(ord(target));expected_gid=tt.getGlyphID(expected) if expected else None
        svs.append({'text':text,'codepoints':[f'U+{ord(c):04X}' for c in text],'target':target,'expected_glyph':expected,'run':run,'actual_glyphs':[order[r['gid']] for r in run],'pass':len(run)==1 and run[0]['gid']==expected_gid})
    # Exercise actual mark positioning where no explicit ccmp sequence exists.
    fallback=[]
    for base,mark in [('A','\u0318'),('x','\u0323'),('B','\u0301'),('q','\u0308'),('n','\u0338')]:
        text=base+mark
        if base not in glyphs or mark not in glyphs:continue
        run=shape(font,text,language='en');fallback.append({'text':text,'normal_run':run,'normal_glyphs':[order[r['gid']] for r in run],'mark_off_run':shape(font,text,{'mark':False},'en'),'missing':any(r['gid']==0 for r in run),'status':'visual-review-required','note':'No explicit sequence expected; inspect real mark offsets, not concatenated strings.'})
    if render:
        for page,start in enumerate(range(0,len(records),48),1):
            im=Image.new('RGB',(1600,1280),'white');d=ImageDraw.Draw(im);d.text((3,3),'LEFT real HB sequence / MIDDLE explicit sequence glyph / RIGHT real HB NFC;160px raster reduced for page layout',fill='black')
            for j,r in enumerate(records[start:start+48]):
                x=j%4*400;y=30+j//4*104;d.rectangle((x,y,x+399,y+103),outline='#ccc');d.text((x+2,y+1),' '.join(r['codepoints']),fill='black')
                for k,mask in enumerate(images[start+j]):
                    # Same origin and fixed crop for all three outputs.
                    tile=Image.eval(mask.crop((120,135,360,385)),lambda p:255-p).resize((96,100))
                    im.paste(tile,(x+k*130,y+12))
                r['viewed_image']=str(output/f'sequences-{page:02}.png');r['cell']=j
            im.save(output/f'sequences-{page:02}.png')
        fim=Image.new('RGB',(1000,max(1,len(fallback))*250),'white');d=ImageDraw.Draw(fim)
        for i,r in enumerate(fallback):
            y=i*250;d.text((3,y+2),' '.join(f'U+{ord(c):04X}' for c in r['text'])+' normal / mark-off',fill='black')
            for k,run in enumerate([r['normal_run'],r['mark_off_run']]):
                mask=draw_run(direct,order,run);tile=Image.eval(mask.crop((120,135,500,385)),lambda p:255-p);fim.paste(tile,(k*480,y+15))
            r['viewed_image']=str(output/'fallback.png')
        fim.save(output/'fallback.png')
    summary={'artifact':str(font_path),'artifact_sha256':hashlib.sha256(data).hexdigest(),'harfbuzz_version':hb.version_string(),'sequence_count':len(records),'normal_explicit_outline_equal':sum(r['normal_equals_explicit_outline'] for r in records),'canonical_reorder_count':sum('canonical_reordering_equal' in r for r in records),'canonical_reorder_pass':sum(r.get('canonical_reordering_equal',False) for r in records),'normal_explicit_pixel_equal':sum(r['normal_equals_explicit_pixels'] for r in records),'normal_nfc_pixel_equal':sum(r['normal_equals_nfc_pixels'] for r in records),'normal_missing':sum(r['normal_missing_glyph'] for r in records),'svs_count':len(svs),'svs_pass':sum(r['pass'] for r in svs),'glyph_order_unchanged':TTFont(font_path).getGlyphOrder()==order_before,'scope':'Real default-feature HarfBuzz input paths with guessed script and explicit reasonable language. Geometry differences require visual judgment. Raster at160; proof-page display reduced. Static/default instance only.'}
    report={'summary':summary,'sequences':records,'svs':svs,'mark_fallback':fallback};(output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));return report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('font',type=Path);parser.add_argument('--output',type=Path,default=ROOT/'build/sequence-shaping');parser.add_argument('--no-render',action='store_true');args=parser.parse_args();print(json.dumps(audit(args.font,args.output,render=not args.no_render)['summary'],indent=2))
if __name__=='__main__':main()
