"""Thirteen bounded repairs supported by Unicode 18 Japanese-source images.

Reference glyphs establish component identities/topology only. All coordinates
are original project centerlines; no external outline is traced or extracted.
Historical components and legacy dictionaries remain immutable.
"""
from copy import deepcopy
from dataclasses import replace
from .proofread_middle_corrections import _p, _fit

CORRECTED_CHARACTERS=tuple('鱜鱥黌鼇鼈齏蘒𠠇𡑮𡿺𢦏𥧔𦥯')
CORRECTION_NOTES={
 '鱜':'J14-7D6C requires 鄕 with 白 over 匕, not the 艮-like crossing lower body inherited from 鄉[G].',
 '鱥':'J3-7E56 puts the 歲 inner crossbar above the point/sweep region; remove the old point/crossbar collisions.',
 '黌':'J0-7354: keep 爻 above 冖 and preserve independent 黃 interior counters.',
 '鼇':'J0-7367: the lower 黽 boxes must not receive extra central vertical partitions.',
 '鼈':'J0-7368: the lower 黽 boxes must not receive extra central vertical partitions.',
 '齏':'J0-706D: place 韭 in the lower 齊 interior, not superimposed on the crown.',
 '蘒':'J4-7738: keep the traditional 龜 comb and crossed compartment; do not substitute a 亀-like rectangular grid.',
 '𠠇':'J4-233F: retain the upper-left inner point and the upper-right 刀 falling stroke, above 亞 and beside 刂.',
 '𡑮':'J3-2F60: separate the 塞 crown bars, uprights, 八 and 土; the old crown bars were only 0.55 grid apart.',
 '𡿺':'J4-286C: keep the 囟 cross wholly inside its enclosure below 巛.',
 '𢦏':'J4-2C72: place 十 at the upper left of 戈 instead of duplicating its central stem/crossbar.',
 '𥧔':'J4-7332: reserve the 气 enclosure and a separate 米 interior below 穴.',
 '𦥯':'J4-755D: both 爻 crosses belong above 冖, between the opposed side parts.',
}

# Retained project-owned crown strokes, from the reviewed pre-repair source.
# These constants are not reference-font data.
_AO_CROWN = [[[1.375, 1.890625], [9.625, 1.890625]], [[5.5, 0.21006944444444442], [5.5, 4.621527777777778]], [[0.4583333333333333, 4.621527777777778], [10.541666666666666, 4.621527777777778]], [[5.041666666666667, 5.729166666666667], [6.416666666666667, 6.416666666666667]], [[0.4583333333333333, 6.875], [10.541666666666666, 6.875]], [[4.583333333333333, 6.875], [4.125, 8.9375], [2.2916666666666665, 10.3125], [0.4583333333333333, 11.0]], [[4.583333333333333, 8.020833333333334], [9.625, 8.020833333333334], [8.708333333333334, 10.770833333333334], [6.416666666666667, 10.770833333333334]], [[16.5, 0.4583333333333333], [14.5, 4.125], [12.5, 5.958333333333333]], [[15.0, 3.2083333333333335], [23.5, 3.2083333333333335]], [[21.5, 3.2083333333333335], [20.0, 6.875], [17.0, 9.625], [13.5, 11.0]], [[15.0, 5.041666666666667], [18.0, 7.791666666666667], [23.0, 11.0]]]
_BIE_CROWN = [[[1.375, 0.4583333333333333], [3.2083333333333335, 2.2916666666666665]], [[9.625, 0.4583333333333333], [7.791666666666667, 2.2916666666666665]], [[1.375, 10.541666666666666], [1.375, 3.2083333333333335], [9.625, 3.2083333333333335], [9.625, 10.541666666666666], [8.25, 10.541666666666666]], [[5.5, 0.4583333333333333], [5.5, 11.0]], [[3.6666666666666665, 5.041666666666667], [2.2916666666666665, 9.166666666666666]], [[7.333333333333333, 5.041666666666667], [8.708333333333334, 9.166666666666666]], [[16.5, 0.4583333333333333], [14.5, 4.125], [12.5, 5.958333333333333]], [[15.0, 3.2083333333333335], [23.5, 3.2083333333333335]], [[21.5, 3.2083333333333335], [20.0, 6.875], [17.0, 9.625], [13.5, 11.0]], [[15.0, 5.041666666666667], [18.0, 7.791666666666667], [23.0, 11.0]]]

_FISH=_p('8,1 3,7;6,3 19,3 15,7;4,7 20,7 20,17 4,17 4,7;12,7 12,17;4,12 20,12;3,20 1,24;8,20 9,24;14,20 16,24;20,20 23,24')
_GRASS=_p('1,3 23,3;7,0 7,6;17,0 17,6')
_GRAIN=_p('21,1 3,5;12,3 12,24;1,10 23,10;12,10 7,18 1,23;12,10 18,18 24,23')


def _learning_crown():
    return _p('7,0 1,2 1,16;1,7 6,7;1,12 6,12;18,1 23,1 23,16;18,7 23,7;18,12 23,12;8,2 16,8;16,2 8,8;8,10 16,16;16,10 8,16;0,24 0,19 24,19 24,24')


def _turtle():
    # The Japanese traditional 龜 topology, distinct from modern 亀.
    return _p('11,0 7,4 1,7;8,2 17,2 13,6;3,6 9,6 9,10 4,10;3,6 3,8 7,8;14,6 22,6 22,10 14,10;14,6 14,21;7,12 7,23;0,13 7,13;0,16 7,16;0,19 7,19;0,22 7,22;14,12 22,12 22,20 14,20;16,14 20,18;20,14 16,18;11,6 11,22 13,24 21,24 24,21;7,17 11,17')


def correction_paths():
    g={}
    fish=_fit(_FISH,0,0,10.5,24)
    # 鄕: left 幺-family member, middle 白+匕, right 阝.
    xiang=_p('14,1 11.7,7 14.7,7;15.2,4 12.4,15 15.1,13;15.3,11 14.7,19 12,24;18.7,1 17.2,3;16.6,3 20,3 20,12 16.6,12 16.6,3;16.6,7.5 20,7.5;17,15 17,22 18,23 20.5,22;20.5,15 17,18;21.5,24 21.5,1 24,1 22.7,8 24,14 24,18 23.4,20 22.3,18')
    g['鱜']=fish+xiang
    sui=_p('11,0 11,7;11,3 22,3;3,3 3,7;0,7 24,7;0,24 2,18 2,10 23,10;16,8 17,17 21,23 24,24 24,20;23,13 19,19 14,24;20,8 23,9;4,14 13,14;9,14 9,20;5,17 4,21;12,17 14,19;14,20 10,23 6,24')
    g['鱥']=fish+_fit(sui,12,0,12,24)
    g['𦥯']=_learning_crown()
    huang=_p('1,13.5 23,13.5;7,12 7,16 17,16 17,12;1,17.5 23,17.5;4,18.5 20,18.5 20,21.5 4,21.5 4,18.5;4,20 20,20;12,18.5 12,21.5;7,22.5 2,24;17,22.5 23,24')
    g['黌']=_fit(_learning_crown(),0,0,24,11)+huang
    # Remove the spurious extra column within each lower 黽 compartment.
    mian=_p('5,1 19,1 19,7 5,7 5,1;5,4 19,4;2,8 10,8 10,16 2,16 2,8;2,12 10,12;14,8 22,8 22,16 14,16 14,8;14,12 22,12;10,7 10,23 3,23;14,7 14,22 18,24 23,24 24,20;10,20 14,20')
    g['鼇']=deepcopy(_AO_CROWN)+_fit(mian,0,12,24,12)
    g['鼈']=deepcopy(_BIE_CROWN)+_fit(mian,0,12,24,12)
    qi=_p('11,0 13,2;1,3 23,3;2,5 8,5 7,10 5,11;5,5 4,9 0,12;10,5 12,8;14,5 12,8 12,12;19,5 17,7 15,8;16,5 19,9 23,11;21,5 21,12;4,14 4,21 2,24;22,14 22,24;4,14 22,14')
    jiu=_p('9,16 9,23;16,16 16,23;6,17 9,17;6,19.5 9,19.5;6,22 9,22;16,17 20,17;16,19.5 20,19.5;16,22 20,22;6,24 20,24')
    g['齏']=qi+jiu
    g['蘒']=_fit(_GRASS,0,0,24,12)+_fit(_GRAIN,0,6,9,18)+_fit(_turtle(),11,6,13,18)
    ya=_p('0,13 16,13;5,13 5,16 1,16 1,20 5,20 5,23;11,13 11,16 15,16 15,20 11,20 11,23;0,23 16,23')
    g['𠠇']=_p('6,0 1,2 1,9;0,10 6,7;4,4 5.5,7;7,1 15,1 14,9 12,9;10,1 9,6 6,11;19,3 19,18;23,1 23,23 21,24')+ya
    sai=_p('11,0 13,2;1,5 1,3 23,3 23,5;2,7 22,7;2,10 22,10;2,13 22,13;7,5 7,13;17,5 17,13;8,13 5,16 1,18;16,13 19,16 23,18;6,20 18,20;12,17 12,24;3,24 21,24')
    g['𡑮']=_p('1,9 7,9;4,1 4,23;0,23 8,23')+_fit(sai,10,0,14,24)
    chuan=_p('6,0 1,4 6,8;14,0 9,4 14,8;23,0 18,4 23,8')
    g['𡿺']=chuan+_p('12,9 9,12;3,12 21,12 21,24 3,24 3,12;7,15 17,21;17,15 7,21')
    g['𢦏']=_p('2,5 13,5;8,1 8,11;0,11 24,11;17,0 18,13 21,22 24,24 24,19;23,15 17,21 10,24;21,2 24,5')
    hole=_p('11,0 13,1;1,4 1,2 23,2 23,4;8,4 5,6 1,7;16,4 19,6 23,7')
    air=_p('6,8 2,11;5,10 23,10;4,12.5 22,12.5;3,15 20,15 20,22 23,24 24,21')
    rice=_p('10,16 10,24;4,16.5 6,18.5;16,16.5 14,18.5;3,20 17,20;10,20 6,23 3,24;10,20 14,23 17,24')
    g['𥧔']=hole+air+rice
    return deepcopy(g)


def apply(glyphs):
    changed=set()
    for c,p in correction_paths().items():
        if c not in glyphs:continue
        old=glyphs[c]
        glyphs[c]=replace(old,paths=p,source='original:family.proofread_deep3_corrections',status='structure-reviewed-large-size',notes={**old.notes,'previous_source':old.notes.get('previous_source',old.source),'previous_status':old.notes.get('previous_status',old.status),'proofread_deep3_correction':CORRECTION_NOTES[c]})
        changed.add(c)
    return changed
