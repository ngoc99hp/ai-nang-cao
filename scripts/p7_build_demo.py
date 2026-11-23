"""P7: Dựng dữ liệu cho demo (chạy trong aai-lab).

- data/processed/demo/model_<problem>.pkl : cho worker phân loại bài mới (cột, trọng số, mode của từng cụm,
  luật ILA, ma trận bài thật để tìm láng giềng, kho lời giải đúng để tính nhóm D).
- results/demo/dashboard.json              : cho giao diện (cụm, tên, luật, bài minh họa, bảng thí nghiệm).
Giao diện (container aai-ui) chỉ đọc results/, không đọc parquet và không chạy code.
"""
import csv
import difflib
import json
import pickle
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
import pandas as pd

import cluster as cl
import config
import diff_features as dfe
import ila
import schema
from p3_extract import ref_pool

OUT_MODEL = config.PROCESSED / 'demo'
OUT_UI = config.ROOT / 'results' / 'demo'
OUT_MODEL.mkdir(parents=True, exist_ok=True)
OUT_UI.mkdir(parents=True, exist_ok=True)

TITLE = {
    'digits': 'In các chữ số của một số nguyên, từ hàng đơn vị, mỗi chữ số một dòng (số âm: chữ số cuối mang dấu -)',
    'grade': 'Nhập 4 ngưỡng A, B, C, D (giảm dần) và điểm; in xếp loại hoặc "failed the course"',
    'median': 'Nhập 3 số nguyên, in số trung vị',
    'smallest': 'Nhập 4 số nguyên, in số nhỏ nhất',
}
SKIP = {'F', 'none', 'n/a', '0'}
M = pd.read_parquet(config.PROCESSED / 'clusters_main.parquet')
NAMES = {(r['problem'], int(r['cluster_id'])): r for r in csv.DictReader(open(config.TABLES / 'p5_cluster_names.csv',
                                                                              encoding='utf-8'))}


def read_code(rel):
    return (config.ROOT / rel).read_text(errors='replace')


def udiff(ref, bug):
    return '\n'.join(l.rstrip() for l in difflib.unified_diff(ref.splitlines(), bug.splitlines(), 'bản đúng',
                                                               'bài sai', n=1, lineterm=''))


dash = {'problems': {}, 'tables': {}}
for p in config.PROBLEMS:
    W = schema.load_wide(config.PROCESSED / 'oav_wide' / f'real_{p}.parquet')
    X, w, cols = cl.feature_matrix(W)
    D = cl.weighted_hamming(X, w)
    y = M[(M.dataset == 'real') & (M.problem == p)].set_index('sub_id').loc[W.sub_id, 'cluster_id'].values
    F = W[cols].reset_index(drop=True)
    modes = {int(c): F[y == c].mode().iloc[0].to_dict() for c in sorted(set(y))}
    rules, _ = ila.fit(F, y, max_c=3)
    pool = ref_pool(p)
    sub = schema.load(config.INTERIM / 'submissions' / f'{p}.parquet', schema.SUBMISSIONS).set_index('sub_id')
    refs = pd.read_parquet(config.PROCESSED / 'refs' / f'real_{p}.parquet').set_index('sub_id')
    model = dict(problem=p, cols=cols, w=w, modes=modes, rules=rules, F=F, y=y, sub_ids=W.sub_id.tolist(),
                 repos=W.repo.tolist(), pool={s: c for s, c in pool.items()},
                 pool_tok={s: dfe.tokens(c) for s, c in pool.items()})
    pickle.dump(model, open(OUT_MODEL / f'model_{p}.pkl', 'wb'))

    clusters = []
    for c in sorted(set(y)):
        idx = np.flatnonzero(y == c)
        Wc = W.iloc[idx]
        feats = []
        for col in cols:
            for v, pc in Wc[col].value_counts(normalize=True).items():
                if v in SKIP or pc < 0.5:
                    continue
                feats.append((pc - (W[col] == v).mean(), col, v, pc, (W[col] == v).mean()))
        feats.sort(reverse=True)
        cr = sorted([r for r in rules if r.cls == c], key=lambda r: -r.n_cls)
        order = idx[np.argsort(D[np.ix_(idx, idx)].sum(axis=1))]          # medoid trước
        examples = []
        for i in order[:3]:
            sid = W.sub_id.iloc[i]
            ref = refs.loc[sid]
            ref_code = read_code(sub.loc[ref.ref_id, 'code_path']) if ref.ref_id in sub.index else \
                pool.get(ref.ref_id, b'').decode(errors='replace')
            bug = read_code(sub.loc[sid, 'code_path'])
            examples.append(dict(sub_id=sid, code=bug, ref_id=ref.ref_id, ref_kind=ref.ref_kind,
                                 diff=udiff(ref_code, bug)))
        nm = NAMES.get((p, int(c)), {})
        clusters.append(dict(
            id=int(c), name=nm.get('name_draft', f'Cụm {c}'), taxonomy=nm.get('taxonomy', '-'),
            evidence=nm.get('evidence', ''), n_sub=int(len(idx)), n_students=int(Wc.repo.nunique()),
            features=[dict(attr=col, value=v, in_cluster=round(pc, 2), overall=round(pa, 2))
                      for _, col, v, pc, pa in feats[:6]],
            rules=[r.fmt(cls_fmt=lambda k: f'Cụm {k}') for r in cr[:5]], examples=examples))
    clusters.sort(key=lambda d: -d['n_students'])
    dash['problems'][p] = dict(title=TITLE[p], n_sub=int(len(W)), n_students=int(W.repo.nunique()),
                               k=int(len(set(y))), clusters=clusters)
    print(f'[{p}] {len(W)} bài, k={len(set(y))}, {len(rules)} luật, pool {len(pool)}', flush=True)

for name in ('E1_E2_synthetic', 'E1b_lopo_weights', 'E3_ablation', 'E4_real', 'E4b_itsp', 'E5_rules', 'p1_stats',
             'p2_mutants'):
    f = config.TABLES / f'{name}.csv'
    if f.exists():
        dash['tables'][name] = json.loads(pd.read_csv(f).round(3).to_json(orient='records', force_ascii=False))
json.dump(dash, open(OUT_UI / 'dashboard.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('DONE', OUT_UI / 'dashboard.json')
