"""Check all TTF cmap entries and actual FreeType pixels against atlas data."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
root=Path(__file__).parent
for size in (18,24):
    for variant in ('ASCII','Full'):
        path=root/f'fonts/SinglelineJP{variant}{size}-Regular.ttf'
        tt=TTFont(path)
        expected={}
        for kind in (('ascii',) if variant=='ASCII' else ('jp','ascii')):
            m=json.loads((root/f'assets/fonts/custom-{kind}-{size}.json').read_text())
            with Image.open(root/'assets/fonts'/m['image']) as im: a=np.asarray(im.convert('L'))>0
            for c,g in m['glyphs'].items():expected[c]=(a[g['y']:g['y']+g['height'],g['x']:g['x']+g['width']],g)
        assert set(tt.getBestCmap())=={ord(c) for c in expected}
        font=ImageFont.truetype(str(path),size,layout_engine=ImageFont.Layout.BASIC)
        for c,(mask,g) in expected.items():
            im=Image.new('L',(g['width'],size));ImageDraw.Draw(im).text((0,size),c,font=font,anchor='ls',fill=255,stroke_width=0)
            assert np.array_equal(np.asarray(im)>127,mask),(path.name,c)
            assert tt['hmtx'][tt.getBestCmap()[ord(c)]][0]==g['advance']*64
        tt.close()
        print('PASS',path.name,len(expected),'cmap, advances and FreeType glyph rasters')
