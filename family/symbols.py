"""Original geometric mathematical, Greek and extended-Latin centerlines.

Coordinates use the project's 24-unit, y-down em. This is a deliberately
enumerated repertoire, not a claim to cover an entire Unicode block. Paths are
newly authored here or transformed from the project's original ASCII paths;
no font, outline, bitmap, or external glyph design is used as an input.
The exported GLYPHS contains additions only, so legacy ASCII/symbols are not
silently replaced. All closed paths are outlines, unless listed in FILLED.
"""
from copy import deepcopy
import unicodedata
from glyphs.ascii import GLYPHS as ASCII
from glyphs.symbols import GLYPHS as LEGACY_SYMBOLS

SOURCE = {
    'kind': 'project-authored geometric centerlines',
    'file': 'family/symbols.py',
    'derived_inputs': ['glyphs/ascii.py', 'glyphs/paths.py'],
    'external_glyph_inputs': [],
    'license': 'AGPL-3.0-only; see repository LICENSE and NOTICE.md',
    'scope': 'Explicit MATH, ARROWS, GREEK, LATIN and enclosure repertoires below; no whole-block coverage claim',
}
FILLED = set()
GLYPHS = {}
CATEGORIES = {}


def line(*points):
    return [tuple(map(float, p)) for p in points]


def stroke(*points):
    return [line(*points)]


def copy(paths):
    return deepcopy(paths)


def transform(paths, sx=1.0, sy=1.0, dx=0.0, dy=0.0):
    return [[(x*sx+dx, y*sy+dy) for x, y in path] for path in paths]


def mirror(paths):
    return transform(paths, sx=-1, dx=24)


def ring(cx=12, cy=12, rx=9, ry=None):
    ry = rx if ry is None else ry
    # Chamfered octagonal ring, shared as a geometric primitive only.
    q = 0.68
    return stroke((cx-rx*q,cy-ry),(cx+rx*q,cy-ry),(cx+rx,cy-ry*q),
                  (cx+rx,cy+ry*q),(cx+rx*q,cy+ry),(cx-rx*q,cy+ry),
                  (cx-rx,cy+ry*q),(cx-rx,cy-ry*q),(cx-rx*q,cy-ry))


def dot(x, y):
    return stroke((x-.35,y),(x+.35,y))


def add(char, paths, category):
    if char in ASCII or char in LEGACY_SYMBOLS:
        return
    if char in GLYPHS:
        raise ValueError(f'duplicate authored symbol: {char!r}')
    GLYPHS[char] = copy(paths)
    CATEGORIES[char] = category


H = stroke((4,12),(20,12))
V = stroke((12,4),(12,20))
PLUS = H + V
CROSS = stroke((5,5),(19,19)) + stroke((19,5),(5,19))
SLASH = stroke((20,3),(4,21))
EQUAL = stroke((4,9),(20,9)) + stroke((4,15),(20,15))
LESS = stroke((19,4),(5,12),(19,20))
GREATER = mirror(LESS)
TILDE = stroke((3,13),(6,10),(9,10),(15,14),(18,14),(21,11))
SUBSET = stroke((20,4),(9,4),(4,8),(4,16),(9,20),(20,20))
UNION = stroke((4,4),(4,15),(7,20),(17,20),(20,15),(20,4))
INTERSECTION = transform(UNION, sy=-1, dy=24)
INTEGRAL = stroke((18,3),(15,2),(12,4),(11,8),(13,16),(12,20),(9,22),(6,21))
TRIANGLE = stroke((12,3),(22,21),(2,21),(12,3))
SQUARE = stroke((3,3),(21,3),(21,21),(3,21),(3,3))
DIAMOND = stroke((12,3),(21,12),(12,21),(3,12),(12,3))

MATH = {
    '∀': stroke((3,3),(12,21),(21,3)) + stroke((7,12),(17,12)),
    '∁': stroke((20,4),(9,4),(4,8),(4,16),(9,20),(20,20)),
    '∂': stroke((6,4),(10,2),(17,4),(20,9),(19,17),(15,21),(8,21),(4,18),(4,13),(8,9),(14,9),(19,13)),
    '∃': stroke((4,3),(20,3),(20,21),(4,21)) + stroke((7,12),(20,12)),
    '∅': ring() + SLASH,
    '∆': TRIANGLE,
    '∇': transform(TRIANGLE, sy=-1, dy=24),
    '∈': SUBSET + stroke((4,12),(18,12)),
    '∋': mirror(SUBSET + stroke((4,12),(18,12))),
    '∏': stroke((3,4),(21,4)) + stroke((6,4),(6,21)) + stroke((18,4),(18,21)),
    '∐': stroke((3,20),(21,20)) + stroke((6,3),(6,20)) + stroke((18,3),(18,20)),
    '∑': stroke((21,3),(3,3),(12,12),(3,21),(21,21)),
    '∓': stroke((4,5),(20,5)) + transform(PLUS, sy=.65, dy=9),
    '∔': PLUS + dot(12,2),
    '∕': stroke((18,2),(6,22)),
    '∖': stroke((6,2),(18,22)),
    '∗': stroke((12,3),(12,21)) + stroke((4,7),(20,17)) + stroke((4,17),(20,7)),
    '∘': ring(rx=3),
    '∙': dot(12,12),
    '√': stroke((2,13),(5,11),(9,21),(14,3),(22,3)),
    '∝': stroke((21,6),(18,5),(14,7),(9,17),(6,19),(3,17),(2,12),(4,7),(7,5),(10,7),(16,17),(19,19),(22,18)),
    '∟': stroke((4,3),(4,20),(21,20)),
    '∠': stroke((20,4),(4,20),(22,20)),
    '∡': stroke((20,4),(4,20),(22,20)) + stroke((12,12),(16,14),(17,20)),
    '∢': stroke((20,3),(4,20),(22,20)) + stroke((11,12),(14,14),(15,17),(14,20)) + stroke((8,4),(15,8),(20,14),(22,20)),
    '∣': V,
    '∥': stroke((8,3),(8,21)) + stroke((16,3),(16,21)),
    '∧': stroke((3,20),(12,4),(21,20)),
    '∨': stroke((3,4),(12,20),(21,4)),
    '∩': INTERSECTION,
    '∪': UNION,
    '∫': INTEGRAL,
    '∬': transform(INTEGRAL,sx=.65,dx=-.5) + transform(INTEGRAL,sx=.65,dx=9),
    '∭': transform(INTEGRAL,sx=.48,dx=-1.5) + transform(INTEGRAL,sx=.48,dx=5.8) + transform(INTEGRAL,sx=.48,dx=13.1),
    '∮': INTEGRAL + ring(rx=6,ry=4),
    '∯': transform(INTEGRAL,sx=.65,dx=-.5) + transform(INTEGRAL,sx=.65,dx=9) + ring(rx=8,ry=4),
    '∰': transform(INTEGRAL,sx=.48,dx=-1.5) + transform(INTEGRAL,sx=.48,dx=5.8) + transform(INTEGRAL,sx=.48,dx=13.1) + ring(rx=10,ry=4),
    '∴': dot(12,5)+dot(5,19)+dot(19,19),
    '∵': dot(5,5)+dot(19,5)+dot(12,19),
    '∶': dot(12,6)+dot(12,18),
    '∷': dot(7,6)+dot(17,6)+dot(7,18)+dot(17,18),
    '∼': TILDE,
    '∽': transform(TILDE,sy=-1,dy=24),
    '≃': transform(TILDE,dy=-4)+stroke((3,17),(21,17)),
    '≅': transform(TILDE,dy=-6)+transform(EQUAL,dy=5),
    '≈': transform(TILDE,dy=-4)+transform(TILDE,dy=4),
    '≊': transform(TILDE,dy=-7)+transform(TILDE,dy=0)+stroke((3,20),(21,20)),
    '≋': transform(TILDE,dy=-6)+TILDE+transform(TILDE,dy=6),
    '≍': stroke((3,5),(8,9),(16,9),(21,5))+stroke((3,19),(8,15),(16,15),(21,19)),
    '≐': EQUAL+dot(12,3),
    '≑': EQUAL+dot(12,3)+dot(12,21),
    '≒': EQUAL+dot(5,3)+dot(19,21),
    '≓': EQUAL+dot(19,3)+dot(5,21),
    '≔': transform(EQUAL,sx=.72,dx=6)+dot(3,9)+dot(3,15),
    '≕': transform(EQUAL,sx=.72,dx=0)+dot(21,9)+dot(21,15),
    '≖': EQUAL+ring(cy=12,rx=4,ry=5),
    '≗': transform(EQUAL,dy=4)+ring(cy=4,rx=2,ry=2),
    '≙': transform(EQUAL,dy=5)+stroke((5,8),(12,2),(19,8)),
    '≜': transform(EQUAL,dy=5)+stroke((12,1),(17,8),(7,8),(12,1)),
    '≟': transform(EQUAL,dy=6)+stroke((8,3),(10,1),(14,1),(16,3),(16,5),(12,8))+dot(12,10),
    '≡': EQUAL+H,
    '≤': transform(LESS,sy=.7,dy=0)+stroke((4,20),(20,20)),
    '≥': transform(GREATER,sy=.7,dy=0)+stroke((4,20),(20,20)),
    '≪': transform(LESS,sx=.6,dx=-1)+transform(LESS,sx=.6,dx=10),
    '≫': transform(GREATER,sx=.6,dx=-1)+transform(GREATER,sx=.6,dx=10),
    '≲': transform(LESS,sy=.65,dy=0)+transform(TILDE,dy=7),
    '≳': transform(GREATER,sy=.65,dy=0)+transform(TILDE,dy=7),
    '≶': transform(LESS,sy=.47,dy=0)+transform(GREATER,sy=.47,dy=13),
    '≷': transform(GREATER,sy=.47,dy=0)+transform(LESS,sy=.47,dy=13),
    '⊂': SUBSET,
    '⊃': mirror(SUBSET),
    '⊆': transform(SUBSET,sy=.7,dy=0)+stroke((4,21),(20,21)),
    '⊇': transform(mirror(SUBSET),sy=.7,dy=0)+stroke((4,21),(20,21)),
    '⊎': UNION+transform(PLUS,sx=.45,sy=.45,dx=6.6,dy=3),
    '⊏': stroke((20,4),(4,4),(4,20),(20,20)),
    '⊐': stroke((4,4),(20,4),(20,20),(4,20)),
    '⊑': stroke((20,3),(4,3),(4,16),(20,16))+stroke((4,21),(20,21)),
    '⊒': stroke((4,3),(20,3),(20,16),(4,16))+stroke((4,21),(20,21)),
    '⊓': stroke((4,20),(4,4),(20,4),(20,20)),
    '⊔': stroke((4,4),(4,20),(20,20),(20,4)),
    '⊕': ring()+transform(PLUS,sx=.6,sy=.6,dx=4.8,dy=4.8),
    '⊖': ring()+stroke((6,12),(18,12)),
    '⊗': ring()+transform(CROSS,sx=.7,sy=.7,dx=3.6,dy=3.6),
    '⊘': ring()+stroke((6,18),(18,6)),
    '⊙': ring()+dot(12,12),
    '⊚': ring()+ring(rx=4),
    '⊛': ring()+stroke((12,6),(12,18))+stroke((7,9),(17,15))+stroke((7,15),(17,9)),
    '⊞': SQUARE+transform(PLUS,sx=.65,sy=.65,dx=4.2,dy=4.2),
    '⊟': SQUARE+stroke((6,12),(18,12)),
    '⊠': SQUARE+transform(CROSS,sx=.75,sy=.75,dx=3,dy=3),
    '⊡': SQUARE+dot(12,12),
    '⊢': stroke((5,3),(5,21))+stroke((5,12),(21,12)),
    '⊣': stroke((19,3),(19,21))+stroke((3,12),(19,12)),
    '⊤': stroke((3,5),(21,5))+stroke((12,5),(12,21)),
    '⊥': stroke((3,19),(21,19))+stroke((12,3),(12,19)),
    '⊦': stroke((6,6),(6,18))+stroke((6,12),(21,12)),
    '⊧': stroke((5,3),(5,21))+stroke((5,9),(21,9))+stroke((5,15),(21,15)),
    '⊨': stroke((5,3),(5,21))+stroke((5,8),(21,8))+stroke((5,16),(21,16)),
    '⊩': stroke((4,3),(4,21))+stroke((9,3),(9,21))+stroke((9,12),(21,12)),
    '⊪': stroke((2,3),(2,21))+stroke((7,3),(7,21))+stroke((12,3),(12,21))+stroke((12,12),(22,12)),
    '⊫': stroke((4,3),(4,21))+stroke((9,3),(9,21))+stroke((9,8),(21,8))+stroke((9,16),(21,16)),
    '⊲': stroke((20,3),(4,12),(20,21),(20,3)),
    '⊳': stroke((4,3),(20,12),(4,21),(4,3)),
    '⊴': stroke((20,2),(4,9),(20,16),(20,2))+stroke((4,21),(20,21)),
    '⊵': stroke((4,2),(20,9),(4,16),(4,2))+stroke((4,21),(20,21)),
    '⋀': stroke((2,22),(12,2),(22,22)),
    '⋁': stroke((2,2),(12,22),(22,2)),
    '⋂': transform(INTERSECTION,sx=1.15,sy=1.15,dx=-1.8,dy=-1.8),
    '⋃': transform(UNION,sx=1.15,sy=1.15,dx=-1.8,dy=-1.8),
    '⋄': transform(DIAMOND,sx=.55,sy=.7,dx=5.4,dy=3.6),
    '⋅': dot(12,12),
    '⋆': stroke((12,4),(14,10),(21,10),(16,14),(18,21),(12,17),(6,21),(8,14),(3,10),(10,10),(12,4)),
    '⋈': stroke((3,4),(21,20),(21,4),(3,20),(3,4)),
    '⋉': stroke((4,3),(4,21))+stroke((4,12),(20,4),(20,20),(4,12)),
    '⋊': stroke((20,3),(20,21))+stroke((20,12),(4,4),(4,20),(20,12)),
    '⋮': dot(12,4)+dot(12,12)+dot(12,20),
    '⋯': dot(4,12)+dot(12,12)+dot(20,12),
    '⋰': dot(4,20)+dot(12,12)+dot(20,4),
    '⋱': dot(4,4)+dot(12,12)+dot(20,20),
    '¬': stroke((3,9),(21,9),(21,17)),
    '‰': stroke((18,2),(3,22))+ring(6,6,3)+ring(14,19,3)+ring(21,19,2),
    '‱': stroke((18,2),(3,22))+ring(6,6,3)+ring(13,18,2)+ring(19,18,2)+ring(19,11,2),
    'ℓ': stroke((5,19),(15,8),(16,4),(14,2),(11,3),(8,9),(8,17),(10,21),(15,21),(19,18)),
    '℘': stroke((5,22),(8,6),(11,3),(15,3),(18,6),(19,12),(16,17),(12,17),(9,14),(6,17),(3,16)),
    'ℏ': stroke((6,2),(6,21))+stroke((3,6),(11,6))+stroke((6,12),(11,8),(16,8),(19,11),(19,21)),
    '℧': stroke((3,3),(3,11),(6,16),(9,17),(9,21),(3,21))+stroke((21,3),(21,11),(18,16),(15,17),(15,21),(21,21)),
}
# Explicit negation mappings; the slash is a semantic overlay, not a fallback.
for negative, positive in {'∄':'∃','∉':'∈','∌':'∋','∤':'∣','∦':'∥',
        '≁':'∼','≄':'≃','≇':'≅','≉':'≈','≢':'≡','≮':'<','≯':'>',
        '≰':'≤','≱':'≥','≴':'≲','≵':'≳','≸':'≶','≹':'≷',
        '⊄':'⊂','⊅':'⊃','⊈':'⊆','⊉':'⊇','⊬':'⊢','⊭':'⊨','⊮':'⊩','⊯':'⊫'}.items():
    base = {'<':LESS,'>':GREATER}.get(positive, MATH.get(positive))
    MATH[negative] = base + SLASH
MATH['⊊'] = MATH['⊆'] + stroke((14,17),(10,23))
MATH['⊋'] = MATH['⊇'] + stroke((14,17),(10,23))
for ch, number in [('∛','3'),('∜','4')]:
    MATH[ch] = stroke((4,14),(7,12),(10,21),(15,4),(22,4)) + transform(ASCII[number],sx=.25,sy=.3,dx=.8,dy=.5)
for ch, paths in MATH.items():
    add(ch, paths, 'mathematical operators and constants')

# Direction and relation arrows are literal constructions of shafts and heads.
RIGHT = stroke((3,12),(21,12))+stroke((15,6),(21,12),(15,18))
LEFT = mirror(RIGHT)
UP = [[(y,24-x) for x,y in path] for path in RIGHT]
DOWN = [[(y,x) for x,y in path] for path in RIGHT]
DOUBLE_RIGHT = stroke((3,9),(15,9),(15,4),(22,12),(15,20),(15,15),(3,15))
ARROWS = {
    '↖': stroke((20,20),(4,4))+stroke((4,13),(4,4),(13,4)),
    '↗': stroke((4,20),(20,4))+stroke((11,4),(20,4),(20,13)),
    '↘': stroke((4,4),(20,20))+stroke((11,20),(20,20),(20,11)),
    '↙': stroke((20,4),(4,20))+stroke((4,11),(4,20),(13,20)),
    '↕': UP + stroke((6,18),(12,24-3),(18,18)),
    '↦': RIGHT+stroke((3,5),(3,19)),
    '↤': LEFT+stroke((21,5),(21,19)),
    '↥': UP+stroke((5,21),(19,21)),
    '↧': DOWN+stroke((5,3),(19,3)),
    '↩': stroke((21,4),(21,10),(17,14),(3,14))+stroke((9,8),(3,14),(9,20)),
    '↪': stroke((3,4),(3,10),(7,14),(21,14))+stroke((15,8),(21,14),(15,20)),
    '↰': stroke((18,22),(18,7),(14,3),(3,3))+stroke((8,0),(3,3),(8,7)),
    '↱': stroke((6,22),(6,7),(10,3),(21,3))+stroke((16,0),(21,3),(16,7)),
    '⇄': transform(RIGHT,sy=.65,dy=0)+transform(LEFT,sy=.65,dy=9),
    '⇆': transform(LEFT,sy=.65,dy=0)+transform(RIGHT,sy=.65,dy=9),
    '⇌': stroke((3,8),(21,8),(16,3))+stroke((21,16),(3,16),(8,21)),
    '⇋': stroke((21,8),(3,8),(8,3))+stroke((3,16),(21,16),(16,21)),
    '⇒': DOUBLE_RIGHT,
    '⇐': mirror(DOUBLE_RIGHT),
    '⇑': [[(y,24-x) for x,y in p] for p in DOUBLE_RIGHT],
    '⇓': [[(y,x) for x,y in p] for p in DOUBLE_RIGHT],
    '⇔': stroke((9,9),(15,9),(15,4),(22,12),(15,20),(15,15),(9,15),(9,20),(2,12),(9,4),(9,9)),
    '⇕': stroke((9,9),(9,15),(4,15),(12,22),(20,15),(15,15),(15,9),(20,9),(12,2),(4,9),(9,9)),
}
for ch, paths in ARROWS.items():
    add(ch, paths, 'arrows')

# Greek: shared shapes are intentional Latin/Greek homographs; distinct letters
# below have independent, explicitly drawn paths. Lowercase descenders fit y=23.
GREEK = {}
for greek, latin in zip('ΑΒΕΖΗΙΚΜΝΟΡΤΥΧ', 'ABEZHIKMNOPTYX'):
    GREEK[greek] = copy(ASCII[latin])
GREEK.update({
    'Γ': stroke((4,22),(4,2),(21,2)),
    'Δ': stroke((12,2),(22,22),(2,22),(12,2)),
    'Θ': ring(cx=12,cy=12,rx=9,ry=10)+stroke((5,12),(19,12)),
    'Λ': stroke((2,22),(12,2),(22,22)),
    'Ξ': stroke((3,2),(21,2))+stroke((5,12),(19,12))+stroke((3,22),(21,22)),
    'Π': stroke((3,22),(3,2),(21,2),(21,22)),
    'Σ': stroke((21,2),(3,2),(12,12),(3,22),(21,22)),
    'Φ': ring(cx=12,cy=12,rx=10,ry=7)+stroke((12,1),(12,23)),
    'Ψ': stroke((3,3),(3,10),(7,15),(17,15),(21,10),(21,3))+stroke((12,2),(12,22)),
    'Ω': stroke((2,22),(8,22),(8,18),(3,14),(3,7),(7,2),(17,2),(21,7),(21,14),(16,18),(16,22),(22,22)),
    'α': stroke((20,7),(16,18),(12,21),(7,21),(3,17),(3,11),(7,7),(12,7),(16,11),(18,18),(21,21)),
    'β': stroke((5,23),(5,6),(8,2),(13,2),(17,5),(16,9),(11,12),(5,12))+stroke((11,12),(17,13),(20,16),(18,20),(13,22),(8,21),(5,18)),
    'γ': stroke((3,7),(7,7),(13,19),(14,23),(11,23),(11,19),(20,7)),
    'δ': stroke((18,3),(11,2),(7,4),(7,6),(17,11),(20,15),(19,19),(15,22),(8,22),(4,18),(4,13),(8,9),(13,9)),
    'ε': stroke((20,8),(16,6),(9,6),(5,9),(6,12),(12,13),(6,14),(4,17),(6,21),(12,22),(19,20)),
    'ζ': stroke((5,3),(20,3),(9,11),(5,16),(7,20),(16,20),(19,22),(18,24),(13,24)),
    'η': stroke((3,8),(5,7),(6,10),(6,21))+stroke((6,11),(10,7),(16,7),(19,10),(19,24)),
    'θ': ring(cx=12,cy=12,rx=7,ry=10)+stroke((5,12),(19,12)),
    'ι': stroke((10,7),(10,18),(12,21),(16,21)),
    'κ': stroke((5,7),(5,22))+stroke((20,7),(5,15),(11,13),(21,22)),
    'λ': stroke((4,2),(8,2),(11,6),(21,22))+stroke((12,9),(3,22)),
    'μ': stroke((4,7),(4,24))+stroke((4,16),(7,21),(12,21),(18,17),(18,7))+stroke((18,17),(20,21),(22,21)),
    'ν': stroke((3,7),(9,22),(17,15),(21,7)),
    'ξ': stroke((18,2),(11,2),(6,5),(7,9),(16,11),(9,11),(4,15),(5,19),(14,21),(18,22),(17,24),(12,24)),
    'ο': ring(cx=12,cy=14,rx=8,ry=8),
    'π': stroke((2,8),(6,6),(22,6))+stroke((7,6),(7,22))+stroke((17,6),(17,19),(20,22),(22,21)),
    'ρ': stroke((4,24),(4,13),(7,8),(12,6),(18,8),(21,13),(20,18),(15,22),(9,22),(4,18)),
    'ς': stroke((20,8),(15,6),(8,7),(4,11),(5,16),(10,19),(17,21),(18,24),(13,24)),
    'σ': stroke((22,7),(10,7),(5,10),(3,15),(6,20),(11,22),(17,20),(20,15),(17,10),(13,7)),
    'τ': stroke((3,9),(7,7),(21,7))+stroke((12,7),(12,18),(15,22),(20,21)),
    'υ': stroke((3,7),(6,7),(6,16),(9,21),(15,22),(20,18),(21,11),(19,7)),
    'φ': ring(cx=12,cy=13,rx=9,ry=7)+stroke((12,3),(12,24)),
    'χ': stroke((3,7),(7,7),(18,23),(22,23))+stroke((21,7),(4,24)),
    'ψ': stroke((3,7),(5,7),(5,16),(9,20),(15,20),(20,16),(21,7))+stroke((12,3),(12,24)),
    'ω': stroke((6,7),(3,11),(3,18),(6,22),(10,21),(12,17),(12,10),(12,17),(15,21),(19,22),(22,18),(22,11),(19,7)),
    'ϐ': stroke((7,22),(7,6),(10,2),(15,2),(18,5),(17,9),(11,12),(7,12))+stroke((11,12),(18,14),(20,18),(17,22),(11,22),(7,20)),
    'ϑ': stroke((7,3),(11,2),(15,4),(16,9),(14,15),(9,18),(5,16),(3,11),(5,7),(10,7),(16,12),(21,12),(21,18),(17,22),(10,22),(6,20)),
    'ϕ': stroke((12,1),(12,24))+stroke((7,5),(3,10),(3,16),(7,20),(17,20),(21,16),(21,10),(17,5)),
    'ϖ': stroke((2,7),(22,7))+stroke((5,7),(3,15),(5,21),(9,22),(12,18),(12,10),(12,18),(16,22),(20,21),(22,15),(20,7)),
    'ϱ': stroke((5,24),(4,15),(6,9),(11,6),(17,7),(21,12),(20,18),(16,21),(10,20),(7,16),(7,12))+stroke((10,20),(17,24)),
    'ϵ': stroke((21,7),(11,7),(5,11),(5,17),(10,21),(21,21))+stroke((5,14),(18,14)),
    'ϰ': stroke((5,7),(6,14),(4,22))+stroke((20,7),(14,7),(7,14),(15,14),(21,22)),
})
for ch, paths in GREEK.items():
    add(ch, paths, 'Greek and Greek symbol variants')

# Single precomposed diacritics in Latin-1 and Latin Extended-A, composed from
# original ASCII only. Body height is reduced so the mark never collides with
# cap height; lower accents reserve a separate descender zone.
ACCENTS = {
    '\u0300': stroke((10,1),(14,4)),
    '\u0301': stroke((10,4),(14,1)),
    '\u0302': stroke((8,4),(12,1),(16,4)),
    '\u0303': stroke((7,4),(10,2),(14,4),(17,2)),
    '\u0304': stroke((7,2),(17,2)),
    '\u0306': stroke((7,1),(9,4),(15,4),(17,1)),
    '\u0307': dot(12,2),
    '\u0308': dot(8,2)+dot(16,2),
    '\u030a': ring(cx=12,cy=2.5,rx=2.5,ry=2),
    '\u030b': stroke((7,4),(11,1))+stroke((13,4),(17,1)),
    '\u030c': stroke((7,1),(12,4),(17,1)),
    '\u0327': stroke((12,19),(10,21),(14,22),(13,24),(9,24)),
    '\u0328': stroke((15,19),(12,22),(13,24),(17,24)),
}
LATIN = {}
for cp in range(0x00c0, 0x0180):
    char = chr(cp)
    decomposed = unicodedata.normalize('NFD',char)
    if len(decomposed) != 2 or decomposed[0] not in ASCII or decomposed[1] not in ACCENTS:
        continue
    base, mark = decomposed
    if not base.isascii() or not base.isalpha():
        continue
    body = copy(ASCII[base])
    if base in 'ij' and mark not in ('\u0327','\u0328'):
        body = [p for p in body if max(y for x,y in p)>6]
    below = mark in ('\u0327','\u0328')
    body = transform(body,sy=.76 if below else .73,dy=1 if below else 6.1)
    LATIN[char] = body+ACCENTS[mark]
LATIN.update({
    'Æ': stroke((1,22),(11,2),(22,2))+stroke((11,2),(11,22),(22,22))+stroke((5,14),(21,14)),
    'æ': stroke((2,9),(5,7),(10,7),(12,10),(12,22))+stroke((12,14),(5,14),(2,17),(3,21),(7,22),(12,18))+stroke((12,14),(22,14),(21,9),(18,7),(15,8),(12,12),(12,18),(16,22),(21,21)),
    'Œ': stroke((12,2),(7,2),(2,7),(2,17),(7,22),(12,22),(12,2),(22,2))+stroke((12,12),(21,12))+stroke((12,22),(22,22)),
    'œ': ring(cx=7,cy=14.5,rx=5,ry=7.5)+stroke((12,14),(22,14),(21,9),(18,7),(15,8),(12,12),(12,18),(16,22),(21,21)),
    'Ø': copy(ASCII['O'])+stroke((22,1),(2,23)),
    'ø': copy(ASCII['o'])+stroke((21,5),(3,24)),
    'Ð': copy(ASCII['D'])+stroke((1,12),(13,12)),
    'ð': stroke((7,2),(17,7),(21,13),(20,18),(16,22),(9,22),(4,18),(4,12),(8,9),(14,9),(20,13))+stroke((5,7),(17,2)),
    'Þ': stroke((4,2),(4,22))+stroke((4,7),(16,7),(21,10),(21,14),(16,17),(4,17)),
    'þ': stroke((4,2),(4,24))+stroke((4,10),(10,7),(16,7),(21,11),(21,17),(17,21),(10,21),(4,18)),
    'ß': stroke((4,22),(4,7),(7,3),(13,2),(17,5),(16,9),(11,12),(18,14),(21,18),(19,22),(13,22),(10,20)),
    'Ł': copy(ASCII['L'])+stroke((1,15),(13,7)),
    'ł': copy(ASCII['l'])+stroke((5,15),(17,7)),
    'Đ': copy(ASCII['D'])+stroke((1,12),(13,12)),
    'đ': copy(ASCII['d'])+stroke((13,4),(24,4)),
    'Ħ': copy(ASCII['H'])+stroke((1,6),(23,6)),
    'ħ': copy(ASCII['h'])+stroke((1,5),(11,5)),
    'ı': stroke((10,8),(13,8),(13,22))+stroke((8,22),(18,22)),
    'ĸ': stroke((4,7),(4,22))+stroke((20,7),(4,15),(21,22)),
    'Ŋ': stroke((3,22),(3,2),(21,22),(21,2))+stroke((21,22),(19,24),(15,24)),
    'ŋ': copy(ASCII['n'])+stroke((21,20),(21,22),(19,24),(15,24)),
    'Ŧ': copy(ASCII['T'])+stroke((5,8),(19,8)),
    'ŧ': copy(ASCII['t'])+stroke((5,15),(19,15)),
    'ſ': stroke((7,22),(7,6),(11,2),(17,2),(21,5)),
})
for ch, paths in LATIN.items():
    add(ch, paths, 'extended Latin')

# Mathematical double-struck constants use an authored parallel stem, rather
# than importing any alphabet/font design. These are not a full styled alphabet.
for char, base, extra in [
    ('ℂ','C',stroke((6,6),(6,18))),
    ('ℍ','H',stroke((6,2),(6,22))+stroke((18,2),(18,22))),
    ('ℕ','N',stroke((6,2),(6,22))+stroke((18,2),(18,22))),
    ('ℙ','P',stroke((6,2),(6,22))),
    ('ℚ','Q',stroke((6,7),(6,17))),
    ('ℝ','R',stroke((6,2),(6,22))),
    ('ℤ','Z',stroke((5,20),(20,5))),
]:
    add(char,copy(ASCII[base])+extra,'mathematical double-struck constants')

SUPERSCRIPT = dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁱⁿ','0123456789+-=()in'))
SUBSCRIPT = dict(zip('₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎','0123456789+-=()'))
for char,base in SUPERSCRIPT.items():
    add(char,transform(ASCII[base],sx=.55,sy=.53,dx=5.4,dy=.1),'superscripts')
for char,base in SUBSCRIPT.items():
    add(char,transform(ASCII[base],sx=.55,sy=.53,dx=5.4,dy=10.8),'subscripts')
for char,base in zip('ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ','aehijklmnoprstuvx'):
    add(char,transform(ASCII[base],sx=.55,sy=.50,dx=5.4,dy=11),'subscripts')
FRACTIONS = {'¼':('1','4'),'½':('1','2'),'¾':('3','4'),'⅐':('1','7'),
    '⅑':('1','9'),'⅒':('1','10'),'⅓':('1','3'),'⅔':('2','3'),
    '⅕':('1','5'),'⅖':('2','5'),'⅗':('3','5'),'⅘':('4','5'),
    '⅙':('1','6'),'⅚':('5','6'),'⅛':('1','8'),'⅜':('3','8'),
    '⅝':('5','8'),'⅞':('7','8')}
for char,(num,den) in FRACTIONS.items():
    paths = transform(ASCII[num],sx=.38,sy=.47,dx=.5,dy=.2)+stroke((3,23),(21,1))
    for n,digit in enumerate(den):
        paths += transform(ASCII[digit],sx=.38/len(den),sy=.47,dx=13+n*4.6,dy=12.5)
    add(char,paths,'vulgar fractions')

# Circled Latin and digits are real character-specific geometric compositions.
for start,letters in [(0x24B6,'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),(0x24D0,'abcdefghijklmnopqrstuvwxyz')]:
    for i,base in enumerate(letters):
        add(chr(start+i),ring(rx=11)+transform(ASCII[base],sx=.52,sy=.6,dx=5.76,dy=4.8),'circled Latin')
for value in range(1,21):
    body=[]
    digits=str(value)
    for i,digit in enumerate(digits):
        if len(digits)==1:
            body += transform(ASCII[digit],sx=.53,sy=.60,dx=5.64,dy=4.8)
        else:
            body += transform(ASCII[digit],sx=.30,sy=.55,dx=4+i*8,dy=5.4)
    add(chr(0x2460+value-1),ring(rx=11)+body,'circled numbers')
add('⓪',ring(rx=11)+transform(ASCII['0'],sx=.53,sy=.6,dx=5.64,dy=4.8),'circled numbers')

# Useful currency and typographical forms, independently constructed.
TYPOGRAPHY = {
    '¢': transform(ASCII['c'],sx=.8,dx=2.4)+stroke((12,2),(12,24)),
    '£': stroke((20,5),(17,2),(10,2),(6,6),(6,18),(3,22),(21,22))+stroke((3,12),(17,12)),
    '¤': ring(rx=6)+stroke((3,3),(7,7))+stroke((17,17),(21,21))+stroke((21,3),(17,7))+stroke((7,17),(3,21)),
    '¥': stroke((3,2),(12,11),(21,2))+stroke((12,11),(12,22))+stroke((4,13),(20,13))+stroke((4,17),(20,17)),
    '€': stroke((21,4),(16,2),(9,2),(4,8),(4,16),(9,22),(16,22),(21,20))+stroke((1,9),(17,9))+stroke((1,15),(17,15)),
    '©': ring(rx=11)+transform(ASCII['C'],sx=.55,sy=.6,dx=5.4,dy=4.8),
    '®': ring(rx=11)+transform(ASCII['R'],sx=.55,sy=.6,dx=5.4,dy=4.8),
    '™': transform(ASCII['T'],sx=.43,sy=.52,dx=.3,dy=1)+transform(ASCII['M'],sx=.43,sy=.52,dx=13,dy=1),
    '†': stroke((12,2),(12,23))+stroke((4,8),(20,8)),
    '‡': stroke((12,1),(12,23))+stroke((4,7),(20,7))+stroke((4,17),(20,17)),
    '§': stroke((19,4),(15,2),(9,2),(5,5),(6,9),(18,15),(19,19),(15,22),(9,22),(5,20))+stroke((17,9),(20,12),(18,16),(13,17),(6,14),(4,11),(6,8),(11,7)),
    '¶': stroke((13,2),(7,2),(3,5),(3,9),(7,12),(13,12))+stroke((13,2),(13,22))+stroke((19,2),(19,22))+stroke((10,2),(23,2)),
    '¡': dot(12,3)+stroke((12,9),(12,22)),
    '¿': dot(12,3)+stroke((12,9),(12,12),(5,16),(5,19),(8,22),(17,22),(20,19)),
    '«': stroke((11,5),(4,12),(11,19))+stroke((21,5),(14,12),(21,19)),
    '»': stroke((3,5),(10,12),(3,19))+stroke((13,5),(20,12),(13,19)),
    '‹': stroke((17,5),(7,12),(17,19)),
    '›': stroke((7,5),(17,12),(7,19)),
    '‘': stroke((14,2),(10,6),(10,10),(14,10),(14,6),(10,6)),
    '’': stroke((10,10),(14,6),(14,2),(10,2),(10,6),(14,6)),
    '“': stroke((9,2),(5,6),(5,10),(9,10),(9,6),(5,6))+stroke((19,2),(15,6),(15,10),(19,10),(19,6),(15,6)),
    '”': stroke((5,10),(9,6),(9,2),(5,2),(5,6),(9,6))+stroke((15,10),(19,6),(19,2),(15,2),(15,6),(19,6)),
    '‚': stroke((10,24),(14,20),(14,16),(10,16),(10,20),(14,20)),
    '„': stroke((5,24),(9,20),(9,16),(5,16),(5,20),(9,20))+stroke((15,24),(19,20),(19,16),(15,16),(15,20),(19,20)),
    '‐': stroke((7,12),(17,12)),
    '–': stroke((4,12),(20,12)),
    '—': stroke((1,12),(23,12)),
    '‒': stroke((5,12),(19,12)),
    '′': stroke((14,2),(10,9)),
    '″': stroke((10,2),(6,9))+stroke((18,2),(14,9)),
    '‴': stroke((6,2),(2,9))+stroke((14,2),(10,9))+stroke((22,2),(18,9)),
    '‵': stroke((10,2),(14,9)),
    '‶': stroke((6,2),(10,9))+stroke((14,2),(18,9)),
    '‷': stroke((2,2),(6,9))+stroke((10,2),(14,9))+stroke((18,2),(22,9)),
    '℉': ring(cx=3.5,cy=4,rx=2.5,ry=2.5)+transform(ASCII['F'],sx=.65,dx=8),
}
for ch,paths in TYPOGRAPHY.items():
    add(ch,paths,'currency and typography')

# Modern Cyrillic: complete U+0400..U+045F, plus Ukrainian Ghe with upturn.
# These are upright Cyrillic designs. Lowercase letters that conventionally
# resemble smaller capitals use their own cap-like skeleton at x-height.
CYRILLIC = {}
for c, a in zip('АВЕКМНОРСТХ', 'ABEKMHOPCTX'):
    CYRILLIC[c] = copy(ASCII[a])
CYRILLIC.update({
    'Б': stroke((21,2),(4,2),(4,22),(15,22),(21,18),(21,13),(16,10),(4,10)),
    'Г': stroke((4,22),(4,2),(21,2)),
    'Д': stroke((2,24),(2,19),(22,19),(22,24))+stroke((5,19),(8,2),(18,2),(18,19)),
    'Ж': stroke((12,2),(12,22))+stroke((2,2),(8,12),(12,12),(16,12),(22,2))+stroke((8,12),(2,22))+stroke((16,12),(22,22)),
    'З': stroke((3,5),(7,2),(16,2),(21,6),(20,10),(15,12),(10,12),(16,12),(21,16),(21,18),(16,22),(7,22),(3,19)),
    'И': stroke((3,2),(3,22),(21,2),(21,22)),
    'Л': stroke((1,22),(4,22),(7,18),(9,2),(21,2),(21,22)),
    'П': stroke((3,22),(3,2),(21,2),(21,22)),
    'У': stroke((2,2),(12,14))+stroke((22,2),(11,21),(7,23),(3,22)),
    'Ф': ring(cx=12,cy=12,rx=10,ry=7)+stroke((12,1),(12,23)),
    'Ц': stroke((3,2),(3,20),(20,20),(20,2))+stroke((20,20),(23,20),(23,24)),
    'Ч': stroke((3,2),(3,9),(7,12),(14,12),(20,9))+stroke((20,2),(20,22)),
    'Ш': stroke((2,2),(2,22),(22,22),(22,2))+stroke((12,2),(12,22)),
    'Щ': stroke((2,2),(2,20),(21,20),(21,2))+stroke((11,2),(11,20))+stroke((21,20),(24,20),(24,24)),
    'Ъ': stroke((1,2),(7,2),(7,22),(17,22),(22,18),(22,14),(17,10),(7,10)),
    'Ы': stroke((3,2),(3,22),(10,22),(14,19),(14,14),(10,11),(3,11))+stroke((21,2),(21,22)),
    'Ь': stroke((4,2),(4,22),(15,22),(21,18),(21,14),(16,10),(4,10)),
    'Э': stroke((3,5),(8,2),(16,2),(21,7),(21,17),(16,22),(8,22),(3,19))+stroke((8,12),(21,12)),
    'Ю': stroke((3,2),(3,22))+stroke((3,12),(9,12))+ring(cx=16,cy=12,rx=7,ry=10),
    'Я': stroke((20,22),(20,2),(9,2),(3,6),(3,10),(8,13),(20,13))+stroke((11,13),(3,22)),
})
for c,a in zip('аеорсух','aeopcyx'):
    CYRILLIC[c] = copy(ASCII[a])
for capital in 'ВГЖЗИКЛМНПТФЦЧШЩЪЫЬЭЮЯ':
    CYRILLIC[capital.lower()] = transform(CYRILLIC[capital],sy=.72,dy=6.1)
CYRILLIC.update({
    'б': stroke((20,2),(14,3),(8,3),(5,7),(4,15),(5,19),(9,22),(16,22),(21,18),(21,12),(17,8),(11,8),(7,11),(4,16)),
    'д': stroke((2,24),(2,20),(22,20),(22,24))+stroke((5,20),(8,7),(18,7),(18,20)),
    # Ukrainian, Belarusian, Serbian and Macedonian letters, upright forms.
    'Є': stroke((21,5),(16,2),(8,2),(3,7),(3,17),(8,22),(16,22),(21,19))+stroke((3,12),(16,12)),
    'є': stroke((21,9),(16,7),(9,7),(4,11),(4,18),(9,22),(16,22),(21,19))+stroke((4,14),(16,14)),
    'Ѕ': copy(ASCII['S']), 'ѕ': copy(ASCII['s']),
    'І': copy(ASCII['I']), 'і': copy(ASCII['i']),
    'Ј': copy(ASCII['J']), 'ј': copy(ASCII['j']),
    'Љ': stroke((1,22),(3,22),(5,19),(7,2),(12,2),(12,22),(19,22),(23,19),(23,14),(19,11),(12,11)),
    'љ': stroke((1,22),(3,22),(5,19),(7,7),(12,7),(12,22),(19,22),(23,19),(23,16),(19,13),(12,13)),
    'Њ': stroke((2,2),(2,22))+stroke((2,11),(11,11))+stroke((11,2),(11,22),(18,22),(23,19),(23,15),(18,11),(11,11)),
    'њ': stroke((2,7),(2,22))+stroke((2,13),(11,13))+stroke((11,7),(11,22),(18,22),(23,19),(23,16),(18,13),(11,13)),
    'Ђ': stroke((2,5),(19,5))+stroke((7,2),(7,22))+stroke((7,12),(12,9),(17,9),(21,13),(21,20),(18,24),(15,24)),
    'ђ': stroke((2,6),(14,6))+stroke((6,2),(6,22))+stroke((6,13),(11,10),(16,10),(20,14),(20,21),(17,24),(14,24)),
    'Ћ': stroke((2,5),(19,5))+stroke((7,2),(7,22))+stroke((7,12),(12,9),(17,9),(21,13),(21,22)),
    'ћ': stroke((2,6),(14,6))+stroke((6,2),(6,22))+stroke((6,13),(11,10),(16,10),(20,14),(20,22)),
    'Џ': stroke((3,2),(3,21),(21,21),(21,2))+stroke((12,21),(12,24)),
    'џ': stroke((3,7),(3,21),(21,21),(21,7))+stroke((12,21),(12,24)),
    'Ґ': stroke((4,22),(4,5),(20,5),(20,1)),
    'ґ': stroke((4,22),(4,9),(20,9),(20,5)),
})
for char,base,mark in [('Ѐ','Е','\u0300'),('ѐ','е','\u0300'),
        ('Ё','Е','\u0308'),('ё','е','\u0308'),('Ѓ','Г','\u0301'),('ѓ','г','\u0301'),
        ('Ї','І','\u0308'),('ї','і','\u0308'),('Ќ','К','\u0301'),('ќ','к','\u0301'),
        ('Ѝ','И','\u0300'),('ѝ','и','\u0300'),('Ў','У','\u0306'),('ў','у','\u0306'),
        ('Й','И','\u0306'),('й','и','\u0306')]:
    body = copy(CYRILLIC[base])
    if base=='і':
        body = [p for p in body if max(y for x,y in p)>6]
    CYRILLIC[char] = transform(body,sy=.78,dy=4.8)+ACCENTS[mark]
for char,paths in CYRILLIC.items():
    add(char,paths,'Cyrillic alphabets')
assert set(map(chr,range(0x0400,0x0460))).issubset(CYRILLIC)

REPERTOIRE = ''.join(sorted(GLYPHS,key=ord))
NAMES = {char:unicodedata.name(char,f'U+{ord(char):04X}') for char in GLYPHS}
"""The generated name index is metadata, never a source of glyph geometry."""
