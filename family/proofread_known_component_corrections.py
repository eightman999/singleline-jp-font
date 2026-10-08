"""Explicit J-source repairs for audited 難/龜 descendants only.

Coordinates are original project centerlines. No Unicode outline is imported,
no shared source component changes, and no recursive substitution is performed.
"""
from copy import deepcopy
from dataclasses import replace
from .kanji import build_kanji, fit, strokes

CORRECTED_CHARACTERS=tuple('難儺攤灘龜龝鬮蘒')
CORRECTION_NOTES={
 '蘒':'J4-7738: restore the six comb bars and continuous top mouths, preserving the compatibility glyph identity.',
 '難':'J0-4671: restore the second independent horizontal below 口; retain the modern open 艹 crown.',
 '儺':'J0-5135: restore 廿 lower edge and the second independent horizontal below 口 in 難.',
 '攤':'J0-5A3A: restore 廿 lower edge and the second independent horizontal below 口 in 難.',
 '灘':'J0-4667: restore 廿 lower edge and the second independent horizontal below 口 in 難.',
 '龜':'J0-737D: replace rectangular-grid substitution by upper/lower three-bar combs and a crossed compartment.',
 '龝':'J0-6354: preserve 禾 and restore the two three-bar combs and crossed compartment in 龜.',
 '鬮':'J0-722D: restore both three-bar combs and their two extended middle bars in the enclosed 龜.',
}


def turtle_paths():
    # Six comb levels: 11,13,15 and 17,19.5,22. The middle bars
    # continue to the top/bottom of the right crossed compartment.
    return strokes('11,0 7,4 1,7;8,2 17,2 13,6;3,6 22,6 22,10 14,10;3,6 3,10 9,10 9,6;14,6 14,21;1,11 7,11 7,15 1,15;0,13 22,13;1,17 7,17 7,22 1,22;0,19.5 22,19.5;22,13 22,19.5;16,14.5 20,18;20,14.5 16,18;11,6 11,22 13,24 21,24 24,21')


def correction_paths():
    C,_=build_kanji(set(CORRECTED_CHARACTERS)|set('禾亻扌氵'))
    g={}
    modern=deepcopy(C['難'])+strokes('0.5,16 11.5,16')
    traditional=deepcopy(modern)+strokes('3.5,7 8.5,7')
    g['難']=modern
    for c,radical in [('儺','亻'),('攤','扌'),('灘','氵')]:
        n={'儺':2,'攤':3,'灘':3}[c]
        g[c]=deepcopy(C[c][:n])+fit(traditional,9,0,15,24)
    g['龜']=turtle_paths()
    g['龝']=deepcopy(C['龝'][:5])+fit(turtle_paths(),11,0,13,24)
    g['鬮']=deepcopy(C['鬮'][:10])+fit(turtle_paths(),3.5,7.5,16.5,15.3)
    from .proofread_deep3_corrections import correction_paths as deep3_paths
    g['蘒']=deepcopy(deep3_paths()['蘒'][:8])+fit(turtle_paths(),11,6,13,18)
    return g


def apply(glyphs):
    changed=set()
    for c,p in correction_paths().items():
        if c not in glyphs:continue
        old=glyphs[c]
        glyphs[c]=replace(old,paths=p,source='original:family.proofread_known_component_corrections',status='structure-reviewed-large-size',notes={**old.notes,'previous_source':old.notes.get('previous_source',old.source),'previous_status':old.notes.get('previous_status',old.status),'proofread_known_component_correction':CORRECTION_NOTES[c]})
        changed.add(c)
    return changed
