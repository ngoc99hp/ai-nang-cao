import pandas as pd
import pytest
import schema


def _tr():
    return pd.DataFrame({
        'sub_id': ['a', 'a', 'b'], 'problem': 'p', 'test_id': ['t0', 't1', None],
        'status': ['PASS', 'FAIL', 'COMPILE_ERROR'], 'status_sem': ['PASS', 'PASS', 'COMPILE_ERROR'],
        'returncode': pd.array([0, 3, None], dtype='Int32'), 'stdout': ['6', '5', 'err'],
    })


def test_round_trip(tmp_path):
    df = _tr()
    p = schema.save(df, schema.TEST_RESULTS, tmp_path / 'tr.parquet')
    back = schema.load(p, schema.TEST_RESULTS)
    pd.testing.assert_frame_equal(back, df[schema.TEST_RESULTS.names])


@pytest.mark.parametrize('bad, sch, msg', [
    (_tr().assign(status='PASSED'), schema.TEST_RESULTS, 'không hợp lệ'),
    (_tr().drop(columns='stdout'),  schema.TEST_RESULTS, 'Thiếu cột'),
    (_tr().assign(status_sem='OK'), schema.TEST_RESULTS, 'không hợp lệ'),
])
def test_validate_rejects(bad, sch, msg):
    with pytest.raises(ValueError, match=msg):
        schema.validate(bad, sch)


def test_duplicate_sub_id():
    df = pd.DataFrame({'sub_id': ['x', 'x'], 'source': 'bench', 'problem': 'p',
                       'code_path': ['a', 'b'], 'is_correct': [True, False],
                       'label_true': [None, None]})
    with pytest.raises(ValueError, match='trùng'):
        schema.validate(df, schema.SUBMISSIONS)
