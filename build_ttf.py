"""Build installable TrueType fonts from the canonical pixel atlases.

Pixel runs become closed outline rectangles, preserving the existing bitmap design.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = Path(__file__).parent

def build(size, ascii_only):
    entries = {}
    for kind in (('ascii',) if ascii_only else ('jp', 'ascii')):
        meta = json.loads((ROOT / f'assets/fonts/custom-{kind}-{size}.json').read_text())
        with Image.open(ROOT / 'assets/fonts' / meta['image']) as im:
            atlas = np.array(im.convert('L')) != 0
        for char, g in meta['glyphs'].items():
            entries[char] = (atlas[g['y']:g['y']+g['height'], g['x']:g['x']+g['width']], g['advance'])
    scale = 64
    em = size * scale
    family = f'Singleline JP {"ASCII" if ascii_only else "Full"} {size}'
    name = family.replace(' ', '') + '-Regular'
    cmap = {ord(c): f'u{ord(c):05X}' for c in sorted(entries)}
    glyphs = {}; metrics = {}
    def outline(mask, advance):
        from shapely.geometry import box
        from shapely.ops import unary_union
        from shapely.geometry.polygon import orient
        pen = TTGlyphPen(None)
        rectangles=[]
        for y, row in enumerate(mask):
            edges = np.flatnonzero(np.diff(np.r_[False, row, False].astype(int)))
            for left, right in zip(edges[::2], edges[1::2]):
                x0, x1 = int(left)*scale, int(right)*scale
                y0, y1 = (size-y-1)*scale, (size-y)*scale
                rectangles.append(box(x0,y0,x1,y1))
        merged=unary_union(rectangles)
        polygons=[] if merged.is_empty else ([merged] if merged.geom_type=='Polygon' else merged.geoms)
        for polygon in polygons:
            polygon=orient(polygon,sign=-1)
            for ring in (polygon.exterior,*polygon.interiors):
                points=[(int(x),int(y)) for x,y in ring.coords[:-1]]
                pen.moveTo(points[0])
                for point in points[1:]:pen.lineTo(point)
                pen.closePath()
        glyph = pen.glyph()
        xs = np.flatnonzero(mask.any(axis=0))
        return glyph, (advance*scale, int(xs[0])*scale if len(xs) else 0)
    missing = np.zeros((size,size), bool)
    missing[2:-2,2] = missing[2:-2,-3] = True
    missing[2,2:-2] = missing[-3,2:-2] = True
    glyphs['.notdef'], metrics['.notdef'] = outline(missing,size+2)
    for c,(mask,advance) in entries.items():
        glyphs[cmap[ord(c)]], metrics[cmap[ord(c)]] = outline(mask,advance)
    fb=FontBuilder(em,isTTF=True)
    fb.setupGlyphOrder(['.notdef',*cmap.values()]);fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=em,descent=0,lineGap=0)
    fb.setupNameTable(dict(familyName=family,styleName='Regular',uniqueFontIdentifier=name+'-1.0',
        fullName=family+' Regular',psName=name,version='Version 1.000',
        licenseDescription='See NOTICE.md: original coordinates AGPL v3; Japanese composition data and generated assets retain GPL v2 notice.',
        licenseInfoURL='https://github.com/eightman999/singleline-jp-font/blob/main/NOTICE.md'))
    fb.setupOS2(sTypoAscender=em,sTypoDescender=0,sTypoLineGap=0,usWinAscent=em,usWinDescent=0,fsType=0)
    fb.setupPost();fb.setupMaxp()
    from fontTools.ttLib import newTable
    from fontTools.ttLib.tables.ttProgram import Program
    fb.font['prep']=newTable('prep')
    fb.font['prep'].program=Program()
    fb.font['prep'].program.fromBytecode([0xB1,1,1,0x8E])  # INSTCTRL: disable grid fitting
    fb.font['gasp']=newTable('gasp');fb.font['gasp'].gaspRange={65535:2}

    # Deterministic build timestamps, not the machine's current time.
    fb.font['head'].created=fb.font['head'].modified=3871756800
    fb.font.recalcTimestamp=False
    out=ROOT/'fonts';out.mkdir(exist_ok=True)
    path=out/(name+'.ttf');fb.save(path)
    print(path.name,len(cmap),'characters')

if __name__=='__main__':
    for size in (18,24):
        for ascii_only in (True,False):build(size,ascii_only)
