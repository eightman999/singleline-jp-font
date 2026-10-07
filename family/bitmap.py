"""1-bit atlas and portable, sequence-aware SJPB v1 binary font pack.

All integers little-endian. Header <4sHHIIIIII> (32 bytes): magic SJPB,
version=1, flags=0, count, nominal_px, index_offset, keys_offset,
pixels_offset, baseline_px. Index <IIHHhhhHII> (28 bytes): UTF8 key offset
relative to keys, key byte length, width, height, advance, bearing_x,
bearing_y, flags=0, packed pixel offset relative to pixels, byte length.
Each bitmap row is padded to a byte, high bit first; 1 means foreground.
Missing glyphs raise KeyError. There is no silent fallback or normalization.
"""
from pathlib import Path
import hashlib,json,struct
import numpy as np
import cv2
from PIL import Image
from .geometry import contours,centerlines
from .font_builder import standard_variants

from .bitmap_reader import BitmapFont,HEADER,INDEX


def raster(glyph,style,size):
    scale=size/1000
    advance=max(0,round(glyph.advance*style.scale*scale))
    polygons=contours(glyph,style)
    xs=[x for p in polygons for x,y in p]
    ys=[y for p in polygons for x,y in p]
    left=min(0,int(np.floor(min(xs)*scale))-1) if xs else 0
    right=max(advance,int(np.ceil(max(xs)*scale))+2) if xs else max(1,advance)
    # A nominal em size is not a clipping rectangle. Subscript box drawings
    # descend to -290 units. Retain real bounds, plus raster sampling guards,
    # and store the changed bitmap origin in the existing SJPB bearing fields.
    top=min(0,int(np.floor(size-max(ys)*scale))-1) if ys else 0
    bottom=max(round(size*1.25),int(np.ceil(size-min(ys)*scale))+2) if ys else round(size*1.25)
    height=bottom-top
    bearing_y=size-top
    if style.key=='singleline':
        mask=np.zeros((height,max(1,right-left)),np.uint8)
        for index,path in enumerate(centerlines(glyph,style)):
            points=np.rint([(x*scale-left,bearing_y-y*scale) for x,y in path]).astype(np.int32)
            if glyph.notes.get('negative'):
                if index==0:cv2.fillPoly(mask,[points],255,lineType=cv2.LINE_8)
                elif len(points):cv2.polylines(mask,[points],False,0,1,cv2.LINE_8)
            elif glyph.filled:cv2.fillPoly(mask,[points],255,lineType=cv2.LINE_8)
            elif len(points):cv2.polylines(mask,[points],False,255,1,cv2.LINE_8)
        return mask,advance,left,bearing_y
    ss=4
    high=np.zeros((height*ss,max(1,right-left)*ss),np.uint8)
    cutouts=np.zeros_like(high) if glyph.notes.get('negative') else None
    for index,polygon in enumerate(polygons):
        # Union of independently rasterized strokes: overlapping strokes must
        # not cancel. Polygon-internal holes remain transparent.
        points=np.rint([((x*scale-left)*ss,(bearing_y-y*scale)*ss) for x,y in polygon]).astype(np.int32)
        if len(set(map(tuple,points)))<3:continue
        area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1]))
        color=0 if glyph.notes.get('negative') and area>0 else 255
        cv2.fillPoly(high,[points],color,lineType=cv2.LINE_8)
        if cutouts is not None and index>0:
            cv2.fillPoly(cutouts,[points],255 if area>0 else 0,lineType=cv2.LINE_8)
    coverage=cv2.resize(high,(high.shape[1]//ss,height),interpolation=cv2.INTER_AREA)
    mask=np.where(coverage>=32,255,0).astype(np.uint8)
    if cutouts is not None:
        # Foreground thresholding alone swallows thin white counters. Give
        # their separately rasterized union the same minimum coverage test.
        cut_coverage=cv2.resize(cutouts,(high.shape[1]//ss,height),interpolation=cv2.INTER_AREA)
        mask[cut_coverage>=32]=0
    return mask,advance,left,bearing_y


def build_bitmaps(glyphs,style,size,directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    name=f'{style.key}-{size}'
    variants=standard_variants(glyphs)
    entries=dict(glyphs)
    for seq,target in variants:entries[seq]=glyphs[target]
    masks={};metrics={}
    for c,g in entries.items():
        masks[c],a,x,y=raster(g,style,size);metrics[c]=(a,x,y)
    baseline=max(by for a,bx,by in metrics.values())
    line_height=max(baseline-metrics[c][2]+m.shape[0] for c,m in masks.items())
    maxw=max(m.shape[1] for m in masks.values());maxh=max(m.shape[0] for m in masks.values())
    cols=32
    atlas=np.zeros(((len(entries)+cols-1)//cols*maxh,cols*maxw),np.uint8)
    atlasmeta={};keys=bytearray();pixels=bytearray();records=[]
    for i,c in enumerate(sorted(entries)):
        mask=masks[c];h,w=mask.shape;advance,bx,by=metrics[c]
        x,y=(i%cols)*maxw,(i//cols)*maxh
        atlas[y:y+h,x:x+w]=mask
        atlasmeta[c]={'x':x,'y':y,'width':w,'height':h,'advance':advance,'bearing_x':bx,'bearing_y':by}
        key=c.encode('utf-8');packed=np.packbits(mask>0,axis=1,bitorder='big').tobytes()
        records.append(INDEX.pack(len(keys),len(key),w,h,advance,bx,by,0,len(pixels),len(packed)))
        keys+=key;pixels+=packed
    image=directory/(name+'.png');Image.fromarray(atlas).convert('1').save(image)
    manifest={'version':1,'image':image.name,'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
        'style':style.key,'nominal_size':size,'baseline':baseline,'line_height':line_height,'binary_values':[0,255],
        'rasterization':('direct 1px centerline LINE_8' if style.key=='singleline' else '4x coverage; threshold>=32/255'),
        'source':'original centerline expansion; no external glyph outlines','glyphs':atlasmeta,
        'warning':'New family rasterization. Legacy custom-jp/custom-ascii atlases remain byte-identical. Nominal16/18/24/32px sizes are1-bit strikes; dense Kanji and reduced styles require per-glyph review.'}
    (directory/(name+'.json')).write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+'\n')
    index_offset=HEADER.size;keys_offset=index_offset+len(records)*INDEX.size;pixels_offset=keys_offset+len(keys)
    binary=directory/(name+'.sjpb')
    binary.write_bytes(HEADER.pack(b'SJPB',1,0,len(records),size,index_offset,keys_offset,pixels_offset,baseline)+b''.join(records)+keys+pixels)
    return {'name':name,'glyphs':len(entries),'bytes':binary.stat().st_size,'binary':str(binary)}
