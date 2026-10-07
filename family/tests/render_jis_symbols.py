"""Render source geometry contact sheets; no external glyph inputs."""
from pathlib import Path
from PIL import Image, ImageDraw
from family import jis_symbols as symbols


def main():
    destination=Path(__file__).with_name('jis-symbol-review')
    destination.mkdir(exist_ok=True)
    items=list(symbols.GLYPHS)
    for page in range((len(items)+79)//80):
        image=Image.new('RGB',(1200,1280),'white')
        draw=ImageDraw.Draw(image)
        for index,char in enumerate(items[page*80:(page+1)*80]):
            x=(index%10)*120+12
            y=(index//10)*160+8
            label='+'.join(f'{ord(s):04X}' for s in char)
            draw.text((x,y),label,fill='#222222')
            for path_index,path in enumerate(symbols.GLYPHS[char]):
                points=[(x+4*a,y+24+4*b) for a,b in path]
                if char in symbols.NEGATIVE:
                    if path_index==0:
                        draw.polygon(points,fill='#111111')
                    else:
                        draw.line(points,fill='white',width=4,joint='curve')
                elif char in symbols.FILLED:
                    draw.polygon(points,fill='#111111')
                else:
                    draw.line(points,fill='#111111',width=3,joint='curve')
        image.save(destination/f'page-{page+1}.png')


if __name__=='__main__':
    main()
