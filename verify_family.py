#!/usr/bin/env python3
"""Run independent family QA and report incomplete builds honestly.

Exit 0 means all selected tests passed with no skips. It is not visual approval
of composition-draft Kanji. Exit 1 means failures; exit 2 means missing outputs,
skipped checks, or another incomplete verification.
"""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent


def is_cjk_scalar(text):
    if len(text) != 1:
        return False
    cp = ord(text)
    return 0x3400 <= cp <= 0x9FFF or 0xF900 <= cp <= 0xFAFF or 0x20000 <= cp <= 0x323AF


def audit_bitmap_collisions(tests, output):
    """Exhaustive exact-render collision report, never a legibility verdict.

    Trim empty margins but preserve advance and baseline-relative ink position,
    so harmless crop guards do not hide genuinely identical displayed glyphs.
    """
    import numpy as np
    source, _ = tests.load_glyphs()
    characters = sorted(c for c in source if is_cjk_scalar(c))
    source_signatures = {}
    for c in characters:
        g = source[c]
        normalized = (g.advance, float(g.width_factor), bool(g.filled),
                      [[(float(x), float(y)) for x, y in path] for path in g.paths])
        source_signatures[c] = hashlib.sha256(json.dumps(normalized, separators=(',', ':')).encode()).hexdigest()
    result = {'comparison': 'Exact baseline-aligned black-pixel masks and advance; blank margins ignored',
              'scalar_cjk_identities': len(characters), 'expected_strikes': len(tests.STYLE_KEYS) * len(tests.STRIKE_SIZES),
              'strikes': [], 'visual_legibility_certified': False}
    for style in tests.STYLE_KEYS:
        for size in tests.STRIKE_SIZES:
            path = output / 'bitmaps' / f'{style}-{size}.sjpb'
            if not path.is_file():
                continue
            font = tests.BitmapFont(path)
            signatures = defaultdict(list)
            blank, missing = [], []
            for c in characters:
                if c not in font.glyphs:
                    missing.append(c)
                    continue
                mask = font.bitmap(c)
                rows, cols = np.nonzero(mask)
                if not len(rows):
                    blank.append(c)
                    continue
                top, bottom, left, right = int(rows.min()), int(rows.max()) + 1, int(cols.min()), int(cols.max()) + 1
                _, _, advance, bx, by, _, _ = font.glyphs[c]
                trim = mask[top:bottom, left:right]
                description = (advance, bx + left, by - top, right - left, bottom - top)
                digest = hashlib.sha256(json.dumps(description).encode() + np.packbits(trim, axis=1, bitorder='big').tobytes()).hexdigest()
                signatures[digest].append(c)
            groups = []
            for group in signatures.values():
                if len(group) < 2:
                    continue
                different_sources = len({source_signatures[c] for c in group})
                groups.append({'characters': group, 'codepoints': [f'U+{ord(c):04X}' for c in group],
                               'classification': 'source-equivalent' if different_sources == 1 else 'raster-only-collapse',
                               'source_geometry_count': different_sources,
                               'all_legacy': all(source[c].status == 'legacy-existing' for c in group)})
            groups.sort(key=lambda g: g['characters'])
            result['strikes'].append({'style': style, 'nominal_pixels': size, 'checked': len(characters) - len(missing),
                                      'missing': missing, 'blank': blank, 'collision_group_count': len(groups),
                                      'raster_only_group_count': sum(g['classification'] == 'raster-only-collapse' for g in groups),
                                      'collision_groups': groups})
    result['strikes_checked'] = len(result['strikes'])
    result['complete_inventory'] = result['strikes_checked'] == result['expected_strikes']
    result['strikes_with_raster_only_collapses'] = sum(s['raster_only_group_count'] > 0 for s in result['strikes'])
    result['warning'] = 'Exact collisions are disclosed separately from structural test success. Different characters can be indistinguishable at low resolution; all glyphs still require visual proofreading.'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/family')
    parser.add_argument('--unit', action='store_true', help='Only source and small-sample tests; does not verify a release')
    parser.add_argument('--report', type=Path, help='Optional JSON report path')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('test_family_inventory', ROOT / 'tests/test_family.py')
    tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tests)
    missing = [] if args.unit else [str(p) for p in tests.required_artifacts() if not (args.output / p).is_file()]
    env = {**os.environ, 'FAMILY_OUTPUT': str(args.output.resolve()), 'FAMILY_REQUIRE_OUTPUTS': '1'}
    with tempfile.TemporaryDirectory(prefix='family-qa-') as temp:
        junit = Path(temp) / 'results.xml'
        command = [sys.executable, '-m', 'pytest', str(ROOT / 'tests/test_family.py'), '-q', f'--junitxml={junit}']
        if args.unit:
            command += ['-k', 'not TestFullArtifacts']
        run = subprocess.run(command, cwd=ROOT, env=env)
        cases = []
        if junit.is_file():
            for case in ET.parse(junit).getroot().iter('testcase'):
                status = 'passed'
                detail = ''
                for tag in ('failure', 'error', 'skipped'):
                    result = case.find(tag)
                    if result is not None:
                        status = tag
                        detail = result.attrib.get('message', '')
                        break
                cases.append({'test': case.attrib.get('classname', '') + '.' + case.attrib.get('name', ''), 'status': status, 'detail': detail})
    counts = {state: sum(c['status'] == state for c in cases) for state in ('passed', 'failure', 'error', 'skipped')}
    incomplete = bool(missing or counts['skipped'] or not cases or run.returncode not in (0, 1))
    outcome = 'incomplete' if incomplete else 'failed' if run.returncode else 'passed'
    report = {'scope': 'source-and-sample-only' if args.unit else 'full-family-structural-verification',
              'outcome': outcome, 'counts': counts, 'missing_artifacts': missing,
              'nominal_pixel_sizes': list(tests.STRIKE_SIZES), 'expected_bitmap_strikes': len(tests.STYLE_KEYS) * len(tests.STRIKE_SIZES),
              'visual_legibility_certified': False,
              'warning': 'Passing verifies structural and binary checks only. Expanded Kanji remain component/composition drafts, not individually proofread; this is not a legibility certificate. Consult coverage.json for exact identities and status counts.',
              'tests': cases}
    if not args.unit:
        try:
            report['bitmap_collision_audit'] = audit_bitmap_collisions(tests, args.output)
        except Exception as error:
            report['bitmap_collision_audit'] = {'outcome': 'incomplete', 'error': str(error)}
            incomplete = True
            report['outcome'] = 'incomplete'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in {'tests', 'bitmap_collision_audit'}}, ensure_ascii=False, indent=2))
    return 2 if incomplete else 1 if run.returncode else 0


if __name__ == '__main__':
    raise SystemExit(main())
