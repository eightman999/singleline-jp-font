"""Restore three Japanese-source variant distinctions in the new family only.

Unicode 18 J-source references: 剥 J0-476D (p30), 填 J0-4536 (p69),
頬 J0-4B4B (p483). Centerlines are independently designed on the project grid.
Legacy assets and their counterpart glyphs are deliberately unmodified.
"""
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
from .kanji import build_kanji, strokes

TARGETS=frozenset('剥填頬')
PAIRS=(('剝','剥'),('塡','填'),('頰','頬'))

@lru_cache(maxsize=1)
def correction_paths():
    C,_=build_kanji(TARGETS)
    P={};N={}
    P['剥']=strokes('2.7,1.5 14,1.5 14,10.5;2.7,6 14,6;0.67,10.5 15.33,10.5')+deepcopy(C['剥'][3:])
    N['剥']='Restore 彐 above 水 (J0-476D), distinct from the bent 彑 of 剝 (J3A-2F7E); preserve 水 and 刂 paths.'
    P['填']=deepcopy(C['填'][:3])+strokes('10,3 23,3;16.5,0.5 16.5,7;11.5,7 22,7 22,18 11.5,18 11.5,7;11.5,10.7 22,10.7;11.5,14.3 22,14.3;9,18 24,18;14,20 10,23.5;20,20 23.5,23.5')
    N['填']='Restore 真: 十 above the upright eye and its full-width lower baseline (J0-4536), distinct from 匕/offset frame in 塡 (J13-2F58).'
    P['頬']=strokes('0.5,4.5 10.5,4.5;5.5,0.5 5.5,12 4,18 0.5,23;5.5,13 8,19 10.5,23;1.5,7 3.3,10.5;9.5,7 7.7,10.5;0.5,13 10.5,13')+deepcopy(C['頬'][7:])
    N['頬']='Restore 夹: paired upper dots and a second crossing horizontal (J0-4B4B), distinct from the two inner 人 of 頰 (J13-7D7A); preserve 頁.'
    return P,N

def apply_corrections(glyphs):
    P,N=correction_paths()
    for c in TARGETS & glyphs.keys():
        g=glyphs[c]
        glyphs[c]=replace(g,paths=deepcopy(P[c]),source='original:family.proofread_variant_pair_corrections',status='structure-reviewed',notes={**g.notes,'proofread_correction':N[c],'previous_source':g.notes.get('previous_source',g.source),'review_scope':'Japanese-source variant distinction; three named targets only'})
    return glyphs
