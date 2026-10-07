"""Independently authored fixes for concrete errors found in sampled QA.

These are still drafts, not a blanket visual certification. Reference glyphs
were viewed only to identify character topology; no outline, pixel or path was
traced/imported. Existing canonical glyphs are restored unchanged by kanji.py.
"""

CORRECTION_NOTES = {
    '戾': 'Continuous 戶 shelter with a compact head and long left stem; 犬 sits below the head, clear of the enclosing stem. Derived 棙淚錑 inherit this correction.',
    '魃': 'Narrow but identifiable left 鬼 and separate right 犮; only the intended sweeping lower leg spans the bottom.',
    '歷': 'Reserve the bottom third for 止, below both 禾 crowns; derivatives cannot overprint it with the enclosure.',
    '癧': 'Flatten the nested enclosure proportions so the bottom 止 remains visible beneath two distinct 禾 forms.',
    '藶': 'Use a compact explicit grass crown and reserve enough height for the lower 止.',
    '魎': 'Separate the left ghost head from a right two-person enclosure; keep the small ghost curl left of the right frame.',
    '㒼': 'Give the 廿-crowned enclosure its own outer verticals, central upright and separated interior 入 strokes, like the corrected 兩.',
    '兩': 'Connected top bar and central stem above a clear 冂, with two subordinate 入 elements. Repairs 輛 and other descendants.',
}


def extend(C, strokes, fit):
    added=set()
    def put(c,value):
        C[c]=strokes(value)
        added.add(c)
    put('戾',
        '20,1 5,3;5,3 5,15 3,21 1,24;'
        '5,5 21,5 21,10 5,10;'
        '6,16 23,16;15,11 15,16 12,21 6,24;'
        '15,16 19,21 24,24;19,12 22,14')
    put('魃',
        '8,1 6,4;3,4 11,4 11,12 3,12 3,4;'
        '3,8 11,8;7,4 7,12;'
        '6,12 6,18 3,22 1,24;'
        '9,12 9,21 12,23 21,23 24,21;'
        '12,14 10,19 14,18;13,16 15,20;'
        '13,7 24,7;17,1 16,9 14,14 11,17;'
        '15,10 22,10 20,15 16,20;'
        '16,12 20,17 24,20;21,2 23,4')
    put('兩',
        '1,2 23,2;3,23 3,6 21,6 21,23 18,23;'
        '12,2 12,23;'
        '6,9 8,9 7,14 4,19;8,12 10,18;'
        '15,9 17,9 16,14 13,19;17,12 20,18')
    # Do not place 止 inside a full-height 厤. Its two 禾 must occupy the upper
    # compartment only, leaving the lower third for the four simple foot paths.
    C['歷']=(strokes('23,2 4,2 4,16 1,24')
              +fit(C['禾'],5,4,8,10)+fit(C['禾'],15,4,8,10)
              +fit(C['止'],6,15,18,9))
    added.add('歷')
    C['癧']=[list(line) for line in C['疒']]+fit(C['歷'],6,5,18,19)
    added.add('癧')
    C['藶']=strokes('1,4 23,4;7,1 7,6;17,1 17,6')+fit(C['歷'],0,6,24,18)
    added.add('藶')
    # A shared 兩 repair does not fix the full-width 鬼 enclosure automatically.
    # 魎 needs the same explicit side/bottom allocation as 魃, with its small
    # curl pulled left of the right-hand enclosing frame.
    C['魎']=([list(line) for line in C['魃'][:6]]
              +strokes('11,14 9.8,19 12,18;11.5,16 12.5,20')
              +fit(C['兩'],12.3,0,11.7,21))
    added.add('魎')
    put('㒼',
        '1,4 23,4;7,1 7,7 17,7 17,1;'
        '3,24 3,9 21,9 21,24 18,24;12,7 12,24;'
        '6,12 8,12 7,17 4,21;8,15 10,21;'
        '15,12 17,12 16,17 13,21;17,15 20,21')
    return added
