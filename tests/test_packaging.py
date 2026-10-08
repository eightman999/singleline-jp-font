"""Small independent regression fixtures for release binding and archive safety."""
import copy
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

import pytest

from family.release import (GATES, MANIFEST, REQUIRED_GATES, VerificationError,
                            canonical, check_release_gates, digest, gate_artifact_digest, seal_report,
                            snapshot, validate_report)
from family.tools import package_family as packaging


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


@pytest.fixture
def checkout(tmp_path):
    root = tmp_path / 'checkout'
    output = root / 'build/family'
    sources = {
        'LICENSE': b'AGPL license fixture\n', 'NOTICE.md': b'Experimental fixture notices\n',
        'GPL.txt': b'GPL license fixture\n', 'UNICODE.txt': b'Unicode license fixture\n',
        'family/__init__.py': b'', 'family/bitmap_reader.py': b'# reader fixture\n',
        'source.py': b'print("source fixture")\n',
    }
    svg = b'<svg xmlns="http://www.w3.org/2000/svg"><defs><symbol id="uni65E5"><title>\xe6\x97\xa5</title><path d="M1,1 L2,2"/></symbol></defs></svg>\n'
    artifacts = {
        'static/SinglelineJPLab-gothic.ttf': b'static fixture',
        'variable/SinglelineJPLab-gothic-VF.ttf': b'variable fixture',
        'bitmaps/gothic-16.sjpb': b'binary fixture',
        'bitmaps/gothic-16.png': b'png fixture',
        'bitmaps/gothic-16.json': canonical({'image': 'gothic-16.png', 'glyphs': {'日': {'width': 2, 'height': 2, 'x': 0, 'y': 0}}}),
        'coverage.json': canonical({'quality_flags': {'composition-draft': {'count': 1}}}),
        'build-summary.json': canonical({'experimental': True}),
        'glyph-provenance.json.gz': gzip.compress(b'{}', mtime=0),
        'centerlines.svgz': gzip.compress(svg, mtime=0),
    }
    for base, entries in ((root, sources), (output, artifacts)):
        for name, data in entries.items():
            path = base / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    write_json(root / GATES, {'schema_version': 1, 'known_limitations_acknowledged': False,
                             'checks': {name: {'status': 'not-run', 'evidence': None, 'artifact_set_sha256': None} for name in REQUIRED_GATES}})
    write_json(root / MANIFEST, {'schema_version': 1, 'source_files': sorted([*sources, MANIFEST, GATES]),
                                'artifact_files': sorted(artifacts), 'licenses': ['LICENSE', 'NOTICE.md', 'GPL.txt', 'UNICODE.txt']})
    reseal(root)
    return root, output


def reseal(root, transform=None):
    output = root / 'build/family'
    subject = snapshot(root, output)
    report = {'scope': 'full-family-structural-verification', 'outcome': 'passed',
              'counts': {'passed': 1, 'failure': 0, 'error': 0, 'skipped': 0},
              'tests': [{'test': 'fixture.pass', 'status': 'passed', 'detail': ''}],
              'execution': {'exit_code': 0, 'test_roots': ['tests', 'family/tests'],
                            'selection_environment_sanitized': True,
                            'inventory': {'collection_exit_code': 0, 'collected': ['fixture.pass'],
                                          'execution_collected': ['fixture.pass'], 'executed': ['fixture.pass'], 'deselected': []}},
              'bitmap_collision_audit': {'complete_inventory': True}}
    if transform:
        transform(report)
    report = seal_report(report, subject, subject)
    write_json(output / 'reports/full-tests.json', report)
    return report


def read_report(output):
    return json.loads((output / 'reports/full-tests.json').read_text())


def test_report_binds_exact_source_and_artifact_inventory(checkout):
    root, output = checkout
    report = read_report(output)
    assert validate_report(root, output, report) == snapshot(root, output)
    assert report['subject']['sources']['source.py'] == digest((root / 'source.py').read_bytes())
    assert report['subject']['artifacts']['static/SinglelineJPLab-gothic.ttf']


@pytest.mark.parametrize('relative', ['source.py', 'build/family/static/SinglelineJPLab-gothic.ttf', MANIFEST, GATES])
def test_after_test_input_changes_are_rejected(checkout, tmp_path, relative):
    root, output = checkout
    with (root / relative).open('ab') as stream:
        stream.write(b'\n')
    with pytest.raises(VerificationError, match='Stale verification'):
        packaging.package_family(root, tmp_path / 'bad.zip')
    assert not (tmp_path / 'bad.zip').exists()


def test_missing_input_is_rejected(checkout, tmp_path):
    root, output = checkout
    (root / 'source.py').unlink()
    with pytest.raises(VerificationError, match='Stale verification'):
        packaging.package_family(root, tmp_path / 'bad.zip')


def test_old_pass_boolean_is_not_verification(checkout, tmp_path):
    root, output = checkout
    write_json(output / 'reports/full-tests.json', {'outcome': 'passed'})
    with pytest.raises(VerificationError, match='binding'):
        packaging.package_family(root, tmp_path / 'bad.zip')


def test_edited_report_is_rejected(checkout, tmp_path):
    root, output = checkout
    report = read_report(output)
    report['tests'][0]['detail'] = 'Changed after verification'
    write_json(output / 'reports/full-tests.json', report)
    with pytest.raises(VerificationError, match='binding'):
        packaging.package_family(root, tmp_path / 'bad.zip')


@pytest.mark.parametrize('mutation', [
    lambda r: r.update(scope='source-and-sample-only'),
    lambda r: r.update(outcome='failed'),
    lambda r: r['counts'].update(passed=2),
    lambda r: r['tests'][0].update(status='skipped'),
    lambda r: r['execution'].update(exit_code=1),
    lambda r: r['execution'].update(test_roots=['tests']),
    lambda r: r['bitmap_collision_audit'].update(complete_inventory=False),
])
def test_non_full_or_inconsistent_runs_cannot_package(checkout, tmp_path, mutation):
    root, output = checkout
    reseal(root, mutation)
    with pytest.raises(VerificationError):
        packaging.package_family(root, tmp_path / 'bad.zip')


def test_changes_during_verification_invalidate_run(checkout):
    root, output = checkout
    before = snapshot(root, output)
    (root / 'source.py').write_text('changed\n')
    report = seal_report(read_report(output), before, snapshot(root, output))
    assert report['outcome'] == 'incomplete'
    assert report['inputs_unchanged'] is False


def test_known_failure_blocks_rc_and_release(checkout, tmp_path):
    root, output = checkout
    gates = json.loads((root / GATES).read_text())
    gates['checks']['macos-install']['status'] = 'failed'
    write_json(root / GATES, gates)
    reseal(root)
    for channel, version in [('rc', '2.0.0-rc.1'), ('release', '2.0.0')]:
        with pytest.raises(VerificationError, match='Known failing'):
            packaging.package_family(root, tmp_path / 'bad.zip', channel=channel, version=version)


def test_unrun_gates_block_formal_release_only(checkout, tmp_path):
    root, output = checkout
    with pytest.raises(VerificationError, match='Formal release blocked'):
        packaging.package_family(root, tmp_path / 'bad.zip', channel='release', version='2.0.0')
    result = packaging.package_family(root, tmp_path / 'rc.zip', channel='rc')
    assert result['channel'] == 'rc'


def test_passed_gate_requires_current_artifact_evidence(checkout):
    root, output = checkout
    gates = json.loads((root / GATES).read_text())
    gates['checks']['macos-install'] = {'status': 'passed', 'evidence': 'manual result', 'artifact_set_sha256': '0' * 64}
    write_json(root / GATES, gates)
    subject = snapshot(root, output)
    with pytest.raises(VerificationError, match='Stale or missing gate evidence'):
        check_release_gates(root, output, subject, 'rc')


def test_formal_version_can_disclose_experimental_quality_without_false_certification(checkout):
    root, output = checkout
    subject = snapshot(root, output)
    gates = json.loads((root / GATES).read_text())
    for name in gates['checks']:
        gates['checks'][name] = {'status': 'passed', 'evidence': 'fixture: priority/platform review, not all glyphs',
                                 'artifact_set_sha256': gate_artifact_digest(subject)}
    gates['known_limitations_acknowledged'] = True
    write_json(root / GATES, gates)
    result = check_release_gates(root, output, snapshot(root, output), 'release')
    assert result['experimental'] is True
    assert result['visual_legibility_certified'] is False
    assert result['japanese_typographic_release_ready'] is False


def test_allowlist_excludes_arbitrary_untracked_files(checkout, tmp_path):
    root, output = checkout
    for name in ('credentials.txt', 'family/scratch.py', 'build/family/static/private.ttf', 'build/family/reports/private.json'):
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('must never leave the checkout')
    path = tmp_path / 'source.zip'
    packaging.package_family(root, path)
    with zipfile.ZipFile(path) as archive:
        assert not any(word in name for name in archive.namelist() for word in ('credentials', 'scratch.py', 'private'))


@pytest.mark.parametrize('name', ['../secret', '/secret', 'family/../../secret', './source.py', 'family//file', 'family\\secret', 'D:/secret', 'C:secret', 'source.py:stream'])
def test_manifest_cannot_escape_root(checkout, name):
    root, output = checkout
    manifest = json.loads((root / MANIFEST).read_text())
    manifest['source_files'].append(name)
    write_json(root / MANIFEST, manifest)
    with pytest.raises(VerificationError, match='Unsafe manifest path'):
        snapshot(root, output)


def test_symlinked_input_is_rejected(checkout, tmp_path):
    root, output = checkout
    source = root / 'source.py'
    source.unlink()
    outside = tmp_path / 'outside.py'
    outside.write_text('secret')
    source.symlink_to(outside)
    with pytest.raises(VerificationError, match='Symlinks'):
        snapshot(root, output)


def test_symlinked_parent_is_rejected(checkout, tmp_path):
    root, output = checkout
    (root / 'family/bitmap_reader.py').unlink()
    (root / 'family/__init__.py').unlink()
    # Other manifest/gate files occupy family, so replace only the static directory.
    original = output / 'static'
    original.rename(tmp_path / 'outside-static')
    original.symlink_to(tmp_path / 'outside-static', target_is_directory=True)
    with pytest.raises(VerificationError, match='Symlinks'):
        snapshot(root, output)


def test_destination_cannot_overwrite_verified_input(checkout):
    root, output = checkout
    original = (root / 'source.py').read_bytes()
    with pytest.raises(VerificationError, match='overwrite an input'):
        packaging.package_family(root, root / 'source.py')
    assert (root / 'source.py').read_bytes() == original


def test_change_during_packaging_leaves_previous_destination_untouched(checkout, tmp_path, monkeypatch):
    root, output = checkout
    destination = tmp_path / 'source.zip'
    destination.write_bytes(b'previous package')
    original = packaging._write_zip
    def changing_write(path, files):
        count = original(path, files)
        (root / 'source.py').write_text('changed during ZIP creation\n')
        return count
    monkeypatch.setattr(packaging, '_write_zip', changing_write)
    with pytest.raises(VerificationError, match='during packaging'):
        packaging.package_family(root, destination)
    assert destination.read_bytes() == b'previous package'


def test_stale_raw_svg_is_rejected_without_overwriting_package(checkout, tmp_path):
    root, output = checkout
    (output / 'centerlines.svg').write_text('<svg>stale</svg>')
    with pytest.raises(VerificationError, match='disagree'):
        packaging.package_family(root, tmp_path / 'source.zip')
    assert not (tmp_path / 'source.zip').exists()


@pytest.mark.parametrize('kind', packaging.KINDS)
def test_archives_are_deterministic_independent_and_checksummed(checkout, tmp_path, kind):
    root, output = checkout
    one, two = tmp_path / 'one.zip', tmp_path / 'two.zip'
    result = packaging.package_family(root, one, kind=kind)
    packaging.package_family(root, two, kind=kind)
    assert one.read_bytes() == two.read_bytes()
    with zipfile.ZipFile(one) as archive:
        names = {name.removeprefix(packaging.PREFIX) for name in archive.namelist()}
        sums = json.loads(archive.read(packaging.PREFIX + 'PACKAGE-SHA256.json'))
        assert names == set(sums) | {'PACKAGE-SHA256.json', 'SHA256SUMS'}
        assert result['files'] == len(sums)
        assert {'LICENSE', 'NOTICE.md', 'GPL.txt', 'UNICODE.txt', 'specimen/index.html', 'QA-REPORT.json'} <= names
        for name, checksum in sums.items():
            assert digest(archive.read(packaging.PREFIX + name)) == checksum
        assert {info.date_time for info in archive.infolist()} == {packaging.ZIP_TIME}
        page = archive.read(packaging.PREFIX + 'specimen/index.html').decode()
        # All downloadable resources and CSS assets must exist in this ZIP.
        for path in re.findall(r'(?:href="|url\(")(\.\./[^"#]+)', page):
            assert path[3:] in names, (kind, path)
        assert 'https://' not in page and 'fetch(' not in page
        if kind == 'source':
            assert archive.read(packaging.PREFIX + 'build/family/centerlines.svg') == gzip.decompress((output / 'centerlines.svgz').read_bytes())
            assert '<svg xmlns=' in page and '<ns0:svg' not in page
        else:
            category = 'bitmaps' if kind == 'bitmap' else kind
            assert any(name.startswith('build/family/' + category + '/') for name in names)
            assert 'build/family/centerlines.svg' not in names


def test_split_distribution_names_and_outer_checksums(checkout, tmp_path):
    root, output = checkout
    destination = tmp_path / 'dist'
    results = packaging.package_distributions(root, destination, channel='rc')
    assert len(results) == 4
    sums = (destination / 'SHA256SUMS').read_text().splitlines()
    for result, line in zip(results, sums):
        checksum, name = line.split('  ')
        assert checksum == digest((destination / name).read_bytes())
        assert name == f'SinglelineJPLab-2.0.0-rc.1-{result["kind"]}.zip'


def test_pytest_selection_environment_cannot_weaken_full_verification(tmp_path, monkeypatch):
    from verify_family import run_pytest_inventory
    module = tmp_path / 'test_inventory_fixture.py'
    module.write_text('def test_first(): pass\ndef test_second(): pass\n')
    monkeypatch.setenv('PYTEST_ADDOPTS', '-k test_first')
    monkeypatch.setenv('PYTEST_PLUGINS', 'nonexistent_poison_plugin')
    monkeypatch.setenv('PYTEST_DISABLE_PLUGIN_AUTOLOAD', '0')
    code, cases, inventory, complete = run_pytest_inventory(tmp_path, test_paths=[str(module)])
    assert code == 0 and complete
    assert len(cases) == 2
    assert inventory['deselected'] == []


def test_sealed_deselected_inventory_is_rejected(checkout, tmp_path):
    root, output = checkout
    reseal(root, lambda r: r['execution']['inventory'].update(deselected=['fixture.not_run']))
    with pytest.raises(VerificationError, match='filtered verification'):
        packaging.package_family(root, tmp_path / 'bad.zip')


def test_sealed_partial_execution_inventory_is_rejected(checkout, tmp_path):
    root, output = checkout
    reseal(root, lambda r: r['execution']['inventory']['collected'].append('fixture.not_run'))
    with pytest.raises(VerificationError, match='filtered verification'):
        packaging.package_family(root, tmp_path / 'bad.zip')


@pytest.mark.parametrize('channel,version', [('rc', '2.0.0'), ('release', '2.0.0-rc.1')])
def test_channel_and_version_must_agree(checkout, tmp_path, channel, version):
    root, output = checkout
    with pytest.raises(VerificationError, match='channel and version'):
        packaging.package_family(root, tmp_path / 'bad.zip', channel=channel, version=version)


def test_binary_docs_keep_available_links_and_label_omitted_references():
    files = {'docs/INSTALL.md': b'[priority](PRIORITY.md) [history](../build/family/reports/old.json) [external](https://example.test/page) [section](#install)',
             'docs/PRIORITY.md': b'[proof](../build/family/proofs/priority-glyphs/gothic.svg)',
             'build/family/proofs/priority-glyphs/gothic.svg': b'<svg/>'}
    packaging.adapt_distribution_docs(files)
    install = files['docs/INSTALL.md'].decode()
    assert '[priority](PRIORITY.md)' in install
    assert '[history](' not in install
    assert 'repository-only: `build/family/reports/old.json`' in install
    assert '[external](https://example.test/page)' in install
    assert '[section](#install)' in install
    assert files['docs/PRIORITY.md'].startswith(b'[proof](')


@pytest.mark.parametrize('source', ['family/specimen.py', 'family/tools/package_family.py'])
def test_gate_evidence_binds_browser_generators(checkout, source):
    root, output = checkout
    subject = snapshot(root, output)
    subject['sources'][source] = 'a' * 64
    before = gate_artifact_digest(subject)
    subject['sources'][source] = 'b' * 64
    assert gate_artifact_digest(subject) != before


def test_gate_evidence_binds_specimen_assets_without_metadata_cycles(checkout):
    root, output = checkout
    subject = snapshot(root, output)
    subject['artifacts']['specimen/index.html'] = 'a' * 64
    before = gate_artifact_digest(subject)
    subject['artifacts']['specimen/index.html'] = 'b' * 64
    assert gate_artifact_digest(subject) != before
    stable = gate_artifact_digest(subject)
    subject['artifacts']['build-summary.json'] = 'c' * 64
    subject['sources'][GATES] = 'd' * 64
    subject['sources'][MANIFEST] = 'e' * 64
    assert gate_artifact_digest(subject) == stable


def test_review_stage_omits_historical_reports(checkout,tmp_path):
    from family.tools.stage_review_artifacts import stage
    root,output=checkout
    doc=root/'docs/FULL-GLYPH-PROOFREAD.md';doc.parent.mkdir();doc.write_text('Review limits')
    stale=output/'reports/stale-success.json';stale.parent.mkdir(exist_ok=True);stale.write_text('old')
    target=tmp_path/'review'
    stage(root,output,output/'reports/full-tests.json',target)
    assert (target/'static/SinglelineJPLab-gothic.ttf').read_bytes()==b'static fixture'
    assert (target/'reports/current-full-tests.json').is_file()
    assert not (target/'reports/stale-success.json').exists()
    assert (target/'LICENSE').exists()
    with pytest.raises(ValueError,match='existing directory'):
        stage(root,output,output/'reports/full-tests.json',target)


def test_review_stage_rejects_stale_verification(checkout,tmp_path):
    from family.tools.stage_review_artifacts import stage
    root,output=checkout
    (output/'static/SinglelineJPLab-gothic.ttf').write_bytes(b'changed')
    with pytest.raises(VerificationError,match='Stale verification'):
        stage(root,output,output/'reports/full-tests.json',tmp_path/'review')
