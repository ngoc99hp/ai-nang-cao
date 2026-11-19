import pandas as pd

import features as ft


def _tr(rows):
    return pd.DataFrame(rows, columns=['test_id', 'status_sem', 'stdout'])


def test_diff_flags_numeric():
    f = ft._diff_flags('median', [3], [2], '1 2 3\n')
    assert f == {'off_by_one', 'wrong_input_elem'}
    assert 'output_zero' in ft._diff_flags('smallest', [0], [5], '5 6 7 8\n')
    assert ft._diff_flags('median', [], [2], '1 2 3\n') == {'missing_answer'}
    assert 'multiple_answers' in ft._diff_flags('median', [2, 3], [2], '1 2 3\n')


def test_diff_flags_digits_and_average():
    assert ft._diff_flags('digits', [6, 7, 8, 9], [6, 7, 8, -9], '-9876\n') == {'sign_error'}
    assert ft._diff_flags('digits', [9, 8, 7, 6], [6, 7, 8, 9], '9876\n') == {'digits_reversed'}
    assert ft._diff_flags('digits', [6, 7, 8], [6, 7, 8, 9], '9876\n') == {'missing_last'}
    assert ft._diff_flags('average', [2.0], [2.33], '') == {'truncated_decimal'}
    assert ft._diff_flags('average', [0.0], [0.33], '') == {'output_zero'}


def test_diff_flags_grade():
    assert ft._diff_flags('grade', ['B'], ['A'], '') == {'adjacent_grade', 'grade_too_low'}


def test_test_props():
    assert ft.test_props('smallest', '2 2 2 3\n') == {'tie', 'sorted'}
    assert ft.test_props('grade', '80 70 60 50\n80\n') == {'boundary', 'top'}
    assert ft.test_props('digits', '-9876\n') == {'negative'}


def test_output_features_aggregate():
    tests = {'bb1': ('1 1 1 1\n', '1 is the smallest\n'), 'bb2': ('4 3 2 1\n', '1 is the smallest\n')}
    tr = _tr([('bb1', 'PASS', '1 is the smallest'), ('bb2', 'FAIL', '4 is the smallest')])
    O = ft.output_features('smallest', tr, tests)
    assert O[('O', 'output', 'wrong_input_elem')] == 'T'
    assert O[('O', 'tests_tie', 'fail')] == 'none'
    assert O[('O', 'tests', 'fail_frac')] == 'mid'


def test_ast_features():
    code = b'''#include <stdio.h>
void upd(int *m, int x){ if (x < *m) *m = x; }
int main(){ int a[4], i, min, s = 0;
  for (i = 0; i <= 3; i++) { scanf("%d", &a[i]); s += a[i]; printf("%d", s); }
  min = a[0]; if (min = 0) upd(&min, a[1]); printf("%d", (float)s / 4); return 0; }'''
    A = ft.ast_features(code)
    assert A[('A', 'loop', 'cmp_op')] == '<='
    assert A[('A', 'loop', 'output_in_loop')] == 'T'
    assert A[('A', 'condition', 'assign_in_cond')] == 'T'
    assert A[('A', 'function', 'has_ptr_param')] == 'T'
    assert A[('A', 'extremum', 'init')] == 'expr'
    assert A[('A', 'accumulator', 'init')] == 'zero'
    assert A[('A', 'division', 'has_cast')] == 'T'
