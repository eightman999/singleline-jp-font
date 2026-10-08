from family.proofread_lower_corrections import correction_paths
from family.kanji import validate_glyph


def test_two_open_king_crowns_and_two_bisected_boxes():
    p=correction_paths()['䰗'];validate_glyph(p)
    # Both crowns have exactly three independent bars and an internal stem.
    for a,b,x in [(3,10,6.5),(14,21,17.5)]:
        for y in (2,4,6):assert [(a,y),(b,y)] in p
        assert [(x,2),(x,6)] in p
    assert [(6,14),(18,14)] in p
    assert [(5,20),(19,20)] in p
    assert [(12,12),(12,23),(14,24),(20,24),(21,22)] in p
    # No accidental extra closing vertical at either crown edge.
    for path in p[2:10]:
        for (x,y),(xx,yy) in zip(path,path[1:]):
            if x==xx:assert x in (6.5,17.5) and {y,yy}=={2,6}


def test_no_repeated_identical_segments():
    p=correction_paths()['䰗'];segments=[]
    for path in p:segments.extend(tuple(sorted((a,b))) for a,b in zip(path,path[1:]))
    assert len(segments)==len(set(segments))
