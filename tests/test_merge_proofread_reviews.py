import gzip
import json
from family.tools.merge_proofread_reviews import EvidenceStore, conservative_status, extract_rows, merge_history, run, sha, summarize


def test_status_never_invents_a_pass():
    assert conservative_status([])=='not-reviewed'
    assert conservative_status([{'status':'passed'}])=='uncertain'
    assert conservative_status([{'status':'uncertain'},{'status':'no-obvious-structural-defect'}])=='uncertain'
    assert conservative_status([{'status':'confirmed-defect'},{'status':'no-obvious-structural-defect'}])=='confirmed-defect'


def test_schema_variants():
    row={'character':'字','status':'uncertain'}
    assert extract_rows([row])[0]==[row]
    assert extract_rows({'glyphs':[row],'scope':'64px'})==([row],{'scope':'64px'})
    assert extract_rows({'entries':[row]})[0]==[row]
    assert extract_rows({'counts':{}})[0]==[]


def test_append_only_history_and_original_verdict():
    old={'event_id':'old','text':'字','phase':'baseline','review_file':'kanji-lower.json','status':'confirmed-defect'}
    new=dict(old,event_id='new',status='no-obvious-structural-defect')
    after=dict(new,event_id='after',phase='after',review_file='after.json')
    history=merge_history([old],[old,new,after])
    assert len(history)==3
    row=summarize({'字':{'id':'U+5B57','kind':'scalar'}},history)[0]
    assert row['baseline_status']=='confirmed-defect'
    assert row['after_event_count']==1
    assert row['release_certification']=='not-certified'


def test_evidence_survives_overwrite(tmp_path):
    file=tmp_path/'proof.png';file.write_bytes(b'before')
    store=EvidenceStore(tmp_path,tmp_path/'out')
    before=sha(file);first=store.preserve(file,before)
    file.write_bytes(b'after')
    fresh=EvidenceStore(tmp_path,tmp_path/'out')
    later=fresh.preserve(file,before)
    assert later['sha256']==before
    assert later['binding']=='declared-hash-verified-snapshot'
    assert (tmp_path/'out'/first['snapshot']).read_bytes()==b'before'


def test_merge_idempotent_and_no_coverage_inflation(tmp_path):
    reviews=tmp_path/'reviews';reviews.mkdir()
    inventory=tmp_path/'source.jsonl.gz'
    with gzip.open(inventory,'wt') as f:
        f.write(json.dumps({'text':'字','id':'U+5B57','kind':'scalar','source_sha256':'abc'})+'\n')
    for name,status in [('kanji-lower.json','uncertain'),('non-japanese-ids.json','confirmed-defect'),('fix-after.json','no-obvious-structural-defect')]:
        (reviews/name).write_text(json.dumps([{'text':'字','status':status,'scope':'singleline 64px'}]))
    out=tmp_path/'merged'
    first=run(tmp_path,reviews,inventory,out)
    first_history=(out/'history.jsonl.gz').read_bytes()
    second=run(tmp_path,reviews,inventory,out)
    assert (out/'history.jsonl.gz').read_bytes()==first_history
    assert first['history_events']==second['history_events']==3
    assert second['baseline_covered']==1
    assert second['duplicate_baseline_targets']==1
    assert second['pre_fix_conservative_counts']=={'confirmed-defect':1}
    assert second['certified_pass_count']==0


def test_hash_mismatch_is_not_silently_bound(tmp_path):
    proof=tmp_path/'proof.png';proof.write_bytes(b'new contents')
    evidence=EvidenceStore(tmp_path,tmp_path/'out').preserve(proof,'0'*64)
    assert evidence['binding']=='declared-hash-mismatch'
    assert evidence['sha256']!='0'*64


def test_after_does_not_fill_missing_baseline():
    event={'event_id':'a','text':'字','phase':'after','review_file':'fix-after.json','status':'no-obvious-structural-defect'}
    row=summarize({'字':{'id':'U+5B57','kind':'scalar'}},[event])[0]
    assert row['baseline_review_count']==0
    assert row['baseline_status']=='not-reviewed'
    assert row['release_certification']=='not-certified'


def test_later_baseline_defect_surfaces_without_rewriting_original():
    old={'event_id':'a','text':'字','phase':'baseline','review_file':'kanji-lower.json','status':'no-obvious-structural-defect'}
    new=dict(old,event_id='b',status='confirmed-defect')
    row=summarize({'字':{'id':'U+5B57','kind':'scalar'}},[old,new])[0]
    assert row['baseline_status']=='no-obvious-structural-defect'
    assert row['pre_fix_conservative_status']=='confirmed-defect'


def test_lower_recheck_schema_preserves_original_and_nested_repair(tmp_path):
    reviews=tmp_path/'reviews';reviews.mkdir()
    inventory=tmp_path/'source.jsonl.gz'
    with gzip.open(inventory,'wt') as f:
        f.write(json.dumps({'text':'字','id':'U+5B57','kind':'scalar','source_sha256':'audit-only'})+'\n')
    (reviews/'kanji-lower.json').write_text(json.dumps([{'text':'字','status':'uncertain'}]))
    recheck={'entries':[{'text':'字','status':'confirmed-defect','viewed_original_font_sha256':'a'*64,
        'repair':{'large_size_status':'specific-structural-defect-addressed','geometry_sha256':'b'*64,
                  'small_size_review':{'result':'No blanket pass','images_actually_viewed':[]}}}]}
    (reviews/'kanji-lower-recheck.json').write_text(json.dumps(recheck))
    m=run(tmp_path,reviews,inventory,tmp_path/'out')
    assert m['baseline_counts']=={'uncertain':1}
    assert m['pre_fix_conservative_counts']=={'confirmed-defect':1}
    assert m['after_reviewed_targets']==1
    assert m['after_review_events']==2
    assert m['certified_pass_count']==0


def test_latest_structure_is_separate_from_original_and_small_size_review():
    from family.tools.merge_proofread_reviews import latest_rows
    inventory={'字':{'id':'U+5B57','kind':'scalar'}}
    base={'event_id':'b','text':'字','phase':'baseline','review_file':'kanji-lower.json','status':'uncertain','reason':'Initial doubt','proof_evidence':[]}
    resolution=dict(base,event_id='r',phase='additional',review_file='kanji-uncertain-resolution.json',status='resolved-no-change',reason='J-source confirms the component')
    small=dict(base,event_id='s',phase='after',review_file='kanji-uncertain-resolution.json#small_size_recheck-after',status='reported-small-size-inspection-with-limits')
    row=latest_rows(inventory,[base,resolution,small])[0]
    assert row['original_baseline_status']=='uncertain'
    assert row['latest_structural_decision']=='resolved-no-change'
    assert row['remaining_specific_doubt']==''
    assert row['limited_after_status'] is None
    assert row['final_distributed_artifact_binding']=='pending'


def test_unknown_after_verdict_cannot_become_corrected():
    from family.tools.merge_proofread_reviews import latest_rows
    event={'event_id':'x','text':'字','phase':'after','review_file':'kanji-upper-recheck-after.json','status':'images-generated','proof_evidence':[]}
    row=latest_rows({'字':{'id':'U+5B57','kind':'scalar'}},[event])[0]
    assert row['latest_structural_decision']=='images-generated'
    assert row['final_distributed_artifact_binding']=='pending'


def test_corrected_source_proof_outranks_later_old_artifact_reinspection():
    from family.tools.merge_proofread_reviews import latest_rows
    before={'event_id':'b','text':'咎','phase':'followup-baseline','review_file':'kanji-lower-recheck.json','status':'confirmed-defect','reason':'Old artifact defect independently confirmed','proof_evidence':[]}
    after=dict(before,event_id='a',phase='after',review_file='non-japanese-ids.json#large_size_recheck-after',status='reported-topology-defect-addressed',reason='Corrected source topology viewed')
    row=latest_rows({'咎':{'id':'U+548E','kind':'scalar'}},[after,before])[0]
    assert row['latest_structural_decision']=='reported-corrected-limited-review'
    assert row['original_conservative_status']=='confirmed-defect'
    assert row['remaining_specific_doubt']==''


def test_small_size_unknown_is_not_unreviewed_or_passed():
    from family.tools.merge_proofread_reviews import small_size_state
    assert small_size_state([])['state']=='unknown'
    e={'event_id':'a','review_file':'kanji-middle.json','status':'uncertain','pixels':64,'style':'singleline','raw_record':{'unreviewed_sizes':'all other sizes'}}
    assert small_size_state([e])['state']=='explicitly-not-viewed-in-recorded-scope'
    small=dict(e,event_id='b',review_file='middle#small_size-after',status='uncertain-small-size',pixels=16,raw_record={})
    assert small_size_state([e,small])['state']=='viewed-specific-difficulty-or-uncertainty'
    assert small_size_state([e,small])['distinct_recorded_style_size_cases']==1


def test_public_sanitization_omits_chart_data_and_internal_paths():
    from family.tools.merge_proofread_reviews import ROOT, sanitize_public
    result=sanitize_public({'path':str(ROOT)+'/family/source.py','temporary':'/tmp/reference.png',
        'reviewer':'/root/task/private_agent','primary_reference':{'url':'https://www.unicode.org/charts/PDF/U4E00.pdf',
        'page_number':3,'image':'private.png','row_text':'raw chart row','clip':[1,2,3,4]}})
    assert result['path']=='family/source.py'
    assert result['temporary']=='local-reference:reference.png'
    assert result['reviewer']=='assistant-review'
    assert set(result['primary_reference'])=={'url','page_number'}


def test_native_final_pen_uncertainty_does_not_replace_structure():
    from family.tools.merge_proofread_reviews import latest_rows
    base={'event_id':'b','text':'A','phase':'baseline','review_file':'nonkanji.json','status':'no-obvious-structural-defect','proof_evidence':[]}
    pixel=dict(base,event_id='p',review_file='nonkanji-final-pen-singleline.json',phase='additional',status='uncertain',pixels=16,raw_record={'inspection_state':'visually-reviewed','size':16})
    row=latest_rows({'A':{'id':'U+0041','kind':'scalar'}},[base,pixel])[0]
    assert row['latest_structural_decision']=='no-obvious-structural-defect'
    assert row['small_size_readability']=='viewed-specific-difficulty-or-uncertainty'


def test_final_component_fix_supersedes_deep3_and_independent_defect():
    from family.tools.merge_proofread_reviews import latest_rows
    old={'event_id':'old','text':'蘒','phase':'after','review_file':'deep-structural-group-3.json#correction-after','status':'reported-structural-defect-corrected','proof_evidence':[]}
    audit=dict(old,event_id='audit',phase='additional',review_file='deep3-fa20-independent-recheck.json',status='confirmed-defect')
    fix=dict(old,event_id='final',review_file='known-component-descendants.json',status='structure-reviewed-large-size')
    inv={'蘒':{'id':'U+FA20','kind':'scalar'}}
    assert latest_rows(inv,[old,audit])[0]['latest_structural_decision']=='confirmed-defect'
    row=latest_rows(inv,[old,audit,fix])[0]
    assert row['latest_event_id']=='final'
    assert row['latest_structural_decision']=='reported-corrected-limited-review'
    assert row['history_event_ids']==['old','audit','final']


def test_music_is_intentional_limit_not_unresolved_queue():
    from family.tools.merge_proofread_reviews import latest_rows
    e={'event_id':'music','text':'♪','phase':'additional','review_file':'music-design-decision.json','status':'uncertain','proof_evidence':[],
       'reason':'Declared outlined pictogram, not conventional filled note notation','raw_record':{'triage':'specification-decision'}}
    row=latest_rows({'♪':{'id':'U+266A','kind':'scalar'}},[e])[0]
    assert row['latest_structural_decision']=='intentional-design-limitation'
    assert row['remaining_specific_doubt']==''
    assert row['latest_raw_status']=='uncertain'


def test_artifact_hash_map_selects_declared_singleline_without_guessing_digest(tmp_path):
    from family.tools.merge_proofread_reviews import EvidenceStore, normalize
    font=tmp_path/'build/static/singleline.ttf';font.parent.mkdir(parents=True);font.write_bytes(b'font')
    m={'artifact_sha256':{'build/static/singleline.ttf':sha(font)}}
    e=normalize({'text':'剥','status':'corrected-japanese-source-distinction'},m,'variant-pairs.json',0,EvidenceStore(tmp_path,tmp_path/'out'),{}, {})
    assert e['artifact_evidence']['sha256']==sha(font)
    assert e['phase']=='after'


def test_160px_outline_difficulty_is_not_a_small_size_or_missing_stroke_verdict():
    from family.tools.merge_proofread_reviews import latest_rows, small_size_state
    base={'event_id':'b','text':'纒','phase':'baseline','review_file':'kanji-upper.json','status':'no-obvious-structural-defect','proof_evidence':[]}
    case=dict(base,event_id='d',review_file='kanji-final-upper/review.json#render-case',phase='additional',status='difficult',pixels=160,
              raw_record={'review_axis':'normal-size-outline-clearance'})
    row=latest_rows({'纒':{'id':'U+7E92','kind':'scalar'}},[base,case])[0]
    assert row['latest_structural_decision']=='no-obvious-structural-defect'
    assert small_size_state([case])['state']=='unknown'


def test_latest_4c17_repair_supersedes_old_full_font_defect():
    from family.tools.merge_proofread_reviews import latest_rows
    old={'event_id':'old','text':'䰗','phase':'additional','review_file':'kanji-final-lower/review.json#structure-defect','status':'confirmed-defect','proof_evidence':[]}
    repaired=dict(old,event_id='new',phase='after',review_file='kanji-final-lower/4c17-correction/repair.json#structure-after',status='reported-structural-defect-corrected')
    row=latest_rows({'䰗':{'id':'U+4C17','kind':'scalar'}},[old,repaired])[0]
    assert row['latest_event_id']=='new'
    assert row['latest_structural_decision']=='reported-corrected-limited-review'
    assert row['history_event_ids']==['old','new']


def test_final_review_cases_replaced_by_local_repair_without_double_count(tmp_path):
    from family.tools.merge_proofread_reviews import collect_final_kanji_reviews
    base=tmp_path/'build/full-proofread-final';styles=['singleline','gothic','serif']
    for index,section in enumerate(['kanji-final-lower','kanji-final-upper']):
        folder=base/section;folder.mkdir(parents=True)
        records=[]
        for i in range(122):
            char='䰗' if index==0 and i==0 else chr(0x4e00+index*122+i)
            cases=[{'style':style,'size_px':size,'viewed':True,'status':'confirmed-structural-defect' if char=='䰗' else 'no-obvious-structural-defect'} for style in styles for size in [160,24,32]]
            records.append({'character':char,'cases':cases,'sheet':'test.png'})
        (folder/'review.json').write_text(json.dumps({'scope':'test review','records':records,'unviewed_count':0}))
    folder=base/'kanji-final-lower/4c17-correction';folder.mkdir()
    for style in styles:(folder/(style+'.ttf')).write_bytes(style.encode())
    repair={'character':'䰗','source_frozen':True,'source_sha256':'a'*64,'visual_status':'actually viewed','source_reference':{},
            'render_observations':[{'style':style,'size':size,'viewed':True,'status':'no-obvious-structural-defect','sheet':'after.png'} for style in styles for size in [160,24,32]]}
    (folder/'repair.json').write_text(json.dumps(repair))
    records,cases,summary=collect_final_kanji_reviews(tmp_path)
    assert summary['cases']==summary['actually_viewed_cases']==2196
    assert summary['local_repair_superseded_case_count']==9
    assert all(c['status']=='no-obvious-structural-defect' for c in cases if c['text']=='䰗')
    assert any(r[3]['status']=='confirmed-defect' for r in records)
