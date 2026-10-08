"""Nine further new-family-only repairs after individual 200px rechecking.

Original centerlines, not derived from external outlines. Only the named final
Glyph records change; shared historical geometry and legacy assets do not.
"""
from copy import deepcopy
from dataclasses import replace
from .proofread_middle_corrections import _p, _fit

CORRECTED_CHARACTERS=tuple('應懴懺斄曩殱殲灋璺')
CORRECTION_NOTES={
 '應':'Separate 亻隹 above 心 inside 广; the old 心 overlapped 隹.',
 '斄':'Separate 未攵 crown, 厂, and enclosed 來 instead of overlaying the crown with 來.',
 '灋':'Keep 廌 above 去 at the right of 氵; remove their superimposed middle strokes.',
 '曩':'Expand compressed 襄 regions; two source horizontal centerlines were only 0.30 grid units apart and fused at 200px.',
 '璺':'Place 同 between 𦥑 and above 冖; retain independent 玉 below.',
}
for c in '懴懺殱殲':CORRECTION_NOTES[c]='Reserve lower-left 韭 and right 戈 within 韯/韱; avoid the old repeated inter-component crossings.'

def correction_paths():
    box=_p('2,2 22,2 22,22 2,22 2,2')
    wood=_p('1,7 23,7;12,1 12,24;12,7 7,16 1,22;12,7 17,16 23,22')
    heart=_p('3,8 1,17;8,5 8,19 11,23 20,23 23,19;12,2 16,7;20,9 24,15')
    zhui=_p('6,0 1,7;4,5 4,24;15,0 17,4;9,5 23,5;9,11 22,11;9,17 22,17;8,23 24,23;9,5 9,23;16,5 16,23')
    g={}
    g['應']=_p('12,0 14,2;3,24 5,15 5,4 24,4;10,6 7,10;8,9 8,16')+_fit(zhui,11,6,12,10)+_fit(heart,7,18,16,6)
    wei=wood+_p('5,3 19,3')
    tap=_p('7,0 2,7;5,5 23,5;17,5 14,14 8,20 1,24;7,7 12,16 24,24')
    come=wood+_p('6,8 3,13 1,15;6,8 8,13;18,8 16,13;18,8 21,14 24,16')
    g['斄']=_fit(wei,0,0,11,8)+_fit(tap,13,0,11,8)+_p('2,24 4,17 4,10 24,10')+_fit(come,6,12,18,12)
    # 韯 has 十 at the crown; 韱 has two 人. Their 韭 is below,
    # never scaled to a tiny overlay at the middle of a full-size 戈.
    fei=_p('6,0 6,22;16,0 16,22;1,5 6,5;1,11 6,11;1,17 6,17;16,5 22,5;16,11 22,11;16,17 22,17;0,24 24,24')
    for c in '懴懺殱殲':
        crown=_p('3,2 13,2;8,0 8,5') if c in '懴殱' else _p('4,0 2,3 0,5;4,0 7,5;11,0 9,3 7,5;11,0 15,5')
        r=crown+_p('0,6 24,6;17,0 18,14 21,23 24,24 24,20;14,24 21,16 24,10;21,0 24,3')+_fit(fei,0,8,15,15)
        left=_p('12,0 12,24;4,5 0,11;19,5 24,9') if c in '懴懺' else _p('0,2 24,2;12,2 7,9 2,13;7,8 21,8 17,17 10,22 1,24;7,11 14,15')
        g[c]=_fit(left,0,0,6,24)+_fit(r,8,0,16,24)
    water=_p('1,1 4,4;0,8 3,11;0,23 4,16')
    zhi=_p('13,0 15,2;5,3 23,3;5,3 5,10 2,17;5,6 22,6 22,10 5,10;12,3 12,10;18,3 18,10;8,11 22,11;9,11 8,13 22,13 21,17 19,17;5,15 4,17;10,15 11,17;14,15 15,17;18,14.5 19,16')
    qu=_p('4,7 20,7;12,0 12,13;0,13 24,13;11,13 4,22 21,22 17,17')
    g['灋']=water+_fit(zhi,5,0,19,16)+_fit(qu,7,18,16,6)
    g['璺']=_p('7,0 1,2 1,11 7,11;1,6 6,6;18,0 23,2 23,11 18,11;18,6 23,6;0,16 0,13 24,13 24,16')+_fit(box,8,0,8,11)+_p('9,3 15,3')+_fit(box,10,5,4,4)+_p('4,17 20,17;12,17 12,24;5,20 19,20;2,24 23,24;17,21 20,23')
    g['曩']=_fit(box,5,0,14,5)+_p('6,2.5 18,2.5;12,6 13,7;2,8 22,8')+_fit(box,2,9,8,4)+_fit(box,14,9,8,4)+_p('1,14 23,14;1,16.5 23,16.5;7,13.5 7,19;17,13.5 17,19;2,19 22,19;11,20 6,22 1,23;7,21.5 7,24 13,23;12,20 17,22 23,24;22,20 17,22')
    return deepcopy(g)

def apply(glyphs):
    changed=set()
    for c,p in correction_paths().items():
        if c not in glyphs:continue
        old=glyphs[c]
        glyphs[c]=replace(old,paths=p,source='original:family.proofread_middle_recheck_corrections',status='structure-reviewed-large-size',notes={**old.notes,'previous_source':old.notes.get('previous_source',old.source),'previous_status':old.notes.get('previous_status',old.status),'proofread_middle_recheck_correction':CORRECTION_NOTES[c]})
        changed.add(c)
    return changed
