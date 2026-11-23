"""Demo: phân loại bài nộp mới (cần mô hình từ scripts/p7_build_demo.py)."""
from pathlib import Path

import pytest

import classify
import config

S = Path(__file__).resolve().parents[1] / 'demo' / 'samples'
pytestmark = pytest.mark.skipif(not (config.PROCESSED / 'demo' / 'model_smallest.pkl').exists(),
                                reason='chưa dựng mô hình demo')


def test_correct(tmp_path):
    r = classify.classify('smallest', (S / 'smallest_dung.c').read_text(), config.WORK / 'pytest_demo' / 'ok')
    assert r['status'] == 'correct'


def test_strict_compare_cluster():
    r = classify.classify('smallest', (S / 'smallest_so_sanh_nghiem_ngat.c').read_text(),
                          config.WORK / 'pytest_demo' / 'bug')
    assert r['status'] == 'buggy' and r['n_fail'] > 0
    assert r['cluster'] == min(r['distances'], key=r['distances'].get)
    assert any(w['attr'] == 'D:diff.cmp_if' for w in r['why'])


def test_compile_error():
    r = classify.classify('smallest', 'int main( {', config.WORK / 'pytest_demo' / 'ce')
    assert r['status'] == 'compile_error'


def test_rejects_unknown_problem():
    with pytest.raises(ValueError):
        classify.classify('syllables', 'int main(){}', config.WORK / 'pytest_demo' / 'x')
