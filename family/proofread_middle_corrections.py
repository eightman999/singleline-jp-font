"""Bounded new-family topology repairs, drawn as original 24-unit centerlines.

Reference typography was viewed to identify components, never traced/imported.
No legacy or component dictionary is modified; no recursive propagation occurs.
"""
from copy import deepcopy
from dataclasses import replace

CORRECTED_CHARACTERS = tuple('截旭昶曆毧毬毯毱氊氤氳爬瓞瓰瓱瓲瓸甅')

def _p(s):
    return [[tuple(map(float, v.split(','))) for v in row.split()] for row in s.split(';') if row.strip()]

def _fit(paths,x,y,w,h):
    return [[(x+a*w/24,y+b*h/24) for a,b in row] for row in paths]

_BOX=_p('2,2 22,2 22,22 2,22 2,2')
_DAY=_BOX+_p('2,12 22,12')
_WOOD=_p('1,7 23,7;12,1 12,23;12,7 8,15 1,22;12,7 17,15 23,22')
_GRAIN=_p('20,1 4,4')+_fit(_WOOD,0,3,24,21)
_FIRE=_p('12,1 12,11 8,18 1,23;12,11 17,18 23,23;3,6 6,11;21,5 17,11')
_MAO=_p('21,2 3,6;2,12 22,8;1,18 23,14;11,4 11,21 14,24 22,24 24,20')
_BA=_p('2,2 22,2 22,13 2,13;12,2 12,13;2,2 2,21 5,24 22,24 24,20')
_FEN=_p('8,1 5,6 1,9;16,1 19,6 23,9;5,12 21,12 19,23 14,23;12,12 9,20 3,24')
_WA=_p('1,2 23,2;9,2 4,21 13,18;8,9 17,9 16,21 20,24 24,21;9,13 12,16')
_GUA=_p('22,1 4,5 4,15 1,23;12,3 10,19 15,17;18,2 18,13 23,23')
_SHI=_p('7,1 3,8;5,6 21,6;1,12 23,12;12,1 12,12 8,19 1,24;12,12 17,19 24,24')
_QIU=_p('1,7 23,7;12,1 12,22 8,24;19,1 22,4;2,11 6,14;10,14 1,21;22,11 17,15;13,11 17,19 24,23')
_RONG=_p('2,7 12,7;7,3 7,22;1,15 13,15;15,1 16,12 20,22 23,24 24,20;14,19 23,10;19,2 22,5')
_YONG=_p('11,1 14,3;6,6 13,6 13,23 9,24;1,11 7,11 5,18 1,22;22,7 16,12;13,9 18,19 24,22')
_LI=_fit(_BOX,1,0,22,15)+_p('3,7 21,7;12,2 12,23;3,18 21,18;1,23 23,23')

CORRECTION_NOTES={c:'Separated original components; removed unintended crossings from generic overlapping composition.' for c in CORRECTED_CHARACTERS}
CORRECTION_NOTES.update({'截':'Separate 隹 at lower left from the right falling 戈; retain 土 above 隹.', '曆':'Put two 禾 above 日 inside 厂, rather than superimposing them.', '氊':'Use 毛 at left and 亶 (亠, 回, 旦) at right.', '氳':'Keep 囚 over 皿 within 气; this is U+6C33, not U+6C32.'})

def correction_paths():
    g={}
    # 截: preserve the only intended crown crossing with the long 戈.
    zhui=_p('6,1 2,6;4,5 4,23;13,1 16,4;8,6 23,6;8,12 22,12;8,18 22,18;7,23 24,23;8,6 8,23;16,6 16,23')
    g['截']=_p('2,4 15,4;8,1 8,8;1,8 23,8;16,1 17,12 20,21 23,24 24,20;14,23 20,16 23,11;20,2 23,5')+_fit(zhui,0,10,14,14)
    nine=_p('1,7 16,7 15,20 18,23 23,23 24,20;9,1 9,10 7,18 1,24')
    g['旭']=_fit(nine,0,0,13,24)+_fit(_DAY,15,3,9,18)
    g['昶']=_fit(_YONG,0,0,12,24)+_fit(_DAY,15,3,9,18)
    g['曆']=_p('2,24 4,15 4,2 24,2')+_fit(_GRAIN,5,4,8,9)+_fit(_GRAIN,15,4,8,9)+_fit(_DAY,7,15,15,9)
    # Left 毛 has short crossbars and a low sweep below the independent right.
    mao_left=_p('9,1 1,4;1,9 9,7;0,15 9,12;4,3 4,21 7,24 22,24 24,21')
    g['毧']=mao_left+_fit(_RONG,11,1,13,19)
    g['毬']=mao_left+_fit(_QIU,11,1,13,19)
    g['毯']=mao_left+_fit(_FIRE,11,0,13,9)+_fit(_FIRE,11,10,13,10)
    g['毱']=mao_left+_p('14,1 11,7;13,4 23,4 22,20 19,21')+_fit(_WOOD+_p('3,1 6,4;21,1 18,4'),12,7,8,11)
    dan=_p('12,0 13,2;1,4 23,4')+_fit(_BOX,1,6,22,9)+_fit(_BOX,7,8,10,5)+_fit(_DAY,3,16,18,6)+_p('1,24 24,24')
    g['氊']=mao_left+_fit(dan,11,0,13,21)
    qi=_p('5,0 1,5;4,3 23,3;4,6 21,6;3,9 20,9 20,19 23,24 24,21')
    g['氤']=qi+_fit(_BOX,2,11,15,12)+_fit(_SHI[2:],4,12,11,10)
    plate=_p('1,22 23,22;3,5 21,5 21,22;3,5 3,22;9,5 9,22;15,5 15,22')
    g['氳']=qi+_fit(_BOX,3,11,13,7)+_p('9.5,12 8,15 5,17;9.5,13 12,16 14,17')+_fit(plate,2,19,15,5)
    claw=_p('23,1 3,5 3,17 0,24;11,4 11,23;19,2 18,15 24,24')
    g['爬']=_fit(claw,0,0,11,24)+_fit(_BA,14,2,10,21)
    g['瓞']=_fit(_GUA,0,0,11,24)+_fit(_SHI,13,1,11,23)
    right={'瓰':_FEN,'瓱':_MAO,'瓲':_p('1,6 23,6;5,3 5,15 21,15 21,9;12,1 12,21 15,24 23,24 24,20'), '瓸':_p('1,1 23,1;12,1 9,6')+_fit(_DAY,1,6,22,18), '甅':_p('1,24 3,16 3,1 24,1')+_fit(_LI,5,4,19,20)}
    for c,r in right.items():g[c]=_fit(_WA,0,0,10,24)+_fit(r,13,1,11,23)
    return deepcopy(g)

def apply(glyphs):
    """Replace only present targets, preserving metadata and source dictionaries."""
    changed=set()
    for char,paths in correction_paths().items():
        if char not in glyphs:continue
        old=glyphs[char]
        glyphs[char]=replace(old,paths=paths,source='original:family.proofread_middle_corrections',status='structure-reviewed-large-size',notes={**old.notes,'previous_source':old.notes.get('previous_source',old.source),'previous_status':old.notes.get('previous_status',old.status),'proofread_middle_correction':CORRECTION_NOTES[char], 'proofread_middle_scope':'independent component topology repair; size proofs separate'})
        changed.add(char)
    return changed
