"""Stage only explicitly inventoried, verified files for a draft CI artifact.

Historical reports and arbitrary build-directory files are never swept into
this archive. This is review delivery, not a release-gate bypass or release.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from family.release import load_manifest,safe_path,validate_report


def stage(root,output,report,destination):
    root,output,report,destination=map(Path,(root,output,report,destination))
    verified=json.loads(report.read_text())
    validate_report(root,output,verified)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Refusing to mix current review files with an existing directory')
    inventory=load_manifest(root)
    files={name:safe_path(output,name) for name in inventory['artifact_files']}
    files.update({name:safe_path(root,name) for name in inventory['licenses']})
    files.update({name:safe_path(root,name) for name in inventory['source_files'] if name.startswith('docs/')})
    files['reports/current-full-tests.json']=report
    sums={}
    for name,source in sorted(files.items()):
        target=safe_path(destination,name);target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        sums[name]=hashlib.sha256(target.read_bytes()).hexdigest()
    (destination/'SHA256SUMS.json').write_text(json.dumps(sums,sort_keys=True,indent=2)+'\n')
    (destination/'README.txt').write_text('Experimental Lab proofreading review artifacts. Not a release.\n'
        'Generated from the exact draft source; tracked repository binaries may still be historical.\n'
        'See build-summary.json, reports/current-full-tests.json, and docs/FULL-GLYPH-PROOFREAD.md.\n'
        'All-character initial review does not certify every style, size, application, or variable axis.\n')
    return len(files)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'build/family')
    p.add_argument('--report',type=Path,required=True)
    p.add_argument('--destination',type=Path,required=True)
    a=p.parse_args();print(json.dumps({'staged_files':stage(ROOT,a.output,a.report,a.destination)}))


if __name__=='__main__':main()
