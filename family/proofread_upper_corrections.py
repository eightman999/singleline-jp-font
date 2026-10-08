"""Family-only repairs for 37 high-codepoint kanji with confirmed overlap defects.

Self-authored layout/centerlines, reusing project geometry only. Noto CJK JP
was viewed at 200/160 px for structure, never imported or traced. Deliberately
local: no legacy source, shared component or other character is modified.
"""
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
from .kanji import build_kanji, fit, strokes

WIND = dict(zip('颫颰颱颶颷颸颺颼飂飃','夫犮台具炎思昜叟翏票'))
FIGHT = dict(zip('鬧鬨鬩鬪鬫',['巿','共','兒','𭔰','敢']))
GHOST = dict(zip('魁魋魍','斗隹罔'))
WHEAT = dict(zip('麨麩麪麭麯麴麵','少夫丏包曲匊面'))
WALK = dict(zip('赳趁趄趨',['丩','㐱','且','芻']))
TARGETS = frozenset('舞賡贋閘閴魘麾齎') | WIND.keys() | FIGHT.keys() | GHOST.keys() | WHEAT.keys() | WALK.keys()


def snug(paths, x, y, width, height):
    """Fit authored component ink bounds into an explicitly reserved region."""
    xs=[a for p in paths for a,b in p];ys=[b for p in paths for a,b in p]
    lo,hi=min(xs),max(xs);top,bottom=min(ys),max(ys)
    return [[(x+(a-lo)*width/(hi-lo or 1),y+(b-top)*height/(bottom-top or 1)) for a,b in p] for p in paths]


@lru_cache(maxsize=1)
def correction_paths():
    needs=set('麥門貝甲舛亻隹猒鬼毛市齊林') | set(WIND.values()) | set(FIGHT.values()) | set(GHOST.values()) | set(WHEAT.values()) | set(WALK.values())
    C,_=build_kanji(needs)
    out={};notes={}
    def put(c,paths,note):out[c]=paths;notes[c]=note
    wind=strokes('1,24 3,17 3,2 11,2 11,17 14,23 23,23 24,20;4,7 9,5;7,6 7,21;4,10 10,10 10,16 4,16 4,10;3,22 10,20;9,18 11,22')
    for c,inner in WIND.items():
        put(c,deepcopy(wind)+snug(C[inner],13,2,10,17),
            'Wind is narrow at left; the added component occupies a separate upper-right region above the sweeping foot.')
    fight=strokes('1,1 1,24;1,2 9,2;1,5 9,5;1,8 9,8;5,1 5,8;23,1 23,24 20,24;15,2 23,2;15,5 23,5;15,8 23,8;19,1 19,8')
    for c,inner in FIGHT.items():
        put(c,deepcopy(fight)+snug(C[inner],4,10,16,13),
            'The two comb-like crown halves of 鬥 stop at y=8; its interior begins at y=10 and stays inside the outer verticals.')
    ghost=strokes('8,1 6,4;3,4 11,4 11,12 3,12 3,4;3,8 11,8;7,4 7,12;6,12 6,18 3,22 1,24;9,12 9,21 12,23 21,23 24,21;11,14 10,18 13,18;12,16 14,20')
    for c,inner in GHOST.items():
        put(c,deepcopy(ghost)+snug(C[inner],14,2,9,17),
            'Compact left 鬼 head and legs; the right component stays above its sweeping lower leg, outside the head and curl.')
    wheat=strokes('1,5 23,5;12,1 12,14;6,6 4,10 1,12;5,9 9,12;18,6 16,10 14,12;17,9 23,13;12,8 7,13 1,15;12,8 17,13 23,15;9,15 5,18 1,20;7,17 21,17 16,21 7,24 1,24;6,19 13,22 24,24')
    wheat_left=snug(wheat,1,1,10,23)
    # Only the final descending sweep reaches beneath the right component.
    wheat_left[-1][-1]=(24,24)
    for c,inner in WHEAT.items():
        put(c,deepcopy(wheat_left)+snug(C[inner],13,2,10,20),
            '麥 occupies the left region rather than the full cell; the right component no longer crosses 來 or 夂.')
    walk=strokes('2,5 10,5;6,1 6,11;1,11 11,11;6,11 6,20;6,16 10,16;3,15 3,20 1,24;3,20 10,23 24,23')
    for c,inner in WALK.items():
        put(c,deepcopy(walk)+snug(C[inner],13,1,10,19),
            '走 has a compact upper-left 土 and a lower sweeping foot; the right component has its own upper-right region.')
    for c,inner in [('閘','甲'),('閴','貝')]:
        put(c,deepcopy(C['門'])+snug(C[inner],6,11,12,11),
            'The interior begins below both closed top boxes of 門, separated by a 2-unit gap.')
    crown=strokes('6,1 2,5;4,4 23,4;1,8 23,8;1,12 23,12;5,4 5,12;10,4 10,12;15,4 15,12;20,4 20,12')
    put('舞',crown+snug(C['舛'],1,14,22,10),
        'Four continuous crown verticals connect all three horizontals; 舛 is below the completed crown.')
    shelter=strokes('11,1 13,3;23,4 3,4 3,17 1,24')
    geng=strokes('7,6 21,6 21,10 7,10;5,8 23,8;14,5 14,10 10,13 5,14;14,10 18,13 23,14')
    put('賡',shelter+geng+snug(C['貝'],7,15,14,9),
        '庚 is in the upper shelter compartment; 貝 occupies a separate lower compartment.')
    cliff=strokes('23,2 3,2 3,16 1,24')
    put('贋',cliff+snug(C['亻'],5,4,4,9)+snug(C['隹'],11,4,12,9)+snug(C['貝'],7,15,14,9),
        '亻 and 隹 share the upper compartment below 厂; 貝 is entirely below them.')
    full_ghost=strokes('13,1 10,4;4,4 20,4 20,13 4,13 4,4;4,8 20,8;12,4 12,13;9,13 8,19 4,23 1,24;15,13 15,21 18,24 23,24 24,20;18,14 16,19 22,18;20,16 23,21')
    put('魘',cliff+snug(C['猒'],6,4,17,8)+snug(full_ghost,5,14,19,10),
        '厭 upper contents and the lower 鬼 are stacked beneath 厂 rather than drawn over each other.')
    put('麾',shelter+snug(C['林'],6,6,17,7)+snug(C['毛'],6,15,18,9),
        '林 is below 广 and above 毛; the branches no longer intersect the lower horizontals.')
    # The first nine project-authored 齊 paths are its crown, not the bottom
    # two horizontal rules. Replace that bottom area with the actual 貝.
    qi_crown=snug(C['齊'][:9],2,1,20,9)
    put('齎',qi_crown+strokes('4,12 4,20 2,24;22,12 22,24')+snug(C['貝'],7,12,12,12),
        'The 齊 crown is complete above a distinct 貝, flanked by lower outer verticals; no crown strokes cross its box.')
    assert set(out)==TARGETS
    return out,notes


def apply_corrections(glyphs):
    paths,notes=correction_paths()
    for c in TARGETS & glyphs.keys():
        old=glyphs[c]
        glyphs[c]=replace(old,paths=deepcopy(paths[c]),
            source='original:family.proofread_upper_corrections',status='structure-reviewed',
            notes={**old.notes,'proofread_correction':notes[c],
                   'previous_source':old.notes.get('previous_source',old.source),
                   'review_scope':'37 target-only structural repairs; not whole-repertoire certification'})
    return glyphs
