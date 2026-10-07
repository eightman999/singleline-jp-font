"""Content-bound verification and explicit distribution inventory.

Digests detect stale inputs and accidental report editing. They are not a
signature or an attestation from a trusted third party: a person able to
replace the verifier and recompute every digest can forge a report.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath

MANIFEST = 'family/package-manifest.json'
GATES = 'family/release-gates.json'
REPORT_SCHEMA = 1
REQUIRED_GATES = ('windows-install', 'macos-install', 'macos-structural', 'linux-fontconfig',
                  'browser-specimen', 'visual-review')


class VerificationError(ValueError):
    """The distribution has not been verified against these exact bytes."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def safe_path(root, relative):
    """Refuse traversal, aliases and symlinks, including symlinked parents."""
    if (not isinstance(relative, str) or not relative or '\\' in relative or
            ':' in relative or any(ord(char) < 32 for char in relative)):
        raise VerificationError(f'Unsafe manifest path: {relative!r}')
    path = PurePosixPath(relative)
    if path.is_absolute() or path.as_posix() != relative or any(p in ('.', '..') for p in path.parts):
        raise VerificationError(f'Unsafe manifest path: {relative!r}')
    root = Path(root).resolve()
    current = root
    for component in path.parts:
        current = current / component
        if current.is_symlink():
            raise VerificationError(f'Symlinks are not distribution inputs: {relative}')
    return current


def load_manifest(root):
    manifest = json.loads(safe_path(root, MANIFEST).read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 1:
        raise VerificationError('Unsupported package manifest schema')
    for key in ('source_files', 'artifact_files', 'licenses'):
        values = manifest.get(key)
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            raise VerificationError(f'Invalid {key} allowlist')
        for name in values:
            safe_path(root, name)
    if MANIFEST not in manifest['source_files'] or GATES not in manifest['source_files']:
        raise VerificationError('Manifest and release gates must be source-bound')
    if not set(manifest['licenses']) <= set(manifest['source_files']):
        raise VerificationError('License files must be source-bound')
    return manifest


def snapshot(root, output):
    """Hash exactly the reviewed inventory. Missing files are explicit failures."""
    manifest = load_manifest(root)
    result = {'manifest_sha256': digest(safe_path(root, MANIFEST).read_bytes()),
              'sources': {}, 'artifacts': {}, 'missing': []}
    for key, base, names in (('sources', root, manifest['source_files']),
                             ('artifacts', output, manifest['artifact_files'])):
        for name in sorted(names):
            path = safe_path(base, name)
            if not path.is_file():
                result['missing'].append(f'{key}:{name}')
            else:
                result[key][name] = digest(path.read_bytes())
    return result


def seal_report(report, before, after):
    """Seal only after the last audit; input mutations invalidate the run."""
    result = dict(report)
    result.update(schema_version=REPORT_SCHEMA, subject=after,
                  inputs_unchanged=before == after,
                  integrity_notice='SHA-256 content binding; not a signature or trusted attestation')
    missing = after['missing']
    if report.get('scope') == 'source-and-sample-only':
        missing = [name for name in missing if name.startswith('sources:')]
    if before != after or missing:
        result['outcome'] = 'incomplete'
    result.pop('report_sha256', None)
    result['report_sha256'] = digest(canonical(result))
    return result


def report_digest_valid(report):
    copy = dict(report)
    checksum = copy.pop('report_sha256', None)
    return checksum == digest(canonical(copy))


def validate_report(root, output, report):
    """Reject old boolean-only records, partial tests, skips, edits and staleness."""
    if report.get('schema_version') != REPORT_SCHEMA or not report_digest_valid(report):
        raise VerificationError('Missing/altered verification binding; rerun verify_family.py')
    if report.get('scope') != 'full-family-structural-verification' or report.get('outcome') != 'passed':
        raise VerificationError('A passed full-family verification report is required')
    if report.get('inputs_unchanged') is not True:
        raise VerificationError('Inputs changed during verification')
    cases = report.get('tests', [])
    if not cases or any(case.get('status') != 'passed' for case in cases):
        raise VerificationError('Every verification test must pass, without skips')
    if len({case.get('test') for case in cases}) != len(cases):
        raise VerificationError('Duplicate verification test records')
    if report.get('counts') != {'passed': len(cases), 'failure': 0, 'error': 0, 'skipped': 0}:
        raise VerificationError('Verification counts disagree with test records')
    execution = report.get('execution', {})
    if execution.get('exit_code') != 0 or execution.get('test_roots') != ['tests', 'family/tests']:
        raise VerificationError('The complete verification suite must have run successfully')
    inventory = execution.get('inventory', {})
    expected = inventory.get('collected', [])
    if (execution.get('selection_environment_sanitized') is not True or
            inventory.get('collection_exit_code') != 0 or not expected or
            len(set(expected)) != len(expected) or inventory.get('deselected') != [] or
            inventory.get('execution_collected') != expected or
            inventory.get('executed') != sorted(expected) or
            sorted(case['test'] for case in cases) != sorted(expected)):
        raise VerificationError('Incomplete or filtered verification test inventory')
    audit = report.get('bitmap_collision_audit', {})
    if audit.get('complete_inventory') is not True:
        raise VerificationError('The full bitmap collision inventory is required')
    current = snapshot(root, output)
    if current['missing'] or report.get('subject') != current:
        raise VerificationError('Stale verification: source or artifact bytes changed, or files are missing')
    return current


def gate_artifact_digest(subject):
    """Platform evidence covers deliverables, excluding cyclic QA/build metadata.

    The full verification report separately binds every metadata/proof byte.
    Including build-summary here would be cyclic: it hashes release-gates.json.
    """
    artifacts = {name: checksum for name, checksum in subject['artifacts'].items()
                 if name != 'build-summary.json' and not name.startswith(('reports/', 'proofs/'))}
    ui_sources = {name: checksum for name, checksum in subject['sources'].items()
                  if name in ('family/specimen.py', 'family/tools/package_family.py')}
    return digest(canonical({'artifacts': artifacts, 'ui_sources': ui_sources}))


def check_release_gates(root, output, subject, channel):
    if channel not in ('rc', 'release'):
        raise VerificationError('Select an explicit rc or release channel')
    gates = json.loads(safe_path(root, GATES).read_text(encoding='utf-8'))
    if gates.get('schema_version') != 1 or set(gates.get('checks', {})) != set(REQUIRED_GATES):
        raise VerificationError('Missing required platform/visual release gates')
    artifact_digest = gate_artifact_digest(subject)
    pending = []
    for name in REQUIRED_GATES:
        gate = gates['checks'][name]
        status = gate.get('status')
        if status not in ('passed', 'failed', 'not-run'):
            raise VerificationError(f'Invalid release gate status: {name}')
        if status == 'failed':
            raise VerificationError(f'Known failing release gate blocks every channel: {name}')
        if status == 'passed':
            if not gate.get('evidence') or gate.get('artifact_set_sha256') != artifact_digest:
                raise VerificationError(f'Stale or missing gate evidence: {name}')
        else:
            pending.append(name)
    summary = json.loads(safe_path(output, 'build-summary.json').read_text(encoding='utf-8'))
    coverage = json.loads(safe_path(output, 'coverage.json').read_text(encoding='utf-8'))
    quality_flags = {name: value.get('count', 0) for name, value in coverage.get('quality_flags', {}).items()
                     if value.get('count', 0)}
    experimental = summary.get('experimental') is not False
    acknowledged = gates.get('known_limitations_acknowledged') is True
    if channel == 'release' and (pending or ((experimental or quality_flags) and not acknowledged)):
        raise VerificationError('Formal release blocked: unresolved platform/priority-review gates or unacknowledged quality limitations')
    return {'channel': channel, 'experimental': experimental, 'not_run': pending,
            'unresolved_quality_flags': quality_flags, 'artifact_set_sha256': artifact_digest,
            'known_limitations_acknowledged': acknowledged,
            'japanese_typographic_release_ready': False, 'visual_legibility_certified': False,
            'gate_details': gates['checks']}
