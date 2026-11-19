"""Checker DP0. Mẫu lấy từ output thật trong metadata.json (log P1.4)."""
import ast
import json

import pytest

import introclass as ic
import normalize as nz

CASES = [  # problem, expected, output, input, strict, semantic
    ('grade', 'Thank you. ... >Student has an A grade\n', '... > Stdent has an A grade\n', '', False, True),
    ('grade', 'Student has failed the course\n', 'Student has an F grade\n', '', False, True),
    ('grade', 'Student has an B grade\n', 'Student has an C grade\n', '', False, False),
    ('median', '> 6 is the median\n', '> 6 IS the median\n', '6 6 1\n', False, True),
    ('median', '> 6 is the median\n', '> 6 is the median\n8 is the median\n', '6 1 8\n', True, False),  # bug gốc: token cuối còn '\n'
    ('smallest', '> -1 is the smallest\n', '> -1 is the smalles\n', '', False, True),
    ('smallest', '> 0 is the smallest\n', '> 0 is the smallest 1 is the smallest', '0 1 2 3\n', True, False),
    ('syllables', '> The number of syllables is 1.\n', '> The number of syllables is 18.\n', '', True, False),
    ('digits', '> \n0\nThat\'s all\n', 'Enter > \n0That\'s all\n', '0\n', False, True),
    ('digits', '> \n4\n7\n3\n9\n8\nbye\n', '> The digits for the 89374 are: \n4\n7\n3\n9\n8\n', '89374\n', True, True),
    ('digits', '> \n6\n7\n8\n-9\nbye\n', '> -6\nbye\n', '-9876\n', False, False),
    ('checksum', '> Check sum is K\n', '> Checksum is K\n', '', True, True),
    ('checksum', '> Check sum is K\n', '> Check sum is: K\n', '', False, True),
]


@pytest.mark.parametrize('prob, exp, out, inp, strict, sem', CASES)
def test_cases(prob, exp, out, inp, strict, sem):
    assert nz.check(prob, out, exp, inp, 'strict') is strict
    assert nz.check(prob, out, exp, inp, 'semantic') is sem


def test_no_problem_token_compare():
    assert nz.check(None, ' 6 \n', '6\n', '', 'strict') and nz.check(None, '6', '6\n', '', 'semantic')


@pytest.mark.skipif(not ic.LOCAL.exists(), reason='IntroClass chưa clone')
@pytest.mark.parametrize('prob', ['checksum', 'digits', 'grade', 'median', 'smallest', 'syllables'])
def test_strict_matches_metadata(prob):
    """Port strict chấm lại output đã ghi trong metadata → khớp pass/fail ≥ 99% (deterministic)."""
    tests = {t: (i.read_text(), o.read_text()) for t, i, o in ic.tests_of(prob)}
    n = ok = 0
    for v in ic.versions(prob):
        m = json.loads((v / 'metadata.json').read_text())
        if m.get('nondeterministic'):
            continue
        for pre, suite in ic.SUITES.items():
            for num, outs in m['output'][suite].items():
                if not outs:
                    continue
                try:
                    out = ast.literal_eval(outs[0]).decode('utf-8', errors='replace')
                except (SyntaxError, ValueError):
                    out = str(outs[0])
                inp, exp = tests[f'{pre}{num}']
                n += 1
                ok += nz.check(prob, out, exp, inp, 'strict') == (num in m[suite]['pass'])
    assert ok / n >= 0.99, (ok, n)
