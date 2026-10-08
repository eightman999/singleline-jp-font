"""Deep group-1 exact-key centreline repairs; no shared glyph mutation.

Every part below is independently authored on the 24-unit project grid.
Unicode J-source and Noto JP are identity/topology references only; no font
outlines, bitmap coordinates, skeletons or traced contours are used.
"""
from dataclasses import replace


def _p(s):
    return [[tuple(map(float,q.split(','))) for q in line.split()]
            for line in s.split(';') if line.strip()]


def _fit(p,x,y,w,h):
    return [[(x+a*w/24,y+b*h/24) for a,b in line] for line in p]


def _part(name,p,box=None):
    return (name,_fit(p,*box) if box else [[tuple(q) for q in line] for line in p])


_MOUTH=_p('2,2 22,2 22,22 2,22 2,2')
_DAY=_MOUTH+_p('2,12 22,12')
_EYE=_MOUTH+_p('2,8.5 22,8.5;2,15.5 22,15.5')
_MOUNTAIN=_p('12,0 12,24;1,7 1,24 23,24 23,7')
_PERSON=_p('16,0 10,8 1,16;10,8 10,24')
_HAND=_p('1,7 23,7;13,0 13,23 8,24;1,16 23,11')
_WOOD=_p('0,7 24,7;12,0 12,24;12,7 7,16 0,23;12,7 17,16 24,23')
_WIDE_ROOF=_p('10,0 14,2;24,4 3,4 3,16 0,24')
_TWO_HAND_CROWN=_p('7,0 1,2 1,8;1,4 6,4;1,7 6,7;'
                   '18,1 24,1 24,8;18,4 24,4;18,7 24,7;'
                   '9,1 16,4;16,1 9,4;9,5 16,8;16,5 9,8')
_STOP=_p('12,0 12,21;12,9 23,9;3,7 3,21;0,22 24,22')
_EIGHT=_p('8,0 6,12 0,24;16,0 18,12 24,24')
_WINTER_TOP=_p('9,0 4,6 1,8;7,4 22,4 17,13 10,20 1,24;'
               '5,8 12,16 24,24')
_GHOST=_p('10,0 7,3;3,4 21,4 21,13 3,13 3,4;3,8.5 21,8.5;12,4 12,13;'
          '8,13 8,18 4,22 0,24;14,13 14,21 17,24 22,24 24,21;'
          '19,15 16,20 22,19;20,17 23,21')
_TURTLE=_p('11,0 6,4;8,2 20,2 16,6;4,6 20,6 20,13 4,13 4,6;4,9.5 20,9.5;'
           '2,14 22,14 22,21 2,21 2,14;2,17.5 22,17.5;12,6 12,23 21,23 24,21')
_CLAMP=_p('0,6 24,6;12,0 12,10 8,18 1,24;12,10 17,18 24,24;'
          '6,8 5,12 3,15;6,10 8,14;18,8 17,12 15,15;18,10 21,15')
_RIDE=_p('21,0 3,4;1,6 23,6;12,2 12,24;12,13 6,20 0,24;12,13 18,20 24,24;'
         '8,6 8,16;1,9 8,9;1,16 8,13;16,6 16,14 19,16 23,16 24,13;23,8 16,11')
_WITCH=_p('1,1 23,1;12,1 12,24;0,24 24,24;'
          '6,6 5,12 2,19;6,10 10,19;18,6 17,12 14,19;18,10 22,19')
_FEATHER_GRASS=_p('4,0 8,3;20,0 16,3;2,4 22,4;3,8 21,8;0,12 24,12;12,4 12,12')
#韱: top two 人, lower 韭, right 戈; domains are intentionally distinct.
_SPEAR_LEEK=_p('6,0 5,3 2,6;6,2 9,6;14,0 13,3 10,6;14,2 17,6;'
               '7,8 7,21;13,8 13,21;2,11 7,11;2,15 7,15;2,19 7,19;'
               '13,11 18,11;13,15 18,15;13,19 18,19;1,23 18,23;'
               '1,7 23,7;19,0 19,10 21,20 23,24 24,20;24,12 20,19 16,24;21,1 24,4')
_WOMAN=_p('11,0 5,14 13,18 24,24;0,8 24,8;19,8 16,17 9,22 0,24')
_HAIR=_p('21,0 3,4;2,10 22,7;1,16 24,13;12,2 12,21 16,24 22,24 24,21')
_KNIFE=_p('8,4 8,18;21,0 21,23 15,24')
_AXE=_p('23,0 4,6 4,17 0,24;4,12 24,12;15,12 15,24')

# Full lower 蜀 is given 13 of 24 units; no sub-box is <2 grid units tall.
_BELONG=_p('2,0 23,0 23,5 2,5;2,0 2,17 0,24;'
           '14,5 14,10;7,6 10,7;21,6 18,7;10,8 7,10;18,8 22,10;'
           '6,11 23,11 23,14 6,14 6,11;11,11 11,14;17,11 17,14;'
           '9,15 5,18;8,16 23,16 22,23 19,24;'
           '7,18 17,18 17,21 7,21 7,18;12,17 12,23;5,24 18,23;17,21 19,24')


def correction_spec():
    """Return semantic groups covering every replacement path exactly once."""
    s={}
    for c,left,box in [('㟴',_MOUNTAIN,(0,0,8,24)),('傀',_PERSON,(0,0,7,24))]:
        s[c]=[_part('left radical',left,box),_part('鬼: head / legs / separate 厶',_GHOST,(9 if c=='㟴' else 8,0,15 if c=='㟴' else 16,24))]
    s['嵬']=[_part('山 crown',_MOUNTAIN,(2,0,20,6)),_part('鬼 below 山',_GHOST,(0,7,24,17))]
    s['廆']=[_part('广 shelter',_WIDE_ROOF),_part('鬼 within 广',_GHOST,(6,6,18,18))]
    s['䀹']=[_part('目',_EYE,(0,1,8,23)),_part('夾: separated inner 人',_CLAMP,(9,0,15,24))]
    s['䆴']=[_part('穴 crown',_p('11,0 13,1;1,5 1,2 23,2 23,5;8,4 6,6 1,8;16,4 19,7 23,8')),_part('亀',_TURTLE,(1,8,22,16))]
    s['乘']=[_part('禾/北 with bounded 北 stems',_RIDE)]
    s['嵊']=[_part('山',_MOUNTAIN,(0,0,7,24)),_part('乘',_RIDE,(8,0,16,24))]
    s['像']=[_part('亻',_PERSON,(0,0,7,24)),_part('象 crown and head',_p('15,0 10,5;12,3 21,3 18,7;10,7 23,7 23,12 10,12 10,7;17,7 17,12')),_part('象 lower three left sweeps, hooked trunk, right limbs',_p('15,12 12,15 8,17;16,15 13,18 8,21;17,18 13,22 8,24;'
                 '15,13 18,17 18,22 16,24 14,23;23,13 20,17;19,16 21,21 24,24'))]
    s['亂']=[_part('爫',_p('2,1 15,0;3,2 5,4;8,2 9,4;14,1 12,4')),_part('龴',_p('2,6 15,6 8,9;4,7 11,10')),_part('冂 containing 厶 and 又',_p('2,24 2,11 16,11 16,24 14,24;10,12 5,15 13,15;11,13 14,16;'
                 '4,17 14,17 10,21 4,24;5,19 9,22 14,24')),_part('乚',_p('20,0 20,21 22,24 24,22'))]
    s['亹']=[_part('亠',_p('11,0 13,1;1,2 23,2')),_part('臼 sides',_p('7,3 2,4 2,12;2,7 6,7;2,10 6,10;18,4 23,4 23,12;18,7 23,7;18,10 23,10')),_part('同 centre',_p('8,12 8,4 16,4 16,12;9,6 15,6;10,8 14,8 14,11 10,11 10,8')),_part('冖',_p('1,15 1,13 24,13 24,15')),_part('且',_p('5,24 5,16 20,16 20,24;5,19 20,19;5,22 20,22;1,24 24,24'))]
    hemp=_p('11,0 14,2;24,3 3,3 3,17 0,24')+_fit(_WOOD,5,4,8,8)+_fit(_WOOD,15,4,8,8)
    non=_p('10,14 10,24;17,14 17,24;5,16 10,16;5,19 10,19;5,22 10,22;17,16 23,16;17,19 23,19;17,22 23,22')
    s['劘']=[_part('麻',hemp,(0,0,19,24)),_part('非 below 林',non,(0,0,19,24)),_part('刂',_KNIFE,(20,0,4,24))]
    s['嚢']=[_part('一中',_p('1,2 23,2;4,1 20,1 20,4 4,4 4,1;12,0 12,4')),_part('冖 and 八',_p('1,7 1,5 23,5 23,7;8,8 5,10 1,11;16,8 20,10 24,11')),_part('𠀎',_p('2,12 22,12;2,14 22,14;1,16 23,16;7,11 7,16;17,11 17,16')),_part('衣 lower limbs',_p('12,17 6,20 0,21;6,19 6,24 13,22;12,18 18,22 24,24;23,18 17,21'))]
    s['屬']=[_part('尸 / water cluster / 蜀',_BELONG)]
    s['囑']=[_part('口',_MOUTH,(0,4,7,18)),_part('屬',_BELONG,(8,0,16,24))]
    s['斸']=[_part('屬',_BELONG,(0,0,17,24)),_part('斤',_AXE,(18,0,6,24))]
    s['埀']=[_part('crown and central vertical',_p('21,0 3,4;1,6 23,6;12,3 12,24;1,20 23,20;2,24 22,24')),_part('bounded 北 side members',_p('8,6 8,17;1,10 8,10;1,17 8,14;16,6 16,15 19,17 23,17 24,14;23,9 16,12'))]
    self_head=_p('13,0 9,3;3,3 21,3 21,23 3,23 3,3;3,10 21,10;3,17 21,17')
    s['夔']=[_part('丷 and top bar',_p('4,0 7,2;20,0 17,2;1,3 23,3')),_part('止 left',_STOP,(0,5,6,8)),_part('自 centre',self_head,(8,4,8,9)),_part('巳 right',_p('0,0 22,0 22,10 0,10;0,0 0,20 6,24 22,24 24,20'),(18,5,6,8)),_part('儿',_p('8,14 8,16 4,18 0,18;16,14 16,17 20,18 24,17')),_part('夂',_WINTER_TOP,(0,18,24,6))]
    hundred=_p('0,0 24,0;13,1 10,5;3,5 21,5 21,24 3,24 3,5;3,14 21,14')
    s['奭']=[_part('大 enclosing frame',_p('1,4 23,4;12,0 12,12 8,20 0,24;12,12 18,21 24,24')),_part('left 百',hundred,(1,6,8,10)),_part('right 百',hundred,(15,6,8,10))]
    s['孅']=[_part('女',_WOMAN,(0,0,6,24)),_part('韱',_SPEAR_LEEK,(7,0,17,24))]
    s['峯']=[_part('山',_MOUNTAIN,(1,0,22,6)),_part('夂',_WINTER_TOP,(0,7,24,7)),_part('丰',_p('2,16 22,16;2,19 22,19;0,22 24,22;12,15 12,24'))]
    s['椶']=[_part('木',_WOOD,(0,0,8,24)),_part('凶',_p('10,1 10,7 23,7 23,1;12,1 21,5;21,1 12,5')),_part('八',_EIGHT,(10,8,14,4)),_part('夂',_WINTER_TOP,(9,13,15,11))]
    black=_p('3,0 21,0 21,9 3,9 3,0;7,2 10,6;17,2 14,6;12,9 12,17;3,13 21,13;1,17 23,17;2,20 0,24;8,20 9,24;14,20 16,24;21,20 24,24')
    s['攩']=[_part('扌',_HAND,(0,0,7,24)),_part('尚 crown',_p('16,0 16,3;11,1 13,3;21,1 19,3;9,6 9,4 23,4 23,6;12,7 21,7 21,10 12,10 12,7')),_part('黑',black,(9,11,15,13))]
    s['攪']=[_part('扌',_HAND,(0,0,6,24)),_part('臼爻 upper',_TWO_HAND_CROWN,(7,0,17,24)),_part('冖',_p('7,12 7,9 24,9 24,12')),_part('見 lower',_p('10,13 22,13 22,20 10,20 10,13;10,15.3 22,15.3;10,17.7 22,17.7;13,20 12,22 8,24;19,20 19,23 22,24 24,22'))]
    rain=_p('0,0 24,0;2,24 2,5 22,5 22,24 19,24;12,0 12,24;5,9 9,12;5,17 9,20;15,9 19,12;15,17 19,20')
    s['欞']=[_part('木',_WOOD,(0,0,6,24)),_part('雨',rain,(7,0,17,7)),_part('three 口',_fit(_MOUTH,7,8,5,5)+_fit(_MOUTH,13,8,5,5)+_fit(_MOUTH,19,8,5,5)),_part('巫 with bounded 人',_WITCH,(7,14,17,10))]
    s['氂']=[_part('未',_p('2,2 10,2;0,5 11,5;6,0 6,10;6,5 2,9 0,10;6,5 9,9 11,10')),_part('攵',_p('17,0 14,4 12,5;15,3 24,3;22,3 20,7 15,10;15,5 19,8 24,10')),_part('厂',_p('24,12 3,12 3,20 0,24')),_part('毛 below roof',_HAIR,(6,14,18,10))]
    s['牽']=[_part('亠',_p('11,0 14,1;0,2 24,2')),_part('幺 above roof',_p('12,3 6,6 12,6;18,4 6,10 19,9;16,7 21,11')),_part('冖',_p('1,12 1,9 23,9 23,12')),_part('牛',_p('6,13 3,17;5,16 23,16;12,13 12,24;0,20 24,20'))]
    tiger=_p('11,0 11,4;11,2 22,2;24,5 3,5 3,18 0,24;8,7 21,6;11,5 11,9 16,10 22,10 24,8')
    cauldron=_p('5,11 24,11;8,13 21,13 21,16 8,16 8,13;5,24 5,18 24,18 24,24 22,24;10,18 8,20;19,18 21,20;8,22 21,22;14,22 14,24')
    dog=_p('0,7 24,7;12,0 11,12 6,20 0,24;12,8 17,18 24,24;18,1 23,4')
    s['獻']=[_part('虍 upper shelter',tiger,(0,0,14,24)),_part('鬲 below 虍',cauldron,(0,0,14,24)),_part('犬',dog,(15,0,9,24))]
    return s


CORRECTED_CHARACTERS=tuple(correction_spec())
CORRECTION_NOTES={
 '㟴':'Reserve a 9-unit 鬼 head and separate the lower 厶 from the sweeping leg beside 山.',
 '傀':'Reserve a 9-unit 鬼 head and separate the lower 厶 from the sweeping leg beside 亻.',
 '嵬':'Give 鬼 below 山 a 6.375-unit head instead of the old 2.177-unit strip.',
 '廆':'Give 鬼 inside 广 a 6.75-unit head and a separate lower 厶 domain.',
 '䀹':'Keep both small 人 of 夾 clear of the main 大 falling limbs.',
 '䆴':'Allocate eight units to 穴 and sixteen to the turtle, keeping its two boxes distinct.',
 '乘':'Limit 北 side stems to the middle domain; the central 禾 stem alone reaches the baseline.',
 '嵊':'Apply an independently fitted bounded 禾/北 layout only within this exact character.',
 '像':'Restore the third left falling stroke of 象, confirmed in J0-417C and absent from the old paths.',
 '亂':'Use a broad left 𤔔 compartment for 爫/龴/冂/厶/又 and narrow the right hook, removing the collapsed lower knot.',
 '亹':'Separate 臼 side compartments from central 同, place 冖 below them and 且 in its own band.',
 '劘':'Separate 林 and 非 vertically inside 麻, keeping 刂 outside their x-domain.',
 '嚢':'Allocate distinct 一中, 冖, 八, 𠀎 and 衣 bands; replace sub-half-unit bar gaps with two-unit gaps.',
 '屬':'Give the 蜀/虫 lower box three units of height instead of about 0.76; separate upper water strokes and net.',
 '囑':'Give the 屬 lower box independent height within the right-side compartment beside 口.',
 '斸':'Give the 屬 lower box independent height and keep 斤 entirely in the right compartment.',
 '埀':'Limit the 北 side stems to the middle domain and restore the central vertical across the lower bars.',
 '夔':'Give 止/自/巳 distinct middle compartments, 儿 its own band and 夂 below; remove the collapsed central strip.',
 '奭':'Shorten and inset both 百 boxes so 大 legs do not cross their interiors.',
 '孅':'Place the two 人 above 韭 and reserve the far-right corridor for 戈.',
 '峯':'Assign separate height to 山, 夂 and 丰 so the middle diagonal paths are not flattened.',
 '椶':'Separate 凶, 八 and 夂 vertically and preserve the lower bend without the old crowded crossing.',
 '攩':'Restore a visible three-unit 尚 middle stroke instead of the old 0.37-unit segment.',
 '攪':'Keep both 爻 crosses above 冖 and provide a separate 見 compartment.',
 '欞':'Keep the two 人 inside the lower 巫 bars rather than crossing both bars.',
 '氂':'Place all 毛 paths below the 厂 roof instead of allowing its first slant above that roof.',
 '牽':'Put the 幺 crown above and across the shallow 冖 band, not wholly inside its stretched enclosure.',
 '獻':'Separate 虍/匕 from the lower 鬲 and keep 犬 in its own right-side domain.',
}


def correction_paths():
    return {c:[line for role,paths in parts for line in paths] for c,parts in correction_spec().items()}


def apply(glyphs):
    changed=set()
    for c,p in correction_paths().items():
        if c not in glyphs:continue
        old=glyphs[c];notes=dict(old.notes)
        notes.setdefault('previous_source',old.source);notes.setdefault('previous_status',old.status)
        notes['proofread_deep1_correction']=CORRECTION_NOTES[c]
        notes['proofread_deep1_scope']='exact-key structural repair; no recursive propagation or small-size approval'
        glyphs[c]=replace(old,paths=p,source='original:family.proofread_deep1_corrections',status='structure-reviewed-large-size',notes=notes)
        changed.add(c)
    return changed
