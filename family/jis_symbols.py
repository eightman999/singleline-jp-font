"""Original non-Kanji centerlines for JIS X 0213:2004.

New paths and semantic transformations of this project's owned ASCII/kana/
Kanji paths only. No external font outlines, bitmaps, or traced designs enter
this module. Unicode names/decompositions identify characters, not geometry.
Coordinates are on the 24-unit y-down source grid; combining below marks can
reach y=25. Explicit shared shapes (turned/reversed IPA letters, enclosures,
width/compatibility forms) are documented in DERIVATIONS, not placeholders.

Consumers should merge MARKS into their composition table, use ADVANCES and
WIDTH_FACTORS, respect FILLED, and preserve multi-scalar GLYPHS keys. MARKS
are actual zero-width marks. A source grid alone does not provide GPOS.
"""
from copy import deepcopy
import json
from pathlib import Path
import unicodedata as ud

from glyphs.ascii import GLYPHS as ASCII
from glyphs.katakana import GLYPHS as KATAKANA
from glyphs.hiragana import GLYPHS as HIRAGANA
from glyphs.kanji import GLYPHS as KANJI
from glyphs.symbols import GLYPHS as LEGACY_SYMBOLS
from .symbols import GLYPHS as SYMBOLS
from .symbols import stroke, transform, ring, dot, mirror
UNIT_KANA = {**KATAKANA, 'ー': LEGACY_SYMBOLS['ー']}

GLYPHS = {}
FILLED = set()
CATEGORIES = {}
ADVANCES = {}
WIDTH_FACTORS = {}
DERIVATIONS = {}
MARKS = {}
NEGATIVE = set()
SOURCE = {
    'kind': 'original geometric centerlines and explicit owned-glyph derivations',
    'external_glyph_inputs': [],
    'license': 'AGPL-3.0-only; see repository LICENSE and NOTICE.md',
}


def add(char, paths, category='symbol', *, filled=False, derivation=None):
    if char in GLYPHS:
        raise ValueError('duplicate JIS symbol: ' + repr(char))
    GLYPHS[char] = deepcopy(paths)
    CATEGORIES[char] = category
    if filled:
        FILLED.add(char)
    if category == 'alphabet':
        ADVANCES[char] = 720
        WIDTH_FACTORS[char] = .72
    elif category == 'mark':
        ADVANCES[char] = 0
        MARKS[char] = deepcopy(paths)
    if derivation:
        DERIVATIONS[char] = derivation


def turn(paths):
    """Turn an x-height glyph 180 degrees about (12,14.5)."""
    return transform(paths, sx=-1, sy=-1, dx=24, dy=29)


def rect(x0, y0, x1, y1):
    return stroke((x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0))


def polygon(*points):
    return stroke(*points, points[0])


# IPA consonants and vowels. The open-O, turned-V, schwa and rhotic schwa
# are also the bases of eight JIS X 0213 multi-scalar accent sequences.
IPA = {
    'ɔ': mirror(ASCII['c']),
    'ə': turn(ASCII['e']),
    'ʌ': turn(ASCII['v']),
    'ɘ': mirror(ASCII['e']),
    'ɐ': turn(ASCII['a']),
    'ɯ': turn(ASCII['m']),
    'ʍ': turn(ASCII['w']),
    'ɹ': turn(ASCII['r']),
    'ɡ': deepcopy(ASCII['g']),
    'ɨ': deepcopy(ASCII['i']) + stroke((5,13),(20,13)),
    'ʉ': deepcopy(ASCII['u']) + stroke((1,14),(23,14)),
    'ɵ': deepcopy(ASCII['o']) + stroke((3,14),(21,14)),
    'ɱ': transform(ASCII['m'],sx=.86,sy=.85,dx=.5,dy=1) + stroke((19.42,19.7),(19.42,23),(17,24),(14,23)),
    'ʋ': stroke((2,8),(5,7),(7,10),(7,18),(10,22),(15,22),(19,18),(21,10),(20,7)),
    'ɾ': stroke((7,22),(7,9),(10,6),(15,6),(18,9),(17,12)),
    'ʃ': stroke((19,3),(17,1),(13,1),(10,4),(10,20),(7,24),(3,24)),
    'ʒ': stroke((4,7),(21,7),(12,14),(17,14),(21,17),(21,20),(17,24),(9,24),(5,22)),
    'ɬ': stroke((13,2),(13,19),(16,22),(20,22)) + stroke((5,12),(7,8),(16,8),(20,11),(17,15),(9,15),(5,12)),
    'ʈ': stroke((10,2),(10,20),(12,24),(16,24),(18,21)) + stroke((3,8),(21,8)),
    'ɖ': stroke((18,2),(18,21),(20,24),(23,24)) + stroke((18,11),(15,7),(8,7),(3,11),(3,18),(7,22),(13,22),(18,18)),
    'ɳ': stroke((3,22),(3,7)) + stroke((3,11),(7,7),(13,7),(17,11),(17,21),(19,24),(22,24)),
    'ɽ': stroke((6,7),(6,21),(8,24),(12,24)) + stroke((6,12),(11,7),(17,7),(21,10)),
    'ʂ': stroke((21,9),(17,7),(9,7),(4,10),(5,13),(18,16),(20,19),(17,22),(9,22),(5,20),(5,23),(8,24),(11,23)),
    'ʐ': stroke((4,7),(20,7),(4,22),(20,22),(20,24),(23,24)),
    'ɻ': turn(ASCII['r']) + stroke((20,22),(20,24),(23,24)),
    'ɭ': stroke((9,2),(9,21),(11,24),(16,24),(18,22)),
    'ɟ': stroke((9,3),(15,3),(15,20),(12,24),(5,24)) + stroke((5,10),(22,10)),
    'ɲ': stroke((7,7),(7,21),(4,24),(1,23)) + stroke((7,11),(11,7),(17,7),(21,11),(21,22)),
    'ʝ': deepcopy(ASCII['j']) + stroke((7,19),(19,23)),
    'ʎ': stroke((3,22),(12,9),(17,7),(21,7)) + stroke((12,9),(21,22)),
    'ɰ': turn(ASCII['m']) + stroke((22,22),(22,24)),
    'ʁ': turn(transform(ASCII['R'],sy=.75,dy=5.5)),
    'ʔ': stroke((4,6),(7,2),(15,2),(20,6),(20,9),(12,14),(12,22)),
    'ɦ': stroke((4,22),(4,5),(7,2),(11,2),(13,4)) + stroke((4,12),(9,8),(16,8),(20,12),(20,22)),
    'ʘ': ring(cx=12,cy=14,rx=9,ry=8) + dot(12,14),
    'ǂ': stroke((12,2),(12,22)) + stroke((3,9),(21,9)) + stroke((3,15),(21,15)),
    'ɓ': stroke((4,21),(4,4),(7,1),(11,1),(13,3)) + stroke((4,11),(9,7),(16,7),(21,11),(21,18),(17,22),(10,22),(4,18)),
    'ɗ': stroke((18,22),(18,4),(21,1),(24,2)) + stroke((18,11),(14,7),(7,7),(2,11),(2,18),(6,22),(13,22),(18,18)),
    'ʄ': stroke((6,5),(8,2),(12,2),(15,5),(15,20),(12,24),(5,24)) + stroke((5,11),(22,11)),
    'ɠ': deepcopy(ASCII['g']) + stroke((21,7),(21,3),(23,1),(24,2)),
    'Ɠ': transform(ASCII['G'],sx=.84,dx=1) + stroke((18.64,6),(18.64,2),(21,1),(23,3)),
    'ɜ': stroke((4,9),(8,7),(16,7),(21,10),(18,14),(11,14),(18,14),(21,18),(17,22),(8,22),(4,20)),
    'ɞ': stroke((8,7),(16,7),(21,11),(21,18),(16,22),(8,22),(3,18),(6,14),(12,14),(6,14),(3,11),(8,7)),
    'ʊ': stroke((3,7),(7,7),(5,17),(8,22),(16,22),(19,17),(17,7),(21,7)),
    # Rams horn needs a crossed junction and a closed lower loop. This
    # project-authored centerline replaces the earlier two open lower legs;
    # Unicode/Noto were viewed for topology only, with no outline extraction.
    'ɤ': stroke((3,7),(6,8),(9,11),(12,15),(15,19),(15,21),(12,23),(9,21),(9,19),(12,15),(15,11),(18,8),(21,7)),
    'ɑ': deepcopy(ASCII['o']) + stroke((21,7),(21,22)),
    'ɕ': deepcopy(ASCII['c']) + stroke((21,19),(17,19),(17,22),(21,22),(22,19),(20,16)),
    'ʑ': stroke((4,7),(21,7),(4,22),(17,22),(20,20),(20,17),(17,16),(15,18),(17,20),(22,20)),
    'ɺ': turn(ASCII['r']) + stroke((20,7),(20,2)),
    'ɧ': stroke((4,22),(4,5),(7,2),(11,2),(13,4)) + stroke((4,12),(9,8),(16,8),(20,12),(20,21),(17,24),(13,24)),
}
IPA['ʕ'] = mirror(IPA['ʔ'])
IPA['ʡ'] = IPA['ʔ'] + stroke((5,16),(19,16))
IPA['ʢ'] = mirror(IPA['ʡ'])
IPA['ɒ'] = turn(IPA['ɑ'])
IPA['ɥ'] = transform(ASCII['h'],sx=-1,sy=-1,dx=24,dy=26)
IPA['ɚ'] = transform(IPA['ə'],sx=.79,dx=.5) + stroke((16,15),(20,12),(23,13),(23,17),(20,19))
IPA['ɮ'] = stroke((5,2),(5,22)) + transform(IPA['ʒ'],sx=.65,dx=8)
for char, paths in IPA.items():
    add(char, paths, 'alphabet', derivation=('semantic rotated/reversed or modified owned Latin form' if char in 'ɔəʌɘɐɯʍɹɡɨʉɵɒɥ' else None))

# Spacing phonetic modifiers and contiguous contour-tone glyphs. A rising
# contour joins low on the left to high at the right-hand vertical stem.
for char, y in zip('˥˦˧˨˩',(3,7.5,12,16.5,21)):
    add(char,stroke((18,3),(18,21))+stroke((6,y),(18,y)),'alphabet')
add('˩˥',stroke((5,21),(18,3),(18,21)),'alphabet')
add('˥˩',stroke((5,3),(18,21),(18,3)),'alphabet')
for char, paths in {
    'ˈ':stroke((12,2),(12,8)), 'ˌ':stroke((12,18),(12,24)),
    'ː':polygon((9,6),(15,6),(12,10))+polygon((9,20),(15,20),(12,16)),
    'ˑ':polygon((9,6),(15,6),(12,10)),
    '˞':stroke((5,13),(10,10),(16,11),(18,15),(16,19),(12,20)),
    '‿':stroke((2,20),(6,23),(18,23),(22,20)),
}.items():
    add(char,paths,'alphabet',filled=char in 'ːˑ')

# Small explicit combining marks. Below marks use y=22..25. Double inverted
# breve is the one-cell mark skeleton; its GPOS span should cover two bases.
for char, paths in {
    '\u030f':stroke((6,0),(10,3))+stroke((13,0),(17,3)),
    '\u0361':stroke((1,3),(4,0),(20,0),(23,3)),
    '\u0325':ring(cx=12,cy=23.5,rx=1.5,ry=1.5),
    '\u032c':stroke((8,22),(12,25),(16,22)),
    '\u0339':stroke((10,22),(14,22),(16,23.5),(14,25),(10,25)),
    '\u031c':stroke((14,22),(10,22),(8,23.5),(10,25),(14,25)),
    '\u031f':stroke((8,23.5),(16,23.5))+stroke((12,22),(12,25)),
    '\u0320':stroke((8,23.5),(16,23.5)),
    '\u033d':stroke((9,0),(15,3))+stroke((15,0),(9,3)),
    '\u0329':stroke((12,22),(12,25)),
    '\u032f':stroke((8,25),(10,22),(14,22),(16,25)),
    '\u0324':dot(8,24)+dot(16,24),
    '\u0330':stroke((6,24),(9,22),(15,25),(18,23)),
    '\u033c':stroke((6,22),(8,25),(12,23),(16,25),(18,22)),
    '\u0334':stroke((3,14),(7,11),(10,11),(15,14),(18,14),(21,11)),
    '\u031d':stroke((8,25),(16,25))+stroke((12,22),(12,25)),
    '\u031e':stroke((8,22),(16,22))+stroke((12,22),(12,25)),
    '\u0318':stroke((16,22),(16,25))+stroke((8,23.5),(16,23.5)),
    '\u0319':stroke((8,22),(8,25))+stroke((8,23.5),(16,23.5)),
    '\u032a':stroke((8,25),(8,22),(16,22),(16,25)),
    '\u033a':stroke((8,22),(8,25),(16,25),(16,22)),
    '\u033b':rect(9,22,15,25),
    '\u031a':stroke((8,0),(16,0),(16,3)),
}.items():
    add(char,paths,'mark')

# Common spacing accents. These are spacing variants, not combining aliases.
for char, paths in {
    '´':stroke((9,6),(15,2)), '¨':dot(8,3)+dot(16,3),
    '¯':stroke((5,3),(19,3)), '¸':stroke((13,19),(10,22),(14,24),(17,22)),
    '˘':stroke((6,2),(9,5),(15,5),(18,2)),
    '˛':stroke((16,19),(11,22),(12,24),(17,23)),
    'ˇ':stroke((6,2),(12,6),(18,2)),
    '˝':stroke((5,6),(10,2))+stroke((13,6),(18,2)),
    # Spacing dots use a near-square stem footprint after the narrow alphabet
    # width transform; the former0.7-unit segments vanished at16px in reduced
    # styles. This is authored dot geometry, never a generic blank fallback.
    '˙':stroke((11.2,3),(12.8,3)), '·':stroke((11.2,12),(12.8,12)),
}.items():
    add(char,paths,'alphabet')


# Geometric symbols and typographical punctuation. Black figures are genuine
# filled polygons. Their white partners remain centerline outlines.
DIAMOND = polygon((12,2),(22,12),(12,22),(2,12))
RIGHT_TRI = polygon((4,3),(21,12),(4,21))
SPADE = polygon((12,2),(20,10),(21,14),(18,17),(14,16),(14,19),(18,22),(6,22),(10,19),(10,16),(6,17),(3,14),(4,10))
HEART = polygon((12,7),(8,3),(4,3),(1,7),(2,12),(12,22),(22,12),(23,7),(20,3),(16,3))
CLUB = polygon((10,19),(10,16),(6,18),(2,16),(1,12),(4,9),(8,9),(6,5),(8,2),(12,1),(16,2),(18,5),(16,9),(20,9),(23,12),(22,16),(18,18),(14,16),(14,19),(18,23),(6,23))
SHOGI = polygon((12,2),(19,5),(22,22),(2,22),(5,5))
for white, black, paths in [('◇','◆',DIAMOND),('▷','▶',RIGHT_TRI),
        ('◁','◀',mirror(RIGHT_TRI)),('♤','♠',SPADE),('♢','♦',DIAMOND),
        ('♧','♣',CLUB),('☖','☗',SHOGI)]:
    add(white,paths,derivation='shared geometry between white outline and black filled semantic partner')
    add(black,paths,filled=True,derivation='filled partner of '+white)
add('♥',HEART,filled=True)
add('◯',ring(rx=11))
add('◦',ring(rx=2))
add('•',ring(rx=2),filled=True)
add('▱',polygon((7,5),(22,5),(17,20),(2,20)))
add('⊿',polygon((3,3),(3,21),(21,21)))
add('‖',stroke((8,2),(8,22))+stroke((16,2),(16,22)))
add('¦',stroke((12,2),(12,9))+stroke((12,15),(12,22)),'alphabet')
# Soft hyphen is a visible discretionary-hyphen source, matching its ordinary
# hyphen semantics; shaping/layout controls whether it is displayed.
add('\u00ad',stroke((7,12),(17,12)),'alphabet',derivation='discretionary form of hyphen')
add('♂',ring(cx=9,cy=15,rx=7)+stroke((14,10),(22,2),(14,2))+stroke((22,2),(22,10)))
add('♀',ring(cx=12,cy=9,rx=7)+stroke((12,16),(12,24))+stroke((7,20),(17,20)))
add('〓',rect(3,5,21,10)+rect(3,15,21,20),filled=True)
# Unicode mathematical semantics: a bar over a wedge, and a double bar over
# a wedge, respectively (not a barred down-pointing vee).
add('⌅',stroke((3,21),(12,8),(21,21))+stroke((3,3),(21,3)))
add('⌆',stroke((3,22),(12,12),(21,22))+stroke((3,3),(21,3))+stroke((3,7),(21,7)))
add('⌒',stroke((2,16),(4,10),(9,7),(15,7),(20,10),(22,16)))
for char,paths in {
    '⦅':stroke((14,2),(8,5),(5,11),(5,15),(8,21),(14,24))+stroke((18,2),(12,5),(9,11),(9,15),(12,21),(18,24)),
    '〘':stroke((17,1),(8,5),(8,19),(17,23))+stroke((21,1),(12,5),(12,19),(21,23)),
    '〖':stroke((20,1),(13,1),(6,8),(6,16),(13,23),(20,23))+stroke((20,5),(15,5),(10,10),(10,14),(15,19),(20,19)),
}.items():
    add(char,paths)
for left,right in [('⦅','⦆'),('〘','〙'),('〖','〗')]:
    add(right,mirror(GLYPHS[left]),derivation='mirrored matching bracket '+left)
add('⧺',stroke((2,12),(22,12))+stroke((8,5),(8,19))+stroke((16,5),(16,19)))
add('⧻',stroke((1,12),(23,12))+stroke((5,5),(5,19))+stroke((12,5),(12,19))+stroke((19,5),(19,19)))
LESS = stroke((20,2),(4,6),(20,10))
GREATER = mirror(LESS)
for char,top,bottom in [('⋚',LESS,GREATER),('⋛',GREATER,LESS)]:
    add(char,transform(top,sy=.8)+stroke((4,11),(20,11))+stroke((4,14),(20,14))+transform(bottom,sy=.8,dy=16))
add('ℵ',stroke((4,2),(20,22))+stroke((15,3),(19,5),(14,11))+stroke((10,13),(5,19),(9,22)))
add('␣',stroke((3,16),(3,21),(21,21),(21,16)))
add('⏎',stroke((21,4),(21,13),(6,13))+polygon((6,8),(1,13),(6,18),(6,15),(19,15),(19,13),(6,13)))
WHITE_ARROW = polygon((2,9),(13,9),(13,3),(23,12),(13,21),(13,15),(2,15))
add('⇨',WHITE_ARROW)
add('⇦',mirror(WHITE_ARROW),derivation='mirrored white arrow')
add('⇧',[[(y,24-x) for x,y in p] for p in WHITE_ARROW],derivation='rotated white arrow')
add('⇩',[[(y,x) for x,y in p] for p in WHITE_ARROW],derivation='rotated white arrow')
add('⤴',stroke((2,20),(13,20),(18,17),(18,4))+stroke((12,10),(18,4),(24,10)))
add('⤵',stroke((2,4),(13,4),(18,7),(18,20))+stroke((12,14),(18,20),(24,14)))
add('〽',stroke((2,7),(7,2),(17,17),(22,12),(22,22)))
SESAME=polygon((15,3),(19,6),(18,11),(13,15),(8,16),(11,10))
add('﹆',SESAME)
add('﹅',SESAME,filled=True,derivation='filled sesame dot')
add('〝',stroke((5,3),(8,9))+stroke((13,3),(16,9)))
add('〟',stroke((8,17),(5,23))+stroke((16,17),(13,23)))
for char,text in [('‼','!!'),('⁇','??'),('⁈','?!'),('⁉','!?')]:
    paths=[]
    for i,c in enumerate(text):
        paths+=transform(ASCII[c],sx=.43,dx=i*12+.4)
    add(char,paths,derivation='paired punctuation '+text)
ASTERISK = transform(ASCII['*'],sx=.35,sy=.35)
add('⁑',transform(ASTERISK,dx=8,dy=1)+transform(ASTERISK,dx=8,dy=14))
add('⁂',transform(ASTERISK,dx=8,dy=0)+transform(ASTERISK,dx=1,dy=14)+transform(ASTERISK,dx=15,dy=14))

# Music symbols, drawn as independent geometric outlines and stems.
add('♯',stroke((8,2),(6,22))+stroke((18,2),(16,22))+stroke((2,10),(22,7))+stroke((2,17),(22,14)))
add('♭',stroke((7,1),(7,22),(18,15),(19,11),(16,9),(12,10),(7,15)))
add('♮',stroke((7,1),(7,18),(18,14))+stroke((18,23),(18,6),(7,10)))
add('♩',ring(cx=8,cy=19,rx=5,ry=3)+rect(12,2,13.5,19),filled=True)
add('♬',ring(cx=5,cy=20,rx=4,ry=2)+ring(cx=18,cy=17,rx=4,ry=2)+rect(8,5,9.5,20)+rect(21,2,22.5,17)+polygon((8,5),(22.5,2),(22.5,4),(8,7))+polygon((8,9),(22.5,6),(22.5,8),(8,11)),filled=True)

# Dentistry symbols have explicit compositional semantics in their Unicode
# names: directional stems plus a circle, triangle, or wave.
dent_stems = {
    'vertical':stroke((12,1),(12,23)),
    'down':stroke((2,9),(22,9))+stroke((12,9),(12,23)),
    'up':stroke((2,15),(22,15))+stroke((12,1),(12,15)),
}
add('⎾',stroke((12,23),(12,2),(23,2)))
add('⎿',stroke((12,1),(12,22),(23,22)))
add('⏋',stroke((12,23),(12,2),(1,2)))
add('⏌',stroke((12,1),(12,22),(1,22)))
for chars,shape in [('⏀⏁⏂',ring(cx=12,cy=12,rx=5)),
        ('⏃⏄⏅',polygon((12,5),(18,17),(6,17))),
        ('⏆⏇⏈',stroke((3,13),(7,10),(11,10),(15,14),(19,14),(22,11)))]:
    for char,direction in zip(chars,['vertical','down','up']):
        add(char,dent_stems[direction]+shape,derivation='dentistry '+direction+' stem and '+ud.name(char).split('WITH ')[-1].lower())
add('⏉',dent_stems['down'])
add('⏊',dent_stems['up'])

# Box strokes are explicit solid rectangles. Heavy and light arms remain
# visually different, including the ten mixed-weight JIS junctions. Filled
# polygons avoid varying contour topology between typographic masters.
# A consumer can special-case category box-drawing for edge-to-edge metrics.
BOXES = {
    '─':'LR','│':'UD','┌':'DR','┐':'DL','┘':'UL','└':'UR',
    '├':'UDR','┬':'DLR','┤':'UDL','┴':'ULR','┼':'UDLR',
    '━':'lr','┃':'ud','┏':'dr','┓':'dl','┛':'ul','┗':'ur',
    '┣':'udr','┳':'dlr','┫':'udl','┻':'ulr','╋':'udlr',
    '┠':'udR','┯':'Dlr','┨':'udL','┷':'Ulr','┿':'UDlr',
    '┝':'UDr','┰':'dLR','┥':'UDl','┸':'uLR','╂':'udLR',
}
for char,arms in BOXES.items():
    paths=[]
    vertical=[]
    horizontal=[]
    for arm in arms:
        t=1.35 if arm.isupper() else 3.0
        if arm.upper() in 'LR':horizontal.append(t)
        else:vertical.append(t)
        if arm.upper()=='L': paths+=rect(0,12-t/2,12,12+t/2)
        if arm.upper()=='R': paths+=rect(12,12-t/2,24,12+t/2)
        if arm.upper()=='U': paths+=rect(12-t/2,0,12+t/2,12)
        if arm.upper()=='D': paths+=rect(12-t/2,12,12+t/2,24)
    if vertical and horizontal:
        v,h=max(vertical),max(horizontal)
        paths+=rect(12-v/2,12-h/2,12+v/2,12+h/2)
    add(char,paths,'box-drawing',filled=True,derivation='explicit light/heavy directional arms '+arms)


def inline(text, alphabet, box=(2,2,20,20)):
    """Set genuine owned glyphs into a bounded horizontal ligature."""
    x,y,w,h=box
    result=[]
    n=len(text)
    for i,c in enumerate(text):
        if c not in alphabet:
            raise KeyError('missing owned component '+repr(c))
        result+=transform(alphabet[c],sx=w/(24*n),sy=h/24,dx=x+i*w/n,dy=y)
    return result


# Circled 21..50, plus double-circle 1..10. Two distinct enclosures are
# geometrically present for the double-circle series.
for value in range(21,51):
    char=chr(0x3251+value-21) if value<=35 else chr(0x32B1+value-36)
    add(char,ring(rx=11)+inline(str(value),ASCII,box=(4,5,16,14)),
        derivation='circled original digit sequence '+str(value))
for value in range(1,11):
    add(chr(0x24F5+value-1),ring(rx=11)+ring(rx=8.5)+inline(str(value),ASCII,box=(5,6,14,12)),
        derivation='double circled original digit sequence '+str(value))
for cp in range(0x32D0,0x32FF):
    c=chr(cp)
    base=ud.normalize('NFKC',c)
    if len(base)==1 and base in KATAKANA:
        add(c,ring(rx=11)+transform(KATAKANA[base],sx=.65,sy=.65,dx=4.2,dy=4.2),
            derivation='circled owned katakana '+base)
for c,base in zip('㊤㊥㊦㊧㊨','上中下左右'):
    add(c,ring(rx=11)+transform(KANJI[base],sx=.64,sy=.64,dx=4.32,dy=4.32),
        derivation='circled owned kanji '+base)
for c,base in zip('㈱㈲㈹','株有代'):
    add(c,transform(ASCII['('],sx=.3,dx=-.5)+transform(ASCII[')'],sx=.3,dx=17)+
        transform(KANJI[base],sx=.58,sy=.85,dx=5,dy=1.8),derivation='parenthesized owned kanji '+base)

# Explicit compatibility ligatures, preserving their Unicode identities.
for cp in [*range(0x2160,0x216C),*range(0x2170,0x217C)]:
    c=chr(cp);base=ud.normalize('NFKC',c)
    add(c,inline(base,ASCII),'alphabet',derivation='Roman numeral compatibility sequence '+base)
for c,base in [('ª','a'),('º','o')]:
    add(c,transform(ASCII[base],sx=.58,sy=.58,dx=5,dy=1)+stroke((6,17),(18,17)),
        'alphabet',derivation='ordinal letter '+base)
for c,base in [('㎜','mm'),('㎝','cm'),('㎞','km'),('㎎','mg'),('㎏','kg'),
        ('㏄','cc'),('㏋','HP'),('㏍','KK'),('℡','TEL')]:
    add(c,inline(base,ASCII,box=(1,3,22,18)),derivation='compatibility unit/abbreviation '+base)
add('㎡',transform(ASCII['m'],sx=.65,sy=.75,dx=.5,dy=5)+transform(ASCII['2'],sx=.35,sy=.4,dx=15,dy=0),derivation='square metre: m with superscript 2')
add('№',transform(ASCII['N'],sx=.55,dx=0)+transform(ASCII['o'],sx=.4,sy=.55,dx=14,dy=0)+stroke((15,16),(22,16)),derivation='numero: N and elevated underlined o')
for c in '㍻㍾㍽㍼':
    base=ud.normalize('NFKC',c)
    add(c,inline(base,KANJI,box=(0,1,24,22)),derivation='era-name ligature '+base)
for c in '㍉㌔㌢㍍㌘㌧㌃㌶㍑㍗㌍㌦㌣㌫㍊㌻':
    base=ud.normalize('NFKC',c)
    # Two rows keep four-to-six kana readable within the square. Two-kana
    # units use a single column; three-kana units have 2+1, with the last
    # character centered. This is this family's own square-unit arrangement.
    columns=(len(base)+1)//2
    rows=[base[:columns],base[columns:]]
    body=[]
    for row,text in enumerate(rows):
        width=22*len(text)/columns
        body+=inline(text,UNIT_KANA,box=(12-width/2,1+row*11,width,10))
    add(c,body,derivation='square-kana unit '+base)

# Remaining Japanese punctuation and compact rebus-like signs. The kana
# digraphs are explicit original ligatures using the corresponding two kana.
add('仝',stroke((1,9),(12,1),(23,9))+stroke((6,11),(18,11))+stroke((12,11),(12,21))+stroke((3,21),(21,21)),derivation='explicit person roof over work ideograph')
add('￣',stroke((2,3),(22,3)),derivation='fullwidth spacing macron')
add('Å',transform(ASCII['A'],sy=.8,dy=4.5)+ring(cx=12,cy=2,rx=2,ry=1.5),
    'alphabet',derivation='Angstrom canonical equivalent of A with ring')
add('〳',stroke((18,0),(5,16),(12,24)))
add('〴',stroke((15,0),(3,16),(10,24))+stroke((18,2),(20,6))+stroke((22,1),(24,5)))
add('〵',stroke((12,0),(19,8),(6,24)))
add('〻',stroke((15,2),(7,9),(16,13),(7,21)))
add('〼',rect(2,2,22,22)+stroke((22,2),(2,22)))
add('ヿ',transform(KATAKANA['コ'],sx=.75,sy=.58,dx=0,dy=0)+transform(KATAKANA['ト'],sx=.7,sy=.72,dx=7,dy=6),derivation='original interlocked コト ligature')
add('ゟ',transform(HIRAGANA['よ'],sx=.64,sy=.8,dx=0,dy=0)+transform(HIRAGANA['り'],sx=.6,sy=.8,dx=9.6,dy=4.8),derivation='original interlocked より ligature')
add('⌘',stroke((8,8),(5,8),(2,5),(2,3),(4,1),(6,1),(8,3),(8,21),(6,23),(4,23),(2,21),(2,19),(4,17),(20,17),(22,19),(22,21),(20,23),(18,23),(16,21),(16,3),(18,1),(20,1),(22,3),(22,5),(20,8),(8,8)))
add('☃',ring(cx=12,cy=7,rx=5,ry=5)+ring(cx=12,cy=17,rx=8,ry=6)+dot(10,6)+dot(14,6)+stroke((12,8),(16,9),(12,10))+dot(12,14)+dot(12,18)+stroke((5,14),(1,10))+stroke((19,14),(23,10)))
add('♨',stroke((5,15),(2,18),(3,21),(8,23),(16,23),(21,21),(22,18),(19,15))+stroke((7,16),(5,12),(7,8),(5,4))+stroke((12,16),(10,11),(13,6),(11,1))+stroke((17,16),(15,12),(18,8),(16,4)))
add('〠',ring(cx=12,cy=14,rx=9,ry=8)+stroke((3,7),(21,7))+stroke((6,7),(6,2),(18,2),(18,7))+stroke((9,4),(15,4))+dot(8,13)+dot(16,13)+stroke((6,17),(9,20),(15,20),(18,17)))
add('☞',stroke((1,12),(5,12),(8,8),(20,8),(23,10),(22,12),(13,12),(18,14),(18,17),(15,17),(17,19),(15,22),(8,22),(4,20),(1,20),(1,12))+stroke((6,12),(6,20))+stroke((12,15),(15,17))+stroke((11,19),(15,20)))


# Fixed project-authored paths preserve the full binary64 coordinates from the
# original build. libm sin/cos can differ by an ULP across macOS/Linux; applying
# rounding only to provenance would conceal source changes. Both rendering and
# provenance now consume the same exact data. See docs/REPRODUCIBILITY.md.
_CIRCLES = json.loads((Path(__file__).with_name('data') / 'jis-circle-paths.json').read_text(encoding='utf-8'))['glyphs']


def fixed_circle_paths(char):
    return [[tuple(point) for point in path] for path in _CIRCLES[char]]


for c in ('⦿','◉'):
    add(c,fixed_circle_paths(c),filled=True,
        derivation='solid annulus segments plus filled central disk')
for c in ('◐','◑','◒','◓'):
    add(c,fixed_circle_paths(c),filled=True,
        derivation='solid annulus and designated filled semicircle')
quarter=polygon((12,2),(16.1,6.1),(12,10.2),(7.9,6.1))
parts=[]
for angle in range(4):
    for path in quarter:
        rotated=[]
        for x,y in path:
            for _ in range(angle):x,y=24-y,x
            rotated.append((x,y))
        parts.append(rotated)
add('❖',parts,filled=True,derivation='four original solid diamond sectors leaving an actual white X')
phone=fixed_circle_paths('☎')
add('☎',phone,filled=True,derivation='filled handset and telephone body with open dial counter')

# Negative-number protocol: one CLOSED SOLID OUTER CONTOUR followed by
# CENTERLINE WHITE NUMERAL STROKES. These keys are intentionally NOT FILLED.
# A consumer must expand the numeral strokes into actual cutouts/counters;
# drawing every path in black or merely outlining the circle is incorrect.
# Overlapping white strokes should be unioned or rendered as a white mask.
for value,c in enumerate('❶❷❸❹❺❻❼❽❾❿⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴',1):
    body=inline(str(value),ASCII,box=((6 if value<10 else 4),4,(12 if value<10 else 16),16))
    add(c,ring(rx=11)+body,'negative-enclosure',derivation='black circled original number '+str(value)+' with real white numeral cutouts')
    NEGATIVE.add(c)
UNSUPPORTED_NEGATIVE_NUMBERS = set()
REPERTOIRE = tuple(sorted(GLYPHS,key=lambda c:tuple(map(ord,c))))
NAMES = {c:' + '.join(ud.name(s,f'U+{ord(s):04X}') for s in c) for c in GLYPHS}
