"""Thirteen exact-codepoint repairs backed by a second Unicode J-source review.

Geometry is newly authored on the project's grid. No reference contours,
image measurements, skeletons, or extracted font data are used.
"""
from dataclasses import replace

CORRECTED_CHARACTERS=tuple('兠劃厴哉唐嚳壚廬彧翺亟焈魲')


def _p(s):
    return [[tuple(map(float,q.split(','))) for q in line.split()]
            for line in s.split(';') if line.strip()]


def _fit(p,x,y,w,h):
    return [[(x+a*w/24,y+b*h/24) for a,b in line] for line in p]


_DAY=_p('2,2 22,2 22,22 2,22 2,2;2,12 22,12')
_MOON=_p('3,1 21,1 21,23 17,23;3,1 3,17 1,24;3,9 21,9;3,16 21,16')
_DOG=_p('1,8 23,8;12,1 11,12 7,19 1,24;12,9 17,18 24,24;18,1 22,4')
# 虍 occupies only its upper band. Its 匕 never overlaps the lower 田.
_LU=_p('11,0 11,4;11,2 21,2;23,5 4,5 4,17 1,24;'
       '8,7 20,6;11,5 11,9 15,10 21,10 23,8;'
       '7,12 22,12 22,17 7,17 7,12;7,14.5 22,14.5;14.5,12 14.5,17;'
       '7,23 7,19 22,19 22,23;12,19 12,23;17,19 17,23;5,24 24,24')

CORRECTION_NOTES={
 '兠':'Place central 白 between, not underneath, the left/right 北 strokes.',
 '劃':'Restore the continuous central vertical of 畫 through its upper bars and lower 田.',
 '厴':'Place 甲 below the 日月/犬 part of 厭, not over its interior.',
 '哉':'Keep the 土 vertical in the upper band so it cannot pass through 口.',
 '唐':'Use the J-source middle コ+一+丨 structure; remove two surplus lower horizontal strokes.',
 '嚳':'Fit both 爻 crosses between the 臼 sides and entirely above 冖.',
 '壚':'Separate 虍/匕, 田 and 皿 into distinct vertical bands beside 土.',
 '廬':'Separate 虍/匕, 田 and 皿 into distinct vertical bands inside 广.',
 '彧':'Keep both additional falling strokes below 口, rather than through its box.',
 '亟':'Join the 丂 fold to the top bar as in J0-5034; remove the detached extra upper level.',
 '焈':'Use the connected sloping 戶 crown of J4-6F6E instead of a detached dot-shaped 户 crown.',
 '魲':'Use the connected sloping 戶 crown of J3-7E43 instead of a detached dot-shaped 户 crown.',
 '翺':'Use the J-source 臯 lower horizontal/vertical form rather than a 米-like radiation.',
}


def correction_paths():
    g={}
    g['兠']=_p('6,1 6,14;0,5 6,5;0,12 6,10;'
               '18,1 18,12 20,14 23,14 24,12;24,4 18,7;'
               '13,0 11,3;8,3 16,3 16,13 8,13 8,3;8,8 16,8;'
               '8,15 8,20 4,23 1,24;16,15 16,22 19,24 23,24 24,21')
    picture=_p('3,3 20,3 20,8 3,8;1,5.5 23,5.5;2,11 22,11;'
               '12,0 12,21;3,14 21,14 21,21 3,21 3,14;3,17.5 21,17.5;1,24 23,24')
    g['劃']=_fit(picture,0,0,17,24)+_p('20,3 20,18;24,0 24,23 21,24')
    g['厴']=_p('23,1 3,1 3,16 0,24')+_fit(_DAY,6,3,8,6)+_fit(_MOON,6,10,8,6)+_fit(_DOG,15,3,9,13)+_p('6,17 22,17 22,22 6,22 6,17;6,19.5 22,19.5;14,17 14,24')
    g['哉']=_p('3,3 13,3;8,0 8,8;1,8 23,7;'
               '15,1 16,12 19,20 22,24 24,20;19,1 22,3;23,11 18,19 12,24;'
               '3,12 12,12 12,21 3,21 3,12')
    g['唐']=_p('11,0 14,2;24,4 3,4 3,16 0,24;'
               '8,7 21,7 21,13 8,13;6,10 24,10;15,5 15,16;'
               '8,18 22,18 22,24 8,24 8,18')
    g['嚳']=_p('7,0 2,2 2,8;2,4 6,4;2,7 6,7;'
               '18,1 23,1 23,8;18,4 23,4;18,7 23,7;'
               '9,1 16,4;16,1 9,4;9,5 16,8;16,5 9,8;'
               '1,13 1,10 24,10 24,13;'
               '7,14 4,17;6,16 22,16;13,14 13,20;2,19 24,19;'
               '5,21 21,21 21,24 5,24 5,21')
    g['壚']=_p('0,8 7,8;4,0 4,22;0,24 7,21')+_fit(_LU,8,0,16,24)
    g['廬']=_p('11,0 14,2;24,4 3,4 3,16 0,24')+_fit(_LU,5,5,19,19)
    g['彧']=_p('1,5 23,5;15,0 16,12 20,21 23,24 24,19;'
               '23,9 18,17 14,23;19,0 23,2;'
               '2,8 11,8 11,14 2,14 2,8;1,17 12,16;'
               '12,19 7,21 1,22;14,21 9,23 4,24')
    gao=_p('13,0 10,3;3,3 22,3 22,12 3,12 3,3;3,6 22,6;3,9 22,9;'
           '12,13 12,24;0,21 24,21;1,15 8,15;16,15 23,15;1,18 8,18;16,18 23,18')
    feather=_p('0,2 10,2 10,23 7,24;13,2 23,2 23,23 20,24;'
               '1,6 5,10;0,19 7,13;14,6 18,10;13,19 20,13')
    g['翺']=_fit(gao,0,0,11,24)+_fit(feather,12,0,12,24)
    g['亟']=_p('1,2 23,2;9,2 7,7 13,7 13,21 10,22;'
                 '2,9 7,9 7,19 2,19 2,9;16,8 23,8 20,16 16,21;17,11 20,17 24,21;1,24 23,24')
    door=_p('22,0 3,4;3,4 3,16 0,24;3,8 23,8 23,15 3,15')
    fire=_p('4,3 2,10;22,2 19,9;12,0 12,9 8,18 0,24;12,10 17,19 24,24')
    g['焈']=_fit(door,0,0,11,14)+_p('13,1 23,1 23,6 13,6;13,1 13,12 17,14 23,14 24,11')+_fit(fire,0,15,24,9)
    fish=_p('11,0 6,5;8,3 20,3 16,7;3,7 21,7 21,18 3,18 3,7;'
            '3,12.5 21,12.5;12,7 12,18;4,21 2,24;9,21 9,24;15,21 16,24;21,21 23,24')
    g['魲']=_fit(fish,0,0,11,24)+_fit(door,12,0,12,24)
    return {c:[[tuple(q) for q in line] for line in g[c]] for c in CORRECTED_CHARACTERS}


def apply(glyphs):
    changed=set()
    for c,p in correction_paths().items():
        if c not in glyphs:continue
        old=glyphs[c];notes=dict(old.notes)
        notes.setdefault('previous_source',old.source)
        notes.setdefault('previous_status',old.status)
        notes['proofread_additional_kanji_correction']=CORRECTION_NOTES[c]
        notes['proofread_additional_kanji_scope']='exact-key large-size structural repair; no global typographic certification'
        glyphs[c]=replace(old,paths=p,notes=notes,source='original:family.proofread_additional_kanji_corrections',status='structure-reviewed-large-size')
        changed.add(c)
    return changed
