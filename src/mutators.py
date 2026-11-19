"""Toán tử đột biến theo taxonomy DP2 (M1–M8). Sửa theo byte offset từ AST tree-sitter.

Mỗi Mutation = 1 misconception (label) gồm ≥ 1 Edit không chồng lấn (vd M2 sửa cả tham số,
thân hàm và lời gọi). `find_all(code)` liệt kê mọi vị trí áp dụng; `apply(code, muts)` áp
một hoặc nhiều mutation (kết hợp 2 lỗi → nhãn 'M1+M7').
Duyệt cây bằng đệ quy (node.children / child_by_field_name), không dùng Query API.
"""
import re
from dataclasses import dataclass

import ast_utils as au

LABELS = {
    'M1': 'Điều kiện biên vòng lặp',
    'M2': 'Truyền tham trị vs tham chiếu',
    'M3': 'Nhầm gán và so sánh',
    'M4': 'Chia nguyên',
    'M5': 'Khởi tạo biến tích lũy / cực trị',
    'M6': 'Phạm vi return/break/khối lệnh',
    'M7': 'Biên so sánh trong chuỗi if',
    'M8': 'Số âm với % và /',
}

LOOPS = ('for_statement', 'while_statement', 'do_statement')
CMP_FLIP = {'<': '<=', '<=': '<', '>': '>=', '>=': '>'}
EXTREMUM = re.compile(r'(?i)(min|max|mn|mx|small|large|big|least|great|low|high|med)')
ABS_FUNCS = {'abs', 'labs', 'llabs', 'fabs', 'fabsf'}


@dataclass(frozen=True)
class Edit:
    start: int
    end: int
    text: bytes


@dataclass(frozen=True)
class Mutation:
    label: str
    op: str
    edits: tuple[Edit, ...]
    line: int
    desc: str

    @property
    def span(self) -> tuple[int, int]:
        return min(e.start for e in self.edits), max(e.end for e in self.edits)


# ---------------------------------------------------------------- helpers

def _t(n) -> str:
    return n.text.decode('utf-8', errors='replace')


def _f(n, name):
    return n.child_by_field_name(name)


def _op(n):
    """Node toán tử của binary/assignment/unary/pointer expression."""
    return _f(n, 'operator')


def _mut(label, op, edits, node, desc) -> Mutation:
    return Mutation(label, op, tuple(edits), node.start_point[0] + 1, desc)


def _replace(node, text: str) -> Edit:
    return Edit(node.start_byte, node.end_byte, text.encode())


def _comparisons(expr):
    for n in au.walk(expr):
        if n.type == 'binary_expression' and _t(_op(n)) in CMP_FLIP:
            yield _op(n)


def _functions(root):
    return [n for n in au.walk(root) if n.type == 'function_definition']


def _func_name(fn_or_decl):
    d = _f(fn_or_decl, 'declarator')
    while d is not None and d.type != 'function_declarator':
        d = _f(d, 'declarator')
    if d is None:
        return None, None
    return _t(_f(d, 'declarator')), _f(d, 'parameters')


def _assignments(scope):
    """(var, value_node, node) cho init_declarator và phép gán '=' đơn giản, theo thứ tự xuất hiện."""
    for n in au.walk(scope):
        if n.type == 'init_declarator' and _f(n, 'declarator').type == 'identifier':
            yield _t(_f(n, 'declarator')), _f(n, 'value'), n
        elif (n.type == 'assignment_expression' and _t(_op(n)) == '='
              and _f(n, 'left').type == 'identifier'):
            yield _t(_f(n, 'left')), _f(n, 'right'), n


def _inside(node, types) -> bool:
    p = node.parent
    while p is not None:
        if p.type in types:
            return True
        p = p.parent
    return False


def _in_condition(node) -> bool:
    """node nằm trong điều kiện của if/for/while/do."""
    p, c = node.parent, node
    while p is not None:
        if p.type in ('if_statement', *LOOPS) and _f(p, 'condition') is not None \
                and _f(p, 'condition').id == c.id:
            return True
        p, c = p.parent, p
    return False


# ---------------------------------------------------------------- M1, M7: so sánh biên

def _m1(root):
    for loop in (n for n in au.walk(root) if n.type in LOOPS):
        cond = _f(loop, 'condition')
        if cond is not None:
            for op in _comparisons(cond):
                new = CMP_FLIP[_t(op)]
                yield _mut('M1', 'loop_cmp', [_replace(op, new)], op, f'vòng lặp: {_t(op)} → {new}')
        init = _f(loop, 'initializer') if loop.type == 'for_statement' else None
        if init is not None:
            for lit in (n for n in au.walk(init) if n.type == 'number_literal' and _t(n) in ('0', '1')):
                new = '1' if _t(lit) == '0' else '0'
                yield _mut('M1', 'loop_init', [_replace(lit, new)], lit, f'khởi tạo biến lặp: {_t(lit)} → {new}')


def _m7(root):
    for st in (n for n in au.walk(root) if n.type == 'if_statement'):
        for op in _comparisons(_f(st, 'condition')):
            new = CMP_FLIP[_t(op)]
            yield _mut('M7', 'if_cmp', [_replace(op, new)], op, f'điều kiện if: {_t(op)} → {new}')


# ---------------------------------------------------------------- M3: = thay ==

def _m3(root):
    for n in au.walk(root):
        if (n.type == 'binary_expression' and _t(_op(n)) == '=='
                and _f(n, 'left').type in ('identifier', 'subscript_expression', 'field_expression')
                and _in_condition(n)):
            yield _mut('M3', 'eq_to_assign', [_replace(_op(n), '=')], n, f'{_t(n)} → dùng ='
                       )


# ---------------------------------------------------------------- M4: chia nguyên

def _m4(root):
    for n in au.walk(root):
        if n.type != 'binary_expression' or _t(_op(n)) != '/':
            continue
        for side in (_f(n, 'left'), _f(n, 'right')):
            if side.type == 'cast_expression' and re.search(r'float|double', _t(_f(side, 'type'))):
                yield _mut('M4', 'drop_cast', [_replace(side, _t(_f(side, 'value')))], side,
                           f'bỏ ép kiểu {_t(side)}')
            elif side.type == 'number_literal' and re.fullmatch(r'\d+\.0*f?', _t(side)):
                new = _t(side).split('.')[0]
                yield _mut('M4', 'float_lit_to_int', [_replace(side, new)], side, f'{_t(side)} → {new}')


# ---------------------------------------------------------------- M5: khởi tạo

def _m5(root):
    for fn in _functions(root):
        body = _f(fn, 'body')
        first = {}
        for var, val, node in _assignments(body):
            # chỉ coi là 'khởi tạo' nếu nằm ngoài vòng lặp / if (không phải phép cập nhật)
            if val is not None and not _inside(node, (*LOOPS, 'if_statement')):
                first.setdefault(var, (val, node))
        accum = {_t(_f(n, 'left')) for n in au.walk(body)
                 if n.type == 'assignment_expression' and _t(_op(n)) in ('+=', '-=', '*=')
                 and _f(n, 'left').type == 'identifier'}
        accum |= {_t(_f(n, 'argument')) for n in au.walk(body)
                  if n.type == 'update_expression' and _f(n, 'argument').type == 'identifier'
                  and not _inside(n, ('for_statement',))}
        for var, (val, node) in first.items():
            if EXTREMUM.search(var) and _t(val) != '0' and val.type != 'number_literal':
                yield _mut('M5', 'extremum_init_zero', [_replace(val, '0')], node,
                           f'khởi tạo {var} = 0 thay vì {_t(val)}')
            elif var in accum and val.type == 'number_literal' and _t(val) in ('0', '1'):
                new = '1' if _t(val) == '0' else '0'
                yield _mut('M5', 'accum_init', [_replace(val, new)], node, f'khởi tạo {var} = {new}')


# ---------------------------------------------------------------- M6: phạm vi khối

def _body_end_insert(body, stmt: str) -> list[Edit]:
    if body.type == 'compound_statement':
        close = body.children[-1]
        return [Edit(close.start_byte, close.start_byte, f' {stmt} '.encode())]
    return [Edit(body.start_byte, body.start_byte, b'{ '), Edit(body.end_byte, body.end_byte, f' {stmt} }}'.encode())]


def _m6(root):
    for loop in (n for n in au.walk(root) if n.type in LOOPS):
        body = _f(loop, 'body')
        if body is None:
            continue
        yield _mut('M6', 'early_break', _body_end_insert(body, 'break;'), loop, 'thêm break cuối thân vòng lặp')
        nxt = loop.next_named_sibling
        if nxt is not None and nxt.type in ('expression_statement', 'return_statement') \
                and loop.parent.type == 'compound_statement':
            edits = [Edit(nxt.start_byte, nxt.end_byte, b'')] + _body_end_insert(body, _t(nxt))
            yield _mut('M6', 'stmt_into_loop', edits, nxt, f'đưa "{_t(nxt)[:40]}" vào trong vòng lặp')


# ---------------------------------------------------------------- M8: số âm

def _is_negate(stmt) -> bool:
    """x = -x;  x *= -1;  x = x * -1;  x = -1 * x;"""
    e = stmt.named_children[0] if stmt.named_child_count else None
    if e is None or e.type != 'assignment_expression' or _f(e, 'left').type != 'identifier':
        return False
    x, op, r = _t(_f(e, 'left')), _t(_op(e)), _t(_f(e, 'right')).replace(' ', '')
    return (op == '=' and r in (f'-{x}', f'{x}*-1', f'-1*{x}', f'{x}*(-1)', f'(-1)*{x}')) or \
           (op == '*=' and r in ('-1', '(-1)'))


def _m8(root):
    for n in au.walk(root):
        if n.type == 'call_expression' and _t(_f(n, 'function')) in ABS_FUNCS:
            args = _f(n, 'arguments').named_children
            if len(args) == 1:
                yield _mut('M8', 'drop_abs', [_replace(n, _t(args[0]))], n, f'bỏ {_t(n)}')
        elif n.type == 'expression_statement' and _is_negate(n):
            yield _mut('M8', 'drop_negate', [Edit(n.start_byte, n.end_byte, b';')], n, f'bỏ "{_t(n)}"')
        elif (n.type == 'unary_expression' and _t(_op(n)) == '-'
              and _f(n, 'argument').type in ('identifier', 'parenthesized_expression', 'subscript_expression')
              and not (n.parent.type == 'assignment_expression' and _is_negate(n.parent.parent))):
            yield _mut('M8', 'drop_minus', [_replace(n, _t(_f(n, 'argument')))], n, f'bỏ dấu trừ {_t(n)}')


# ---------------------------------------------------------------- M2: tham trị vs tham chiếu

def _strip_ptr(decl) -> str:
    """'*a' / '* a' → 'a' (pointer_declarator → declarator bên trong)."""
    return _t(_f(decl, 'declarator'))


def _m2(root):
    protos = [n for n in au.walk(root) if n.type == 'declaration']
    calls = [n for n in au.walk(root) if n.type == 'call_expression']
    for fn in _functions(root):
        name, params = _func_name(fn)
        if name is None or name == 'main':
            continue
        plist = [p for p in params.named_children if p.type == 'parameter_declaration']
        ptr_idx = [k for k, p in enumerate(plist)
                   if _f(p, 'declarator') is not None and _f(p, 'declarator').type == 'pointer_declarator'
                   and _f(_f(p, 'declarator'), 'declarator').type == 'identifier']
        groups = [[k] for k in ptr_idx] + ([ptr_idx] if len(ptr_idx) > 1 else [])
        for ks in groups:
            edits, names = [], []
            for k in ks:
                d = _f(plist[k], 'declarator')
                pname = _strip_ptr(d)
                names.append(pname)
                edits.append(_replace(d, pname))
                for n in au.walk(_f(fn, 'body')):          # *p → p
                    if n.type == 'pointer_expression' and _t(_op(n)) == '*' \
                            and _f(n, 'argument').type == 'identifier' and _t(_f(n, 'argument')) == pname:
                        edits.append(_replace(n, pname))
                for pr in protos:                           # prototype
                    pn, pp = _func_name(pr)
                    if pn == name and pp is not None:
                        pl = [p for p in pp.named_children if p.type == 'parameter_declaration']
                        if k < len(pl) and _f(pl[k], 'declarator') is not None \
                                and _f(pl[k], 'declarator').type == 'pointer_declarator':
                            edits.append(_replace(_f(pl[k], 'declarator'), _strip_ptr(_f(pl[k], 'declarator'))))
                for c in calls:                             # &x → x tại lời gọi
                    if _t(_f(c, 'function')) == name:
                        args = _f(c, 'arguments').named_children
                        if k < len(args) and args[k].type == 'pointer_expression' and _t(_op(args[k])) == '&':
                            edits.append(_replace(args[k], _t(_f(args[k], 'argument'))))
            yield _mut('M2', 'by_value' if len(ks) == 1 else 'by_value_all', edits, fn,
                       f'{name}: truyền {", ".join(names)} theo giá trị')


FINDERS = {'M1': _m1, 'M2': _m2, 'M3': _m3, 'M4': _m4, 'M5': _m5, 'M6': _m6, 'M7': _m7, 'M8': _m8}


def find_all(code: bytes, labels=None) -> list[Mutation]:
    root = au.parse(code).root_node
    out = []
    for lab, f in FINDERS.items():
        if labels is None or lab in labels:
            out.extend(f(root))
    return out


def overlaps(a: Mutation, b: Mutation) -> bool:
    for x in a.edits:
        for y in b.edits:
            if x.start < y.end and y.start < x.end:
                return True
            if x.start == y.start:                 # cùng điểm chèn
                return True
    return False


def apply(code: bytes, muts) -> bytes:
    edits = sorted((e for m in muts for e in m.edits), key=lambda e: (e.start, e.end), reverse=True)
    for a, b in zip(edits[1:], edits):             # a đứng trước b
        if a.end > b.start or (a.start == b.start and a.end == a.start == b.end):
            raise ValueError('edits chồng lấn')
    for e in edits:
        code = code[:e.start] + e.text + code[e.end:]
    return code


def label_of(muts) -> str:
    return '+'.join(sorted({m.label for m in muts}))
