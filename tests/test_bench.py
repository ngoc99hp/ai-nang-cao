"""Mọi lời giải tự viết phải PASS toàn bộ test (strict + semantic)."""
import pytest

import bench
import runner


@pytest.mark.parametrize('prob', bench.SYNTH_PROBLEMS)
def test_bench_solutions_pass(prob, tmp_path):
    subs = bench.sources(prob)
    assert subs, f'chưa có lời giải tự viết cho {prob}'
    rows = runner.run_batch(subs, bench.tests_of(prob), tmp_path, problem=prob)
    bad = [(r['sub_id'], r['test_id'], r['status'], r['status_sem'], r['stdout'][:80])
           for r in rows if r['status'] != 'PASS' or r['status_sem'] != 'PASS']
    assert not bad, bad
