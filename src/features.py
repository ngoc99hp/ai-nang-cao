"""Trích xuất bộ ba Đối tượng–Thuộc tính–Giá trị (OAV) cho mỗi bài làm sai (Phase 3).

Ba nhóm (khóa cột wide = '<G>:<object>.<attribute>'):
  T  Test        : object = test_id, attribute = status        (PASS/FAIL/TIMEOUT/CRASH/OUTPUT_LIMIT)
  O  Output-diff : so đáp án trích từ output với đáp án đúng trên các test fail; và fail theo
                   thuộc tính của test (ca bằng nhau, số âm, đúng ngưỡng...) → none/some/all
  A  AST         : đặc trưng cấu trúc mã nguồn (tree-sitter, duyệt đệ quy)
Mọi giá trị là chuỗi (categorical); bool ghi 'T'/'F'.
"""
import re
from collections import defaultdict

import ast_utils as au
import normalize as nz

GROUPS = ('T', 'O', 'A')
LOOPS = ('for_statement', 'while_statement', 'do_statement')
CMP = ('<', '<=', '>', '>=')
EXTREMUM = re.compile(r'(?i)(min|max|mn|mx|small|large|big|least|great|low|high|med)')


def _b(x) -> str:
    return 'T' if x else 'F'


# =============================================================== T: Test

def test_features(tr_sub) -> dict:
    """tr_sub: các dòng test_results của 1 bài (đã bỏ test_id null)."""
    return {('T', t, 'status'): s for t, s in zip(tr_sub.test_id, tr_sub.status_sem)}


# =============================================================== O: Output-diff

def _ints(s):
    return [int(x) for x in re.findall(r'-?\d+', s)]


def test_props(problem: str, inp: str) -> set[str]:
    """Thuộc tính của input test — dùng cho 'fail_on_<prop>'."""
    v = _ints(inp)
    props = set()
    if problem in ('median', 'smallest'):
        if len(set(v)) < len(v):
            props.add('tie')
        if any(x < 0 for x in v):
            props.add('negative')
        if 0 in v:
            props.add('zero')
        if v == sorted(v):
            props.add('sorted')
    elif problem == 'digits':
        n = v[0]
        props |= {p for p, c in [('negative', n < 0), ('zero', n == 0), ('single_digit', abs(n) < 10),
                                 ('inner_zero', n != 0 and '0' in str(abs(n)))] if c}
    elif problem == 'grade':
        t, score = v[:4], v[4]
        props |= {p for p, c in [('boundary', score in t), ('failing', score < t[3]),
                                 ('top', score >= t[0])] if c}
    elif problem == 'average':
        n, xs = v[0], v[1:]
        props |= {p for p, c in [('negative', any(x < 0 for x in xs)), ('single', n == 1),
                                 ('non_integer', sum(xs) % n != 0)] if c}
    return props


_GRADE_ORDER = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'failed': 4}


def _diff_flags(problem, got, truth, inp) -> set[str]:
    """Kiểu sai của 1 test fail (đã chạy xong)."""
    f = set()
    if not got:
        return {'missing_answer'}
    if problem == 'digits':
        ag, at = [abs(x) for x in got], [abs(x) for x in truth]
        if ag == at:
            f.add('sign_error')
        elif ag == at[::-1]:
            f.add('digits_reversed')
        elif ag == at[:-1]:
            f.add('missing_last')
        elif len(got) > len(truth):
            f.add('extra_items')
        elif len(got) < len(truth):
            f.add('missing_items')
        else:
            f.add('wrong_digit')
        return f
    if len(set(got)) > 1:
        f.add('multiple_answers')
    g, t = got[-1], truth[0]
    if problem == 'grade':
        d = _GRADE_ORDER.get(g, 9) - _GRADE_ORDER[t]
        f.add('adjacent_grade' if abs(d) == 1 else 'far_grade')
        f.add('grade_too_low' if d > 0 else 'grade_too_high')
        return f
    if g == 0 and t != 0:
        f.add('output_zero')
    if t != 0 and g == -t:
        f.add('sign_error')
    if problem == 'average':
        if g == float(int(t)) and g != t and int(t) != 0:      # |t| < 1 thì không phân biệt được với output_zero
            f.add('truncated_decimal')
        return f
    vals = _ints(inp)
    if abs(g - t) == 1:
        f.add('off_by_one')
    f.add('wrong_input_elem' if g in vals else 'not_input_elem')
    return f


def output_features(problem, tr_sub, tests: dict, flags: dict | None = None) -> dict:
    """tests: test_id → (input_text, expected_text). flags: cờ phụ của dữ liệu thật."""
    out = {}
    kinds, n_fail = defaultdict(int), 0
    prop_tot, prop_fail = defaultdict(int), defaultdict(int)
    for t, st, so in zip(tr_sub.test_id, tr_sub.status_sem, tr_sub.stdout):
        inp, exp = tests[t]
        props = test_props(problem, inp)
        failed = st != 'PASS'
        for p in props:
            prop_tot[p] += 1
            prop_fail[p] += failed
        if not failed:
            continue
        n_fail += 1
        if st == 'FAIL':
            for k in _diff_flags(problem, nz.answers(problem, so), nz.answers(problem, exp), inp):
                kinds[k] += 1
        else:
            kinds[st.lower()] += 1                      # timeout / crash / output_limit
    for k in sorted(kinds):
        out[('O', 'output', k)] = 'T'
    for p in sorted(prop_tot):
        r = prop_fail[p] / prop_tot[p]
        out[('O', f'tests_{p}', 'fail')] = 'none' if r == 0 else 'all' if r == 1 else 'some'
    frac = n_fail / max(len(tr_sub), 1)
    out[('O', 'tests', 'fail_frac')] = 'all' if frac == 1 else 'high' if frac > 2 / 3 else \
        'mid' if frac > 1 / 3 else 'low'
    for k, v in (flags or {}).items():
        out[('O', 'run', k)] = _b(v)
    return out


# =============================================================== A: AST

def _t(n):
    return n.text.decode('utf-8', errors='replace')


def _f(n, name):
    return n.child_by_field_name(name)


def _inside(n, types):
    p = n.parent
    while p is not None:
        if p.type in types:
            return True
        p = p.parent
    return False


def _cmp_ops(expr):
    return {_t(_f(n, 'operator')) for n in au.walk(expr)
            if n.type == 'binary_expression' and _t(_f(n, 'operator')) in CMP}


def _opset(ops):
    return ','.join(sorted(ops)) if ops else 'none'


def ast_features(code: bytes) -> dict:
    root = au.parse(code).root_node
    nodes = list(au.walk(root))
    loops = [n for n in nodes if n.type in LOOPS]
    ifs = [n for n in nodes if n.type == 'if_statement']
    funcs = [n for n in nodes if n.type == 'function_definition']
    calls = [n for n in nodes if n.type == 'call_expression']
    A = {}

    # vòng lặp
    A[('A', 'loop', 'count')] = '0' if not loops else '1' if len(loops) == 1 else '2+'
    A[('A', 'loop', 'cmp_op')] = _opset(set().union(*[_cmp_ops(_f(l, 'condition')) for l in loops
                                                      if _f(l, 'condition') is not None]))
    A[('A', 'loop', 'output_in_loop')] = _b(any(_t(_f(c, 'function')) in ('printf', 'puts', 'putchar')
                                                and _inside(c, LOOPS) for c in calls))
    A[('A', 'loop', 'return_in_loop')] = _b(any(n.type == 'return_statement' and _inside(n, LOOPS) for n in nodes))
    A[('A', 'loop', 'break_in_loop')] = _b(any(n.type == 'break_statement' and _inside(n, LOOPS)
                                               and not _inside(n, ('switch_statement',)) for n in nodes))
    # điều kiện
    conds = [_f(n, 'condition') for n in ifs + loops if _f(n, 'condition') is not None]
    A[('A', 'condition', 'assign_in_cond')] = _b(any(m.type == 'assignment_expression'
                                                     for c in conds for m in au.walk(c)))
    if_ops = set().union(*[_cmp_ops(_f(i, 'condition')) for i in ifs]) if ifs else set()
    strict, loose = if_ops & {'<', '>'}, if_ops & {'<=', '>='}
    A[('A', 'condition', 'if_cmp')] = 'none' if not if_ops else 'mixed' if strict and loose else \
        'strict' if strict else 'nonstrict'
    A[('A', 'condition', 'n_if')] = '0' if not ifs else '1-3' if len(ifs) <= 3 else '4+'
    # hàm, con trỏ
    user_funcs = [f for f in funcs if 'main' not in _t(_f(f, 'declarator')).split('(')[0]]
    A[('A', 'function', 'n_user_funcs')] = '0' if not user_funcs else '1' if len(user_funcs) == 1 else '2+'
    ptr_params = [p for f in user_funcs for p in au.walk(_f(f, 'declarator'))
                  if p.type == 'parameter_declaration' and _f(p, 'declarator') is not None
                  and _f(p, 'declarator').type == 'pointer_declarator']
    A[('A', 'function', 'has_ptr_param')] = _b(ptr_params)
    A[('A', 'function', 'addr_arg_user_call')] = _b(any(
        _t(_f(c, 'function')) not in ('scanf', 'printf') and
        any(a.type == 'pointer_expression' and _t(_f(a, 'operator')) == '&'
            for a in _f(c, 'arguments').named_children) for c in calls))
    # khởi tạo biến cực trị / tích lũy (phép gán đầu tiên ngoài vòng lặp/if)
    first = {}
    for n in nodes:
        if n.type == 'init_declarator' and _f(n, 'declarator').type == 'identifier':
            var, val = _t(_f(n, 'declarator')), _f(n, 'value')
        elif n.type == 'assignment_expression' and _t(_f(n, 'operator')) == '=' \
                and _f(n, 'left').type == 'identifier':
            var, val = _t(_f(n, 'left')), _f(n, 'right')
        else:
            continue
        if not _inside(n, (*LOOPS, 'if_statement')):
            first.setdefault(var, val)
    accum = {_t(_f(n, 'left')) for n in nodes if n.type == 'assignment_expression'
             and _t(_f(n, 'operator')) in ('+=', '-=', '*=') and _f(n, 'left').type == 'identifier'}

    def init_kind(v):
        if v is None:
            return 'none'
        if v.type == 'number_literal':
            return {'0': 'zero', '1': 'one'}.get(_t(v), 'literal')
        return 'expr'
    ext = [v for v in first if EXTREMUM.search(v)]
    A[('A', 'extremum', 'init')] = 'n/a' if not ext else _opset({init_kind(first[v]) for v in ext})
    acc = [v for v in accum if v in first] + [v for v in accum if v not in first]
    A[('A', 'accumulator', 'init')] = 'n/a' if not acc else _opset({init_kind(first.get(v)) for v in acc})
    # phép chia
    divs = [n for n in nodes if n.type == 'binary_expression' and _t(_f(n, 'operator')) == '/']
    floaty = lambda s: s.type == 'cast_expression' and re.search(r'float|double', _t(_f(s, 'type'))) or \
        (s.type == 'number_literal' and '.' in _t(s))
    float_ctx = bool(re.search(r'\b(float|double)\b', code.decode('utf-8', errors='replace')))
    A[('A', 'division', 'int_div_float_ctx')] = _b(float_ctx and any(
        not floaty(_f(d, 'left')) and not floaty(_f(d, 'right')) for d in divs))
    A[('A', 'division', 'has_cast')] = _b(any(floaty(_f(d, 'left')) or floaty(_f(d, 'right')) for d in divs))
    # số âm
    A[('A', 'negation', 'uses_abs')] = _b(any(_t(_f(c, 'function')) in ('abs', 'labs', 'fabs') for c in calls))
    A[('A', 'negation', 'unary_minus')] = _b(any(n.type == 'unary_expression' and _t(_f(n, 'operator')) == '-'
                                                 and _f(n, 'argument').type != 'number_literal' for n in nodes))
    return A


def extract(problem, code: bytes, tr_sub, tests, flags=None) -> dict:
    return {**test_features(tr_sub), **output_features(problem, tr_sub, tests, flags), **ast_features(code)}


def key(k) -> str:
    g, o, a = k
    return f'{g}:{o}.{a}'
