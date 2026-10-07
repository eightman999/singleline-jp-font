"""Explicitly loaded pytest audit hook; no optional third-party plugin required."""
import json
import os
from pathlib import Path

_collected = []
_deselected = []
_cases = {}


def pytest_collection_finish(session):
    _collected[:] = [item.nodeid for item in session.items]


def pytest_deselected(items):
    _deselected.extend(item.nodeid for item in items)


def pytest_runtest_logreport(report):
    if report.when == 'call' or report.failed or report.skipped:
        previous = _cases.get(report.nodeid)
        status = ('failure' if report.when == 'call' else 'error') if report.failed else 'skipped' if report.skipped else 'passed'
        # A successful teardown must not overwrite a call/setup failure.
        if previous is None or status != 'passed':
            _cases[report.nodeid] = {'test': report.nodeid, 'status': status,
                                    'detail': str(report.longrepr) if report.failed or report.skipped else ''}


def pytest_sessionfinish(session, exitstatus):
    path = os.environ.get('FAMILY_QA_INVENTORY')
    if path:
        Path(path).write_text(json.dumps({'collected': _collected, 'deselected': _deselected,
                                         'tests': list(_cases.values()), 'exit_code': int(exitstatus)}, indent=2) + '\n', encoding='utf-8')
