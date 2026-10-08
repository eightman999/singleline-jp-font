import gzip
import json
import os
import pytest
from family.tools.materialize_proofread_report import FILES, MAX_PART_BYTES, materialize, pack_reports, validate_public


def sample_reports(path):
    path.mkdir()
    for name in FILES:
        # Repeated textual records with different random hex strings defeat
        # compression enough to exercise multiple transport chunks.
        payload=('User-facing review '+os.urandom(100000).hex()+'\n').encode()
        if name.endswith('.gz'):payload=gzip.compress(payload,mtime=0)
        (path/name).write_bytes(payload)


def test_exact_roundtrip_all_five_files(tmp_path):
    original=tmp_path/'original';sample_reports(original)
    source=tmp_path/'source';output=tmp_path/'output'
    manifest=pack_reports(original,source)
    assert all(p.stat().st_size<=MAX_PART_BYTES for p in source.iterdir())
    materialize(source,output)
    assert all((original/name).read_bytes()==(output/name).read_bytes() for name in FILES)
    assert len(manifest['outputs'])==5


def test_corrupt_part_blocks_all_output_writes(tmp_path):
    original=tmp_path/'original';sample_reports(original)
    source=tmp_path/'source';out=tmp_path/'out';m=pack_reports(original,source)
    part=source/m['outputs'][0]['parts'][0]['file'];part.write_bytes(b'corrupt')
    with pytest.raises(ValueError,match='Part integrity'):materialize(source,out)
    assert not out.exists()


def test_traversal_rejected(tmp_path):
    original=tmp_path/'original';sample_reports(original)
    source=tmp_path/'source';m=pack_reports(original,source)
    m['outputs'][0]['parts'][0]['file']='../secret'
    (source/'manifest.json').write_text(json.dumps(m))
    with pytest.raises(ValueError,match='Unsafe part path'):materialize(source,tmp_path/'out')


def test_private_paths_and_embedded_reference_images_blocked():
    with pytest.raises(ValueError,match='Unsanitized'):validate_public(b'/workspace/private/file','example.txt')
    with pytest.raises(ValueError,match='Unsanitized'):validate_public(b'/tmp/chart.png','example.txt')
    with pytest.raises(ValueError,match='Embedded'):validate_public(b'data:image/png;base64,AAAA','example.txt')
    validate_public(b'https://www.unicode.org/charts/PDF/U4E00.pdf#page=3; local-reference:chart','example.txt')
