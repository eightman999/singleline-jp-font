"""Direct centerline expansion with master-compatible contour topology.

No bitmap tracing or external font outlines. Each path becomes a clockwise
stroke polygon with bevel-limited joins. Separate same-winding paths overlap;
the TrueType overlap flag is set by the builder. Variable masters have the
same path order, point count and contour order, including serif triangles.
"""
from math import hypot, tan, radians
from functools import lru_cache
from fontTools.pens.ttGlyphPen import TTGlyphPen


# Original cursive alternatives, to distinguish Italic from the variable
# family's purely slanted (Oblique) instances. Coordinates remain editable.
ITALIC_ALTERNATES = {
    'a': [[(18,10),(14,8),(9,9),(6,13),(6,18),(9,21),(13,21),(17,17),
           (18,9),(17,21),(21,20)]],
    'g': [[(18,10),(14,8),(9,9),(6,13),(7,18),(10,20),(14,19),(18,15),
           (19,9),(17,22),(14,24),(9,24),(7,22)]],
    'f': [[(6,24),(10,5),(13,2),(17,2),(19,4)],[(5,10),(17,10)]],
}


def centerlines(glyph, style):
    paths = ITALIC_ALTERNATES.get(glyph.text, glyph.paths) if style.italic else glyph.paths
    if glyph.category=='box-drawing':
        # Upright text cells have 1000-unit advance and a1200-unit line box.
        # Rules must reach cell boundaries, not inherit text sidebearings.
        return [[(x*1000/24,1000-y*1200/24) for x,y in p] for p in paths]
    width = glyph.width_factor
    # Original 24-unit em sits in an 840-unit body, with generous side bearings.
    return [[(80*width + 35*x*width, 880 - 35*y) for x, y in p] for p in paths]


def _normal(a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = hypot(dx, dy)
    return (-dy/length, dx/length) if length else (0, 1)


def _clockwise(points):
    area = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points, points[1:]+points[:1]))
    return points if area <= 0 else list(reversed(points))


def _stroke(path, vx, hy):
    points = [p for i,p in enumerate(path) if i == 0 or p != path[i-1]]
    if not points:
        return []
    if len(points) == 1:
        x,y = points[0]
        return [(x-vx/2,y-hy/2),(x-vx/2,y+hy/2),(x+vx/2,y+hy/2),(x+vx/2,y-hy/2)]
    closed = points[0] == points[-1]
    normals = [_normal(a,b) for a,b in zip(points,points[1:])]
    offsets = []
    for i in range(len(points)):
        if i == 0:
            left,right = (normals[-1],normals[0]) if closed else (normals[0],normals[0])
        elif i == len(points)-1:
            left,right = (normals[-1],normals[0]) if closed else (normals[-1],normals[-1])
        else:
            left,right = normals[i-1], normals[i]
        nx,ny = left[0]+right[0],left[1]+right[1]
        denominator = max(0.5, 1+left[0]*right[0]+left[1]*right[1])
        offsets.append((nx/denominator*vx/2, ny/denominator*hy/2))
    polygon = [(x+dx,y+dy) for (x,y),(dx,dy) in zip(points,offsets)]
    polygon += [(x-dx,y-dy) for (x,y),(dx,dy) in reversed(list(zip(points,offsets)))]
    return _clockwise(polygon)


@lru_cache(maxsize=128)
def _negative_contours(frozen_paths):
    """Union counter strokes before reversing winding, avoiding cancellation.

    Enclosed numeral cutouts deliberately keep a fixed 34-unit stroke across
    weight styles/masters; the enclosing disc is also a fixed filled shape.
    Slant/scale still transform the exact same topology. This prevents a
    variable overlap-removal operation from changing the number of points.
    """
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    paths=[list(p) for p in frozen_paths]
    result=[_clockwise(paths[0])]
    cuts=unary_union([Polygon(_stroke(p,34,34)).buffer(0) for p in paths[1:] if len(p)>1])
    polygons=[cuts] if cuts.geom_type=='Polygon' else list(cuts.geoms)
    for polygon in polygons:
        result.append(list(reversed(_clockwise(list(polygon.exterior.coords)[:-1]))))
        for ring in polygon.interiors:result.append(_clockwise(list(ring.coords)[:-1]))
    return result


def contours(glyph, style, *, feature=None):
    """Return integer point contours in a 1000 UPM, y-up coordinate system."""
    polygons=[]
    paths=centerlines(glyph,style)
    if glyph.notes.get('negative'):
        polygons=_negative_contours(tuple(tuple(tuple(p) for p in path) for path in paths))
        paths=[]
    for index,path in enumerate(paths):
        if not path:
            continue
        if glyph.filled:
            polygons.append(_clockwise(list(path)))
            continue
        polygons.append(_stroke(path,style.vertical,style.horizontal))
        # Fixed topology even at serif=0 enables honest interpolation. A zero
        # area serif is a degenerate contour, never a placeholder glyph.
        if len(path) >= 2 and path[0] != path[-1]:
            for endpoint,neighbor in ((path[0],path[1]),(path[-1],path[-2])):
                x,y=endpoint
                dx,dy=neighbor[0]-x,neighbor[1]-y
                s=style.serif
                if abs(dx) > abs(dy)*1.8:
                    direction=1 if dx<0 else -1
                    polygons.append(_clockwise([(x,y-style.horizontal/2),
                        (x-direction*43*s,y-style.horizontal/2),
                        (x-direction*7*s,y+38*s)]))
                elif abs(dy) > abs(dx)*1.8:
                    polygons.append(_clockwise([(x-40*s,y-7*s),(x-40*s,y+7*s),
                        (x+40*s,y+7*s),(x+40*s,y-7*s)]))
    scale,rise=style.scale,style.rise
    if feature in ('subs','sups'):
        scale*=0.65
        rise+=-160 if feature=='subs' else 340
    shear=-tan(radians(style.slant))
    return [[(round((x + shear*(y-60))*scale),round(y*scale+rise))
             for x,y in polygon] for polygon in polygons if polygon]


def make_glyph(glyph,style,*,feature=None):
    pen=TTGlyphPen(None)
    polygons=contours(glyph,style,feature=feature)
    for polygon in polygons:
        pen.moveTo(polygon[0])
        for point in polygon[1:]:pen.lineTo(point)
        pen.closePath()
    result=pen.glyph()
    if result.numberOfContours and len(result.flags):
        result.flags[0] |= 0x40  # OVERLAP_SIMPLE, multiple strokes can intersect.
    scale=style.scale*(0.65 if feature else 1)
    advance=round(glyph.advance*scale)
    xs=[x for p in polygons for x,y in p]
    return result,(advance,min(xs) if xs else 0)
