"""Render delivered SJPB bytes, rather than regenerating or tracing outlines."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from family.bitmap_reader import BitmapFont
from family.styles import STYLES

ROOT=Path(__file__).resolve().parent/'build/family'


def main():
    label=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',28)
    image=Image.new('RGB',(2500,1260),'#f6f3e9');draw=ImageDraw.Draw(image)
    draw.text((35,22),'Actual 1-bit binary strikes | nearest-neighbor 2x view',font=title,fill='#173b40')
    draw.text((35,68),'Read directly from delivered SJPB files. Native sizes are16/18/24/32px; all data remain1-bit. Dense and reduced forms are experimental.',font=label,fill='#665e54')
    sample='日本語鬱齋髙𠮷\ue000\ue00d'
    for row,key in enumerate(STYLES):
        y=115+row*140
        for x,size in ((35,16),(645,18),(1255,24),(1865,32)):
            draw.text((x,y),STYLES[key].label+f' /{size}px',font=label,fill='#936048')
            font=BitmapFont(ROOT/f'bitmaps/{key}-{size}.sjpb')
            pixels=font.mask(sample)
            tile=Image.fromarray(np.where(pixels,255,0).astype(np.uint8)).convert('RGB')
            tile=tile.resize((tile.width*2,tile.height*2),Image.Resampling.NEAREST)
            image.paste(tile,(x,y+30))
    image.save(ROOT/'specimen/bitmap-proof.png')
    report=json.loads((ROOT/'reports/bitmap-collisions.json').read_text())
    groups=report['styles']['singleline']['24']['collision_groups']
    image=Image.new('RGB',(1400,100+len(groups)*165),'#f6f3e9');draw=ImageDraw.Draw(image)
    draw.text((30,20),'Raster collisions | exact code-point pairs, original bytes',font=title,fill='#173b40')
    for row,chars in enumerate(groups):
        y=90+row*165
        draw.text((30,y),' / '.join(f'U+{ord(c):04X}' for c in chars),font=label,fill='#665e54')
        for column,size in enumerate((18,24)):
            font=BitmapFont(ROOT/f'bitmaps/singleline-{size}.sjpb')
            x=380+column*450
            draw.text((x,y-10),f'{size}px, 4x nearest-neighbor',font=label,fill='#936048')
            for j,c in enumerate(chars):
                pixels=font.bitmap(c)
                tile=Image.fromarray(np.where(pixels,255,0).astype(np.uint8)).convert('RGB')
                image.paste(tile.resize((tile.width*4,tile.height*4),Image.Resampling.NEAREST),(x+j*130,y+24))
    image.save(ROOT/'specimen/bitmap-collisions.png')


if __name__=='__main__':main()
