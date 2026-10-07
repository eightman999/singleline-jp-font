"""Assemble original geometry, explicit derivations and sequence glyphs."""
import unicodedata as ud
from glyphs import kanji,hiragana,katakana,ascii,symbols
from custom_japanese_strokes import FULLWIDTH_ALIASES
from custom_symbol_strokes import FILLED as LEGACY_FILLED
from .model import Glyph
from .repertoire import targets,standards


MARKS={
 '\u0300':[[(14,0),(9,3)]], '\u0301':[[(9,3),(14,0)]],
 '\u0302':[[(7,3),(12,0),(17,3)]], '\u0303':[[(6,2),(9,0),(14,3),(18,1)]],
 '\u0304':[[(7,1),(17,1)]], '\u0306':[[(7,0),(9,3),(15,3),(17,0)]],
 '\u0307':[[(12,0),(12,1)]], '\u0308':[[(8,0),(8,1)],[(16,0),(16,1)]],
 '\u030A':[[(10,0),(14,0),(15,1),(14,3),(10,3),(9,1),(10,0)]],
 '\u030B':[[(7,3),(11,0)],[(13,3),(17,0)]],
 '\u030C':[[(7,0),(12,3),(17,0)]],
 '\u0327':[[(12,22),(10,24),(14,25),(16,23)]],
 '\u0328':[[(16,21),(12,24),(14,25),(17,24)]],
 '\u0323':[[(12,24),(12,25)]],
 '\u0338':[[(5,22),(19,3)]],
 '\u3099':[[(19,1),(21,4)],[(22,0),(24,3)]],
 '\u309A':[[(20,1),(23,1),(24,3),(22,5),(20,4),(20,1)]],
}


def transform(paths,sx=1,sy=1,dx=0,dy=0):
    return [[(x*sx+dx,y*sy+dy) for x,y in p] for p in paths]


def composed(base,marks):
    if any(m not in MARKS for m in marks):return None
    # Kana voicing marks reserve their own upper-right corner, while Latin
    # accents shrink the base cap area. Below marks do not shift the base.
    above=any(ud.combining(m) in (230,232,233,234) for m in marks)
    paths=transform(base.paths,sy=.84,dy=3.4) if above else list(base.paths)
    for m in marks:paths+=MARKS[m]
    return paths


def load_glyphs(*,expand_kanji=True):
    glyphs={}
    for module,category in ((kanji,'kanji'),(hiragana,'kana'),(katakana,'kana'),(symbols,'symbol'),(ascii,'latin')):
        for c,paths in module.GLYPHS.items():
            narrow=category=='latin'
            glyphs[c]=Glyph(c,paths,advance=680 if narrow else 1000,width_factor=.66 if narrow else 1,
                filled=c in LEGACY_FILLED,source=f'legacy:{module.__name__}',status='legacy-existing',category=category)
    for c,base in FULLWIDTH_ALIASES.items():
        glyphs[c]=Glyph(c,ascii.GLYPHS[base],source=f'legacy:fullwidth:{base}',status='legacy-existing',category='latin')
    provenance={}
    if expand_kanji:
        from .kanji import build_kanji
        expanded,provenance=build_kanji(targets()|set('髙𠮷'))
        for c,paths in expanded.items():
            if c not in glyphs:
                info=provenance.get(c,{})
                status='component-draft' if info.get('status')=='component_draft' else 'composition-draft'
                glyphs[c]=Glyph(c,paths,source='project-component-composition',status=status,category='kanji',notes=info)
    try:
        from . import symbols as extended
        for c,paths in extended.GLYPHS.items():
            if c not in glyphs:
                category='alphabet' if ud.category(c).startswith('L') else 'math-symbol'
                glyphs[c]=Glyph(c,paths,advance=720 if category=='alphabet' else 1000,
                    width_factor=.72 if category=='alphabet' else 1,
                    filled=c in getattr(extended,'FILLED',set()),source='original:family.symbols',category=category)
    except ImportError:
        pass
    try:
        from . import jis_symbols as jis_extra
        MARKS.update(jis_extra.MARKS)
        for c,paths in jis_extra.GLYPHS.items():
            if c not in glyphs:
                category=jis_extra.CATEGORIES.get(c,'symbol')
                glyphs[c]=Glyph(c,paths,advance=jis_extra.ADVANCES.get(c,1000),
                    width_factor=jis_extra.WIDTH_FACTORS.get(c,1),filled=c in jis_extra.FILLED,
                    source='original:family.jis_symbols',category=category,
                    notes={'derivation':jis_extra.DERIVATIONS.get(c),
                           'negative':c in getattr(jis_extra,'NEGATIVE',set())})
    except ImportError:
        pass
    try:
        from . import original_pictograms as pict
        for c,paths in pict.GLYPHS.items():
            if c not in glyphs:
                glyphs[c]=Glyph(c,paths,filled=c in getattr(pict,'FILLED',set()),source='original:retro-pictogram',category='pictogram')
    except ImportError:
        pass
    # Explicit zero-width marks are real marks, not stand-ins for missing glyphs.
    for c,paths in MARKS.items():
        glyphs.setdefault(c,Glyph(c,paths,advance=0,source='original:combining-mark',category='mark'))
    # Latin, Greek and Cyrillic canonical diacritic derivatives.
    for cp in [*range(0xA0,0x250),*range(0x370,0x530),*range(0x1E00,0x2000)]:
        c=chr(cp)
        if c in glyphs:continue
        seq=ud.normalize('NFD',c)
        if len(seq)>1 and seq[0] in glyphs:
            paths=composed(glyphs[seq[0]],seq[1:])
            if paths:
                base=glyphs[seq[0]]
                glyphs[c]=Glyph(c,paths,advance=base.advance,width_factor=base.width_factor,
                    source=f'canonical-diacritic:{seq}',category='alphabet')
    # Standard width forms are explicit semantic aliases, unlike fake kanji.
    for cp in range(0xFF01,0xFFEF+1):
        c=chr(cp)
        seq=ud.normalize('NFKC',c)
        if c not in glyphs and len(seq)==1 and seq in glyphs:
            base=glyphs[seq];half=cp>=0xFF61
            glyphs[c]=Glyph(c,base.paths,advance=550 if half else 1000,width_factor=.50 if half else 1,
                filled=base.filled,source=f'width-variant:{seq}',category=base.category)
    for c in ('\u00a0','\u2002','\u2003','\u2009'):
        glyphs[c]=Glyph(c,[],advance={'\u00a0':680,'\u2002':500,'\u2003':1000,'\u2009':200}[c],category='space',source='Unicode-space-metrics')
    # Unicode superscript/subscript characters plus shapeable OpenType forms.
    explicit={'\u00b2':'2','\u00b3':'3','\u00b9':'1','\u2070':'0','\u2071':'i','\u207f':'n'}
    explicit.update({chr(0x2074+i):str(4+i) for i in range(6)})
    explicit.update(dict(zip('⁺⁻⁼⁽⁾₊₋₌₍₎','+-=()+-=()')))
    explicit.update({chr(0x2080+i):str(i) for i in range(10)})
    explicit.update(dict(zip('ₐₑₒₓₕₖₗₘₙₚₛₜ','aeoxhklmnpst')))
    for c,b in explicit.items():
        if c in glyphs:continue
        base=glyphs[b];below=0x2080<=ord(c)<=0x209f
        # y-up scaling/rise is converted back to the 24-unit source grid.
        paths=transform(base.paths,sx=.65,sy=.65,dy=10.36 if below else -3.93)
        glyphs[c]=Glyph(c,paths,advance=460,width_factor=.66,source=f'Unicode-{"sub" if below else "super"}script:{b}',category='alphabet')
    jis,_=standards()
    # Keep all 25 JIS multiscalar character identities intact.
    sequences={e['text'] for e in jis['entries'] if len(e['text'])>1}
    # NFC-equivalent decompositions also get ccmp substitutions when available.
    sequences.update(ud.normalize('NFD',c) for c in list(glyphs) if len(c)==1 and len(ud.normalize('NFD',c))>1)
    for seq in sorted(sequences):
        if seq in glyphs:continue
        if seq[0] not in glyphs:continue
        paths=composed(glyphs[seq[0]],seq[1:])
        if paths is not None:
            base=glyphs[seq[0]]
            glyphs[seq]=Glyph(seq,paths,advance=base.advance,width_factor=base.width_factor,
                source=f'sequence-composition:{seq}',category=base.category)
    return dict(sorted(glyphs.items())),provenance
