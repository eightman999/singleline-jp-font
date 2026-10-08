"""Current-file evidence and explicit unsupported-platform status."""
import hashlib
from family.tools import fontconfig_discovery as discovery


def test_missing_fontconfig_records_current_hashes_without_success(tmp_path, monkeypatch):
    fonts = discovery.font_paths(tmp_path)
    for path in fonts:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(path.name.encode())
    monkeypatch.setattr(discovery.shutil, 'which', lambda name: None)
    report = discovery.audit(tmp_path)
    assert report['status'] == 'not-run'
    assert report['font_file_count'] == 10
    assert report['match_requests'] == []
    assert not report['system_or_user_font_directories_modified']
    assert report['fonts_sha256'] == {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in fonts}
    next(iter(fonts)).write_bytes(b'new font bytes')
    assert discovery.audit(tmp_path)['fonts_sha256'] != report['fonts_sha256']


def test_missing_input_is_failure(tmp_path):
    report = discovery.audit(tmp_path)
    assert report['status'] == 'failed'
    assert report['reason']


def test_configuration_has_only_private_paths_and_escapes_xml(tmp_path):
    import xml.etree.ElementTree as ET
    font_dir = tmp_path / 'fonts & more'
    cache_dir = tmp_path / 'cache'
    root = ET.fromstring(discovery.configuration(font_dir, cache_dir))
    assert [(child.tag, child.text) for child in root] == [
        ('dir', str(font_dir)), ('cachedir', str(cache_dir))]


def test_subprocess_timeout_is_failure_and_config_is_disposable(tmp_path, monkeypatch):
    import subprocess
    from pathlib import Path
    fonts = discovery.font_paths(tmp_path)
    for path in fonts:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(path.name.encode())
    before = discovery.hashes(fonts)
    monkeypatch.setattr(discovery.shutil, 'which', lambda name: '/usr/bin/' + name)
    configs = []

    def fail(args, **kwargs):
        config = Path(kwargs['env']['FONTCONFIG_FILE'])
        configs.append(config)
        assert config.is_file()
        assert kwargs['timeout'] == 30
        assert 'FONTCONFIG_SYSROOT' not in kwargs['env']
        raise subprocess.TimeoutExpired(args, 30)

    monkeypatch.setattr(discovery.subprocess, 'run', fail)
    report = discovery.audit(tmp_path)
    assert report['status'] == 'failed'
    assert 'timed out' in report['reason']
    assert discovery.hashes(fonts) == before
    assert configs and not configs[0].exists()
