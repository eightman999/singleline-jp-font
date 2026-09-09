"""Render one line to a PNG: python render.py '日本語 ABC 123' -o output.png."""
import argparse
from PIL import Image
from dot_font import DotFont
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('text');p.add_argument('-o','--output',default='output.png')
p.add_argument('--size',type=int,choices=(18,24),default=24)
p.add_argument('--scale',type=int,default=1)
a=p.parse_args()
if a.scale<1:p.error('--scale must be positive')
f=DotFont(f'custom-jp-{a.size}',f'custom-ascii-{a.size}')
if f.missing(a.text):p.error('Missing glyphs: '+''.join(f.missing(a.text)))
im=Image.fromarray(f.mask(a.text).astype('uint8')*255)
im.resize((im.width*a.scale,im.height*a.scale),Image.Resampling.NEAREST).save(a.output)
