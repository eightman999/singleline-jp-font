#!/usr/bin/env python3
"""Reproduce project component snapshot and structure-only IDS selection.

No downloaded glyph geometry is used. The legacy source is this repository's
own first commit; CJKVI supplies Unicode character structure only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
REVISION = '17d6ad0'
IDCS = '⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻'

def parse_ids(value):
    tokens = re.findall(r'&[^;]+;|.', value)
    def read(i):
        token = tokens[i]
        i += 1
        if token in IDCS:
            children = []
            for _ in range(3 if token in '⿲⿳' else 2):
                child, i = read(i)
                children.append(child)
            return [token, *children], i
        return token, i
    tree, end = read(0)
    if end != len(tokens):
        raise ValueError(f'Unconsumed IDS input: {value}')
    return tree

def export_components():
    # Executing only the project's historical source, in a temporary tree.
    with tempfile.TemporaryDirectory(prefix='singleline-legacy-') as directory:
        tar = subprocess.Popen(['git', 'archive', REVISION], cwd=ROOT, stdout=subprocess.PIPE)
        subprocess.run(['tar', '-x', '-C', directory], stdin=tar.stdout, check=True)
        if tar.wait():
            raise RuntimeError('Historical project revision is unavailable')
        code = '''
import json
import custom_japanese_strokes as old
C=dict(old.R); C.update(old.G)
for name in ['education_strokes_1_2','education_strokes_3_4','education_strokes_5_6']:
    C.update(__import__(name).register(dict(old.G),dict(old.R),old.strokes,old.fit) or {})
__import__('joyo_components').extend(C,old.strokes,old.fit)
print(json.dumps(C,ensure_ascii=False))
'''
        result = subprocess.check_output([sys.executable, '-c', code], cwd=directory)
    return json.loads(result)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ids', type=Path, required=True)
    ap.add_argument('--targets', type=Path, required=True, help='JIS repertoire JSON with entries')
    args = ap.parse_args()
    sys.path.insert(0, str(ROOT))
    from glyphs.kanji import GLYPHS
    components = {k:v for k,v in export_components().items()
                  if len(k)==1 and ord(k)>=0x2e80 and k not in GLYPHS}
    records = {}
    for line in args.ids.read_text().splitlines():
        fields = line.split('\t')
        if len(fields)<3 or fields[0].startswith('#'):
            continue
        variants = []
        for sequence in fields[2:]:
            tags = ''.join(re.findall(r'\[([^\]]+)\]',sequence))
            bare = re.sub(r'\[[^\]]*\]','',sequence)
            try:
                tree = parse_ids(bare)
            except (ValueError, IndexError):
                continue
            if tree == fields[1]:
                continue
            variants.append({'tree':tree,'sequence':sequence,'regions':tags})
        if variants:
            # Do not silently choose a non-Japanese alternative when J exists.
            preferred = [v for v in variants if 'J' in v['regions']]
            if not preferred:
                preferred = [v for v in variants if not v['regions']]
            records[fields[1]] = preferred or variants
    target = {e['text'] for e in json.loads(args.targets.read_text())['entries'] if e['level']>0}
    selected = {}
    def visit(node):
        if isinstance(node,list):
            for c in node[1:]: visit(c)
        elif node not in selected and node in records:
            selected[node] = records[node]
            for row in records[node]:visit(row['tree'])
    for c in target:visit(c)
    data = ROOT/'family'/'data'
    data.mkdir(parents=True,exist_ok=True)
    def write(name,obj):
        (data/name).write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    write('legacy-components.json',components)
    write('ids-trees.json',selected)
    revision = subprocess.check_output(['git','rev-parse',REVISION],cwd=ROOT,text=True).strip()
    write('kanji-sources.json',{
        'geometry':{'project_revision':revision,'source':'https://github.com/eightman999/singleline-jp-font',
                    'files':['custom_japanese_strokes.py','education_strokes_1_2.py','education_strokes_3_4.py','education_strokes_5_6.py','joyo_components.py','joyo_primitive_strokes.py'],
                    'license':'AGPL-3.0','scope':'Project-authored centerline geometry; canonical current glyphs remain authoritative'},
        'structure':{'revision':'86b4d16159f0079437870408f0ca186e529015db',
                     'url':'https://github.com/cjkvi/cjkvi-ids/blob/86b4d16159f0079437870408f0ca186e529015db/ids.txt',
                     'sha256':hashlib.sha256(args.ids.read_bytes()).hexdigest(),
                     'license':'GPL-2.0','scope':'Character structure only; no font outlines or stroke coordinates'},
        'component_count':len(components),'ids_record_count':len(selected),
        'target_count':len(target),
        'snapshot_sha256':{n:hashlib.sha256((data/n).read_bytes()).hexdigest() for n in ['legacy-components.json','ids-trees.json']},
    })
    print(f'Exported {len(components)} project components and {len(selected)} IDS records for {len(target)} target kanji')
if __name__=='__main__':main()
