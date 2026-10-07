"""Make independent, deterministic, content-verified family distributions.

Run from a reviewed checkout after verify_family.py --report REPORT. The
allowlist is family/package-manifest.json, never a filesystem walk. All four
archives include their own specimen, notices, QA report and checksums.
"""
import argparse
import gzip
import hashlib
import html
import json
from pathlib import Path
import re
import posixpath
from urllib.parse import unquote, urlsplit
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from family.release import (VerificationError, canonical, check_release_gates,
                            digest, load_manifest, safe_path, snapshot, validate_report)

KINDS = ('static', 'variable', 'bitmap', 'source')
VERSION = '2.0.0-rc.1'
PREFIX = 'singleline-jp-font/'
SAMPLES = '日本語永鬱明朝Agfg0123未末土士己已巳髙𠮷∑√∞'
ZIP_TIME = (2026, 10, 6, 0, 0, 0)


def editable_centerlines(output):
    """Expose exact lossless source without silently accepting a stale raw SVG."""
    svg = gzip.decompress(safe_path(output, 'centerlines.svgz').read_bytes())
    raw = safe_path(output, 'centerlines.svg')
    if raw.exists() and raw.read_bytes() != svg:
        raise VerificationError('centerlines.svg and centerlines.svgz disagree; rebuild before packaging')
    return svg


def specimen(kind, files):
    """Generate a file://-usable specimen referencing only this archive's files."""
    faces, content, script = [], [], ''
    warning = ('Experimental composition drafts. Encoding and structural QA do not certify '
               'Japanese glyph accuracy, small-size legibility, OS installation or application support.')
    if kind in ('static', 'variable'):
        font_paths = sorted(name for name in files if name.endswith('.ttf') and '/'+kind+'/' in name)
        for index, name in enumerate(font_paths):
            face = f'font{index}'
            attributes = ';font-weight:200 700;font-style:oblique 0deg 12deg' if kind == 'variable' else ''
            faces.append(f'@font-face{{font-family:{face};src:url("../{name}"){attributes}}}')
            title = html.escape(Path(name).stem)
            content.append(f'<section><h2>{title}</h2>')
            if kind == 'variable':
                content.append(f'<label>Weight <input type="range" min="200" max="700" value="400" data-axis="wght" data-target="sample{index}"></label> '
                               f'<label>Slant <input type="range" min="-12" max="0" value="0" data-axis="slnt" data-target="sample{index}"></label>')
            content.append(f'<p id="sample{index}" class="sample" style="font-family:{face}" contenteditable="true">{SAMPLES}</p></section>')
        script = '''document.querySelectorAll('input[data-axis]').forEach(input=>input.addEventListener('input',()=>{const target=input.dataset.target;const axes=[...document.querySelectorAll('input[data-target="'+target+'"]')].map(x=>'"'+x.dataset.axis+'" '+x.value);document.getElementById(target).style.fontVariationSettings=axes.join(', ');}));'''
    elif kind == 'bitmap':
        content.append('<p>Actual atlas pixels at native scale. The adjacent code point identifies each sample. PNG, metrics and SJPB are in build/family/bitmaps/.</p>')
        for name in sorted(name for name in files if name.startswith('build/family/bitmaps/') and name.endswith('.json')):
            metadata = json.loads(files[name])
            image = str(Path(name).parent / metadata['image'])
            if image not in files:
                raise VerificationError(f'Bitmap specimen image missing from archive: {image}')
            content.append(f'<section><h2>{html.escape(Path(name).stem)}</h2><div class="bitmap-row">')
            for character in SAMPLES:
                box = metadata['glyphs'].get(character)
                if box is None:
                    continue
                # CSS background cropping works offline without cross-origin canvas reads.
                style = (f'width:{int(box["width"])}px;height:{int(box["height"])}px;'
                         f'background-image:url("../{image}");background-position:-{int(box["x"])}px -{int(box["y"])}px')
                content.append(f'<figure><div class="pixel" style=\'{style}\'></div><figcaption>U+{ord(character):04X}</figcaption></figure>')
            content.append('</div></section>')
    else:
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        root = ET.fromstring(files['build/family/centerlines.svg'])
        namespace = '{http://www.w3.org/2000/svg}'
        content.append('<p>Editable centerlines, not installable font outlines. Sample shapes below are taken directly from the included SVG.</p>')
        for symbol in root.iter(namespace + 'symbol'):
            title = symbol.find(namespace + 'title')
            if title is None or title.text not in SAMPLES:
                continue
            canvas = ET.Element(namespace + 'svg', {'viewBox': '0 0 24 24', 'width': '96', 'height': '96'})
            for child in symbol:
                canvas.append(child)
            content.append(f'<figure>{ET.tostring(canvas, encoding="unicode")}<figcaption>{html.escape(title.text)} U+{ord(title.text):04X}</figcaption></figure>')
    document = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
                f'<title>Singleline JP Lab {kind} specimen</title><style>' + ''.join(faces) +
                'body{font:16px system-ui;margin:2rem;background:#f6f3e9;color:#18343b}section{border-top:1px solid #bbb;padding:1rem 0}'
                '.sample{font-size:48px;line-height:1.8;overflow-wrap:anywhere}.warning{border-left:5px solid #a64;padding:1rem}'
                '.bitmap-row{display:flex;align-items:start;flex-wrap:wrap}figure{display:inline-block;margin:8px;padding:8px;background:#fff}'
                '.pixel{image-rendering:pixelated;background-repeat:no-repeat;filter:invert(1)}figcaption{font:10px monospace;margin-top:8px}'
                'label{display:inline-block;margin-right:1rem}</style>'
                f'<h1>Singleline JP Lab: {kind}</h1><p class="warning">{warning}</p>'
                '<p><a href="../PACKAGE-README.md">Package instructions</a> · <a href="../NOTICE.md">Notices</a> · '
                '<a href="../QA-REPORT.json">Bound QA report</a> · <a href="../PACKAGE-SHA256.json">Checksums</a></p>' +
                ''.join(content) + f'<script>{script}</script></html>\n')
    return document.encode('utf-8')


def adapt_distribution_docs(files):
    """Keep copied binary-package docs honest about omitted historical assets."""
    pattern = re.compile(r'!?\[([^\]]+)\]\(([^\s()]+)\)')
    for name in list(files):
        if not name.startswith('docs/') or not name.endswith('.md'):
            continue
        def link(match):
            label, target = match.groups()
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                return match.group(0)
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path)))
            if resolved in files:
                return match.group(0)
            return f'{label} (repository-only: `{resolved}`)'
        files[name] = pattern.sub(link, files[name].decode('utf-8')).encode('utf-8')


def package_readme(kind, version, gates):
    instructions = {
        'static': 'Install the eight TTF files in build/family/static using your OS font installer. Close and reopen applications. Remove conflicting older copies first. OS compatibility is unverified until the relevant gate passes.',
        'variable': 'Install the two TTF files in build/family/variable. Test wght 200–700 and slnt -12–0 in a variable-font-capable application. Support varies by application. The specimen has independent controls for both families.',
        'bitmap': 'The PNG/JSON/SJPB triplets are fixed 1-bit strikes, not OS-installable fonts. Use family/bitmap_reader.py with NumPy: BitmapFont(path).mask(text). All 8 styles × 16/18/24/32 px are included. The HTML specimen shows actual native atlas pixels.',
        'source': 'Editable centerlines are in build/family/centerlines.svg and centerlines.svgz. Both contain the complete source. The HTML specimen embeds sample centerlines and needs no fonts. Create a Python 3.12 virtual environment, install requirements-family.txt, then run build_family.py, python -m family.specimen, python family/tools/priority_glyph_qa.py, and verify_family.py --report build/family/reports/full-tests.json. Legacy assets are included for exact preservation checks; family binaries must be rebuilt or obtained from the other independent ZIPs.',
    }[kind]
    return (f'# Singleline JP Lab {version}: {kind}\n\n'
            f'Channel: {gates["channel"]}. Experimental: {gates["experimental"]}.\n\n'
            'This archive is independent: extract it and open specimen/index.html. Do not merge it with another archive to make the specimen work.\n\n'
            f'{instructions}\n\n'
            'Known limits: composition drafts have not all been proofread; small-size collisions remain. Structural/encoding success is not Japanese typographic approval. '
            f'Unrun platform/visual gates: {", ".join(gates["not_run"]) or "none"}.\n\n'
            'Read LICENSE, NOTICE.md, the CJKVI-IDS notices and Unicode license before redistribution or embedding. No OFL or unrestricted font license is implied.\n\n'
            'Copied binary-package docs mark links to omitted historical files as repository-only; editable source-package docs retain their original references.\n\n'
            'PACKAGE-SHA256.json and SHA256SUMS cover every other file except these two checksum indexes. QA-REPORT.json binds the complete reviewed source and artifact inventory, including files shipped in the other ZIPs. Digests detect changes; they are not signatures.\n').encode('utf-8')


def _read_inputs(root, output, subject):
    # Hash the same bytes we archive, not a previous stat or later independent read.
    sources, artifacts = {}, {}
    for target, base, entries in ((sources, root, subject['sources']), (artifacts, output, subject['artifacts'])):
        for name, expected in entries.items():
            data = safe_path(base, name).read_bytes()
            if digest(data) != expected:
                raise VerificationError(f'Input changed after verification: {name}')
            target[name] = data
    return sources, artifacts


def _write_zip(path, files):
    sums = {name: digest(data) for name, data in sorted(files.items())}
    entries = {**files, 'PACKAGE-SHA256.json': (json.dumps(sums, indent=2) + '\n').encode(),
               'SHA256SUMS': ''.join(f'{checksum}  {name}\n' for name, checksum in sums.items()).encode()}
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(PREFIX + name, ZIP_TIME)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None or len(archive.namelist()) != len(entries):
            raise VerificationError('ZIP integrity check failed')
        for name, checksum in sums.items():
            if digest(archive.read(PREFIX + name)) != checksum:
                raise VerificationError(f'ZIP checksum mismatch: {name}')
    return len(sums)


def package_family(root, destination, *, kind='source', channel='rc', version=VERSION,
                   output=None, report=None):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    output = Path(output).resolve() if output is not None else root / 'build/family'
    report = Path(report).resolve() if report is not None else output / 'reports/full-tests.json'
    if kind not in KINDS or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-rc\.[0-9]+)?', version):
        raise VerificationError('Invalid package kind or distribution version')
    if (channel == 'release' and '-rc.' in version) or (channel == 'rc' and '-rc.' not in version):
        raise VerificationError('The channel and version must agree: rc requires -rc.N; release forbids it')
    report_bytes = report.read_bytes()
    validation = json.loads(report_bytes)
    subject = validate_report(root, output, validation)
    gates = check_release_gates(root, output, subject, channel)
    inputs = {safe_path(root, name).resolve() for name in subject['sources']}
    inputs.update(safe_path(output, name).resolve() for name in subject['artifacts'])
    inputs.update((report, output / 'centerlines.svg'))
    if destination in inputs:
        raise VerificationError('Package destination would overwrite an input')
    manifest = load_manifest(root)
    sources, artifacts = _read_inputs(root, output, subject)
    files = {name: sources[name] for name in manifest['licenses']}
    files.update({name: data for name, data in sources.items() if name.startswith('docs/') and name.endswith('.md')})
    for name in ('coverage.json', 'build-summary.json', 'glyph-provenance.json.gz'):
        files['build/family/' + name] = artifacts[name]
    for name, data in artifacts.items():
        if name.startswith(('reports/', 'proofs/priority-glyphs/')):
            files['build/family/' + name] = data
    if kind == 'source':
        files.update(sources)
        files['build/family/centerlines.svgz'] = artifacts['centerlines.svgz']
        files['build/family/centerlines.svg'] = editable_centerlines(output)
    else:
        category = 'bitmaps' if kind == 'bitmap' else kind
        files.update({'build/family/' + name: data for name, data in artifacts.items() if name.startswith(category + '/')})
        if kind == 'bitmap':
            for name in ('family/__init__.py', 'family/bitmap_reader.py'):
                files[name] = sources[name]
            files['requirements-bitmap.txt'] = b'numpy==2.2.6\n'
    files['QA-REPORT.json'] = report_bytes
    files['RELEASE-STATUS.json'] = (json.dumps(gates, indent=2) + '\n').encode()
    files['PACKAGE-README.md'] = package_readme(kind, version, gates)
    files['specimen/index.html'] = specimen(kind, files)
    if kind != 'source':
        adapt_distribution_docs(files)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.family-package-', dir=destination.parent) as temporary:
        pending = Path(temporary) / 'package.zip'
        count = _write_zip(pending, files)
        if snapshot(root, output) != subject or report.read_bytes() != report_bytes:
            raise VerificationError('Inputs/report changed during packaging; no package was published')
        # Check the optional raw representation again; it is not part of tracked inputs.
        editable_centerlines(output)
        pending.replace(destination)
    return {'package': str(destination), 'kind': kind, 'channel': channel,
            'size_bytes': destination.stat().st_size, 'files': count,
            'sha256': digest(destination.read_bytes())}


def package_distributions(root, destination, **options):
    destination = Path(destination)
    version = options.get('version', VERSION)
    results = [package_family(root, destination / f'SinglelineJPLab-{version}-{kind}.zip',
                              kind=kind, **options) for kind in KINDS]
    # The directory checksum file is itself deterministic and covers the four ZIPs.
    (destination / 'SHA256SUMS').write_text(''.join(f'{item["sha256"]}  {Path(item["package"]).name}\n' for item in results), encoding='utf-8')
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path, help='Directory for all ZIPs, or a ZIP path with --kind')
    parser.add_argument('--kind', choices=KINDS, help='Build only one self-contained archive')
    parser.add_argument('--channel', choices=('rc', 'release'), required=True)
    parser.add_argument('--version', default=VERSION)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/family')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    options = dict(channel=args.channel, version=args.version, output=args.output, report=args.report)
    try:
        result = (package_family(ROOT, args.destination, kind=args.kind, **options) if args.kind else
                  package_distributions(ROOT, args.destination, **options))
    except (VerificationError, FileNotFoundError, json.JSONDecodeError) as error:
        parser.exit(1, f'Refusing to package: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
