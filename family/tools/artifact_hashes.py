"""Print portable exact-byte hashes of regenerated Lab deliverables.

Environment/verification reports are intentionally separate. This manifest
compares shipped font/bitmap data, not operating-system text appearance.
"""
import argparse
import hashlib
import json
from pathlib import Path


def artifact_hashes(root):
    root=Path(root)
    paths=[]
    for directory,extensions in (('static',{'.ttf'}),('variable',{'.ttf'}),('bitmaps',{'.sjpb','.json','.png'})):
        paths.extend(p for p in (root/directory).iterdir() if p.is_file() and p.suffix in extensions)
    paths.extend(root/name for name in ('centerlines.svgz','glyph-provenance.json.gz','coverage.json'))
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path('build/family'))
    p.add_argument('--output',type=Path)
    args=p.parse_args();result=artifact_hashes(args.root)
    text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    print(text,end='')


if __name__=='__main__':main()
