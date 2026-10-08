"""38 target-only structural repairs after the 794-glyph 160px recheck.

The review's 88 unresolved glyphs are NOT silently changed. No legacy/component
source is edited, and no external font contours are used. Reused coordinates
are project-authored; local layouts reserve explicit non-overlapping regions.
"""
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
from .kanji import build_kanji,fit,strokes
from .proofread_upper_corrections import correction_paths as upper_paths,snug

TARGETS=frozenset('翹聽艫蘼趯躙躪釄鑪靡顱飇飈飋馗鬜鬭鬱鱸鷹鸕鼯鼷鼹虜勉𠠺𠥼𢌞𣆶𤄃𤭖𤭯𧄍𨴐𨵱𨷻𪎌')


@lru_cache(maxsize=1)
def correction_paths():
    needs=set('木缶髟酉金頁魚鳥舟林非亻隹耳壬𢛳艹羽翟門月屋先䜌活猋焱瑟首斲鼠吾奚晏力日元免囘镸泉麦来毌')
    C,_=build_kanji(needs|{'鬱'});U,_=upper_paths();out={};notes={}
    def put(c,p,n):out[c]=p;notes[c]=n
    def lr(left,right,width=10):return fit(left,0,0,width,24)+fit(right,width+1,0,23-width,24)
    def gate(inner):return deepcopy(C['門'])+snug(inner,6,11,12,11)
    shelter=strokes('11,1 13,3;23,4 3,4 3,17 1,24')
    mi=shelter+snug(C['林'],6,6,17,7)+snug(C['非'],6,15,17,9)
    put('靡',mi,'Separate 林 above 非 below 广; remove their former full-height overlap.')
    put('蘼',fit(C['艹'],0,0,24,4)+fit(mi,0,5,24,19),'Apply the verified 靡 separation locally below 艹.')
    put('釄',lr(C['酉'],mi,10),'Separate the right 靡 contents without changing the left 酉.')
    # 虍's short inner curl belongs above the separate lower content.
    tiger=strokes('11,1 11,5;11,3 22,3;24,6 4,6 4,16 1,24;8,9 21,7;11,7 11,10 15,11 21,11 23,9')
    lu=tiger+strokes('8,13 21,13 21,18 8,18 8,13;14.5,13 14.5,18;8,15.5 21,15.5;7,23 7,20 22,20 22,23;12,20 12,23;17,20 17,23;6,24 24,24')
    for c,left in [('艫','舟'),('鑪','金'),('鱸','魚')]:put(c,lr(C[left],lu,10),'Right 盧: keep 虍 inner curl above the separate 田 and 皿.')
    for c,right in [('顱','頁'),('鸕','鳥')]:put(c,lr(lu,C[right],11),'Left 盧: keep 虍 inner curl above the separate 田 and 皿.')
    put('虜',deepcopy(tiger)+snug(C['毌'],7,13,14,5)+snug(C['力'],7,19,16,5),'Preserve U+F936 毌 identity; place 毌 and 力 below the short 虍 curl.')
    for c,inner in [('飇','猋'),('飈','焱'),('飋','瑟')]:put(c,deepcopy(U['颫'][:6])+snug(C[inner],13,2,10,17),'Narrow left 風 and separate upper-right component, above its sweeping foot.')
    put('趯',deepcopy(U['赳'][:7])+snug(C['翟'],13,1,10,19),'Compact upper-left 走; independent right 翟 above its bottom sweep.')
    put('鬭',deepcopy(U['鬧'][:10])+snug(C['斲'],4,10,16,13),'Stop the two 鬥 crown halves at y=8; start the interior 斲 below them.')
    put('聽',snug(C['耳'],0,1,10,13)+snug(C['壬'],1,16,9,8)+snug(C['𢛳'],12,1,12,23),'Ear is above 壬 at left; preserve separate right 𢛳.')
    qiao=strokes('1,2 11,2;6,0 6,4;1,4 11,4;1,7 5,7;3,5 3,10;0,10 5,10;7,7 11,7;9,5 9,10;6,10 11,10;1,13 11,13;4,15 4,20 1,24;8,15 8,21 12,24 23,24 24,21')+snug(C['羽'],13,1,10,19)
    put('翹',qiao,'Three compact 土 at left and separate right 羽; only the intended lower leg extends beneath 羽.')
    put('𧄍',fit(C['艹'],0,0,24,4)+fit(qiao,0,5,24,19),'Apply the verified 翹 separation locally below 艹.')
    put('鬱',snug(C['木'],0,0,7,8)+snug(C['缶'],8,0,8,9)+snug(C['木'],17,0,7,8)+deepcopy(C['鬱'][13:]),'Three disjoint top regions for 木/缶/木; retain the existing lower 冖,鬯,彡.')
    put('鷹',shelter+snug(C['亻'],5,6,4,7)+snug(C['隹'],11,6,12,7)+snug(C['鳥'],6,15,18,9),'Separate 亻隹 upper compartment and 鳥 lower compartment under 广.')
    for c,inner in [('𨴐','先'),('𨵱','屋'),('𨷻','䜌')]:put(c,gate(C[inner]),'Interior begins below the two top boxes of 門 rather than touching/crossing them.')
    foot,_=build_kanji({'𧾷'})
    put('躙',lr(foot['𧾷'],gate(C['隹']),10),'Place 隹 below the two top boxes of right 門.')
    put('躪',lr(foot['𧾷'],fit(C['艹'],0,0,24,4)+fit(gate(C['隹']),0,5,24,19),10),'Keep 艹 above the right gate and 隹 below both gate boxes.')
    put('鬜',snug(C['髟'],0,0,24,8)+fit(gate(C['月']),0,10,24,14),'U+9B1C is 髟 above 閒: separate 月 from the gate boxes in the lower compartment.')
    water,_=build_kanji({'氵'})
    put('𤄃',lr(water['氵'],gate(C['活']),6),'The right 闊 interior 活 starts below the gate boxes; preserve the outer 氵.')
    mouse=snug(C['鼠'],1,1,10,22)
    mouse[-1]=[(8,11),(8.5,18),(11,23),(23,23),(24,20)]
    for c,inner in [('鼯','吾'),('鼷','奚'),('鼹','晏')]:put(c,deepcopy(mouse)+snug(C[inner],13,1,10,19),'Compact left 鼠 with right component above the long terminal tail; no overlap with 臼 or lower verticals.')
    nine=strokes('1,8 8,8 8,20 12,23 23,23 24,20;5,1 5,12 3,20 1,24')
    put('馗',nine+snug(C['首'],11,1,12,18),'Narrow 九 at left, with 首 above its extended foot at right.')
    rabbit=strokes('5,1 1,6;4,3 10,3 7,7;2,8 11,8 11,14 2,14 2,8;7,7 6,15 4,21 1,24;9,14 9,21 12,24 23,24 24,20')
    for c,inner in [('勉','力'),('𣆶','日')]:put(c,deepcopy(rabbit)+snug(C[inner],13,1,10,18),'Compact left 免 and distinct upper-right component above its long lower leg.')
    yuan=strokes('2,3 10,3;1,8 11,8;4,8 4,18 1,24;8,8 8,21 12,24 23,24 24,20')
    put('𠠺',yuan+snug(C['力'],13,1,10,18),'U+2083A has 元, not 兀: retain both top horizontals and place 力 at right.')
    put('𠥼',strokes('1,7 11,7;6,2 6,15;2,21 23,17;17,1 17,24'),'U+2097C: independent left and right 十 verticals; lower right 十 has a rising horizontal.')
    walking=strokes('1,3 8,3 4,9 8,9 6,16 2,20;1,16 6,21 13,23 24,23')
    put('𢌞',walking+snug(C['囘'],10,1,13,18),'Keep 廴 turns left of 囘; only its final bottom sweep extends below the enclosure.')
    tile=strokes('1,2 11,2;5,2 3,21 8,19;5,8 10,8 9,19 13,23 23,23 24,20;5,12 8,16')
    for c,inner in [('𤭖','镸'),('𤭯','泉')]:put(c,deepcopy(tile)+snug(C[inner],13,1,10,18),'Compact left 瓦 and separate right component above the extended bottom foot.')
    barley=snug(C['麦'],1,1,10,23);barley[-1][-1]=(24,24)
    put('𪎌',barley+snug(C['来'],13,1,10,20),'Narrow the simplified 麦 at left; only its lower sweep spans below the right 来.')
    assert set(out)==TARGETS
    return out,notes


def apply_corrections(glyphs):
    paths,notes=correction_paths()
    for c in TARGETS & glyphs.keys():
        old=glyphs[c]
        glyphs[c]=replace(old,paths=deepcopy(paths[c]),source='original:family.proofread_recheck_corrections',status='structure-reviewed',
            notes={**old.notes,'proofread_correction':notes[c],'previous_source':old.notes.get('previous_source',old.source),'review_scope':'38 separately verified high-resolution recheck targets; low-size readability remains separate'})
    return glyphs
