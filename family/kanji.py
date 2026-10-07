"""Original centerline kanji expansion, with explicit draft/missing status.

The canonical 24-unit project glyphs are never changed. Extra glyphs combine
project-authored paths using CJKVI *structure*, not external glyph geometry.
Automatic component layout, especially overlays/enclosures, is a design draft,
not a claim of typographic correctness or per-character visual approval.

Public API: ``build_kanji(target_chars) -> (glyphs, character_report)``.
Only drawable, finite, nonblank, distinct new geometry enters ``glyphs``.
Unknown structures remain missing; there is no tofu or repeated-glyph fallback.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

from glyphs.kanji import GLYPHS as CANONICAL

DATA = Path(__file__).with_name('data')
Point = tuple[float, float]
Glyph = list[list[Point]]
IDCS = set('⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻')


def fit(glyph, x, y, width, height):
    return [[(x+a*width/24, y+b*height/24) for a,b in line] for line in glyph]


def strokes(value):
    return [[tuple(map(float, point.split(','))) for point in line.split()]
            for line in value.split(';') if line.strip()]


def geometry_fingerprint(glyph):
    """Order/direction independent; catches a repeated placeholder glyph."""
    lines = []
    for line in glyph:
        points = tuple((round(x,8),round(y,8)) for x,y in line)
        lines.append(min(points,points[::-1]))
    return hashlib.sha256(repr(tuple(sorted(lines))).encode()).hexdigest()


def validate_glyph(glyph):
    if not glyph:
        raise ValueError('blank_geometry')
    for line in glyph:
        if len(line)<2:
            raise ValueError('path_has_fewer_than_two_points')
        for x,y in line:
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError('non_finite_geometry')
            if not -0.001<=x<=24.001 or not -0.001<=y<=24.001:
                raise ValueError('out_of_cell_geometry')
    if not any(a!=b for line in glyph for a,b in zip(line,line[1:])):
        raise ValueError('zero_length_geometry')


@dataclass
class Resolved:
    paths: Glyph
    leaves: frozenset[str]
    flags: frozenset[str]
    depth: int = 0


class Missing(ValueError):
    def __init__(self, reasons):
        self.reasons=frozenset(reasons)
        super().__init__('; '.join(sorted(self.reasons)))


def _left_width(left,right):
    if isinstance(right,str) and right in {'刂','阝','彡'}:
        return 16
    narrow={'亻','氵','扌','忄','礻','衤','彳','冫','阝','土','牜'}
    medium={'糸','糹','言','木','女','王','日','月','金','釒','火','石','禾','虫','目','貝','食','飠','車'}
    return 8 if isinstance(left,str) and left in narrow else 10 if isinstance(left,str) and left in medium else 11


def _boxes(op,children):
    if op=='⿰':
        width=_left_width(*children)
        return [(0,0,width,24),(width+1,0,23-width,24)]
    if op=='⿱':
        top,bottom=children
        height=6 if isinstance(top,str) and top in {'艹','宀','亠','冖','⺌','⺍','𭕄'} else 11
        bh=7 if isinstance(bottom,str) and bottom in {'灬','心','皿'} else 23-height
        return [(0,0,24,23-bh),(0,24-bh,24,bh)]
    if op=='⿲':return [(0,0,7,24),(8,0,7,24),(16,0,8,24)]
    if op=='⿳':return [(0,0,24,7),(0,8,24,7),(0,16,24,8)]
    if op=='⿻':return [(0,0,24,24),(0,0,24,24)]
    inner={'⿴':(5,5,14,14),'⿵':(5,7,14,15),'⿶':(5,1,14,16),
           '⿷':(7,4,15,16),'⿸':(7,8,16,15),'⿹':(2,9,14,13),'⿺':(8,0,16,19)}[op]
    return [(0,0,24,24),inner]


@lru_cache(maxsize=1)
def _sources():
    legacy=json.loads((DATA/'legacy-components.json').read_text())
    components={c:[[tuple(p) for p in line] for line in g] for c,g in legacy.items()}
    sources={c:'historical_project_component' for c in components}
    components.update(CANONICAL)
    try:
        from .kanji_components import extend
        new=extend(components,strokes,fit)
        for c in new:sources[c]='new_project_authored_component'
        from .kanji_variant_components import extend as extend_variants
        for c in extend_variants(components,strokes,fit):sources[c]='new_project_authored_variant'
        from .kanji_review_corrections import extend as extend_corrections
        for c in extend_corrections(components,strokes,fit):sources[c]='new_project_authored_structure_correction'
        from .kanji_dense_corrections import extend as extend_dense
        for c in extend_dense(components,strokes,fit):sources[c]='new_project_authored_structure_correction'
    except ImportError as exc:
        if exc.name not in {'family.kanji_components'}:raise
    # Preserve current canonical glyphs over all old/draft component versions.
    components.update(CANONICAL)
    sources.update({c:'canonical_project_centerline' for c in CANONICAL})
    trees=json.loads((DATA/'ids-trees.json').read_text())
    return components,sources,trees


def build_kanji(target_chars: Iterable[str]):
    """Return independent centerline lists plus one honest record per target.

    Status values: ``canonical``, ``component_draft``, ``composed_draft``,
    ``missing``. No draft has ``visually_reviewed=True``. Failure records contain
    actionable missing leaves, cycles, invalid geometry, or duplicate targets.
    """
    target=sorted(set(target_chars),key=lambda c:tuple(map(ord,c)))
    if any(len(c)!=1 for c in target):
        raise ValueError('Kanji targets must be individual Unicode scalars')
    components,sources,trees=_sources()
    cache={}
    used_variants={}
    def resolve(node,active=frozenset()):
        if isinstance(node,str):
            if node in components:
                return Resolved(components[node],frozenset([node]),frozenset())
            if node in cache:return cache[node]
            if node in active:raise Missing(['cyclic_ids:'+node])
            if node not in trees:
                reason='ambiguous_ids_placeholder:' if len(node)==1 and '\u2460'<=node<='\u2473' else 'undefined_component:'
                raise Missing([reason+node])
            failures=[]
            for variant in trees[node]:
                try:
                    result=resolve(variant['tree'],active|{node})
                except Missing as exc:
                    failures.append(exc.reasons)
                    continue
                flags=set(result.flags)
                if variant['regions'] and 'J' not in variant['regions']:
                    flags.add('non_japanese_ids_variant')
                result=Resolved(result.paths,result.leaves,frozenset(flags),result.depth)
                cache[node]=result
                used_variants[node]=variant
                return result
            raise Missing(min(failures,key=lambda r:(len(r),sorted(r))))
        if not isinstance(node,list) or not node or node[0] not in IDCS:
            raise Missing(['unsupported_ids_node:'+repr(node)])
        op=node[0]; children=node[1:]
        if len(children)!=(3 if op in {'⿲','⿳'} else 2):
            raise Missing(['invalid_ids_arity:'+op])
        resolved=[]; failures=set()
        for child in children:
            try:resolved.append(resolve(child,active))
            except Missing as exc:failures.update(exc.reasons)
        if failures:raise Missing(failures)
        flags=set().union(*(r.flags for r in resolved))
        if op=='⿻':flags.add('unreviewed_overlay')
        elif op in set('⿴⿵⿶⿷⿸⿹⿺'):flags.add('unreviewed_enclosure')
        paths=[line for r,box in zip(resolved,_boxes(op,children)) for line in fit(r.paths,*box)]
        return Resolved(paths,frozenset().union(*(r.leaves for r in resolved)),frozenset(flags),1+max(r.depth for r in resolved))

    glyphs={}; report={}
    fingerprints={}
    # Canonical duplicates, if any, are inherited and documented, not introduced.
    for c in sorted(CANONICAL):
        fingerprints.setdefault(geometry_fingerprint(CANONICAL[c]),c)
    for c in target:
        base={'codepoint':f'U+{ord(c):04X}','visually_reviewed':False}
        try:
            result=resolve(c)
            validate_glyph(result.paths)
            digest=geometry_fingerprint(result.paths)
            duplicate=fingerprints.get(digest)
            if duplicate is not None and duplicate!=c and c not in CANONICAL:
                raise Missing(['duplicate_geometry:'+duplicate])
            fingerprints.setdefault(digest,c)
            glyphs[c]=[[tuple(p) for p in line] for line in result.paths]
            status='canonical' if c in CANONICAL else 'component_draft' if c in components else 'composed_draft'
            flags=sorted(result.flags)
            if result.depth>=4:flags.append('deep_composition')
            report[c]={**base,'status':status,'geometry_sha256':digest,
                       'geometry_source':sources.get(c,'project_components_with_ids_layout'),
                       'component_sources':{k:sources[k] for k in sorted(result.leaves)},
                       'structure_source':'CJKVI-IDS GPL-2.0' if c not in components else None,
                       'ids':used_variants.get(c,{}).get('sequence'),
                       'flags':flags,'composition_depth':result.depth,'path_count':len(result.paths)}
            if c in CANONICAL and duplicate!=c:
                report[c]['inherited_geometry_equivalent']=duplicate
        except (Missing,ValueError) as exc:
            reasons=sorted(exc.reasons) if isinstance(exc,Missing) else [str(exc)]
            report[c]={**base,'status':'missing','reasons':reasons}
    return glyphs,report
