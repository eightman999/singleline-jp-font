"""Exact-key new-family repairs from the independent lower-range recheck.

Original geometric centerlines. No reference font outlines, pixels, skeletons,
or coordinates are copied. Legacy modules and shared components are untouched.
"""
from dataclasses import replace

CORRECTED_CHARACTERS = tuple('䰗䰠亙儔壔壽囟廸廹廼剋尅匙彪奠奥奧嶴冖宀凾巫')


def _p(s):
    return [[tuple(map(float,q.split(','))) for q in line.split()]
            for line in s.split(';') if line.strip()]


def _fit(p,x,y,w,h):
    return [[(x+a*w/24,y+b*h/24) for a,b in line] for line in p]


_RECT = _p('2,2 22,2 22,22 2,22 2,2')
_DAY = _RECT + _p('2,12 22,12')
_WHITE = _p('13,0 9,4;3,4 21,4 21,23 3,23 3,4;3,13 21,13')
_BIG = _p('1,7 23,7;12,0 11,11 7,19 1,24;12,8 17,18 24,24')
_MOUNTAIN = _p('12,1 12,23;2,8 2,23 22,23 22,8')
_LONG_LIFE = _p('3,3 21,3;12,0 12,6;5,6 19,6;'
                '3,8 21,8 19,10;4,11 20,11;12,11 12,14;3,14 21,14;2,17 23,17;'
                '3,19 10,19 10,24 3,24 3,19;'
                '13,20 24,20;21,18 21,24 18,24;14,21 16,23')
# Keep the zigzag at x<=7; the enclosed part starts at x>=9. The old
# enclosure extended to x=13 and crossed the inner glyph at x=10.
_LONG_STRIDE = _p('1,3 6,3 2,10 7,10 5,17 1,22;'
                  '1,16 6,21 13,24 24,24')
_OVERCOME = _p('2,4 20,4;11,0 11,8;4,8 18,8 18,14 4,14 4,8;'
               '8,14 8,19 4,23 0,24;14,14 14,22 17,24 22,24 24,21')
_RIGHT = _fit(_DAY,4,0,16,10) + _p('1,12 23,12;12,12 12,22;12,17 21,17;'
                                 '6,15 4,21 1,24;5,19 12,23 24,23')
_TIGER = _p('11,0 11,5;11,2 22,2;23,5 4,5 4,17 1,24;'
            '8,8 21,7;11,6 11,11 16,12 21,12 23,10;'
            '10,15 10,20 7,24;17,15 17,22 20,24 23,24 24,22')

CORRECTION_NOTES = {
    '䰗':'JA3-7E3E: keep both 鬥 crowns as open three-bar 王 shapes; restore the inner 亀 upper middle bar and continuous central stem across both boxes.',
    '䰠':'Reserve separate regions for the 鬼 head/legs and 申; only the sweeping 鬼 leg encloses the bottom.',
    '亙':'Replace two full-width interior horizontal bars with two independent diagonal inner strokes.',
    '儔':'Use a proportionate continuous 壽 structure beside 亻.',
    '壔':'Use a proportionate continuous 壽 structure beside 土.',
    '壽':'Restore the middle hooked/工 bands and remove the large accidental gap above 口寸.',
    '囟':'Keep the two crossing inner strokes entirely inside 囗; leave only the top short slant above it.',
    '廸':'Keep 廴 in the left and bottom margin, clear of 由.',
    '廹':'Keep 廴 in the left and bottom margin, clear of 白.',
    '廼':'Keep 廴 in the left and bottom margin, clear of 西.',
    '剋':'Reserve separate upper-left 克 and right 刂; remove crossing through the 古 head.',
    '尅':'Reserve upper-left 克 and right 寸 with a sweeping lower 克 leg.',
    '匙':'Place 匕 to the right of 是 instead of over its 日 and central stem.',
    '彪':'Place the three 彡 strokes to the right of 虎, not through its interior.',
    '奠':'Allocate enough height for 酉 between the crown and 大 instead of crushing it to a narrow strip.',
    '奥':'Place 米 within the enclosing upper box and keep the leading short slant separate.',
    '奧':'Place 釆 within the enclosing upper box and keep the leading short slant separate.',
    '嶴':'Use the repaired 奧 above 山, retaining all three vertical bands.',
    '冖':'Restore a shallow roof instead of the full-height 冂-like outline.',
    '宀':'Restore the compact roof/dot proportions rather than long enclosure legs.',
    '凾':'Separate the top 了 hook, inner 口/又 and outer 凵 so they no longer collide.',
    '巫':'Keep the two inner 人 between the top and bottom 工 bars.',
}


def correction_paths():
    g={}
    g['亙']=_p('2,1 22,1;9,4 5,21;9,4 20,4 16,21;'
               '10,9 15,12;9,15 14,18;1,24 23,24')
    g['壽']=_LONG_LIFE
    g['儔']=_p('6,1 4,8 1,13;4,8 4,24')+_fit(_LONG_LIFE,8,0,16,24)
    g['壔']=_p('0,8 7,8;4,1 4,22;0,23 7,21')+_fit(_LONG_LIFE,8,0,16,24)
    g['囟']=_p('13,0 10,4;3,5 21,5 21,24 3,24 3,5;'
               '7,9 17,20;17,9 7,20')
    g['冖']=_p('2,12 2,6 22,6 22,12')
    g['宀']=_p('11,3 13,6;2,13 2,8 22,8 21,13')
    by=_RECT+_p('2,12 22,12;12,0 12,22')
    west=_p('0,2 24,2;2,7 22,7 22,23 2,23 2,7;'
            '8,2 8,12 5,17;15,2 15,16 20,16')
    for c,inside in [('廸',by),('廹',_WHITE),('廼',west)]:
        g[c]=_LONG_STRIDE+_fit(inside,9,0,15,20)
    g['剋']=_fit(_OVERCOME,0,0,16,24)+_p('19,3 19,17;23,0 23,22 20,23')
    # 克's lower hooked leg sweeps below the right 寸 but does not cross its head.
    g['尅']=_fit(_OVERCOME,0,0,16,24)+_p('15,7 24,7;21,1 21,18 18,19;16,10 18,13')
    g['匙']=_fit(_RIGHT,0,0,15,24)+_p('18,2 18,20 20,22 23,22 24,19;24,6 18,10')
    g['彪']=_fit(_TIGER,0,0,16,24)+_p('23,1 18,6;23,8 18,13;24,15 21,20 17,23')
    g['巫']=_p('2,2 22,2;12,2 12,23;1,23 23,23;'
              '6,7 5,12 2,18;6,10 10,18;18,7 17,12 14,18;18,10 22,18')
    g['凾']=_p('2,8 2,24 22,24 22,8;5,2 20,2 13,7;'
               '13,7 13,20 10,21;5,8 10,8 10,17 5,17 5,8;'
               '15,8 21,8 19,14 15,19;15,10 18,16 21,19')
    wine=_p('1,0 23,0;3,5 21,5 21,24 3,24 3,5;'
            '9,0 9,10 6,14;15,0 15,13 18,14 21,14;3,19 21,19')
    g['奠']=_p('6,0 8,2;18,0 16,2')+_fit(wine,2,4,20,12)+_fit(_BIG,0,17,24,7)
    rice=_p('12,0 12,24;2,11 22,11;3,2 7,7;21,2 17,7;'
            '12,11 7,18 2,23;12,11 17,18 23,23')
    grain=_p('4,3 21,0;12,2 12,24;2,11 22,11;4,5 7,8;20,4 17,8;'
             '12,11 7,18 2,23;12,11 17,18 23,23')
    frame=_p('13,0 10,3;3,16 3,4 21,4 21,16')
    for c,inside in [('奥',rice),('奧',grain)]:
        g[c]=frame+_fit(inside,6,6,12,9)+_fit(_BIG,0,17,24,7)
    g['嶴']=_fit(g['奧'],0,0,24,17)+_fit(_MOUNTAIN,3,18,18,6)
    ghost=_p('8,0 5,3;2,3 12,3 12,12 2,12 2,3;'
             '2,7.5 12,7.5;7,3 7,12;'
             '5,12 5,18 2,22 0,24;9,12 9,22 12,24 21,24 24,21;'
             '11,15 10,19 13,18;12,16 14,20')
    g['䰠']=ghost+_p('15,4 23,4 23,16 15,16 15,4;15,10 23,10;19,0 19,21')
    # U+4C17 only. JA3-7E3E has two 王 crowns, not boxed side panels.
    # Its inner 亀 has two bisected boxes and one continuous central stem.
    fight=_p('1,0 1,24;23,0 23,23 21,24;'
             '3,2 10,2;3,4 10,4;3,6 10,6;6.5,2 6.5,6;'
             '14,2 21,2;14,4 21,4;14,6 21,6;17.5,2 17.5,6')
    turtle=_p('12,8 8,11 5,13;9,10 17,10 14,12;'
              '6,12 18,12 18,16 6,16 6,12;6,14 18,14;'
              '5,18 19,18 19,22 5,22 5,18;5,20 19,20;'
              '12,12 12,23 14,24 20,24 21,22')
    g['䰗']=fight+turtle
    return {c:[[tuple(q) for q in line] for line in g[c]] for c in CORRECTED_CHARACTERS}


def apply(glyphs):
    changed=set()
    for c,p in correction_paths().items():
        if c not in glyphs:continue
        old=glyphs[c];notes=dict(old.notes)
        notes.setdefault('previous_source', old.source)
        notes.setdefault('previous_status', old.status)
        notes['proofread_lower_correction']=CORRECTION_NOTES[c]
        notes['proofread_lower_scope']='exact-key topology repair; small-size legibility not certified'
        glyphs[c]=replace(old,paths=p,notes=notes,source='original:family.proofread_lower_corrections',status='structure-reviewed-large-size')
        changed.add(c)
    return changed
