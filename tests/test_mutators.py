import pytest

import mutators as mu

SRC = b'''#include <stdio.h>
#include <stdlib.h>
void sw(int *a, int *b);
void sw(int *a, int *b){int t=*a; *a=*b; *b=t;}
int main(){
  int n, i, s = 0, mn, x;
  scanf("%d", &n);
  mn = n;
  for (i = 0; i < n; i++) { s += i; if (mn >= i && n == 2) mn = i; }
  while (n > 0) n = n / 10;
  printf("%f\\n", (float)s / n);
  printf("%d\\n", 7 / 2.0);
  x = -n;
  n = -n;
  sw(&n, &mn);
  return abs(n);
}
'''


def _by_op(op):
    return [m for m in mu.find_all(SRC) if m.op == op]


def _apply1(op, k=0):
    return mu.apply(SRC, [_by_op(op)[k]]).decode()


def test_all_labels_found():
    assert {m.label for m in mu.find_all(SRC)} == set(mu.LABELS)


@pytest.mark.parametrize('op, must_contain', [
    ('loop_cmp', 'i <= n'),
    ('loop_init', 'for (i = 1;'),
    ('if_cmp', 'mn > i'),
    ('eq_to_assign', 'n = 2)'),
    ('drop_cast', 'printf("%f\\n", s / n)'),
    ('float_lit_to_int', '7 / 2)'),
    ('extremum_init_zero', 'mn = 0;'),
    ('accum_init', 's = 1,'),
    ('drop_abs', 'return n;'),
    ('drop_negate', '  ;\n'),
])
def test_single_ops(op, must_contain):
    assert must_contain in _apply1(op)


def test_m6_stmt_into_loop_moves_statement():
    outs = [mu.apply(SRC, [m]).decode() for m in _by_op('stmt_into_loop')]
    # while không có ngoặc → được bọc { ... } và printf chuyển vào trong
    assert any('{ n = n / 10; printf("%f\\n", (float)s / n); }' in o for o in outs)


def test_m6_early_break():
    assert any('mn = i;  break; }' in mu.apply(SRC, [m]).decode() for m in _by_op('early_break'))


def test_m2_by_value_rewrites_param_body_proto_and_call():
    m = next(m for m in _by_op('by_value') if 'truyền a ' in m.desc)
    out = mu.apply(SRC, [m]).decode()
    assert out.count('void sw(int a, int *b)') == 2          # prototype + định nghĩa
    assert 'int t=a; a=*b; *b=t;' in out
    assert 'sw(n, &mn)' in out
    allp = mu.apply(SRC, [_by_op('by_value_all')[0]]).decode()
    assert 'int t=a; a=b; b=t;' in allp and 'sw(n, mn)' in allp


def test_drop_minus_skips_negate_statement():
    descs = [m.desc for m in _by_op('drop_minus')]
    assert descs == ['bỏ dấu trừ -n']                       # chỉ x = -n, không phải n = -n
    assert 'x = n;' in _apply1('drop_minus')


def test_combine_non_overlapping():
    a, b = _by_op('loop_cmp')[0], _by_op('if_cmp')[0]
    assert not mu.overlaps(a, b)
    out = mu.apply(SRC, [a, b]).decode()
    assert 'i <= n' in out and 'mn > i' in out
    assert mu.label_of([a, b]) == 'M1+M7'


def test_overlap_rejected():
    a = _by_op('loop_cmp')[0]
    with pytest.raises(ValueError):
        mu.apply(SRC, [a, a])
