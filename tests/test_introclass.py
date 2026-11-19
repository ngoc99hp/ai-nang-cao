"""Kiểm tra parser trên dataset thật (bỏ qua nếu chưa clone)."""
import json

import pytest

import introclass as ic
import schema

pytestmark = pytest.mark.skipif(not ic.LOCAL.exists(), reason='IntroClass chưa clone')

EXPECTED = {  # (bb, wb, versions) — mục 5.3 của plan
    'checksum': (6, 10, 69), 'digits': (6, 10, 236), 'grade': (9, 9, 268),
    'median': (7, 6, 232), 'smallest': (8, 8, 177), 'syllables': (6, 10, 161),
}


def test_problems():
    assert ic.problems() == sorted(EXPECTED)


@pytest.mark.parametrize('prob', sorted(EXPECTED))
def test_counts_and_schema(prob):
    bb, wb, nv = EXPECTED[prob]
    tids = [t for t, _, _ in ic.tests_of(prob)]
    assert sum(t.startswith('bb') for t in tids) == bb
    assert sum(t.startswith('wb') for t in tids) == wb
    df = ic.load_versions(prob)
    assert len(df) == nv
    assert df['code_path'].notna().all()
    assert df['meta_complete'].all()
    assert df['bc_sha_ok'].all()
    schema.validate(df, schema.SUBMISSIONS)       # sub_id duy nhất, enum hợp lệ


@pytest.mark.parametrize('prob', sorted(EXPECTED))
def test_sh_mapping_matches_metadata(prob):
    """pN trong *_test.sh phải đúng là các test pass trong metadata.json."""
    for v in ic.versions(prob)[:40]:
        m = json.loads((v / 'metadata.json').read_text())
        for pre, suite in ic.SUITES.items():
            mp = ic.parse_test_sh(v / f'{suite}_test.sh')
            assert {t for k, t in mp.items() if k[0] == 'p'} == {f'{pre}{n}' for n in m[suite]['pass']}
            assert {t for k, t in mp.items() if k[0] == 'n'} == {f'{pre}{n}' for n in m[suite]['fail']}
