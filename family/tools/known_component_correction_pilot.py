import sys,copy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from PIL import Image,ImageDraw,ImageFont
from family.data_loader import load_glyphs
from family.proofread_known_component_corrections import apply,CORRECTED_CHARACTERS
from family.font_builder import build_font
from family.bitmap import build_bitmaps
from family.bitmap_reader import BitmapFont
from family.styles import STYLES
import numpy as np
out=ROOT/'build/full-proofread/known-component-review';out.mkdir(parents=True,exist_ok=True)
g,*_=load_glyphs()
from family.proofread_deep3_corrections import apply as apply_deep3
compat={'蘒':g['蘒']};apply_deep3(compat);g['蘒']=compat['蘒']
before={c:g[c] for c in CORRECTED_CHARACTERS};after=copy.deepcopy(before);apply(after)
for label,gs in [('before',before),('after',after)]:
 for st in STYLES.values():build_font(gs,st,out/label/(st.key+'.ttf'))
for start in range(0,len(before),4):
 chars=CORRECTED_CHARACTERS[start:start+4];im=Image.new('RGB',(len(chars)*410,900),'white');d=ImageDraw.Draw(im)
 for row,label in enumerate(['before','after']):
  f=ImageFont.truetype(str(out/label/'singleline.ttf'),400)
  for col,c in enumerate(chars):d.text((col*410,row*445),f'{ord(c):04X} {label}',fill='black');d.text((col*410,row*445+25),c,font=f,fill='black')
 im.save(out/f'large-{start//4}.png')
for st in STYLES.values():
 im=Image.new('RGB',(len(after)*225+120,770),'white');d=ImageDraw.Draw(im);d.text((5,5),st.key+' actual TTF at 32/64/200px',fill='black')
 for col,c in enumerate(after):d.text((120+col*225,25),f'U+{ord(c):04X}',fill='black')
 for row,size in enumerate([32,64,200]):
  f=ImageFont.truetype(str(out/'after'/(st.key+'.ttf')),size)
  for col,c in enumerate(after):d.text((120+col*225,60+row*180),c,font=f,fill='black')
  d.text((5,60+row*180),f'{size}px',fill='black')
  result=build_bitmaps(after,st,size,out/'bitmaps');bf=BitmapFont(result['binary'])
  assert all(bf.bitmap(c).any() for c in after)
 im.save(out/(st.key+'.png'))
refs={'難': {'pdf_page': 475, 'j_source': 'J0-4671', 'printed_page': '1031'}, '儺': {'pdf_page': 23, 'j_source': 'J0-5135', 'printed_page': '579'}, '攤': {'pdf_page': 152, 'j_source': 'J0-5A3A', 'printed_page': '708'}, '灘': {'pdf_page': 225, 'j_source': 'J0-4667', 'printed_page': '781'}, '龜': {'pdf_page': 531, 'j_source': 'J0-737D', 'printed_page': '1087'}, '龝': {'pdf_page': 531, 'j_source': 'J0-6354', 'printed_page': '1087'}, '鬮': {'pdf_page': 503, 'j_source': 'J0-722D', 'printed_page': '1059'}, '蘒': {'pdf_page': 10, 'j_source': 'J4-7738', 'printed_page': None}}
for c in after:
 r={'character':c,'codepoint':f'U+{ord(c):04X}','decision':'corrected','source':'https://www.unicode.org/charts/PDF/'+('UF900.pdf' if c=='蘒' else 'U4E00.pdf'),**refs[c],'reason':after[c].notes['proofread_known_component_correction'],'before_paths':before[c].paths,'after_paths':after[c].paths,'geometry_module':'family.proofread_known_component_corrections','render_sizes':[32,64,200,400],'styles':list(STYLES),'native_os_check':'not run','unicode_reference_images_published':False}
 r.pop('excerpt',None);(out/f'review-U{ord(c):04X}.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print(out)

for c in after:
 im=Image.new('RGB',(440,460),'white');d=ImageDraw.Draw(im);d.text((10,5),f'U+{ord(c):04X} after / 400px',fill='black');d.text((20,30),c,font=ImageFont.truetype(str(out/'after/singleline.ttf'),400),fill='black');im.save(out/f'after-U{ord(c):04X}.png')
