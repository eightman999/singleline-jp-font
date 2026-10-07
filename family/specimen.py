"""Offline visual proof sheets and a self-contained HTML specimen interface."""
import json,html
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from .styles import STYLES

SYSTEM_LABEL='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def label(size=18):
    try:return ImageFont.truetype(SYSTEM_LABEL,size)
    except OSError:return ImageFont.load_default(size=size)


def font(root,key,size):return ImageFont.truetype(str(root/'static'/f'SinglelineJPLab-{key}.ttf'),size)


def image_surface(w,h,title,subtitle):
    im=Image.new('RGB',(w,h),'#f6f3e9');d=ImageDraw.Draw(im)
    d.text((42,24),title,font=label(30),fill='#173b40')
    d.text((44,70),subtitle,font=label(16),fill='#665e54')
    return im,d


def render(root,glyphs):
    root=Path(root);folder=root/'specimen';folder.mkdir(exist_ok=True)
    keys=[key for key in STYLES if (root/'static'/f'SinglelineJPLab-{key}.ttf').is_file()]
    im,d=image_surface(1600,120+len(keys)*148,'Singleline JP Lab | eight original geometric treatments',
        'EXPERIMENTAL / direct centerline outlines / Italian = upright reverse contrast / PC98 = original interpretation')
    for i,key in enumerate(keys):
        y=125+i*148
        d.text((44,y),STYLES[key].label,font=label(21),fill='#936048')
        d.line((44,y+116,1544,y+116),fill='#ddd6c7',width=1)
        d.text((44,y+25),'日本語 永鬱 明朝 Agfg 0123',font=font(root,key,64),fill='#142c36')
        d.text((1090,y+43),'∑ ∫ √ ∞ α β γ',font=font(root,key,43),fill='#142c36')
    im.save(folder/'style-overview.png')
    # Close forms, dense characters, compatibility and supplementary scalars.
    samples=list('未末土士己已巳斉斎齊齋鬱龜鷗纏鱗髙𠮷神﨑')
    im,d=image_surface(1600,1450,'Kanji proof sheet | identity is not quality assurance',
        'Original and mechanically composed drafts. Labels show raw code points; no NFC/NFKC folding. Inspect at native pixel size.')
    for i,c in enumerate(samples):
        x=38+(i%10)*156;y=125+(i//10)*315
        present=c in glyphs
        d.text((x,y),f'U+{ord(c):04X}',font=label(17),fill='#665e54')
        if present:
            d.text((x,y+23),c,font=font(root,'singleline',105),fill='#102d34')
            d.text((x,y+150),c,font=font(root,'gothic',48),fill='#102d34')
            for j,size in enumerate((18,24,32)):
                d.text((x+j*47,y+224),c,font=font(root,'singleline',size),fill='#102d34')
                d.text((x+j*47,y+263),str(size),font=label(12),fill='#777063')
            d.text((x,y+290),'legacy' if glyphs[c].status=='legacy-existing' else 'draft',font=label(12),fill='#9c503f')
        else:d.text((x,y+95),'MISSING',font=label(19),fill='#a33228')
    d.text((42,810),'Additional composed Kanji: 72 px / 36 px / 24 px',font=label(22),fill='#936048')
    additional=[c for c,g in glyphs.items() if len(c)==1 and g.category=='kanji' and g.status in ('composition-draft','component-draft')]
    # Deterministic spread through Unicode order, not just the easiest glyphs.
    spread=additional[::max(1,len(additional)//36)][:36]
    for i,c in enumerate(spread):
        x=38+(i%12)*130;y=865+(i//12)*176
        d.text((x,y),f'{ord(c):04X}',font=label(12),fill='#777063')
        d.text((x,y+17),c,font=font(root,'singleline',72),fill='#102d34')
        d.text((x,y+99),c,font=font(root,'gothic',36),fill='#102d34')
        d.text((x+67,y+113),c,font=font(root,'singleline',24),fill='#102d34')
    im.save(folder/'kanji-proof.png')
    # Original carrier-independent pictograms, not DoCoMo artwork or mapping.
    from .original_pictograms import PUA_GLYPHS,PICTOGRAM_NAMES
    im,d=image_surface(1440,1200,'Original retro-mobile pictograms | 64 designs',
        'New PUA mapping U+E000 onward, with explicit Unicode aliases. No carrier artwork or carrier-map compatibility.')
    for i,c in enumerate(sorted(PUA_GLYPHS)):
        x=40+(i%8)*175;y=125+(i//8)*132
        d.text((x,y),c,font=font(root,'singleline',72),fill='#173b40')
        name=str(PICTOGRAM_NAMES.get(c,f'U+{ord(c):04X}'))
        d.text((x,y+84),name[:23],font=label(12),fill='#665e54')
        d.text((x,y+102),f'U+{ord(c):04X}',font=label(11),fill='#997856')
    im.save(folder/'pictograms.png')
    for key in ('gothic','serif'):
        path=root/'variable'/f'SinglelineJPLab-{key}-VF.ttf'
        if not path.exists():continue
        im,d=image_surface(1600,1100,f'{STYLES[key].label} variable | real outline variation',
            'Weight 200 / 400 / 700; upright and -12 degree slant. Slanted instances are Oblique, separate from authored Italic.')
        for i,(weight,slant) in enumerate((w,s) for s in (0,-12) for w in (200,400,700)):
            y=120+i*155
            d.text((44,y),f'wght {weight}   slnt {slant}',font=label(19),fill='#936048')
            f=ImageFont.truetype(str(path),72);f.set_variation_by_axes([weight,slant])
            d.text((44,y+25),'日本語 永鬱 ABC ag 123  ∑√∞',font=f,fill='#142c36')
        im.save(folder/f'variable-{key}.png')
    write_html(root,glyphs,keys)


def write_html(root,glyphs,keys):
    coverage=json.loads((root/'coverage.json').read_text())
    faces='\n'.join(f'@font-face{{font-family:"{key}";src:url("../static/SinglelineJPLab-{key}.ttf")}}' for key in keys)
    faces+='\n@font-face{font-family:variable;src:url("../variable/SinglelineJPLab-gothic-VF.ttf");font-weight:200 700;font-style:oblique 0deg 12deg}'
    rows=''.join(f'<section><h2>{html.escape(STYLES[k].label)}</h2><p class="proof" style="font-family:{k}">日本語 永鬱 明朝 Agfg 0123 ∑√∞ αβγ</p></section>' for k in keys)
    inventory=[{'c':c,'u':' '.join(f'U+{ord(x):04X}' for x in c),'status':g.status,'category':g.category,
                'flags':' '.join(g.notes.get('flags',[]))} for c,g in glyphs.items()]
    data=json.dumps(inventory,ensure_ascii=False).replace('</','<\\/')
    groups=''.join(f'<li>{html.escape(k)}: {v["present"]:,} / {v["target"]:,}, missing {v["missing_count"]}</li>' for k,v in coverage['groups'].items())
    groups+=''.join(f'<li>Unfinished quality check: {html.escape(k)} — {v["count"]:,} glyphs</li>' for k,v in coverage.get('quality_flags',{}).items())
    missing=''.join(sorted({c for v in coverage['groups'].values() for c in v['missing'] if len(c)==1}))
    content='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Singleline JP Lab specimen</title>
<style>'''+faces+'''body{margin:0;background:#f6f3e9;color:#19353b;font:16px system-ui}main{max-width:1280px;margin:auto;padding:36px}h1{font-size:40px}h2{font-size:18px;color:#8e5b42}section{border-top:1px solid #d9d0bf;padding:12px 0}.proof{font-size:54px;line-height:1.7;overflow-wrap:anywhere}.note{padding:18px;border-left:5px solid #a56239;background:#eee7d8}input,select,textarea{font:inherit;padding:10px;background:#fffdf7;border:1px solid #b9b4a5}textarea{width:95%;min-height:110px;font-family:variable;font-size:44px}#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(135px,1fr));gap:10px}.card{padding:12px;background:white;min-height:132px}.card span{display:block;font:52px gothic;min-height:66px}.card small{display:block;font-size:11px;overflow-wrap:anywhere}a{color:#905631}.missing{font-family:system-ui;overflow-wrap:anywhere;line-height:1.8}label{display:inline-block;margin:8px}button{padding:10px}</style>
<main><h1>Singleline JP Lab</h1><p>Original geometric centerlines · 8 static styles · 2 variable families · 1-bit binary fonts</p>
<p class="note"><strong>Experimental, not release-certified.</strong> Expanded Kanji are mechanical composition drafts and have not all been individually proofread. Encoding coverage does not certify correct Japanese forms or small-size legibility. Missing characters remain missing. Italian means upright reverse contrast. PC98 is an original stylistic interpretation, not copied ROM artwork.</p>
<ul>'''+groups+'''</ul><p><a href="../coverage.json">Exact coverage report</a> · <a href="../../../docs/FAMILY.md">Build and format notes</a> · <a href="../centerlines.svgz" download>Complete centerline SVGZ (gzip)</a> · <a href="../../../docs/FAMILY.md#editable-centerline-svg">SVG extraction instructions</a></p>'''+rows+'''
<section><h2>Variable Gothic: try both axes</h2><label>Weight <input id="weight" type="range" min="200" max="700" value="400"></label><label>Slant <input id="slant" type="range" min="-12" max="0" value="0"></label><textarea id="live">日本語 永鬱 ABC ag 123 ∑√∞</textarea></section>
<section><h2>Glyph inventory, including explicit sequence identities</h2><input id="query" placeholder="Character, U+ code point, category, status"><select id="style">'''+''.join(f'<option value="{k}">{STYLES[k].label}</option>' for k in keys)+'''</select><p id="count"></p><div id="grid"></div><button id="more">Show 160 more</button></section>
<section><h2>Missing requested characters</h2><p class="missing">'''+html.escape(missing)+'''</p><p>These are deliberately not mapped to substitute or repeated shapes. Consult coverage.json for separate Kanji/non-Kanji requirements.</p></section>
<section><h2>Original retro pictograms</h2><img src="pictograms.png" style="max-width:100%" alt="64 original retro-mobile pictograms"></section>
<p>Code/coordinates retain AGPL v3. CJKVI-IDS structure and derived Japanese assets retain GPL v2 notices. Unicode data license is bundled. See NOTICE.md before redistribution.</p>
</main><script>const inventory='''+data+''';let limit=160;const q=document.getElementById('query'),grid=document.getElementById('grid'),style=document.getElementById('style');function draw(){const s=q.value.toLowerCase();const found=inventory.filter(g=>[g.c,g.u,g.status,g.category,g.flags].some(x=>x.toLowerCase().includes(s)));grid.replaceChildren();found.slice(0,limit).forEach(g=>{const card=document.createElement('div');card.className='card';const face=document.createElement('span');face.style.fontFamily=style.value;face.textContent=g.c;card.append(face);[g.u,g.category,g.status,g.flags].filter(Boolean).forEach(t=>{const l=document.createElement('small');l.textContent=t;card.append(l)});grid.append(card)});document.getElementById('count').textContent=found.length+' matches; '+Math.min(limit,found.length)+' displayed';}q.oninput=()=>{limit=160;draw()};style.onchange=draw;document.getElementById('more').onclick=()=>{limit+=160;draw()};function vary(){document.getElementById('live').style.fontVariationSettings='"wght" '+document.getElementById('weight').value+', "slnt" '+document.getElementById('slant').value;}document.getElementById('weight').oninput=vary;document.getElementById('slant').oninput=vary;draw();vary();</script></html>'''
    (root/'specimen/index.html').write_text(content)


if __name__=='__main__':
    from .data_loader import load_glyphs
    import argparse
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path,nargs='?',default=Path('build/family'))
    args=p.parse_args();render(args.directory,load_glyphs()[0])
