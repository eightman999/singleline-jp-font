"""Reproducible TrueType and real two-axis variable TrueType construction."""
import json,unicodedata
from pathlib import Path
from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from .geometry import make_glyph
from .model import Glyph,glyph_name
from .styles import variable_style

FIXED_TIME=3874089600 # Fixed timestamp; clock time must not change the binary.
DATA=Path(__file__).parent/'data'


def standard_variants(glyphs):
    result=[]
    for item in json.loads((DATA/'jis-compatibility-svs.json').read_text())['entries']:
        target=chr(int(item['compatibility_target'][2:],16))
        seq=''.join(chr(int(x[2:],16)) for x in item['sequence'])
        if target in glyphs:result.append((seq,target))
    return result


def feature_glyphs(glyphs):
    return [c for c,g in glyphs.items() if len(c)==1 and
            (c in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-=()' or
             0x391<=ord(c)<=0x3D6) and g.category!='mark']


def features(glyphs):
    header='\n'.join(f'languagesystem {s} dflt;' for s in ('DFLT','latn','grek','cyrl','kana','hani'))
    seqs=[c for c in glyphs if len(c)>1 and all(t in glyphs for t in c)]
    text=[header,'feature ccmp {']
    for seq in sorted(seqs,key=lambda c:(-len(c),c)):
        text.append('sub '+' '.join(glyph_name(c) for c in seq)+' by '+glyph_name(seq)+';')
    text.append('} ccmp;')
    for tag in ('subs','sups'):
        text.append(f'feature {tag} {{')
        for c in feature_glyphs(glyphs):text.append(f'sub {glyph_name(c)} by {glyph_name(c)}.{tag};')
        text.append('} '+tag+';')
    # Mark placement also supports arbitrary base+mark combinations not in the
    # explicit composition inventory. Kana marks remain ccmp-only.
    from .data_loader import MARKS
    above=[c for c in MARKS if unicodedata.combining(c) in (230,232,233,234) and c in glyphs]
    below=[c for c in MARKS if unicodedata.combining(c) in (202,216,220,222,224,226) and c in glyphs]
    overlay=[c for c in MARKS if unicodedata.combining(c)==1 and c in glyphs]
    for c in above:text.append(f'markClass {glyph_name(c)} <anchor 500 880> @TOP;')
    for c in below:text.append(f'markClass {glyph_name(c)} <anchor 500 40> @BOTTOM;')
    for c in overlay:text.append(f'markClass {glyph_name(c)} <anchor 500 460> @OVERLAY;')
    if above or below or overlay:
        text.append('feature mark {')
        for c,g in glyphs.items():
            if len(c)!=1 or g.category not in ('latin','alphabet'):continue
            if above:text.append(f'pos base {glyph_name(c)} <anchor {round(g.advance/2)} 960> mark @TOP;')
            if below:text.append(f'pos base {glyph_name(c)} <anchor {round(g.advance/2)} -30> mark @BOTTOM;')
            if overlay:text.append(f'pos base {glyph_name(c)} <anchor {round(g.advance/2)} 460> mark @OVERLAY;')
        text.append('} mark;')
    return '\n'.join(text)


def _notdef():
    return Glyph('',[[(3,3),(21,3),(21,21),(3,21),(3,3)],[(3,3),(21,21)],[(21,3),(3,21)]],source='missing-glyph-indicator')


def build_font(glyphs,style,path,*,variable=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    names={text:glyph_name(text) for text in glyphs}
    entries=[('.notdef',_notdef(),None)]
    entries.extend((names[c],g,None) for c,g in glyphs.items())
    entries.extend((names[c]+'.'+tag,glyphs[c],tag) for tag in ('subs','sups') for c in feature_glyphs(glyphs))
    outlines={};metrics={}
    for name,g,feature in entries:
        outlines[name],metrics[name]=make_glyph(g,style,feature=feature)
    family='Singleline JP Lab '+style.label
    if variable:family+=' Variable'
    postscript='SinglelineJPLab-'+style.key.replace('-','').title()+('-VF' if variable else '-Regular')
    fb=FontBuilder(1000,isTTF=True)
    fb.setupGlyphOrder([name for name,_,_ in entries])
    fb.setupCharacterMap({ord(c):name for c,name in names.items() if len(c)==1})
    fb.setupGlyf(outlines);fb.setupHorizontalMetrics(metrics)
    y_values=[y for outline in outlines.values() if outline.numberOfContours for x,y in outline.coordinates]
    ascent=max(1000,max(y_values,default=0)+10)
    descent=min(-200,min(y_values,default=0)-10)
    fb.setupHorizontalHeader(ascent=ascent,descent=descent,lineGap=0)
    fb.setupNameTable({'familyName':family,'styleName':'Regular' if not style.italic else 'Italic',
        'uniqueFontIdentifier':postscript+'-0.201','fullName':family,
        'psName':postscript,'version':'Version 0.201; EXPERIMENTAL composition drafts',
        'manufacturer':'singleline-jp-font project','designer':'Project-original geometric centerline family',
        'description':'Experimental family. Additional Kanji are structure-composition drafts, not individually proofread. Italian = reverse contrast; PC98 is an original stylistic interpretation, not ROM data.',
        'licenseDescription':'Original code and coordinates retain AGPL v3. CJKVI-IDS structure and derived Japanese assets retain GPL v2 notices. See bundled NOTICE.md and source.',
        'licenseInfoURL':'https://github.com/eightman999/singleline-jp-font/blob/main/NOTICE.md'})
    fb.setupOS2(version=4,sTypoAscender=ascent,sTypoDescender=descent,sTypoLineGap=0,usWinAscent=max(1100,ascent),
        usWinDescent=max(250,-descent),usWeightClass=style.weight,fsType=0,
        fsSelection=(1 if style.italic else 64)|128, sxHeight=460,sCapHeight=770,
        ySubscriptXSize=650,ySubscriptYSize=650,ySubscriptYOffset=160,
        ySuperscriptXSize=650,ySuperscriptYSize=650,ySuperscriptYOffset=340)
    fb.setupPost(italicAngle=style.slant);fb.setupMaxp()
    fb.font['head'].macStyle=2 if style.italic else 0
    addOpenTypeFeaturesFromString(fb.font,features(glyphs))
    variants=standard_variants(glyphs)
    if variants:
        table=CmapSubtable.newSubtable(14);table.platformID=0;table.platEncID=5
        table.language=0;table.cmap={};table.uvsDict={}
        for seq,target in variants:
            table.uvsDict.setdefault(ord(seq[1]),[]).append((ord(seq[0]),names[target]))
        fb.font['cmap'].tables.append(table)
    if variable:
        fb.setupFvar([('wght',200,400,700,'Weight'),('slnt',-12,0,0,'Slant')],
            [{'location':{'wght':w,'slnt':s},'stylename':name} for name,w,s in
             [('Light',200,0),('Regular',400,0),('Bold',700,0),('Light Oblique',200,-12),('Oblique',400,-12),('Bold Oblique',700,-12)]])
        buildStatTable(fb.font,[{'tag':'wght','name':'Weight','ordering':0,'values':[
            {'value':200,'name':'Light'},{'value':400,'name':'Regular','flags':2},{'value':700,'name':'Bold'}]},
            {'tag':'slnt','name':'Slant','ordering':1,'values':[{'value':0,'name':'Upright','flags':2},{'value':-12,'name':'Oblique'}]}])
        variations={}
        for name,g,feature in entries:
            base=outlines[name]
            if not base.numberOfContours:continue
            coords=list(base.coordinates)
            delta_map={}
            for weight,slant in ((200,0),(700,0),(400,-12),(200,-12),(700,-12)):
                master,_=make_glyph(g,variable_style(style,weight,slant),feature=feature)
                if list(master.endPtsOfContours)!=list(base.endPtsOfContours) or len(master.coordinates)!=len(coords):
                    raise ValueError(f'Incompatible variable topology: {name} {weight} {slant}')
                delta_map[weight,slant]=[(x-bx,y-by) for (x,y),(bx,by) in zip(master.coordinates,coords)]
            tuples=[]
            for (weight,slant),delta in delta_map.items():
                axes={}
                if weight!=400:axes['wght']=(-1,-1,0) if weight==200 else (0,1,1)
                if slant:axes['slnt']=(-1,-1,0)
                # Bilinear correction makes weight+slant corners match the
                # actual source master; it is not just independent fake axes.
                if weight!=400 and slant:
                    wd=delta_map[weight,0];sd=delta_map[400,-12]
                    delta=[(dx-wx-sx,dy-wy-sy) for (dx,dy),(wx,wy),(sx,sy) in zip(delta,wd,sd)]
                if any(dx or dy for dx,dy in delta):
                    tuples.append(TupleVariation(axes,delta+[(0,0)]*4))
            variations[name]=tuples
        fb.setupGvar(variations)
    fb.font['gasp']=newTable('gasp');fb.font['gasp'].gaspRange={65535:15}
    fb.font['head'].fontRevision=0.201
    fb.font['head'].created=fb.font['head'].modified=FIXED_TIME
    fb.font.recalcTimestamp=False
    fb.save(path)
    return {'path':str(path),'cmap':sum(len(c)==1 for c in glyphs),'glyphs':len(entries),
            'standardized_variants':len(variants),'variable':variable,'size_bytes':path.stat().st_size}
