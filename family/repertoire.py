"""Pinned character *identities*, kept separate from glyph coverage claims."""
import json
from pathlib import Path

DATA=Path(__file__).parent/'data'


def standards():
    return json.loads((DATA/'jisx0213-2004.json').read_text()), json.loads((DATA/'unicode-jinmeiyo.json').read_text())


def targets():
    jis,jin=standards()
    return {e['text'] for e in jis['entries'] if e['level']>0} | {e['text'] for e in jin['entries']}


def report(glyphs, provenance):
    jis,jin=standards()
    result={}
    groups={f'jis_level_{i}':{e['text'] for e in jis['entries'] if e['level']==i} for i in range(1,5)}
    groups['jinmeiyo']={e['text'] for e in jin['entries']}
    groups['jis_nonkanji']={e['text'] for e in jis['entries'] if e['level']==0}
    groups['jis_multiscalar']={e['text'] for e in jis['entries'] if len(e['text'])>1}
    for name,chars in groups.items():
        present=chars & glyphs.keys()
        result[name]={'target':len(chars),'present':len(present),'missing_count':len(chars-present),
                      'missing':sorted(chars-present),'complete_encoding':not(chars-present)}
    flag_names=sorted({f for g in glyphs.values() for f in g.notes.get('flags',[])})
    flags={f:{'count':sum(f in g.notes.get('flags',[]) for g in glyphs.values()),
              'characters':[c for c,g in glyphs.items() if f in g.notes.get('flags',[])]} for f in flag_names}
    return {'schema_version':1,'target_definition':'JIS X 0213:2004 levels 1–4 and Unicode 18.0.0 kJinmeiyoKanji',
            'scalar_cmap_count':sum(len(c)==1 for c in glyphs),'sequence_glyph_count':sum(len(c)>1 for c in glyphs),
            'groups':result,'warning':'Encoding presence is not a legibility or typographic quality certificate. Composed Kanji are experimental drafts, not individually proofread.',
            'japanese_typographic_release_ready':False,
            'japanese_form_validation':'UNFINISHED, including flagged non-Japanese IDS variants. Complete encoding coverage does not certify correct Japanese glyph forms.',
            'quality_flags':flags,
            'status_counts':{s:sum(g.status==s for g in glyphs.values()) for s in sorted({g.status for g in glyphs.values()})},
            'kanji_provenance':provenance}
