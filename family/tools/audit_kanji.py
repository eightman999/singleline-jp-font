#!/usr/bin/env python3
"""Audit actual original centerline coverage without counting placeholders."""
from __future__ import annotations
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from family.kanji import build_kanji,CANONICAL,geometry_fingerprint,validate_glyph


def main():
    data=ROOT/'family'/'data'
    jis=json.loads((data/'jisx0213-2004.json').read_text())['entries']
    target={e['text'] for e in jis if e['level']>0}
    extras=set('髙𠮷')
    glyphs,report=build_kanji(target|extras)
    groups=defaultdict(list)
    for c,glyph in glyphs.items():
        validate_glyph(glyph)
        groups[geometry_fingerprint(glyph)].append(c)
    duplicates=[sorted(chars) for chars in groups.values() if len(chars)>1]
    # Retain only the known inherited geometry equivalences; all introduced
    # duplicates are rejected by build_kanji rather than counted as covered.
    assert all(set(chars)<=CANONICAL.keys() for chars in duplicates),duplicates
    levels={}
    for level in range(1,5):
        chars={e['text'] for e in jis if e['level']==level}
        missing=sorted(chars-glyphs.keys())
        levels[str(level)]={'target':len(chars),'drawn':len(chars)-len(missing),'missing':missing}
    names={e['text'] for e in json.loads((data/'unicode-jinmeiyo.json').read_text())['entries']}
    failed={c:r['reasons'] for c,r in report.items() if r['status']=='missing'}
    files=['family/kanji.py','family/kanji_components.py','family/kanji_rare_components.py',
           'family/kanji_variant_components.py','family/kanji_review_corrections.py','family/kanji_dense_corrections.py','family/data/legacy-components.json','family/data/ids-trees.json','family/data/kanji-structure-notes.json']
    summary={
        'scope':'JIS X 0213:2004 levels 1–4 plus separately tracked surname extras',
        'target_kanji':len(target),'drawn_kanji':len(target&glyphs.keys()),
        'canonical_inherited_kanji':len(CANONICAL),'official_joyo_count':2136,
        'five_additional_legacy_forms':list('剥填栢頬𠮟'),
        'status_counts':dict(Counter(report[c]['status'] for c in sorted(target))),
        'quality':'All expanded geometry is an unreviewed original-centerline draft. Drawable does not mean visually approved.',
        'levels':levels,
        'jinmeiyo':{'target':len(names),'drawn':len(names&glyphs.keys()),'missing':sorted(names-glyphs.keys())},
        'extras':{c:report[c]['status'] for c in sorted(extras)},
        'inherited_identical_geometry_groups':duplicates,
        'rejected_duplicate_geometry':{c:r for c,r in failed.items() if any(x.startswith('duplicate_geometry:') for x in r)},
        'missing':failed,
        'flags':dict(Counter(flag for c,r in report.items() if c in target for flag in r.get('flags',[]))),
        'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
    }
    (data/'kanji-coverage-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    # Full per-character provenance is reproducible through the public API.
    output=ROOT/'build'/'family'/'reports'
    output.mkdir(parents=True,exist_ok=True)
    (output/'kanji-provenance.json').write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
