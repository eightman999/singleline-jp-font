"""Append-only, artifact-scoped integration of heterogeneous visual reviews.

This never converts rendering, absence of a detected defect, or a limited
post-correction recheck into all-style/size/Japanese/native-OS certification.
Original review files are read only. Evidence is content-addressed and copied.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import html
import json
import re
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
BASELINE = {'kanji-lower.json','kanji-middle.json','kanji-upper.json','nonkanji.json'}
KNOWN = {'no-obvious-structural-defect','uncertain','confirmed-defect'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def extract_rows(document):
    if isinstance(document,list):
        return document,{}
    if isinstance(document,dict):
        for key in ('glyphs','entries','records','reviews'):
            if isinstance(document.get(key),list):
                return document[key],{k:v for k,v in document.items() if k!=key}
    return [],document


def row_text(row):
    value = row.get('text',row.get('character'))
    if isinstance(value,str):
        return value
    cps = row.get('codepoints') or ([row['codepoint']] if row.get('codepoint') else [])
    try:
        return ''.join(chr(int(cp.removeprefix('U+'),16)) for cp in cps)
    except (ValueError,TypeError):
        return None


def conservative_status(events):
    """Unrecognized verdicts remain uncertain; there is deliberately no pass."""
    statuses = {e['status'] for e in events}
    if 'confirmed-defect' in statuses:
        return 'confirmed-defect'
    if not statuses:
        return 'not-reviewed'
    if statuses != {'no-obvious-structural-defect'}:
        return 'uncertain'
    return 'no-obvious-structural-defect'


class EvidenceStore:
    def __init__(self,root,output):
        self.root,self.output = Path(root),Path(output)
        self.directory = self.output/'evidence'
        self.directory.mkdir(parents=True,exist_ok=True)
        self.cache = {}
        self.artifact_candidates = None

    def preserve(self,path,declared_sha=None):
        if not path:
            return {'path':None,'declared_sha256':declared_sha,'binding':'unavailable'}
        path = Path(path)
        if not path.is_absolute():
            path = self.root/path
        key=(str(path),declared_sha)
        if key in self.cache:
            return self.cache[key]
        result={'path':str(path),'declared_sha256':declared_sha}
        if declared_sha and path.suffix in ('.ttf','.sjpb') and (not path.exists() or sha(path)!=declared_sha):
            if self.artifact_candidates is None:
                self.artifact_candidates={}
                for candidate in (p for p in (self.root/'build').rglob('*') if p.suffix in ('.ttf','.sjpb')):
                    if 'evidence' not in candidate.parts:
                        self.artifact_candidates.setdefault(sha(candidate),candidate)
            if declared_sha in self.artifact_candidates:
                result['requested_path']=str(path)
                path=self.artifact_candidates[declared_sha]
                result['path']=str(path)

        # A pre-fix artifact might already have been replaced. The declared
        # digest can resolve an earlier immutable snapshot, never the new file.
        existing=list(self.directory.glob(str(declared_sha)+'.*')) if declared_sha else []
        if declared_sha and existing and sha(existing[0])==declared_sha:
            result.update(sha256=declared_sha,snapshot=str(existing[0].relative_to(self.output)),binding='declared-hash-verified-snapshot')
        elif path.exists():
            actual=sha(path)
            destination=self.directory/(actual+path.suffix)
            if not destination.exists():
                shutil.copy2(path,destination)
            result.update(sha256=actual,snapshot=str(destination.relative_to(self.output)),
                          binding='declared-hash-verified' if actual==declared_sha else 'declared-hash-mismatch' if declared_sha else 'captured-at-merge-original-view-hash-unpinned')
        else:
            result['binding']='missing'
        self.cache[key]=result
        return result


def first_value(row,meta,keys):
    for source in (row,meta):
        for key in keys:
            if source.get(key) is not None:
                return source[key]
    return None


def normalize(row,meta,filename,index,store,source_inventory,review_evidence):
    text=row_text(row)
    if not text or ('status' not in row and filename not in ('elephant-propagation.json','longevity-propagation.json')):
        return None
    phase='baseline' if filename in BASELINE else 'duplicate-baseline' if filename=='non-japanese-ids.json' else 'after' if 'after' in filename else 'additional'
    if row.get('viewed_original_font_sha256'):
        phase='followup-baseline'
    if filename.startswith('deep-structural-group-') and row.get('status','').startswith('repaired-'):
        phase='after'
    if filename in ('elephant-propagation.json','longevity-propagation.json','known-component-descendants.json'):
        phase='after'
    if filename=='variant-pairs.json' and row.get('status')=='corrected-japanese-source-distinction':
        phase='after'
    artifact=first_value(row,meta,('artifact','artifact_path','font','target_font'))
    artifact_hash=first_value(row,meta,('artifact_sha256','source_font_sha256','font_sha256','target_font_sha256','viewed_original_font_sha256'))
    if isinstance(artifact_hash,dict):
        selected=artifact if isinstance(artifact,str) and artifact in artifact_hash else next((p for p in artifact_hash if p.endswith('/static/singleline.ttf')),None)
        artifact,artifact_hash=selected,artifact_hash.get(selected) if selected else None
    if isinstance(artifact,dict):
        artifact_hash=artifact.get('sha256',artifact_hash)
        artifact=artifact.get('path')
    if filename.startswith('deep-structural-group-') and not artifact:
        face=meta.get('after_subset_fonts',{}).get('singleline',{})
        artifact,artifact_hash=face.get('path'),face.get('sha256')
    if 'final-pen' in filename and row.get('kind') in ('ttf','sjpb'):
        kind=row['kind'];artifact_hash=row.get(kind+'_sha256',artifact_hash)
        if not artifact:
            artifact=f'build/family/bitmaps/{row.get("style")}-{row.get("size")}.sjpb' if kind=='sjpb' else f'build/family/static/SinglelineJPLab-{row.get("style")}.ttf'
    if not artifact and artifact_hash:
        artifact='build/family/static/SinglelineJPLab-singleline.ttf'
    artifact_evidence=store.preserve(artifact,artifact_hash)
    image_values=first_value(row,meta,('viewed_image','viewed_png','image','proof_image','viewed_comparison','after_viewed_image','after_image')) or []
    images=image_values if isinstance(image_values,list) else [image_values]
    declared_image=first_value(row,meta,('viewed_image_sha256','image_sha256','proof_sha256','after_image_sha256'))
    proof=[store.preserve(p,declared_image if len(images)==1 else None) for p in images]
    if row.get('style_size_reviews'):
        # The classification-only propagation schema pins each viewed case.
        seen_proofs=set()
        for case in row['style_size_reviews']:
            if case.get('before_after_actually_viewed') and case.get('image') not in seen_proofs:
                proof.append(store.preserve(case.get('image'),case.get('image_sha256')))
                seen_proofs.add(case.get('image'))
    if row.get('detail_png'):
        proof.append(store.preserve(row['detail_png'],row.get('detail_png_sha256')))
    source_hash=first_value(row,meta,('source_geometry_sha256','source_sha256','after_sha256','after_geometry_sha256','after_paths_sha256'))
    source_binding='review-declared' if source_hash else 'audit-time-source-snapshot-not-verified-as-artifact-source' if phase in ('baseline','duplicate-baseline') and text in source_inventory else 'unavailable'
    if not source_hash and phase in ('baseline','duplicate-baseline'):
        source_hash=source_inventory.get(text,{}).get('source_sha256')
    status=row.get('status',row.get('classification'))
    event={'event_id':canonical_hash([filename,index,row,meta]),'review_file':filename,'row_index':index,
           'text':text,'id':'+'.join(f'U+{ord(c):04X}' for c in text),'phase':phase,
           'status':status,'known_status':status in KNOWN,'reason':row.get('reason',row.get('decision_reason',row.get('specific_question',row.get('note',row.get('decision',row.get('conclusion')))))),
           'review_evidence':review_evidence,'artifact_evidence':artifact_evidence,'proof_evidence':proof,
           'source_sha256':source_hash,'source_hash_binding':source_binding,
           'style':first_value(row,meta,('viewed_style','style','styles')) or 'singleline (scope text remains authoritative)',
           'pixels':first_value(row,meta,('viewed_pixels','viewed_px','render_px','sizes_px','size','comparison_px')),
           'scope':first_value(row,meta,('scope','review_method','method')),
           'raw_record':row,'raw_metadata':meta,'certification':'not-certified'}
    return event


def merge_history(old,new):
    result=list(old)
    seen={e['event_id'] for e in result}
    for event in new:
        if event['event_id'] not in seen:
            result.append(event);seen.add(event['event_id'])
    return result


def summarize(inventory,history):
    grouped=defaultdict(list)
    for event in history:
        grouped[event['text']].append(event)
    rows=[]
    for text,item in inventory.items():
        events=grouped[text]
        # First event from each baseline review file is the original verdict.
        original={}
        for event in events:
            if event['phase'] in ('baseline','duplicate-baseline'):
                original.setdefault(event['review_file'],event)
        baselines=[e for e in original.values() if e['phase']=='baseline']
        duplicates=[e for e in original.values() if e['phase']=='duplicate-baseline']
        after=[e for e in events if e['phase']=='after']
        additional=[e for e in events if e['phase']=='additional']
        status=conservative_status([e for e in events if e['phase'] in ('baseline','duplicate-baseline','followup-baseline')])
        rows.append({'text':text,'id':item['id'],'kind':item['kind'],
                     'baseline_status':conservative_status(baselines),
                     'pre_fix_conservative_status':status,'baseline_review_count':len(baselines),
                     'duplicate_review_count':len(duplicates),'after_event_count':len(after),
                     'later_confirmed_defect':any(e['status']=='confirmed-defect' for e in after+additional),
                     'additional_event_count':len(additional),'additional_statuses':sorted({e['status'] for e in additional}),
                     'after_statuses':sorted({e['status'] for e in after}),
                     'history_event_ids':[e['event_id'] for e in events],
                     'resolution':'after-review-available-scope-limited' if after else 'pre-fix-observation-only',
                     'release_certification':'not-certified',
                     'remaining':['post-fix distributed artifact check','all-style and 16/18/24/32 px review',
                                  'variable axes','native OS rendering','independent Japanese typography review']})
    return rows



def collect_final_kanji_reviews(root):
    """Read completed 3-style reviews and the later bounded U+4C17 repair."""
    root=Path(root);base=root/'build/full-proofread-final'
    records=[];documents=[];before=[];latest={};outline=[]
    for section in ('kanji-final-lower','kanji-final-upper'):
        path=base/section/'review.json'
        if not path.exists():
            continue
        doc=json.loads(path.read_text())
        glyphs=doc.get('records',doc.get('glyphs',[]))
        if len(glyphs)!=122 or doc.get('unviewed_count',doc.get('unviewed_requested_cells',0))!=0:
            raise ValueError('Final glyph review is incomplete: '+str(path))
        documents.append((path,doc))
        for glyph in glyphs:
            text=row_text(glyph)
            if len(glyph.get('cases',[]))!=9:
                raise ValueError('Expected 9 viewed cases per glyph: '+str(text))
            for case in glyph['cases']:
                if not case.get('viewed'):
                    raise ValueError('Unviewed final case: '+str(text))
                size=case.get('nominal_font_px',case.get('size_px'))
                style=case['style'];status=case.get('observation_status',case.get('status'))
                shape=case.get('structure_status')
                if not shape:
                    shape='confirmed-structural-defect' if 'structurally-defective' in status or status=='confirmed-structural-defect' else 'no-obvious-new-structural-defect' if size==160 else 'not-a-structural-certification-at-small-size'
                artifact=doc.get('artifacts',{}).get(style,{})
                row={'text':text,'status':status,'readability_status':status,'structure_status':shape,
                     'review_axis':'normal-size-outline-clearance' if size==160 and shape=='unresolved-outline-clearance' else 'final-render-observation',
                     'reason':case.get('reason',glyph.get('observation_note')),'viewed_style':style,'viewed_px':size,
                     'actually_viewed':True,'observation_scale':case.get('observation_scale',case.get('display_enlargement')),
                     'viewed_image':case.get('sheet_path',glyph.get('sheet')),
                     'viewed_image_sha256':case.get('sheet_sha256'),
                     'artifact':case.get('font_snapshot_path',artifact.get('path')),
                     'artifact_sha256':case.get('font_sha256',artifact.get('sha256',doc.get('font_bindings',{}).get(style))),
                     'scope':doc.get('scope')+'; actual TTF only, three styles at 160/24/32px; other styles and SJPB not covered',
                     'artifact_generation':'full-TTF snapshot before the later U+4C17 local correction'}
                before.append(row);latest[(text,style,size)]=row
                records.append((path,section+'/review.json#render-case',len(records),row))
                if shape=='confirmed-structural-defect':
                    structural=dict(row,status='confirmed-defect',review_axis='structure')
                    records.append((path,section+'/review.json#structure-defect',len(records),structural))
                if size==160 and shape=='unresolved-outline-clearance':
                    outline.append({'text':text,'id':'+'.join(f'U+{ord(c):04X}' for c in text),'style':style,'nominal_px':160,
                                    'reason':row['reason'],'classification':'normal-size-outline-clearance-not-confirmed-missing-stroke',
                                    'artifact_sha256':row['artifact_sha256'],'proof_sha256':row['viewed_image_sha256']})
    repair_path=base/'kanji-final-lower/4c17-correction/repair.json'
    if repair_path.exists():
        doc=json.loads(repair_path.read_text());documents.append((repair_path,doc));text=doc['character']
        if text!='䰗' or len(doc.get('render_observations',[]))!=9 or not doc.get('source_frozen'):
            raise ValueError('Expected frozen bounded U+4C17 repair with 9 reviewed cases')
        for i,case in enumerate(doc['render_observations']):
            if not case.get('viewed'):
                raise ValueError('Unviewed U+4C17 repair case')
            size=case['size'];style=case['style'];font=repair_path.parent/(style+'.ttf')
            row={'text':text,'status':case['status'],'readability_status':case['status'],
                 'structure_status':'no-obvious-new-structural-defect' if size==160 else 'not-a-structural-certification-at-small-size',
                 'review_axis':'final-render-observation','reason':'Bounded U+4C17 repair observed; source mapping and local proof in repair.json',
                 'viewed_style':style,'viewed_px':size,'actually_viewed':True,'observation_scale':case.get('scale'),
                 'viewed_image':str(repair_path.parent/case['sheet']),'artifact':str(font),'artifact_sha256':sha(font),
                 'source_sha256':doc['source_sha256'],'scope':doc['visual_status']+'; local repair proof, full redistributed file rebind remains separate',
                 'primary_reference':doc['source_reference'],'artifact_generation':'later local U+4C17 repair proof'}
            latest[(text,style,size)]=row
            records.append((repair_path,'kanji-final-lower/4c17-correction/repair.json#render-case',i,row))
        large=next(r for r in latest.values() if r['text']==text and r['viewed_style']=='singleline' and r['viewed_px']==160)
        structural=dict(large,status='reported-structural-defect-corrected',review_axis='structure',reason='Latest bounded repair restores both 鬥 crowns and the internal 亀 upper-box middle bar and central stem; actual local proof viewed.')
        records.append((repair_path,'kanji-final-lower/4c17-correction/repair.json#structure-after',0,structural))
    all_cases=list(latest.values())
    if documents and (len(before)!=2196 or len(all_cases)!=2196):
        raise ValueError('Both completed 122-glyph reviews are required before publication')
    summary={'scope':'244 changed kanji identities; three actual static TTF styles at nominal 160/24/32px only',
             'targets':len({r['text'] for r in all_cases}),'cases':len(all_cases),'actually_viewed_cases':len(all_cases),'unviewed_cases':0,
             'before_snapshot_status_counts':dict(Counter(r['status'] for r in before)),
             'latest_status_counts':dict(Counter(r['status'] for r in all_cases)),
             'latest_by_nominal_size':{str(size):dict(Counter(r['status'] for r in all_cases if r['viewed_px']==size)) for size in (160,24,32)},
             'local_repair_superseded_case_count':9 if repair_path.exists() else 0,
             'normal_size_outline_clearance_cases':outline,
             'normal_size_outline_clearance_case_count':len(outline),
             'other_styles_and_sjpb':'not reviewed in this additional round','native_os':'not tested',
             'full_family_binding':'Original full-TTF snapshots remain pinned; later local U+4C17 proof is separate, final regenerated file binding pending',
             'sources':[{'file':str(path.relative_to(root)),'sha256':sha(path)} for path,_ in documents]}
    return records,all_cases,summary

def run(root,review_dir,inventory_path,output):
    root,review_dir,inventory_path,output=map(Path,(root,review_dir,inventory_path,output))
    output.mkdir(parents=True,exist_ok=True)
    store=EvidenceStore(root,output)
    inventory_evidence=store.preserve(inventory_path)
    with gzip.open(inventory_path,'rt',encoding='utf-8') as f:
        inventory={r['text']:r for r in map(json.loads,f)}
    history_path=output/'history.jsonl.gz'
    old=[]
    if history_path.exists():
        with gzip.open(history_path,'rt',encoding='utf-8') as f:
            old=[json.loads(line) for line in f]
    current=[];inputs=[];ignored=[]
    for path in sorted(review_dir.glob('*.json')):
        document=json.loads(path.read_text())
        rows,meta=extract_rows(document)
        if not rows:
            ignored.append(path.name);continue
        evidence=store.preserve(path)
        count=0
        for i,row in enumerate(rows):
            event=normalize(row,meta,path.name,i,store,inventory,evidence)
            if event:
                current.append(event);count+=1
                correction=row.get('correction',{})
                if correction.get('after_image') and correction.get('post_repair_status'):
                    after_row={'text':row_text(row),'status':'reported-structural-defect-corrected',
                               'declared_after_status':correction['post_repair_status'],
                               'reason':correction.get('confirmed_removed_error'),
                               'source_geometry_sha256':correction.get('post_repair_paths_sha256'),
                               'artifact':correction.get('after_ttf'),'artifact_sha256':correction.get('after_ttf_sha256'),
                               'viewed_image':correction['after_image'],'viewed_image_sha256':correction.get('after_image_sha256'),
                               'scope':'Declared local source correction, actual post-repair proof; final distribution binding pending',
                               'viewed_px':220,'viewed_style':'singleline'}
                    current.append(normalize(after_row,{},path.name+'#correction-after',i,store,inventory,evidence));count+=1
                repair=row.get('repair',{})
                sections={k:repair[k] for k in ('large_size_recheck','small_size_recheck') if k in repair}
                if repair.get('large_size_status'):
                    sections['large_size_recheck']={'status':repair['large_size_status'],'viewed_png':repair.get('viewed_comparison_image'),'render_px':repair.get('comparison_pixels')}
                if isinstance(repair.get('small_size_review'),dict):
                    small=repair['small_size_review']
                    sections['small_size_recheck']=dict(small,status='reported-small-size-inspection-with-limits',actual_images_viewed=small.get('images_actually_viewed'),warning=small.get('result'))
                if repair.get('large_size_comparison'):
                    sections['large_size_recheck']={'status':repair.get('status','reported-structural-repair'),'viewed_png':repair['large_size_comparison'],'render_px':repair.get('large_size_px')}
                if repair.get('small_size_images_actually_viewed'):
                    sections['small_size_recheck']={'status':'reported-small-size-inspection-with-limits','actual_images_viewed':repair['small_size_images_actually_viewed'],'sizes_px':repair.get('small_sizes_px'),'warning':repair.get('small_size_result')}
                remediation=row.get('remediation',{})
                if remediation.get('viewed_after'):
                    sections['large_size_recheck']={'status':remediation.get('state','reported-local-repair'),'viewed_png':remediation['viewed_after'],'warning':remediation.get('small_size')}
                for section,recheck in sections.items():
                    if not isinstance(recheck,dict) or 'status' not in recheck:
                        continue
                    derived=dict(recheck,text=row_text(row),source_geometry_sha256=repair.get('geometry_sha256'),
                                 viewed_image=recheck.get('actual_images_viewed',recheck.get('viewed_png')),
                                 scope='Nested repair '+section+'; source/proof recheck, NOT regenerated release certification; '+repair.get('scope',''),
                                 reason=recheck.get('warning',repair.get('reason',repair.get('note'))))
                    nested=normalize(derived,{'parent_review_file':path.name},path.name+'#'+section+'-after',i,store,inventory,evidence)
                    if nested:
                        current.append(nested);count+=1
        inputs.append({'file':str(path),'sha256':sha(path),'records':count,'snapshot':evidence['snapshot']})
    # These reviewer-authored files explicitly state actual 200px viewing.
    # Merely generated bitmap/outline reports are deliberately not imported.
    for directory in ('middle-corrections','middle-recheck-corrections'):
        path=review_dir.parent/directory/'review-status.json'
        if not path.exists():
            continue
        document=json.loads(path.read_text())
        cells=document.get('cells',[])
        scope=document.get('large_ttf_scope','')
        if not cells or 'viewed' not in scope.lower():
            continue
        evidence=store.preserve(path)
        targets=sorted({row_text(cell) for cell in cells if row_text(cell)})
        for index,text in enumerate(targets):
            large_images=[str(p.relative_to(root)) for p in sorted(path.parent.glob('large-*.png'))]
            artifact=path.parent/'singleline.ttf'
            row={'text':text,'status':'reported-structural-defect-corrected',
                 'reason':scope,'scope':scope+' Local proof only; final regenerated artifact binding pending.',
                 'viewed_image':large_images,'viewed_px':200,'viewed_style':'local 8-style proof',
                 'artifact':str(artifact),'artifact_sha256':sha(artifact) if artifact.exists() else None}
            event=normalize(row,{},directory+'/review-status.json#large_size_recheck-after',index,store,inventory,evidence)
            current.append(event)
        for index,cell in enumerate(cells):
            for kind in ('ttf','bitmap'):
                if kind+'_status' not in cell:
                    continue
                row=dict(cell,status=cell[kind+'_status'],scope=document.get('small_scope'),viewed_px=cell.get('px'))
                event=normalize(row,{},directory+'/review-status.json#small_size-'+kind+'-after',index,store,inventory,evidence)
                if event:
                    current.append(event)
        inputs.append({'file':str(path),'sha256':sha(path),'records':len(targets)+len(cells)*2,'snapshot':evidence['snapshot']})
    final_records,_,_=collect_final_kanji_reviews(root)
    final_inputs={}
    for path,name,index,row in final_records:
        evidence=store.preserve(path)
        event=normalize(row,{},name,index,store,inventory,evidence)
        if event:
            current.append(event)
        final_inputs[str(path)]={'file':str(path),'sha256':sha(path),'snapshot':evidence['snapshot'],'records':final_inputs.get(str(path),{}).get('records',0)+1}
    inputs.extend(final_inputs.values())
    history=merge_history(old,current)
    if len(history)>len(old) or not history_path.exists():
        history_temp=history_path.with_name(history_path.name+'.tmp')
        with gzip.open(history_temp,'wt',encoding='utf-8') as f:
            for event in history:
                f.write(json.dumps(event,ensure_ascii=False,separators=(',',':'))+'\n')
        history_temp.replace(history_path)
    # Keep first-capture history immutable. A separate current normalization
    # can improve schema/binding interpretation without replacing raw verdicts.
    current_by_id={event['event_id']:event for event in current}
    history=[current_by_id.get(event['event_id'],event) for event in history]
    with gzip.open(output/'normalized-history.jsonl.gz','wt',encoding='utf-8') as f:
        for event in history:
            f.write(json.dumps(event,ensure_ascii=False,separators=(',',':'))+'\n')
    rows=summarize(inventory,history)
    with gzip.open(output/'glyph-review-history.jsonl.gz','wt',encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
    counts=Counter(r['pre_fix_conservative_status'] for r in rows)
    baseline_counts=Counter(r['baseline_status'] for r in rows)
    remaining=[r for r in rows if r['pre_fix_conservative_status']!='no-obvious-structural-defect']
    (output/'remaining-pre-fix-findings.json').write_text(json.dumps(remaining,ensure_ascii=False,indent=2))
    fields=['id','text','kind','baseline_status','pre_fix_conservative_status','baseline_review_count','duplicate_review_count','after_event_count','after_statuses','additional_event_count','additional_statuses','resolution','release_certification']
    with (output/'coverage.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for row in rows:
            writer.writerow({k:';'.join(row[k]) if isinstance(row[k],list) else row[k] for k in fields})
    # Count only each original review and preserve its own scope; duplicates
    # never increase distinct coverage, and after events never erase findings.
    manifest={'schema_version':1,'snapshot_role':'pre-fix baseline with separately scoped after history',
              'source_inventory_evidence':inventory_evidence,
              'targets':len(inventory),'baseline_covered':sum(r['baseline_review_count']>0 for r in rows),
              'baseline_missing':[r['id'] for r in rows if not r['baseline_review_count']],
              'baseline_counts':dict(baseline_counts),'pre_fix_conservative_counts':dict(counts),
              'duplicate_baseline_targets':sum(r['duplicate_review_count']>0 for r in rows),
              'after_reviewed_targets':sum(r['after_event_count']>0 for r in rows),
              'after_review_events':sum(r['after_event_count'] for r in rows),
              'additional_reviewed_targets':sum(r['additional_event_count']>0 for r in rows),
              'followup_baseline_counts':dict(Counter(e['status'] for e in history if e['phase']=='followup-baseline')),
              'additional_counts':dict(Counter(e['status'] for e in history if e['phase']=='additional')),
              'remaining_full_release_certification_targets':len(inventory),
              'later_confirmed_defect_targets':sum(r['later_confirmed_defect'] for r in rows),
              'after_counts':dict(Counter(e['status'] for e in history if e['phase']=='after')),
              'history_events':len(history),'current_input_events':len(current),'input_files':inputs,'ignored_summary_files':ignored,
              'out_of_inventory_events':[e['event_id'] for e in history if e['text'] not in inventory],
              'evidence_binding_counts':dict(Counter(p['binding'] for e in history for p in e['proof_evidence'])),
              'artifact_binding_counts':dict(Counter(e['artifact_evidence']['binding'] for e in history)),
              'unknown_statuses':dict(Counter(e['status'] for e in history if not e['known_status'])),
              'baseline_scope':'singleline 64 px first visual screen, some targeted larger details; not typographic certification',
              'unconfirmed':['full 10-style visual coverage','full 16/18/24/32 px coverage','variable axis space','native OS rendering','post-fix release artifact certification'],
              'certified_pass_count':0,'japanese_proofreading_certified':False,
              'history_policy':'append-only event IDs; first baseline verdict per reviewer remains original; all after verdicts remain separate and scoped',
              'source_provenance_warning':'Audit-time source hashes are NOT verified as the generator source of baseline artifacts. Baseline source reference: repository commit 911326b and original glyph-provenance.json.gz; exact rebuild linkage remains separately unverified.',
              'generator_sha256':sha(__file__)}
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    cards=[]
    event_lookup={e['event_id']:e for e in history}
    for r in [r for r in rows if r['pre_fix_conservative_status']!='no-obvious-structural-defect' or r['later_confirmed_defect']]:
        events=[event_lookup[i] for i in r['history_event_ids']]
        details=[]
        for e in events:
            images=' '.join(f'<a href="{html.escape(p["snapshot"])}">proof</a>' for p in e['proof_evidence'] if p.get('snapshot'))
            details.append('<li>'+html.escape(e['phase']+' / '+e['status']+' / '+str(e['reason']))+' '+images+'</li>')
        cards.append('<details><summary>'+html.escape(r['id']+' '+r['text']+' : '+r['pre_fix_conservative_status'])+'</summary><ul>'+''.join(details)+'</ul></details>')
    document='''<!doctype html><meta charset="utf-8"><title>Scoped visual review history</title><style>body{font:16px sans-serif;max-width:1100px;margin:2em auto}summary{padding:.4em}li{margin:.5em}aside{background:#fff0c7;padding:1em}</style><h1>Visual review history</h1><aside>NO blanket pass. Baseline is a singleline 64 px initial structural screen. An after review does not overwrite the original finding and does not certify distributed post-fix files, all styles/sizes, variable axes or native OS. Unpinned evidence is explicitly labelled in history.</aside>'''
    document+=f'<p>Baseline coverage: {manifest["baseline_covered"]}/{len(inventory)} unique identities. Duplicate-review targets: {manifest["duplicate_baseline_targets"]}. After-review targets: {manifest["after_reviewed_targets"]}.</p>'
    document+='<p>Original baseline: '+html.escape(json.dumps(dict(baseline_counts)))+'</p><p>Pre-fix conservative findings including duplicate reviews: '+html.escape(json.dumps(dict(counts)))+'</p>'
    document+='<p><a href="manifest.json">Counts and limits</a> | <a href="coverage.csv">Per-glyph CSV</a> | <a href="history.jsonl.gz">Full immutable-event history</a> | <a href="normalized-history.jsonl.gz">Current schema-normalized history</a> | <a href="glyph-review-history.jsonl.gz">Per-glyph history links</a> | <a href="remaining-pre-fix-findings.json">Pre-fix findings remaining</a> | <a href="../index.html">All proof sheets</a></p><h2>Pre-fix findings and scoped later evidence</h2>'+''.join(cards)
    (output/'index.html').write_text(document)
    parent_index=output.parent/'index.html'
    if parent_index.exists() and output.name=='review-merge':
        parent_html=parent_index.read_text()
        if 'review-merge/index.html' not in parent_html:
            parent_html += '<p><a href="review-merge/index.html">Scoped visual review report and preserved before/after evidence</a></p>'
            parent_index.write_text(parent_html)
    print(json.dumps({k:manifest[k] for k in ('targets','baseline_covered','baseline_counts','pre_fix_conservative_counts','duplicate_baseline_targets','after_reviewed_targets','history_events')},ensure_ascii=False))
    return manifest



def stage_rank(event):
    """Explicit review-stage order, never filesystem mtime or a pass heuristic."""
    name=event['review_file'].split('#')[0]
    if '4c17-correction/repair.json' in name:
        rank=250
    elif name.startswith('kanji-final-'):
        rank=300
    elif name=='known-component-descendants.json':
        rank=90
    elif name=='deep3-fa20-independent-recheck.json':
        rank=185  # explicitly supersedes the earlier deep3 source claim
    elif name in ('elephant-propagation.json','longevity-propagation.json','variant-pairs.json'):
        rank=80
    elif name.startswith('deep-structural-group-'):
        rank=60
    elif name=='music-design-decision.json':
        rank=60
    elif name in BASELINE:
        rank=0
    elif name=='non-japanese-ids.json':
        rank=10
    elif name=='kanji-uncertain-resolution.json':
        rank=40
    elif name in ('kanji-upper-recheck-after.json','nonkanji-accent-after.json','nonkanji-uncertain-followup.json'):
        rank=30
    elif 'recheck' in name:
        rank=20
    else:
        rank=15
    if '#large_size_recheck-after' in event['review_file']:
        rank+=1
    if event['phase']=='after' and 'small_size' not in event['review_file']:
        rank+=100  # corrected-source proof outranks a later look at the OLD artifact
    return rank



def small_size_state(events):
    """Keep actual-view reports, difficulty, explicit non-review and unknown apart."""
    viewed=[];difficult=[];explicit_unviewed=[];cases=set()
    for event in events:
        raw=event.get('raw_record',{})
        nested=raw.get('small_size_review',raw.get('style_size_review',{}))
        pixels=event.get('pixels',raw.get('size'))
        pixels=pixels if isinstance(pixels,list) else [pixels] if pixels is not None else []
        if not pixels:
            pixels=nested.get('sizes_px',nested.get('sizes',nested.get('sizes_physically_viewed',[])))
        small=[p for p in pixels if isinstance(p,(int,float)) and p<=32]
        reported=bool('small_size' in event['review_file'] or raw.get('all_small_proofs_viewed') or raw.get('actual_images_viewed') or raw.get('images_actually_viewed') or raw.get('review_completed') or raw.get('inspection_state')=='visually-reviewed' or nested.get('all_eight_style_sheets_actually_viewed') or nested.get('actual_images_viewed') or nested.get('styles_physically_viewed'))
        propagation=raw.get('style_size_reviews',[])
        if propagation:
            reported=any(c.get('before_after_actually_viewed') and c.get('size_px',999)<=32 for c in propagation)
            for c in propagation:
                if c.get('before_after_actually_viewed') and c.get('size_px',999)<=32:
                    cases.add((c.get('style','unknown'),c['size_px']))
        if (small or reported) and not (pixels and min(pixels)>32):
            viewed.append(event)
            if event['status'] in ('uncertain-small-size','confirmed-defect','uncertain','difficult','difficult-and-structurally-defective') and (small or 'small_size' in event['review_file']):
                difficult.append(event)
            styles=event.get('style') or nested.get('styles',nested.get('styles_physically_viewed'))
            styles=styles if isinstance(styles,list) else [styles]
            for style in styles:
                for pixel in small:
                    cases.add((str(style),pixel))
        elif raw.get('unreviewed_sizes') or 'not assessed' in str(raw.get('small_sizes','')).lower():
            explicit_unviewed.append(event)
    if difficult:
        state='viewed-specific-difficulty-or-uncertainty'
    elif viewed:
        state='viewed-no-obvious-defect-in-recorded-cases' if all(e['status']=='no-obvious-structural-defect' for e in viewed) else 'viewed-scope-limited-readability-not-certified'
    elif explicit_unviewed:
        state='explicitly-not-viewed-in-recorded-scope'
    else:
        state='unknown'
    return {'state':state,'review_event_ids':[e['event_id'] for e in viewed],
            'difficulty_event_ids':[e['event_id'] for e in difficult],
            'explicit_nonreview_event_ids':[e['event_id'] for e in explicit_unviewed],
            'distinct_recorded_style_size_cases':len(cases),
            'recorded_style_size_cases':[list(c) for c in sorted(cases)],
            'full_repertoire_all_style_size_certification':False}

def latest_rows(inventory, history):
    grouped=defaultdict(list)
    for e in history:
        grouped[e['text']].append(e)
    original_rows={r['text']:r for r in summarize(inventory,history)}
    results=[]
    for text,item in inventory.items():
        events=grouped[text]
        baseline_original={}
        candidates=[]
        for ordinal,e in enumerate(events):
            if e.get('raw_record',{}).get('review_axis') in ('final-render-observation','normal-size-outline-clearance') or 'small_size' in e['review_file'] or 'nonkanji-final-pen' in e['review_file'] or 'nonkanji-small' in e['review_file']:
                continue  # readability observations cannot replace structure
            if e['review_file'] in BASELINE:
                if e['review_file'] in baseline_original:
                    continue
                baseline_original[e['review_file']]=e
            candidates.append((stage_rank(e),ordinal,e))
        latest=max(candidates,key=lambda x:(x[0],x[1]))[2] if candidates else None
        after=[e for _,_,e in candidates if e['phase']=='after']
        latest_after=max(enumerate(after),key=lambda pair:(stage_rank(pair[1]),pair[0]))[1] if after else None
        status=latest['status'] if latest else 'not-reviewed'
        repair_verdicts={'no-obvious-structural-defect','reported-topology-defect-addressed','specific-structural-defect-addressed','reported-structural-defect-corrected','structure-reviewed-large-size','repaired-structure-reviewed-large-size','confirmed-structural-defect-repaired','confirmed-layout-defect-repaired','corrected-japanese-source-distinction'}
        corrected=(latest is not None and latest['phase']=='after' and (status in repair_verdicts or status.startswith('local-repair-verified-'))) or status=='confirmed-defect-repaired'
        decision='reported-corrected-limited-review' if corrected else 'intentional-design-limitation' if latest and latest.get('raw_record',{}).get('triage')=='specification-decision' else status
        remaining=(latest.get('reason') or 'Specific question not supplied') if status in ('uncertain','confirmed-defect','not-reviewed') and not corrected and decision!='intentional-design-limitation' else ''
        proofs=[]
        for e in [latest,latest_after]:
            if e:
                proofs.extend({'sha256':p.get('sha256'),'declared_sha256':p.get('declared_sha256'),'binding':p['binding']} for p in e['proof_evidence'])
        original=original_rows[text]
        references={k:latest.get('raw_record',{}).get(k) for k in ('primary_reference','official_reference','reference_url','primary_url','j_source_ids','j_source_id','j_source','unicode_version','pdf_page_1_based','primary_pdf_page','pdf_page') if k in latest.get('raw_record',{})} if latest else {}
        source_url=latest.get('raw_record',{}).get('source') if latest else None
        if isinstance(source_url,str) and source_url.startswith('https://'):
            page=latest.get('raw_record',{}).get('pdf_page')
            references.setdefault('primary_url',source_url+('#page='+str(page) if page and '#' not in source_url else ''))
        results.append({'id':item['id'],'text':text,'kind':item['kind'],
                        'original_baseline_status':original['baseline_status'],
                        'original_conservative_status':original['pre_fix_conservative_status'],
                        'latest_structural_decision':decision,'latest_raw_status':status,
                        'latest_reason':latest.get('reason') if latest else None,
                        'latest_review_file':latest['review_file'] if latest else None,
                        'latest_event_id':latest['event_id'] if latest else None,
                        'latest_review_scope':latest.get('scope') if latest else None,
                        'reference_identifiers':references,
                        'limited_after_status':latest_after['status'] if latest_after else None,
                        'limited_after_event_id':latest_after['event_id'] if latest_after else None,
                        'remaining_specific_doubt':remaining,
                        'artifact_sha256':(latest.get('artifact_evidence',{}).get('declared_sha256') or latest.get('artifact_evidence',{}).get('sha256')) if latest else None,
                        'artifact_evidence_binding':latest.get('artifact_evidence',{}).get('binding') if latest else None,
                        'source_sha256':latest.get('source_sha256') if latest else None,
                        'source_hash_binding':latest.get('source_hash_binding') if latest else None,
                        'proof_hashes':proofs,'history_event_ids':[e['event_id'] for e in events],
                        'final_distributed_artifact_binding':'pending',
                        'small_size_readability':small_size_state(events)['state'],
                        'small_size_review':small_size_state(events),'all_style_variable_native_os':'not-certified'})
    return results



def sanitize_public(value):
    """Publish selected review outcomes, never private paths or source images."""
    if isinstance(value,list):
        return [sanitize_public(v) for v in value]
    if isinstance(value,dict):
        result={}
        for key,item in value.items():
            if key in ('agent_id','worker_id','primary_image_internal_only','row_text','clip'):
                continue
            if key in ('primary_reference','official_reference') and isinstance(item,dict):
                item={k:v for k,v in item.items() if k in ('url','verified_page_url','page_index','page_number','j_source','unicode_version')}
            result[key]=sanitize_public(item)
        return result
    if isinstance(value,str):
        value=value.replace(str(ROOT)+'/', '')
        value=re.sub(r'/root/[A-Za-z0-9_./-]+','assistant-review',value)
        value=re.sub(r'/(?:workspace|tmp)/[^\s\"<>;,]+',lambda m:'local-reference:'+Path(m.group(0)).name,value)
        value=re.sub(r'/usr/share/fonts/[^\s\"<>;,]+',lambda m:'reference-font:'+Path(m.group(0)).name,value)
        value=re.sub(r'\b(?:worker|subagent|agent)[-_:#][A-Za-z0-9_./-]+','assistant-review',value,flags=re.I)
        value=value.replace('parent task handoff','review source summary').replace('pending parent integration','pending integration').replace('pending coordinator integration','pending integration')
        return value
    return value


def final_pen_reviews(proof_root):
    styles=('singleline','pc98-mincho','gothic','italian','serif','italic','subscript','superscript')
    grouped=defaultdict(list);files=[];seen=set();counts=Counter();viewed=0
    for style in styles:
        path=Path(proof_root)/'reviews'/('nonkanji-final-pen-'+style+'.json')
        if not path.exists():
            continue
        records=json.loads(path.read_text())
        files.append({'review_file':path.name,'sha256':sha(path),'records':len(records)})
        for r in records:
            key=(row_text(r),style,r.get('size'),r.get('kind'))
            if key in seen:
                raise ValueError('Duplicate final-pen visual case: '+str(key))
            seen.add(key)
            is_viewed=bool(r.get('review_completed') or r.get('inspection_state')=='visually-reviewed' or r.get('visual_review')=='viewed')
            viewed+=is_viewed;counts[r['status']]+=1
            kind=r.get('kind')
            grouped[row_text(r)].append({'style':style,'size':r.get('size'),'format':kind,'status':r['status'],
                  'actually_viewed':is_viewed,'uncertainty_type':r.get('uncertainty_type'),'reason':r.get('reason'),
                  'artifact_sha256':r.get(str(kind)+'_sha256',r.get('artifact_sha256')),
                  'proof_sha256':r.get('viewed_image_sha256'),
                  'renderer_source_sha256':r.get('source_geometry_py_sha256'),
                  'scope':'Final-pen subset proof; final full-family artifact binding pending'})
    summary={'scope':'219 nonkanji identities x 8 styles x 4 sizes x 2 formats; actual subset proof viewing, not full repertoire certification',
             'expected_cases':14016,'recorded_cases':len(seen),'actually_viewed_cases':viewed,'not_viewed_cases':len(seen)-viewed,
             'missing_cases':14016-len(seen),'status_counts':dict(counts),'review_sources':files,
             'uncertain_means':'Observed native-size readability limitation; not unviewed work',
             'final_distributed_artifact_binding':'pending'}
    return grouped,summary

def export_compact(proof_root, reports):
    proof_root,reports=Path(proof_root),Path(reports)
    merged=proof_root/'review-merge'
    with gzip.open(proof_root/'source-inventory.jsonl.gz','rt') as f:
        inventory={r['text']:r for r in map(json.loads,f)}
    with gzip.open(merged/'normalized-history.jsonl.gz','rt') as f:
        history=[json.loads(line) for line in f]
    rows=latest_rows(inventory,history)
    native,native_summary=final_pen_reviews(proof_root)
    _,final_cases,final_summary=collect_final_kanji_reviews(ROOT)
    final_grouped=defaultdict(list)
    for case in final_cases:
        final_grouped[case['text']].append(case)
    outline_grouped=defaultdict(list)
    for case in final_summary['normal_size_outline_clearance_cases']:
        outline_grouped[case['text']].append(case)
    for row in rows:
        row['final_three_style_ttf_cases']=final_grouped.get(row['text'],[])
        row['normal_size_outline_clearance_cases']=outline_grouped.get(row['text'],[])
        row['normal_size_outline_clearance_state']='unresolved-at-160px' if row['normal_size_outline_clearance_cases'] else 'no-specific-finding-in-reviewed-scope' if row['final_three_style_ttf_cases'] else 'not-reviewed-in-this-round'
    deep_entries=[]
    for path in sorted((proof_root/'reviews').glob('deep-structural-group-*.json')):
        entries,_=extract_rows(json.loads(path.read_text()));deep_entries.extend(entries)
    if len({row_text(r) for r in deep_entries})!=len(deep_entries):
        raise ValueError('Deep-review groups overlap; resolve before publishing counts')
    deep_fixed=sum(r.get('status','').startswith('repaired-') or bool(r.get('correction',{}).get('post_repair_status')) for r in deep_entries)
    deep_normal=sum(r.get('status') in ('structure-confirmed-no-change','no-obvious-structural-defect') for r in deep_entries)
    deep_summary={'reviewed_identities':len(deep_entries),'local_repairs_with_scoped_recheck':deep_fixed,
                  'structurally_normal_no_change':deep_normal,'unresolved':len(deep_entries)-deep_fixed-deep_normal,
                  'full_distribution_binding':'pending'}
    for row in rows:
        cases=native.get(row['text'],[])
        row['final_pen_native_review']={'cases':len(cases),'viewed':sum(c['actually_viewed'] for c in cases),
                                       'status_counts':dict(Counter(c['status'] for c in cases))}
        row['final_pen_native_cases']=cases
    merged_manifest=json.loads((merged/'manifest.json').read_text())
    # Full evidence-rich handoff for the next structural review, not a closure.
    by_id={e['event_id']:e for e in history}
    remaining=[]
    for row in rows:
        if not row['remaining_specific_doubt']:
            continue
        event=by_id[row['latest_event_id']]
        raw=event.get('raw_record',{})
        relevant=[by_id[i] for i in row['history_event_ids']]
        remaining.append({'text':row['text'],'id':row['id'],'codepoints':[f'U+{ord(c):04X}' for c in row['text']],
                          'latest_status':row['latest_structural_decision'],'specific_question':row['remaining_specific_doubt'],
                          'original_findings':[{'event_id':e['event_id'],'status':e['status'],'reason':e.get('reason'),'review_file':e['review_file']} for e in relevant if e['status'] in ('uncertain','confirmed-defect')],
                          'latest_event_id':event['event_id'],'viewed_images':event['proof_evidence'],
                          'primary_references':{k:raw.get(k,event.get('raw_metadata',{}).get(k)) for k in ('primary_reference','official_reference','reference','reference_face','j_source_ids','unicode_version','ids_identity_context','ids_candidates') if k in raw or k in event.get('raw_metadata',{})},
                          'review_scope':event.get('scope'),
                          'source_flags':{k:raw[k] for k in ('source','source_module','source_fix','source_paths_checked_for_defect','source_structure_checked','source_path_count','repair','remediation','actual_primary_row_viewed','scope_note') if k in raw},
                          'source_sha256':row['source_sha256'],'source_hash_binding':row['source_hash_binding'],
                          'artifact_sha256':row['artifact_sha256'],'artifact_binding':row['artifact_evidence_binding'],
                          'small_size_review':row['small_size_review'],
                          'planned_triage_class':None,'triage_options':['expert-judgment','insufficient-evidence','specification-choice','additional-repair-possible'],
                          'next_review_status':'pending','final_distributed_artifact_binding':'pending'})
    (proof_root/'remaining-structural-review.json').write_text(json.dumps({'schema_version':1,'count':len(remaining),'purpose':'Next concrete structural review; not an end-of-work rationale','entries':remaining},ensure_ascii=False,indent=2))
    reports.mkdir(parents=True,exist_ok=True)
    prefix='full-glyph-proofread-'
    public_rows=sanitize_public(rows)
    payload={'schema_version':1,'targets':len(rows),'glyphs':public_rows,
             'limits':'Latest structural and limited local-repair observations only. Final regenerated release artifact linkage pending. No all-style/size/axes/native-OS certification.'}
    (reports/(prefix+'compact.json.gz')).write_bytes(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    columns=['id','text','kind','original_baseline_status','original_conservative_status','latest_structural_decision','limited_after_status','remaining_specific_doubt','latest_reason','latest_review_file','latest_event_id','limited_after_event_id','artifact_sha256','artifact_evidence_binding','source_sha256','source_hash_binding','final_distributed_artifact_binding','small_size_readability','normal_size_outline_clearance_state','all_style_variable_native_os']
    with (reports/(prefix+'coverage.csv')).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
        for row in public_rows:
            writer.writerow({k:row[k] for k in columns})
    summary={'schema_version':1,'targets':len(rows),'baseline_covered':merged_manifest['baseline_covered'],
             'original_baseline_counts':merged_manifest['baseline_counts'],
             'historical_conservative_counts':merged_manifest['pre_fix_conservative_counts'],
             'latest_structural_counts':dict(Counter(r['latest_structural_decision'] for r in rows)),
             'final_pen_nonkanji_native_review':native_summary,
             'deep_structural_review':deep_summary,
             'final_three_style_kanji_review':final_summary,
             'remaining_normal_size_outline_clearance_case_count':final_summary['normal_size_outline_clearance_case_count'],
             'final_followup_review_sources':[{'file':name,'sha256':sha(proof_root/'reviews'/name)} for name in ('elephant-propagation.json','longevity-propagation.json','known-component-descendants.json','variant-pairs.json','deep3-fa20-independent-recheck.json','music-design-decision.json') if (proof_root/'reviews'/name).exists()],
             'final_layer_interpretation':'Known-component final corrections supersede earlier deep3 source claims; superseded evidence remains in history. Outlined music symbols retain their declared pictogram design and notation limitations; they are not unresolved work.',
             'deep_review_reports':[{"file":p.name,"sha256":sha(p)} for p in sorted((proof_root/'reviews').glob('deep-structural-group-*.json'))],
             'limited_after_counts':dict(Counter(r['limited_after_status'] for r in rows if r['limited_after_status'])),
             'remaining_specific_doubt_count':sum(bool(r['remaining_specific_doubt']) for r in rows),
             'remaining_structural_doubt_count':sum(r['latest_structural_decision'] in ('uncertain','confirmed-defect','not-reviewed') for r in rows),
             'specification_decision_count':sum(r['latest_structural_decision']=='specification-choice-required' for r in rows),
             'intentional_design_limitation_count':sum(r['latest_structural_decision']=='intentional-design-limitation' for r in rows),
             'small_size_review_state_counts':dict(Counter(r['small_size_readability'] for r in rows)),
             'remaining_specific_doubts':[{'id':r['id'],'text':r['text'],'status':r['latest_structural_decision'],'question':r['remaining_specific_doubt'],'event_id':r['latest_event_id']} for r in rows if r['remaining_specific_doubt']],
             'source_change_context':{'centerline_identities':None,'kanji':None,'nonkanji':219,'previous_snapshot_centerline_identities':438,'final_delta_status':'pending final frozen-source inventory comparison','global_anisotropic_pen_change':True,'global_pen_change_scope':'All rendered outlines may be affected; local pre-pen reviews are not final artifact reviews','provenance':'Reported source-change count; independent final rebuild linkage pending'},
             'final_distributed_artifact_binding':'pending','source_allowlist':'pending later addition',
             'continuous_axes_and_native_os':'not-certified','japanese_proofreading_certified':False,
             'latest_selection':'Corrected-source structural after evidence outranks reinspection of the original artifact. Within a state: original baseline < duplicate < recheck < nonkanji followup < Unicode resolution; nested structural after follows its parent. Small-size-only observations cannot replace structural verdicts.',
             'original_history_preserved':True,'history_sha256':sha(merged/'history.jsonl.gz'),
             'normalized_history_sha256':sha(merged/'normalized-history.jsonl.gz'),
             'evidence_archive':'Large PNGs and content-addressed evidence remain separate in build/full-proofread; compact files contain hashes and event IDs only.',
             'files':{name:sha(reports/name) for name in (prefix+'compact.json.gz',prefix+'coverage.csv')}}
    summary=sanitize_public(summary)
    (reports/(prefix+'summary.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    text='Full glyph proofreading: scoped observations\n\n'
    for label,key in [('Original baseline','original_baseline_counts'),('Historical conservative','historical_conservative_counts'),('Latest structure','latest_structural_counts'),('Limited after review','limited_after_counts')]:
        text+=label+': '+json.dumps(summary[key],ensure_ascii=False)+'\n'
    text+='Deep structural review: '+json.dumps(deep_summary,ensure_ascii=False)+'\n'
    text+='Final-pen native-size review: '+str(native_summary['actually_viewed_cases'])+'/'+str(native_summary['expected_cases'])+' cases actually viewed; '+json.dumps(native_summary['status_counts'])+'; unviewed='+str(native_summary['not_viewed_cases'])+'. Readability limitations are separate from structural judgments.\n'
    text+='Additional actual TTF review: '+str(final_summary['actually_viewed_cases'])+' viewed cases across 244 identities / three styles / 160,24,32px. Normal-size outline-clearance cases at160px: '+str(final_summary['normal_size_outline_clearance_case_count'])+' (not small-size-only and not confirmed missing strokes).\n'
    text+='Remaining structural doubts: '+str(summary['remaining_structural_doubt_count'])+'; pending specification choices: '+str(summary['specification_decision_count'])+'; intentional design limitations: '+str(summary['intentional_design_limitation_count'])+'\nFinal distributed artifact binding: PENDING. All styles/small sizes/variable axes/native OS: NOT certified.\n'
    (reports/(prefix+'summary.txt')).write_text(text)
    # A small local report links only the compact deliverables, not bulk evidence.
    links=''.join('<li><a href="'+prefix+ext+'">'+html.escape(ext)+'</a></li>' for ext in ('compact.json.gz','coverage.csv','summary.json','summary.txt'))
    (reports/(prefix+'index.html')).write_text('<!doctype html><meta charset="utf-8"><title>Full glyph proofread summary</title><h1>Scoped full-glyph review</h1><pre>'+html.escape(text)+'</pre><ul>'+links+'</ul>')
    (merged/'latest-structural-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps({k:summary[k] for k in ('targets','latest_structural_counts','remaining_specific_doubt_count')},ensure_ascii=False))
    return summary

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--proof-root',type=Path,default=ROOT/'build/full-proofread')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--public-reports',type=Path,help='Write compact latest-structure report separately from immutable raw review history')
    args=parser.parse_args()
    run(args.root,args.proof_root/'reviews',args.proof_root/'source-inventory.jsonl.gz',args.output or args.proof_root/'review-merge')
    if args.public_reports:
        export_compact(args.proof_root,args.public_reports)


if __name__=='__main__':
    main()
