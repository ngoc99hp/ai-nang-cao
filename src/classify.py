"""Phân loại một bài nộp mới (demo): chấm test → OAV → cụm gần nhất → luật ILA khớp.

Chỉ chạy trong aai-lab (gọi runner). Mô hình dựng bởi scripts/p7_build_demo.py.
Gán cụm như bước gán của K-modes: khoảng cách Hamming có trọng số tới mode của từng cụm.
"""
import difflib
import pickle
import re
from functools import lru_cache

import numpy as np
import pandas as pd

import bench
import config
import diff_features as dfe
import features as ft
import runner

MAX_CODE = 64 * 1024
GROUP_NAME = {'T': 'Test', 'O': 'Output', 'A': 'Cấu trúc (AST)', 'D': 'Khác bản đúng'}


@lru_cache
def model(problem):
    return pickle.load(open(config.PROCESSED / 'demo' / f'model_{problem}.pkl', 'rb'))


def _row(F: dict, cols) -> dict:
    """Căn dòng thuộc tính của bài mới theo cột của mô hình (vắng mặt: cờ output → 'F', còn lại 'n/a')."""
    keyed = {ft.key(k): v for k, v in F.items()}
    return {c: keyed.get(c, 'F' if c.startswith('O:output.') else 'n/a') for c in cols}


def classify(problem: str, code: str, job_dir) -> dict:
    if problem not in config.PROBLEMS:
        raise ValueError(f'problem không hỗ trợ: {problem}')
    if len(code.encode()) > MAX_CODE:
        raise ValueError('code quá dài (> 64 KB)')
    job_dir.mkdir(parents=True, exist_ok=True)
    src = job_dir / 'sub.c'
    src.write_text(code)
    tests = bench.tests_of(problem)
    rows = runner.run_batch([('sub', src)], tests, job_dir / 'bin', problem=problem)
    if rows[0]['status'] == 'COMPILE_ERROR':
        return dict(status='compile_error', stderr=re.sub(r'\S*/sub\.c', 'sub.c', rows[0]['stdout']))
    tr = pd.DataFrame(rows).sort_values('test_id', key=lambda s: s.map(
        lambda t: (t[:2], int(t[2:]))))
    tio = {t: (i.read_text(errors='replace'), o.read_text(errors='replace')) for t, i, o in tests}
    test_rows = [dict(test_id=r.test_id, status=r.status_sem, strict=r.status, input=tio[r.test_id][0],
                      expected=tio[r.test_id][1], output=r.stdout[:1000]) for r in tr.itertuples()]
    n_fail = int((tr.status_sem != 'PASS').sum())
    if n_fail == 0:
        fmt = int((tr.status != 'PASS').sum())
        return dict(status='correct', tests=test_rows, format_fail=fmt)

    m = model(problem)
    flags = {'uninit_dependent': False, 'nondet_dataset': False,
             'format_only_any': bool(((tr.status != 'PASS') & (tr.status_sem == 'PASS')).any())}
    cb = code.encode()
    F = ft.extract(problem, cb, tr, tio, flags)
    tok = dfe.tokens(cb)
    sims = {s: dfe.similarity(tok, t) for s, t in m['pool_tok'].items()}
    ref_id = max(sims, key=sims.get)
    F.update(dfe.diff_features(cb, m['pool'][ref_id]))
    row = _row(F, m['cols'])
    cols, w = m['cols'], m['w']
    v = np.array([row[c] for c in cols], dtype=object)

    dist = {c: float(np.sum(w * (v != np.array([md[c2] for c2 in cols], dtype=object))) / w.sum())
            for c, md in m['modes'].items()}
    best = min(dist, key=dist.get)
    # thuộc tính giải thích: khớp mode của cụm được chọn, không phải giá trị "trống", trọng số lớn
    md = m['modes'][best]
    why = sorted([(w[j], c) for j, c in enumerate(cols) if row[c] == md[c] and row[c] not in ('F', 'n/a', 'none', '0')],
                 reverse=True)[:8]
    X1 = pd.DataFrame([row])
    matched = [r for r in m['rules'] if r.matches(X1)[0]]
    Fm = m['F'].values
    dn = (w[None, :] * (Fm != v[None, :])).sum(axis=1) / w.sum()
    nn = np.argsort(dn)[:3]
    ref_code = m['pool'][ref_id].decode(errors='replace')
    diff = '\n'.join(l.rstrip() for l in difflib.unified_diff(ref_code.splitlines(), code.splitlines(),
                                                               'bản đúng gần nhất', 'bài nộp', n=1, lineterm=''))
    oav = [dict(group=GROUP_NAME[g], object=o, attribute=a, value=val) for (g, o, a), val in F.items()
           if g != 'T' and val not in ('F', 'n/a', 'none', '0')]
    return dict(
        status='buggy', tests=test_rows, n_fail=n_fail, oav=oav,
        cluster=int(best), distances={int(k): round(d, 3) for k, d in dist.items()},
        why=[dict(attr=c, value=row[c]) for _, c in why],
        rules=[dict(text=r.fmt(cls_fmt=lambda k: f'Cụm {k}'), cls=int(r.cls), n_cls=r.n_cls, cls_size=r.cls_size)
               for r in matched],
        neighbors=[dict(sub_id=m['sub_ids'][i], cluster=int(m['y'][i]), distance=round(float(dn[i]), 3)) for i in nn],
        ref=dict(id=ref_id, similarity=round(sims[ref_id], 3), diff=diff))
