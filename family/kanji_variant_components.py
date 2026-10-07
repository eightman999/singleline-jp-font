"""Independent centerline drafts for explicit traditional-form distinctions.

Added 2026-10-06. These hand-authored 24-unit constructions use the project's
component bank; no external glyph paths, pixels or contour coordinates are
imported. Character identities were visually checked, but these are still
experimental designs and not a blanket Japanese-form certification.
"""


def extend(C,strokes,fit):
    added=set()
    def put(c,paths):C[c]=paths;added.add(c)
    # The eye body in 倶 ends above the independent supporting horizontal.
    # 俱 has side stems continuing to that horizontal. This is a structural
    # change, never a hash mark or arbitrary shift to evade a duplicate check.
    person=fit(C['亻'],0,0,8,24)
    eye=strokes('10,2 21,2 21,14 10,14 10,2;10,6 21,6;10,10 21,10;9,18 23,18;13,20 9,23;18,20 23,23')
    put('倶',person+eye)
    extended=strokes('10,2 21,2 21,18;10,2 10,18;10,6 21,6;10,10 21,10;10,14 21,14;9,18 23,18;13,20 9,23;18,20 23,23')
    put('俱',person+extended)
    # Traditional 殼: 士, cover, explicit 一, and 几 before the strike radical.
    shell=strokes('2,5 11,5;6.5,1 6.5,8;3,8 10,8;1,13 1,10 12,10 12,13;3,13 10,13;3,23 5,19 5,16 9,16 9,22 11,23 12,22')
    put('殼',shell+fit(C['殳'],13,0,11,24))
    # 簔 uses the extended middle crossbar in its traditional garment part.
    garment=strokes('11,7 13,8;2,9 22,9;6,10.5 18,10.5 18,15 6,15 6,10.5;1,12.7 23,12.7;12,15 4,19 1,20;8,17 8,23 14,21;18,16 14,19;12,17 17,21 23,23')
    put('簔',fit(C['竹'],0,0,24,7)+garment)
    # The radical 飠 has a compact bottom cut, not the full 食 right sweep.
    put('飠',strokes('12,1 7,5 2,8;12,1 17,5 22,8;12,6 12,8;7,9 18,9 18,15 7,15;7,9 7,23 14,21;7,12 18,12;13,17 16,20 19,23'))
    # U+24D14 is the upright historical foot component, distinct from 疋.
    put('𤴔',strokes('4,2 19,2 12,8;12,8 12,22;5,10 5,23;12,13 20,13;1,24 23,19'))
    # 衞 retains a hanging cloth-like lower part inside 行.
    middle=strokes('9,4 16,4;11,1 10,4;14,1 14,7;10,8 15,8 15,12 10,12 10,8;8,15 17,15;12.5,15 12.5,24;9,18 16,18 16,23;9,18 9,23')
    put('衞',fit(C['彳'],0,0,7,24)+middle+fit(C['亍'],18,0,6,24))
    # 繁 has 每 in its upper-left constituent; keep its old-form path bank.
    put('繁',fit(C['每'],0,0,12,12)+fit(C['攵'],13,0,11,12)+fit(C['糸'],1,13,22,11))
    # 謹 keeps an explicit traditional 廿 head over the centered 口/stem.
    traditional=strokes('1,4 23,4;6,1 6,8 18,8 18,1;4,10 20,10 20,14 4,14 4,10;12,8 12,24;3,18 21,18;2,21 22,21;1,24 23,24')
    put('謹',fit(C['言'],0,0,9,24)+fit(traditional,10,0,14,24))
    return added
