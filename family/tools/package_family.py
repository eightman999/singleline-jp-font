"""Package source plus verified build; exclude scratch/reference/font tooling."""
import argparse,gzip,hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def package_family(root,destination):
    root=Path(root);destination=Path(destination)
    out=root/'build/family'
    report=json.loads((out/'reports/full-tests.json').read_text())
    if report['outcome']!='passed':raise SystemExit('Refusing to package an unverified full build')
    # Git stores the complete lossless SVGZ; source bundles also expose the
    # editable SVG, including when packaging directly from a clean clone.
    svg=gzip.decompress((out/'centerlines.svgz').read_bytes())
    raw=out/'centerlines.svg'
    if raw.is_file() and raw.read_bytes()!=svg:
        raise ValueError('centerlines.svg and centerlines.svgz disagree; rebuild centerlines before packaging')
    files=[]
    for file in sorted(root.rglob('*')):
        rel=file.relative_to(root)
        if not file.is_file() or any(p in ('.git','.venv','__pycache__','.pytest_cache') for p in rel.parts):continue
        if file.resolve()==destination.resolve():continue
        if rel.parts[0]=='build':
            if rel.parts[:2]!=('build','family'):continue
            sub=rel.parts[2:]
            # Third-party visual references and throwaway probes stay private.
            if sub and sub[0] not in ('static','variable','bitmaps','specimen','reports','proofs',
                    'coverage.json','glyph-provenance.json.gz','build-summary.json','centerlines.svgz'):
                continue
            if 'bitmap-diagnostic.png' in sub:continue
        files.append((file,rel))
    destination.parent.mkdir(exist_ok=True,parents=True)
    sums={str(rel):hashlib.sha256(file.read_bytes()).hexdigest() for file,rel in files}
    raw_relative=Path('build/family/centerlines.svg')
    sums[str(raw_relative)]=hashlib.sha256(svg).hexdigest()
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for file,rel in sorted(files+[(None,raw_relative)],key=lambda item:str(item[1])):
            item=zipfile.ZipInfo('singleline-jp-font/'+str(rel),(2026,10,6,0,0,0))
            item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16
            archive.writestr(item,svg if file is None else file.read_bytes())
        archive.writestr('singleline-jp-font/PACKAGE-SHA256.json',json.dumps(sums,indent=2)+'\n')
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist())==len(sums)+1
    return {'package':str(destination),'size_bytes':destination.stat().st_size,
        'files':len(sums),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}


def main():
    p=argparse.ArgumentParser();p.add_argument('destination',type=Path);args=p.parse_args()
    print(json.dumps(package_family(ROOT,args.destination),indent=2))


if __name__=='__main__':main()
