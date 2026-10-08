"""23 local repairs supported by Unicode 18 J-source, JP reference and paths.

No external contours are imported. Coordinates and region allocations are
independently authored on the project grid. Other regional/design differences
in the 44-character review are deliberately left unchanged. No shared component
or legacy source is edited; all reuse below is read-only project geometry.
"""
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
from .kanji import build_kanji, fit, strokes
from .proofread_upper_corrections import snug

TARGETS=frozenset('甗癱矚籌籖籭籰纎纒纖臟虁讖軈釁鐡鐵鑄鑭鑲鑿饟鬖')


@lru_cache(maxsize=1)
def correction_paths():
    needs=TARGETS|set('瓦疒隹糸月目麗又言身亻心金𩙿髟臼酉分殳林')
    C,_=build_kanji(needs);P={};N={}
    def put(c,p,n):P[c]=p;N[c]=n
    def lr(left,right,w=9):return fit(left,0,0,w,24)+snug(right,w+1,0,23-w,24)
    bamboo=strokes('4,0 2,3 1,4;3,2 10,2;6,2 7,4;16,0 14,3 13,4;15,2 23,2;19,2 20,4')
    def crown(body):return deepcopy(bamboo)+snug(body,0,6,24,18)
    # Short tiger curl above, separate mouth and tripod below.
    yan=strokes('10,0 10,4;10,2 22,2;23,5 4,5 4,17 1,24;8,8 21,6;10,6 10,9 14,10 21,10 23,8;7,12 22,12;9,14 20,14 20,17 9,17 9,14;7,24 7,19 22,19 22,24 20,24;11,19 10,21;18,19 19,21;9,22 20,22;14.5,22 14.5,24')
    put('甗',lr(yan,C['瓦'],12),'Shorten the 虍 inner curl before the distinct 口/冂 contents; remove verified crossings in left 鬳.')
    japanese_black=deepcopy(C['纒'])
    # J0-6575 uses the Japanese 黒 top (田). Other regional 黑 forms are
    # valid elsewhere; this explicitly chooses the stated Japanese source.
    box=japanese_black[6]
    mid=(box[0][1]+box[2][1])/2
    japanese_black[8:10]=[[(box[0][0],mid),(box[1][0],mid)]]
    put('纒',japanese_black,'Japanese-source adoption: J0-6575 has 田 in 黒; replace two inner dots by its middle horizontal without calling other regional forms invalid.')
    # 難 left portion: both lower horizontals are independent of mouth bottom.
    nan_left=strokes('1,4 11,4;3,1 3,7 9,7 9,1;2,9 10,9 10,13 2,13 2,9;6,7 6,17 4,21 1,24;1,16 11,16;1,19 11,19;6,19 9,22 12,24')
    nan=nan_left+snug(C['隹'],14,1,10,23)
    put('癱',deepcopy(C['疒'])+snug(nan,7,7,17,17),'Restore the missing 廿 lower edge and the second horizontal below the left mouth in 難; J13-785F confirms both distinctions.')
    shu=strokes('4,1 23,1 23,5 4,5;4,1 4,17 1,24;14,6 14,11;7,6 10,7;21,6 18,7;11,9 8,11 5,12;17,9 20,11 23,12;6,13 22,13 22,16 6,16 6,13;11,13 11,16;17,13 17,16;9,17 6,19 4,20;8,18 23,18 22,23 20,24 18,24;8,20 17,20 17,22 8,22 8,20;12,18.5 12,23.5;7,24 18,23;16,22.5 19,24')
    put('矚',lr(C['目'],shu,8),'Allocate separate water, net and lower insect regions inside 屬; enlarge the formerly sub-unit insect counter.')
    shou=strokes('1,3 23,3;12,0 12,6;4,6 20,6;2,9 22,9 17,11;4,13 20,13;12,13 12,16;1,16 23,16;2,18 22,18;2,20 10,20 10,24 2,24 2,20;13,20 24,20;20,18 20,24 17,24;14,22 16,23')
    put('籌',crown(shou),'Give 壽 consecutive independent levels; old 0.3-unit upper levels merged even at 240px.')
    put('鑄',lr(C['金'],shou,9),'Spread 壽 upper strokes through the available height instead of compressing them into the top 6.8 units.')
    # 韯/韱: top element ends before 韭; 戈 stays outside its right side.
    frame=strokes('1,7 23,7;17,0 18,14 21,23 24,20;23,12 20,19 15,24;21,1 23,3')
    leek=strokes('5,9 5,23;11,9 11,23;1,11 5,11;1,15 5,15;1,19 5,19;11,11 15,11;11,15 15,15;11,19 15,19;1,23 15,23')
    soil=strokes('7,0 7,7;3,3 12,3')
    people=strokes('5,0 3,4 1,6;5,0 8,5;12,0 10,4 8,6;12,0 15,5')
    xian_soil=frame+soil+leek;xian_people=frame+people+leek
    put('籖',crown(xian_soil),'Stop top 土 above 韭; place both 韭 columns left of the 戈 sweep rather than in its central overlap.')
    put('纎',lr(C['糸'],xian_soil,9),'Separate top 土, lower 韭 and outside 戈 in the right 韯; preserve 纎/纖 top distinction.')
    put('纖',lr(C['糸'],xian_people,9),'Separate two top 人 above 韭 from the outside 戈; former long 人 strokes cut through the lower bars.')
    put('讖',lr(C['言'],xian_people,9),'Use a separately allocated 人人/韭/戈 right component; keep the left 言 unchanged in topology.')
    jp_li=deepcopy(C['麗'])
    jp_li[2]=[(5,7.2),(6,9.2)];jp_li[5]=[(17.5,7.2),(18.5,9.2)]
    put('籭',crown(jp_li),'Reserve 18 units beneath a compact bamboo crown for 鹿 counters and adopt the two short internal dot strokes shown by J13-7970.')
    eyes=strokes('1,6 10,6 10,11 1,11 1,6;1,7.7 10,7.7;1,9.3 10,9.3;14,6 23,6 23,11 14,11 14,6;14,7.7 23,7.7;14,9.3 23,9.3')
    put('籰',deepcopy(bamboo)+eyes+snug(C['隹'],1,12.5,23,6.5)+snug(C['又'],1,20,22,4),'Make separate eye, bird and 又 compartments; old eye/bird horizontal gaps were only 0.57-0.69 units.')
    zang=strokes('2,0 2,10 6,10;6,0 6,24;1,16 6,16;3,16 2,21 0,24;7,6 23,4;18,0 19,14 22,24 24,20;23,11 20,19 15,24;21,0 23,2;16,8 9,8 9,21 16,21;9,12 15,12 15,17 9,17;12,8 12,12;12,17 12,21')
    grass=strokes('1,2 23,2;7,0 7,4;17,0 17,4')
    put('臟',lr(C['月'],grass+snug(zang,0,6,24,18),8),'Place 臣 between the left 爿 and outside 戈, not over the long 爿 stem in the right 藏.')
    naocrown=strokes('6,0 6,4;1,2 11,2;18,0 18,4;13,2 23,2;2,6 22,6;3,8 3,13;3,10 6,10;1,10 1,13;0,13 6,13;11,7 10,8;8,8 15,8 15,13 8,13 8,8;8,9.7 15,9.7;8,11.3 15,11.3;17,8 23,8 23,10 17,10;17,8 17,12 19,13 23,13 24,12;8,14 8,16 5,18 1,19;16,14 16,17 19,18 23,18 24,17;9,19 5,21 1,22;7,20 21,20 16,22 9,23 1,24;5,21 12,23 23,24')
    put('虁',naocrown,'Keep 艹 compact and reserve distinct 止/自/巳 and lower-leg/夂 levels; old central frame heights fell below 0.6 units.')
    shelter=strokes('11,0 13,2;23,4 3,4 3,17 0,24')
    ying=shelter+snug(C['亻'],5,6,4,9)+snug(C['隹'],11,6,12,9)+snug(C['心'],5,17,19,7)
    put('軈',lr(C['身'],ying,9),'Separate upper 亻隹 from lower 心 within 應; old 心 strokes entered the bird stem and horizontal bars.')
    old_xin=C['釁']
    upper=strokes('7,1 2,2;2,2 2,9;2,4 6,4;2,7 6,7;18,1 23,1 23,9;18,4 23,4;18,7 23,7;1,12 1,9 24,9 24,12')
    put('釁',upper+snug(old_xin[8:11],8,1,8,7)+snug(C['酉'],1,12.5,22,6)+snug(C['分'],1,19.5,22,4.5),'Place the central nested component strictly between both 臼 arms; the old inner uprights crossed the arms horizontal strokes.')
    iron_base=frame+soil
    dou=strokes('3,9 13,9 13,14 3,14 3,9;4,17 6,20;12,17 10,20;1,23 15,23')
    cheng=strokes('3,9 13,9 13,14 3,14 3,9;3,16 13,16;3,19 13,19;1,23 15,23;8,16 8,23')
    put('鐡',lr(C['金'],iron_base+dou,9),'End the top 土 stem before the lower 口/䒑; prevent the previous vertical from splitting 口.')
    put('鐵',lr(C['金'],iron_base+cheng,9),'End the top 土 stem before the lower 呈; keep 口/王 left of the outer 戈.')
    put('鑭',deepcopy(C['鑭'][:13])+snug(C['鑭'][13:],13.75,10.5,7.5,12.5),'Separate the inner 柬 top bar from 門: old 0.5-grid gap is 17.5 UPM, smaller than the 20-UPM horizontal pen and causes actual ink contact.')
    xiang=strokes('12,0 14,2;1,3 23,3;2,5 10,5 10,9 2,9 2,5;14,5 22,5 22,9 14,9 14,5;1,11 23,11;1,14 23,14;1,17 23,17;7,10 7,17;17,10 17,17;12,17 7,20 1,22;7,20 7,24 14,22;12,19 17,22 23,24;22,18 16,21')
    put('鑲',lr(C['金'],xiang,9),'Expand the three middle 襄 horizontals and their two stems; old two bars were only 0.60 units apart.')
    put('饟',lr(C['𩙿'],xiang,10),'Use separate 口口 / middle-bar / 衣 regions in 襄 while preserving the Japanese food radical.')
    zuo=strokes('3,0 3,3;8,0 8,3;0,1 1,2;11,1 10,2;0,3 11,3;2,4 3,5;9,4 8,5;1,6 10,6;5.5,5 5.5,8;0,8 11,8')
    put('鑿',zuo+snug(C['臼'],1,9,10,5)+snug(C['殳'],13,0,11,14)+snug(C['金'],0,16,24,8),'Separate upper-left 丵 and lower-left 臼 before adding 殳 and bottom 金; old 丵/臼 shared the entire upper-left region.')
    three=strokes('12,0 7,5 17,5;15,3 19,6;5,7 1,11 10,11;8,9 12,12;17,7 13,11 22,11;20,9 24,12;12,11 8,15 2,18;12,11 17,15 23,18;20,16 8,20;21,19 6,23;23,21 13,24 2,24')
    put('鬖',snug(C['髟'],0,0,24,6)+snug(three,0,8,24,16),'Reserve enough vertical extent for all three 厶 above 人 and 彡; old first triangle height was below 1 unit.')
    assert set(P)==TARGETS
    return P,N


def apply_corrections(glyphs):
    P,N=correction_paths()
    for c in TARGETS & glyphs.keys():
        old=glyphs[c]
        glyphs[c]=replace(old,paths=deepcopy(P[c]),source='original:family.proofread_deep2_corrections',status='structure-reviewed',
            notes={**old.notes,'proofread_correction':N[c],'previous_source':old.notes.get('previous_source',old.source),
                   'review_scope':'Unicode J-source + JP reference + 240px source correspondence, 23 named targets only'})
    return glyphs
