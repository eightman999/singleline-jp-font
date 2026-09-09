"""CJKVI composition-tree evaluator for the complete Jōyō repertoire."""

import json
from pathlib import Path

from joyo_repertoire import JOYO


_COMPOSITIONS = Path(__file__).with_name("assets") / "fonts" / "source" / "joyo-compositions.json"
_IDCS = {"⿰", "⿱", "⿲", "⿳", "⿴", "⿵", "⿶", "⿷", "⿸", "⿹", "⿺"}


def register(G, R, strokes, fit):
    C = dict(R)
    C.update(G)

    # Education modules are the only permitted external source of reusable
    # project-authored parts.  Their return value is accepted for the newer
    # contract; older modules still communicate through their scratch G.
    from education_strokes_1_2 import register as r12
    from education_strokes_3_4 import register as r34
    from education_strokes_5_6 import register as r56
    for fn in (r12, r34, r56):
        scratch = dict(G)
        result = fn(scratch, dict(R), strokes, fit)
        C.update(result if isinstance(result, dict) else scratch)
    # The caller's existing glyphs are authoritative over education aliases.
    C.update(G)
    try:
        from joyo_components import extend
    except ImportError as exc:
        raise RuntimeError("joyo_components is not connected yet") from exc
    extend(C, strokes, fit)

    trees = json.loads(_COMPOSITIONS.read_text(encoding="utf-8"))
    cache = {}
    active = set()

    def left_width(left, right):
        if isinstance(right,str) and right in {'刂','阝','彡'}:
            return 16
        narrow = {'亻','氵','扌','忄','礻','衤','彳','冫','阝','土','牜'}
        medium = {'糸','糹','言','木','女','王','日','月','金','釒','火','石','禾','虫','目','貝','食','飠','車'}
        return 8 if isinstance(left,str) and left in narrow else (10 if isinstance(left,str) and left in medium else 11)

    def head_frame(lines, stem_index, factor, threshold):
        # Keep the descending left stroke full height; compress only the head.
        return [[(x, y if i==stem_index and y>threshold else y*factor) for x,y in line]
                for i,line in enumerate(lines)]

    def eval_node(node):
        if isinstance(node, str):
            if node in C:
                return C[node]
            if node in trees:
                return build(node)
            raise KeyError("undefined composition leaf: " + node)
        if not isinstance(node, list) or len(node) < 2 or node[0] not in _IDCS:
            raise ValueError("unsupported composition node: " + repr(node))
        op = node[0]
        children = node[1:]
        if len(children) != (3 if op in ('⿲','⿳') else 2):
            raise ValueError("wrong child count for " + op)
        outer = children[0] if isinstance(children[0],str) else ''
        if op=='⿸' and outer in {'麻','府','𠩵'}:
            frame,header = {'麻':('广','林'),'府':('广','付'),'𠩵':('厂','林')}[outer]
            return (eval_node(frame) + fit(eval_node(header),6,6,18,7)
                    + fit(eval_node(children[1]),6,14,18,10))
        if op=='⿸' and outer in {'戸','虍'}:
            frame = head_frame(eval_node(outer),2,0.6,14 if outer=='戸' else 8)
            return frame + fit(eval_node(children[1]),6,12,18,12)
        if op=='⿺' and outer in {'走','麦','鬼'}:
            frame=[[(x*(0.45+0.55*max(0,y-19)/5),y) for x,y in line] for line in eval_node(outer)]
            return frame + fit(eval_node(children[1]),11,0,13,20)
        if op in {"⿰", "⿱"}:
            if op == "⿰":
                a = left_width(*children)
                boxes = [(0, 0, a, 24), (a + 1, 0, 24 - a - 1, 24)]
            else:
                top = children[0] if isinstance(children[0], str) else ""
                bottom = children[1] if isinstance(children[1], str) else ""
                h = 6 if top in {"艹", "宀", "亠", "冖", "⺌", "⺍", "𭕄"} else 11
                bottom_h = 7 if bottom in {"灬", "心", "皿"} else 23 - h
                boxes = [(0, 0, 24, 24 - bottom_h - 1), (0, 24 - bottom_h, 24, bottom_h)]
        elif op in ("⿲", "⿳"):
            if op == "⿲":
                boxes = [(0, 0, 7, 24), (8, 0, 7, 24), (16, 0, 8, 24)]
            else:
                boxes = [(0, 0, 24, 7), (0, 8, 24, 7), (0, 16, 24, 8)]
        else:
            inner = (5, 5, 14, 14)
            if op == "⿵": inner = (5, 7, 14, 15)
            elif op == "⿶": inner = (5, 1, 14, 16)
            elif op == "⿷": inner = (7, 4, 15, 16)
            elif op == "⿸": inner = (7, 8, 16, 15)
            elif op == "⿹": inner = (2, 9, 14, 13)
            elif op == "⿺": inner = (8, 0, 16, 19)
            boxes = [(0, 0, 24, 24), inner]
        if len(children) != len(boxes):
            raise ValueError("unsupported arity for " + op)
        return [line for child, box in zip(children, boxes) for line in fit(eval_node(child), *box)]

    def build(ch):
        if ch in C:
            return C[ch]
        if ch in cache:
            return cache[ch]
        if ch in active:
            raise ValueError("cyclic composition: " + ch)
        active.add(ch)
        try:
            if ch in trees:
                glyph = eval_node(trees[ch])
            else:
                raise KeyError("undefined Jōyō glyph: " + ch)
            cache[ch] = glyph
            return glyph
        finally:
            active.remove(ch)

    for ch in JOYO:
        if ch not in G:
            G[ch] = build(ch)
