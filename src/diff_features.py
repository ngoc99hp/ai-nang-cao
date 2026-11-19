"""Nhóm thuộc tính D: khác biệt giữa bài sai và lời giải đúng gần nhất (Phase 3b).

Bản tham chiếu: bản đúng gần nhất VỀ SAU của chính SV (nếu có), ngược lại bản đúng gần nhất
theo độ tương đồng chuỗi token trong kho lời giải đúng. Dữ liệu sinh dùng cùng quy trình
(không dùng parent_id) để không rò nhãn.
So khớp chuỗi token (difflib) rồi phân loại từng chỗ khác theo ngữ cảnh AST của token.
"""
import difflib
from collections import Counter

import ast_utils as au

LOOPS = ('for_statement', 'while_statement', 'do_statement')
CMP = {'<', '<=', '>', '>='}
ARITH = {'+', '-', '*', '/', '%'}
STRICT_PAIR = {frozenset({'<', '<='}), frozenset({'>', '>='})}

D_FLAGS = ('cmp_loop', 'cmp_if', 'eq_assign', 'logic_op', 'loop_init', 'init_value', 'literal_other',
           'ptr_missing', 'ptr_extra', 'cast_missing', 'neg_missing', 'neg_extra', 'moved_into_loop',
           'moved_out_of_loop', 'extra_break', 'missing_break', 'extra_output', 'missing_output',
           'var_changed', 'arith_changed', 'stmt_missing', 'stmt_extra')


# ---------------------------------------------------------------- token + ngữ cảnh

def _leaves(code: bytes):
    root = au.parse(code).root_node
    return [n for n in au.walk(root) if n.child_count == 0 and n.type != 'comment' and n.text]


def _txt(n):
    return n.text.decode('utf-8', errors='replace')


def _ctx(n) -> set[str]:
    """Ngữ cảnh của 1 token lá: loop_cond / if_cond / for_init / init / loop_body / cast / ptr / abs..."""
    c, out, child = n.parent, set(), n
    while c is not None:
        f = None
        for i, ch in enumerate(c.children):
            if ch.id == child.id:
                f = c.field_name_for_child(i)
                break
        if c.type in LOOPS and f == 'condition':
            out.add('loop_cond')
        elif c.type in LOOPS and f == 'initializer':
            out.add('for_init')
        elif c.type in LOOPS and f == 'body':
            out.add('loop_body')
        elif c.type == 'if_statement' and f == 'condition':
            out.add('if_cond')
        elif c.type == 'cast_expression':
            out.add('cast')
        elif c.type in ('pointer_expression', 'pointer_declarator'):
            out.add('ptr')
        elif c.type == 'call_expression' and child.type == 'identifier' and f == 'function':
            out.add('callee')
        elif c.type == 'unary_expression' and _txt(child) == '-':
            out.add('unary_minus')
        elif c.type in ('init_declarator',) or (c.type == 'assignment_expression' and f == 'right'):
            out.add('assign_value')
        child, c = c, c.parent
    if 'assign_value' in out and not out & {'loop_body', 'loop_cond', 'if_cond'}:
        out.add('init')
    return out


def _stmts(code: bytes):
    """[(text chuẩn hóa, độ sâu vòng lặp)] của expression/return/break statement."""
    out = []
    for n in au.walk(au.parse(code).root_node):
        if n.type in ('expression_statement', 'return_statement', 'break_statement'):
            d, p = 0, n.parent
            while p is not None:
                d += p.type in LOOPS
                p = p.parent
            out.append((' '.join(_txt(x) for x in _leaves(n.text)), d, n.type))
    return out


def similarity(a_tokens, b_tokens) -> float:
    return difflib.SequenceMatcher(None, a_tokens, b_tokens, autojunk=False).ratio()


def tokens(code: bytes) -> list[str]:
    return [_txt(n) for n in _leaves(code)]


# ---------------------------------------------------------------- thuộc tính

def diff_features(buggy: bytes, ref: bytes) -> dict:
    A, B = _leaves(buggy), _leaves(ref)
    ta, tb = [_txt(n) for n in A], [_txt(n) for n in B]
    F = {k: False for k in D_FLAGS}
    cmp_kinds, n_changed = set(), 0
    sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        n_changed += max(i2 - i1, j2 - j1)
        pairs = list(zip(range(i1, i2), range(j1, j2))) if tag == 'replace' and i2 - i1 == j2 - j1 else []
        only_a = [] if pairs else list(range(i1, i2))
        only_b = [] if pairs else list(range(j1, j2))
        for i, j in pairs:
            x, y, na, nb = ta[i], tb[j], A[i], B[j]
            cx = _ctx(na)
            if x in CMP and y in CMP:
                F['cmp_loop' if 'loop_cond' in cx else 'cmp_if'] = True
                cmp_kinds.add('strictness' if frozenset({x, y}) in STRICT_PAIR else 'reversed')
            elif x == '=' and y == '==':
                F['eq_assign'] = True
            elif {x, y} == {'&&', '||'}:
                F['logic_op'] = True
            elif na.type == 'number_literal' and nb.type == 'number_literal':
                F['loop_init' if 'for_init' in cx else 'init_value' if 'init' in cx else 'literal_other'] = True
            elif na.type == 'number_literal' and 'init' in cx:
                F['init_value'] = True                       # vd min = 0 thay vì min = a[0]
            elif na.type == 'identifier' and nb.type == 'identifier':
                F['var_changed'] = True
            elif x in ARITH and y in ARITH:
                F['arith_changed'] = True
            else:
                only_a.append(i)
                only_b.append(j)
        for j in only_b:                                     # có ở bản đúng, thiếu ở bài sai
            cb, y = _ctx(B[j]), tb[j]
            if y in ('*', '&') and 'ptr' in cb:
                F['ptr_missing'] = True
            elif 'cast' in cb or (B[j].type == 'number_literal' and '.' in y):
                F['cast_missing'] = True
            elif (y == '-' and 'unary_minus' in cb) or (y in ('abs', 'labs', 'fabs') and 'callee' in cb):
                F['neg_missing'] = True
            elif B[j].type == 'number_literal' and 'init' in cb:
                F['init_value'] = True
        for i in only_a:                                     # có ở bài sai, không có ở bản đúng
            ca, x = _ctx(A[i]), ta[i]
            if x in ('*', '&') and 'ptr' in ca:
                F['ptr_extra'] = True
            elif (x == '-' and 'unary_minus' in ca) or (x in ('abs', 'labs', 'fabs') and 'callee' in ca):
                F['neg_extra'] = True
            elif A[i].type == 'number_literal' and 'init' in ca:
                F['init_value'] = True
    # cấp câu lệnh: di chuyển vào/ra vòng lặp, break, output
    sa, sb = _stmts(buggy), _stmts(ref)
    da, db = {}, {}
    for t, d, _ in sa:
        da.setdefault(t, []).append(d)
    for t, d, _ in sb:
        db.setdefault(t, []).append(d)
    for t in set(da) & set(db):
        x, y = sorted(da[t]), sorted(db[t])
        if len(x) == len(y) and x != y:
            F['moved_into_loop'] |= sum(x) > sum(y)
            F['moved_out_of_loop'] |= sum(x) < sum(y)
    ca, cb = Counter(t for _, _, t in sa), Counter(t for _, _, t in sb)
    pa = sum('printf' in t or 'puts' in t for t, _, _ in sa)
    pb = sum('printf' in t or 'puts' in t for t, _, _ in sb)
    F['extra_break'] = ca['break_statement'] > cb['break_statement']
    F['missing_break'] = ca['break_statement'] < cb['break_statement']
    F['extra_output'], F['missing_output'] = pa > pb, pa < pb
    na_, nb_ = len(sa), len(sb)
    F['stmt_extra'] = na_ > nb_ and not (F['extra_break'] or F['extra_output'])
    F['stmt_missing'] = na_ < nb_ and not (F['missing_break'] or F['missing_output'])

    out = {('D', 'diff', k): 'T' if v else 'F' for k, v in F.items()}
    out[('D', 'diff', 'cmp_kind')] = 'none' if not cmp_kinds else 'mixed' if len(cmp_kinds) > 1 else cmp_kinds.pop()
    out[('D', 'diff', 'size')] = '0' if n_changed == 0 else '1' if n_changed == 1 else \
        '2-5' if n_changed <= 5 else '6-20' if n_changed <= 20 else '21+'
    return out
