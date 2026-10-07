"""Build the experimental family without modifying any legacy font artifact."""
import argparse,gzip,hashlib,io,json,platform,gc,subprocess
from pathlib import Path
from xml.sax.saxutils import escape
from family.data_loader import load_glyphs
from family.styles import STYLES
from family.font_builder import build_font
from family.bitmap import build_bitmaps
from family.model import glyph_name
from family.repertoire import report

ROOT=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def legacy_check():
    expected=json.loads((ROOT/'family/data/legacy-sha256.json').read_text())
    changed=[p for p,h in expected.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    if changed:raise RuntimeError('Legacy files changed: '+', '.join(changed))
    return {'files':len(expected),'unchanged':True}


def compress_centerlines(svg):
    """Lossless SVGZ with no filename, clock time, or platform-specific header."""
    output=io.BytesIO()
    with gzip.GzipFile(filename='',mode='wb',fileobj=output,compresslevel=9,mtime=0) as stream:
        stream.write(svg)
    return output.getvalue()


def write_centerlines(glyphs,path):
    lines=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">',
        '<title>Project-original centerline glyph collection; experimental composition drafts</title>',
        '<metadata>See coverage.json, glyph-provenance.json.gz and NOTICE.md. This is not an installable SVG font.</metadata>','<defs>']
    for c,g in glyphs.items():
        lines.append(f'<symbol id="{glyph_name(c)}" viewBox="0 0 24 24"><title>{escape(c)}</title>')
        if g.notes.get('negative'):
            mask_id=glyph_name(c)+'-cutout'
            lines.append(f'<mask id="{mask_id}" maskUnits="userSpaceOnUse" x="0" y="0" width="24" height="24"><rect width="24" height="24" fill="white"/>')
            for p in g.paths[1:]:
                data='M'+' L'.join(f'{x:.4f},{y:.4f}' for x,y in p)
                lines.append(f'<path d="{data}" fill="none" stroke="black" stroke-width="0.8"/>')
            lines.append('</mask>')
            data='M'+' L'.join(f'{x:.4f},{y:.4f}' for x,y in g.paths[0])+' Z'
            lines.append(f'<path d="{data}" fill="currentColor" mask="url(#{mask_id})"/>')
            lines.append('</symbol>')
            continue
        for p in g.paths:
            if not p:continue
            data='M'+' L'.join(f'{x:.4f},{y:.4f}' for x,y in p)
            if g.filled:data+=' Z'
            lines.append(f'<path d="{data}" fill="{"currentColor" if g.filled else "none"}" stroke="currentColor" stroke-width="0.6" stroke-linecap="round" stroke-linejoin="round"/>')
        lines.append('</symbol>')
    lines+=['</defs>','</svg>']
    svg=('\n'.join(lines)+'\n').encode('utf-8')
    path=Path(path)
    path.write_bytes(svg)
    path.with_suffix('.svgz').write_bytes(compress_centerlines(svg))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'build/family')
    parser.add_argument('--styles',nargs='+',choices=STYLES,default=list(STYLES))
    parser.add_argument('--bitmap-sizes',type=int,nargs='*',default=[16,18,24,32])
    parser.add_argument('--no-variable',action='store_true')
    parser.add_argument('--reuse-bitmaps',action='store_true',help='Resume export: validate and retain existing bitmaps; run full QA afterward')
    parser.add_argument('--without-kanji-expansion',action='store_true',help='Small development build, explicitly incomplete')
    args=parser.parse_args()
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    legacy=legacy_check()
    glyphs,provenance=load_glyphs(expand_kanji=not args.without_kanji_expansion)
    coverage=report(glyphs,{})
    coverage['development_without_expansion']=args.without_kanji_expansion
    coverage['legacy']=legacy
    (out/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
    details={c:{'source':g.source,'status':g.status,'category':g.category,'notes':g.notes,
                'centerline_sha256':hashlib.sha256(json.dumps(g.paths,separators=(',',':')).encode()).hexdigest()}
             for c,g in glyphs.items()}
    details['_kanji_expansion']=provenance
    (out/'glyph-provenance.json.gz').write_bytes(gzip.compress(json.dumps(details,ensure_ascii=False,sort_keys=True).encode(),mtime=0))
    write_centerlines(glyphs,out/'centerlines.svg')
    try:
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
        source_dirty=bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=ROOT,text=True))
    except (OSError,subprocess.CalledProcessError):
        source_commit=None;source_dirty=None
    summary={'legacy':legacy,'fonts':[],'bitmaps':[],'source_commit':source_commit,
             'source_tree_dirty':source_dirty,
             'source_identity_note':'source_commit is the checkout base; source_hashes bind actual working bytes, including uncommitted changes.',
        'python':platform.python_version(),'experimental':True,'reused_bitmap_strikes':args.reuse_bitmaps}
    for key in args.styles:
        style=STYLES[key]
        path=out/'static'/f'SinglelineJPLab-{key}.ttf'
        print(f'Building {key}: {len(glyphs)} glyph identities',flush=True)
        summary['fonts'].append(build_font(glyphs,style,path))
        gc.collect()
        for size in args.bitmap_sizes:
            if args.reuse_bitmaps:
                from family.bitmap_reader import BitmapFont
                from family.font_builder import standard_variants
                from PIL import Image
                import numpy as np
                name=f'{style.key}-{size}';base=out/'bitmaps'
                meta=json.loads((base/(name+'.json')).read_text());font=BitmapFont(base/(name+'.sjpb'))
                assert meta['sha256']==sha(base/meta['image'])
                expected=set(glyphs)|{seq for seq,target in standard_variants(glyphs)}
                assert set(font.glyphs)==set(meta['glyphs'])==expected
                assert font.size==size and meta['style']==style.key
                assert font.baseline==meta['baseline'] and font.height==meta['line_height']
                with Image.open(base/meta['image']) as im:atlas=np.array(im.convert('L'))!=0
                for c,box in meta['glyphs'].items():
                    bitmap=font.bitmap(c)
                    assert np.array_equal(bitmap,atlas[box['y']:box['y']+box['height'],box['x']:box['x']+box['width']])
                summary['bitmaps'].append({'name':name,'glyphs':len(expected),'bytes':(base/(name+'.sjpb')).stat().st_size,'binary':str(base/(name+'.sjpb'))})
                del atlas,font,meta
            else:summary['bitmaps'].append(build_bitmaps(glyphs,style,size,out/'bitmaps'))
            gc.collect()
    if not args.no_variable:
        for key in ('gothic','serif'):
            if key in args.styles:
                print('Building variable '+key,flush=True)
                summary['fonts'].append(build_font(glyphs,STYLES[key],out/'variable'/f'SinglelineJPLab-{key}-VF.ttf',variable=True))
                gc.collect()
    summary['source_hashes']={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'family').rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
    for name in ('build_family.py','requirements-family.txt'):
        summary['source_hashes'][name]=sha(ROOT/name)
    summary['legacy_after']=legacy_check()
    (out/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:{'present':v['present'],'target':v['target']} for k,v in coverage['groups'].items()},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
