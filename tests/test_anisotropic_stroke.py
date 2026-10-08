"""Acute joins must retain segment width with isotropic and anisotropic pens."""
import math
import pytest
from family.geometry import _stroke, _bevel_stroke_unit, contours
from family.data_loader import load_glyphs
from family.styles import STYLES, variable_style


def edge_separation(poly, i, j):
    a,b=poly[i],poly[j]
    other=poly[-1-i]
    dx,dy=b[0]-a[0],b[1]-a[1]
    return abs(dx*(other[1]-a[1])-dy*(other[0]-a[0]))/math.hypot(dx,dy)


@pytest.mark.parametrize('vx,hy',[(45,20),(42,15),(19,58),(37,19),(20,20),(36,36)])
def test_n_diagonal_retains_nonzero_pen_width(vx,hy):
    path=[(100,0),(100,700),(600,0),(600,700)]
    poly=_stroke(path,vx,hy)
    assert len(poly)==4*len(path)
    assert edge_separation(poly,3,4)>min(vx,hy)*0.75


def test_anisotropic_pen_is_affine_equivariant():
    path=[(1,1),(1,22),(18,2),(18,23)]
    expected=[(x*45,y*20) for x,y in _bevel_stroke_unit([(x/45,y/20) for x,y in path])]
    assert _stroke(path,45,20)==expected


@pytest.mark.parametrize('c',['N','Ǹ','И','Ѝ','M','W'])
def test_variable_master_contour_topology_is_preserved(c):
    glyphs,_=load_glyphs()
    if c not in glyphs:
        pytest.fail('Required regression glyph missing')
    polygons=[contours(glyphs[c],variable_style(STYLES['serif'],w,s))
              for w in (200,400,700) for s in (0,-6,-12)]
    assert len({tuple(map(len,p)) for p in polygons})==1
    assert all(math.isfinite(v) for p in polygons for contour in p for xy in contour for v in xy)


def test_safe_right_angle_retains_miter_corner():
    polygon = _stroke([(0,0),(0,10),(10,10)],2,2)
    assert (-1,11) in polygon
    assert (1,9) in polygon
