"""Pack sanitized review deliverables into small source blobs, or restore them.

Default: rebuild the five published reports byte-for-byte from the hash-pinned
ASCII parts. No source fonts, images, reference charts or private raw reviews
are embedded. Packing is explicit; normal builds only materialize.
"""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'family/data/proofread-review'
REPORTS=ROOT/'build/family/reports'
PREFIX='full-glyph-proofread-'
FILES=tuple(PREFIX+suffix for suffix in ('compact.json.gz','coverage.csv','summary.json','summary.txt','index.html'))
PART_RAW_BYTES=64*1024
MAX_PART_BYTES=128*1024
MAX_OUTPUT_BYTES=128*1024*1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_public(data,name):
    if name.endswith('.gz'):
        from io import BytesIO
        with gzip.GzipFile(fileobj=BytesIO(data)) as stream:
            decoded=stream.read(MAX_OUTPUT_BYTES+1)
        if len(decoded)>MAX_OUTPUT_BYTES:
            raise ValueError('Public payload exceeds safety bound')
    else:
        decoded=data
    text=decoded.decode('utf-8-sig')
    forbidden=(r'/(?:workspace|tmp|root)/',r'\b(?:agent_id|worker_id)\b',r'\b(?:agent|worker)[-_][0-9a-f]{8,}\b')
    for pattern in forbidden:
        if re.search(pattern,text,re.IGNORECASE):
            raise ValueError('Unsanitized private path/identifier in '+name)
    if re.search(r'data:image/|JVBERi0|iVBORw0KGgo',text):
        raise ValueError('Embedded image or PDF payload in '+name)


def pack_reports(reports=REPORTS,source=SOURCE):
    reports,source=Path(reports),Path(source)
    source.mkdir(parents=True,exist_ok=True)
    entries=[]
    for name in FILES:
        data=(reports/name).read_bytes()
        validate_public(data,name)
        transport=gzip.compress(data,compresslevel=9,mtime=0) if name.endswith('.csv') else data
        codec='gzip' if name.endswith('.csv') else 'identity'
        parts=[]
        for index,offset in enumerate(range(0,len(transport),PART_RAW_BYTES)):
            payload=base64.b64encode(transport[offset:offset+PART_RAW_BYTES])+b'\n'
            assert len(payload)<=MAX_PART_BYTES
            part_name=name+'.part-'+f'{index:04d}'
            (source/part_name).write_bytes(payload)
            parts.append({'file':part_name,'bytes':len(payload),'sha256':digest(payload)})
        entries.append({'output':name,'output_bytes':len(data),'output_sha256':digest(data),
                        'transport_codec':codec,'transport_bytes':len(transport),'transport_sha256':digest(transport),
                        'part_encoding':'base64-ascii','parts':parts})
    manifest={'schema_version':1,'purpose':'Sanitized user-facing glyph proofreading reports; not raw private review history',
              'part_limit_bytes':MAX_PART_BYTES,'outputs':entries,
              'excluded_assets':['font binaries','PNG evidence','Unicode PDFs','reference chart images','raw private reviewer records'],
              'verification':'Exact part SHA, decoded transport SHA, and restored output SHA; all outputs verified before replacement.'}
    encoded=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    if len(encoded)>MAX_PART_BYTES:
        raise ValueError('Manifest itself exceeds source-blob limit')
    (source/'manifest.json').write_bytes(encoded)
    # Do not remove old parts: source history can retain them without granting
    # this helper authority to delete files. Only manifest-listed parts load.
    return manifest


def _safe_part(name):
    if not isinstance(name,str) or Path(name).name!=name or '/' in name or '\\' in name or '..' in name:
        raise ValueError('Unsafe part path')
    if not re.fullmatch(r'full-glyph-proofread-[a-z.]+\.part-[0-9]{4}',name):
        raise ValueError('Unexpected part filename')
    return name


def materialize(source=SOURCE,output=REPORTS):
    source,output=Path(source),Path(output)
    manifest_path=source/'manifest.json'
    if manifest_path.stat().st_size>MAX_PART_BYTES:
        raise ValueError('Manifest exceeds source-blob limit')
    manifest=json.loads(manifest_path.read_text())
    if manifest.get('schema_version')!=1 or manifest.get('part_limit_bytes')!=MAX_PART_BYTES:
        raise ValueError('Unsupported manifest')
    entries=manifest.get('outputs',[])
    if len(entries)!=len(FILES) or {e.get('output') for e in entries}!=set(FILES):
        raise ValueError('Expected exactly the five allowed output names')
    restored={}
    for entry in entries:
        name=entry['output']
        if entry.get('part_encoding')!='base64-ascii':
            raise ValueError('Unsupported part encoding')
        chunks=[]
        for part in entry['parts']:
            path=source/_safe_part(part['file'])
            if path.is_symlink():
                raise ValueError('Symlink part is not allowed')
            if path.stat().st_size>MAX_PART_BYTES:
                raise ValueError('Part exceeds source-blob limit')
            payload=path.read_bytes()
            if len(payload)>MAX_PART_BYTES or len(payload)!=part['bytes'] or digest(payload)!=part['sha256']:
                raise ValueError('Part integrity mismatch: '+part['file'])
            chunks.append(base64.b64decode(payload.strip(),validate=True))
        transport=b''.join(chunks)
        if len(transport)!=entry['transport_bytes'] or digest(transport)!=entry['transport_sha256']:
            raise ValueError('Transport integrity mismatch: '+name)
        if entry['output_bytes']>MAX_OUTPUT_BYTES:
            raise ValueError('Declared output exceeds safety bound')
        if entry['transport_codec']=='gzip':
            # Bound decompression instead of trusting the supplied output size.
            from io import BytesIO
            with gzip.GzipFile(fileobj=BytesIO(transport)) as file:
                data=file.read(MAX_OUTPUT_BYTES+1)
        elif entry['transport_codec']=='identity':
            data=transport
        else:
            raise ValueError('Unsupported transport codec')
        if len(data)>MAX_OUTPUT_BYTES or len(data)!=entry['output_bytes'] or digest(data)!=entry['output_sha256']:
            raise ValueError('Output integrity mismatch: '+name)
        validate_public(data,name)
        restored[name]=data
    output.mkdir(parents=True,exist_ok=True)
    for name,data in restored.items():
        temporary=output/(name+'.materializing')
        temporary.write_bytes(data)
        temporary.replace(output/name)
    return {name:digest(data) for name,data in restored.items()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=SOURCE)
    parser.add_argument('--output',type=Path,default=REPORTS)
    parser.add_argument('--pack',type=Path,metavar='REPORT_DIRECTORY',help='Explicitly pack already sanitized public reports')
    args=parser.parse_args()
    if args.pack:
        manifest=pack_reports(args.pack,args.source)
        print(json.dumps({'files':len(manifest['outputs']),'parts':sum(len(e['parts']) for e in manifest['outputs'])}))
    else:
        print(json.dumps(materialize(args.source,args.output),indent=2))


if __name__=='__main__':
    main()
