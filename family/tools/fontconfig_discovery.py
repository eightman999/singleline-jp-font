"""Check current Lab fonts with a private, disposable Fontconfig configuration.

This checks discovery and character selection, not desktop rendering or installation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from xml.sax.saxutils import escape

FAMILIES = {
    'gothic': 'Gothic', 'italian': 'Italian Reverse Contrast',
    'italic': 'Italic', 'pc98-mincho': 'PC98 Mincho Inspired',
    'serif': 'Serif', 'singleline': 'Singleline',
    'subscript': 'Subscript', 'superscript': 'Superscript',
}
CHARSETS = ('20bb7', '9ad9', '65e5')


def font_paths(root):
    root = Path(root)
    result = {root / 'static' / f'SinglelineJPLab-{key}.ttf':
              f'Singleline JP Lab {name}' for key, name in FAMILIES.items()}
    result.update({root / 'variable' / f'SinglelineJPLab-{key}-VF.ttf':
                   f'Singleline JP Lab {FAMILIES[key]} Variable'
                   for key in ('gothic', 'serif')})
    return result


def hashes(paths):
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)}


def configuration(font_dir, cache_dir):
    # No include of system or user configuration, directories, or caches.
    return ('<?xml version="1.0"?>\n<!DOCTYPE fontconfig SYSTEM "fonts.dtd">\n'
            '<fontconfig><dir>' + escape(str(font_dir)) + '</dir><cachedir>'
            + escape(str(cache_dir)) + '</cachedir></fontconfig>\n')


def audit(root):
    fonts = font_paths(root)
    report = {
        'scope': 'Isolated Fontconfig discovery and family/character matching only; '
                 'not installation, desktop application rendering, or visual certification',
        'status': 'failed', 'font_file_count': len(fonts),
        'match_requests': [], 'fonts_sha256': {},
        'system_or_user_font_directories_modified': False,
        'isolation': 'Temporary private configuration, font copies and cache; '
                     'no system/user font directories changed.',
    }
    try:
        report['fonts_sha256'] = hashes(fonts)
        commands = {name: shutil.which(name) for name in ('fc-list', 'fc-match')}
        missing = [name for name, path in commands.items() if not path]
        if missing:
            report.update(status='not-run', reason='Fontconfig unavailable: ' + ', '.join(missing))
            return report
        with tempfile.TemporaryDirectory(prefix='singleline-fontconfig-') as temp:
            temp = Path(temp)
            font_dir = temp / 'fonts'
            font_dir.mkdir()
            cache_dir = temp / 'cache'
            cache_dir.mkdir()
            original_by_copy = {}
            for path in fonts:
                copied = font_dir / path.name
                shutil.copyfile(path, copied)
                if hashlib.sha256(copied.read_bytes()).hexdigest() != report['fonts_sha256'][str(path)]:
                    raise ValueError(f'Font changed during copy: {path}')
                original_by_copy[str(copied)] = path
            config = temp / 'fonts.conf'
            config.write_text(configuration(font_dir, cache_dir), encoding='utf-8')
            env = dict(os.environ, FONTCONFIG_FILE=str(config), FONTCONFIG_PATH=str(temp),
                       XDG_CACHE_HOME=str(cache_dir), HOME=str(temp))
            env.pop('FONTCONFIG_SYSROOT', None)

            def run(name, *args):
                return subprocess.run([commands[name], *args], env=env, check=True,
                                      capture_output=True, text=True, timeout=30)

            version = run('fc-list', '--version')
            report['fontconfig_version'] = (version.stdout + version.stderr).strip()
            discovered = set(run('fc-list', '--format=%{file}\n').stdout.splitlines())
            if discovered != set(original_by_copy):
                raise ValueError('Discovery did not return exactly the ten isolated fonts')
            report['discovered_files'] = sorted(str(original_by_copy[p]) for p in discovered)
            for original, family in fonts.items():
                requests = [family] + [f'{family}:charset={c}' for c in CHARSETS]
                if original.parent.name == 'variable':
                    requests += [f'{family}:fontvariations={v}' for v in
                                 ('wght=700,slnt=-12', 'wght=200,slnt=0')]
                for request in requests:
                    line = run('fc-match', '--format=%{file}\t%{family}\t%{style}\t%{fontvariations}', request).stdout
                    selected, actual_family, style, variations = line.split('\t')
                    path = original_by_copy.get(selected)
                    row = {'request': request, 'selected_file': str(path) if path else selected,
                           'family': actual_family, 'style': style}
                    if ':fontvariations=' in request:
                        row['fontvariations'] = variations
                    report['match_requests'].append(row)
                    if path != original or family not in actual_family.split(','):
                        raise ValueError(f'Unexpected family selection: {request}')
                    if ':charset=' in request:
                        supported = set(run('fc-list', request, '--format=%{file}\n').stdout.splitlines())
                        if selected not in supported:
                            raise ValueError(f'Selected font does not support requested charset: {request}')
                    if ':fontvariations=' in request and variations != request.split(':fontvariations=', 1)[1]:
                        raise ValueError(f'Variation request was not retained: {request}')
        if hashes(fonts) != report['fonts_sha256']:
            raise ValueError('Input fonts changed during discovery')
        report['status'] = 'passed'
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report['reason'] = str(error)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('build/family'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit(args.root)
    output = args.output or args.root / 'reports' / 'fontconfig-discovery.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Fontconfig discovery: {report['status']} ({output})")
    return 1 if report['status'] == 'failed' else 0


if __name__ == '__main__':
    raise SystemExit(main())
