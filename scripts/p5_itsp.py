"""E4b: ITSP — OAV (O tổng quát + A + D so với bản sửa của chính SV) → gom cụm gộp mọi bài → đối chiếu nhãn tay.

Lọc: buggy compile được và fail ≥ 1 test (so token), bản correct pass toàn bộ test.
Gộp mọi bài ITSP vào một lần gom cụm (D và O tổng quát không phụ thuộc đề bài).
Nhãn tham chiếu: results/tables/itsp_labels.csv (gán blind từ diff trước khi gom cụm, mẫu nhỏ).
→ data/processed/oav_wide/itsp_all.parquet, results/tables/E4b_itsp.csv, results/rules/itsp_all.txt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import numpy as np
import pandas as pd

import cluster as cl
import config
import diff_features as dfe
import features as ft
import ila
import itsp
import schema

P = itsp.pairs()
TR = pd.concat([schema.load(f, schema.TEST_RESULTS) for f in (config.INTERIM / 'test_results').glob('itsp_*.parquet')])
ok = TR.groupby('sub_id').apply(lambda g: g.test_id.notna().all() and (g.status == 'PASS').all())
fails = TR.groupby('sub_id').apply(lambda g: g.test_id.notna().all() and (g.status != 'PASS').any())
keep = P[P.correct_id.map(ok).fillna(False) & P.buggy_id.map(fails).fillna(False)]
print(f'cặp: {len(P)}; correct pass hết: {int(P.correct_id.map(ok).sum())}; '
      f'buggy fail ≥1 (so token): {int(P.buggy_id.map(fails).sum())}; giữ: {len(keep)} ({keep.pid.nunique()} bài)')

trg = dict(tuple(TR[TR.test_id.notna()].groupby('sub_id')))
rows = []
for r in keep.itertuples():
    tests = {t: (i.read_text(errors='replace'), o.read_text(errors='replace')) for t, i, o in itsp.tests_of(r.pid)}
    code = (config.ROOT / r.buggy_path).read_bytes()
    F = {**ft.output_features_generic(trg[r.buggy_id], tests), **ft.ast_features(code),
         **dfe.diff_features(code, (config.ROOT / r.correct_path).read_bytes())}
    rows.append({'sub_id': r.buggy_id, 'problem': r.problem, 'source': 'itsp', 'label_true': None,
                 'repo': r.prog, **{ft.key(k): v for k, v in F.items()}})
W = pd.DataFrame(rows)
feats = [c for c in W.columns if c not in schema.WIDE_KEYS]
oc = [c for c in feats if c.startswith('O:output.')]
W[oc] = W[oc].fillna('F')
W[feats] = W[feats].fillna('n/a')
lab = pd.read_csv(config.TABLES / 'itsp_labels.csv').set_index('sub_id').label
W['label_true'] = W.sub_id.map(lab)
schema.save_wide(W, config.PROCESSED / 'oav_wide' / 'itsp_all.parquet')
print(f'OAV: {len(W)} bài × {len(feats)} thuộc tính; có nhãn: {W.label_true.notna().sum()}/{len(lab)} '
      f'(nhãn bị lọc: {sorted(set(lab.index) - set(W.sub_id))})')

L = W.label_true.notna().values
y = W.label_true[L].values
res = []
for groups in ('O', 'A', 'D', 'OD', 'AD', 'OAD'):
    X, w, cols = cl.feature_matrix(W, tuple(groups))
    D = cl.weighted_hamming(X, w)
    for k in (6, 8, 10, 12, 15, 20):
        for method in ('kmodes', 'agglomerative'):
            lb = cl.kmodes(X, w, k)[0] if method == 'kmodes' else cl.agglomerative(D, k)[0]
            e = cl.external(y, lb[L])
            res.append(dict(groups=groups, method=method, k=k, silhouette=cl.silhouette(D, lb),
                            min_size=np.bincount(lb).min(), **e))
R = pd.DataFrame(res).round(3)
R.to_csv(config.TABLES / 'E4b_itsp.csv', index=False)
print(R.pivot_table(index=['groups', 'method'], columns='k', values='ari').to_string())
print(R.pivot_table(index=['groups', 'method'], columns='k', values='silhouette').to_string())

# Cấu hình chính (DP3: O+A+D, K-modes); k = số nhãn → ma trận nhãn × cụm + luật ILA
k_main = len(set(y))
X, w, cols = cl.feature_matrix(W, ('O', 'A', 'D'))
lb = cl.kmodes(X, w, k_main)[0]
print(f'\nO+A+D K-modes k={k_main}: ', {m: round(v, 3) for m, v in cl.external(y, lb[L]).items()})
print(pd.crosstab(pd.Series(y, name='nhãn'), pd.Series(lb[L], name='cụm')).to_string())
pd.DataFrame({'sub_id': W.sub_id, 'cluster_id': lb}).to_csv(config.TABLES / 'E4b_itsp_clusters.csv', index=False)
rules, info = ila.fit(W[cols], lb)
Path(config.ROOT / 'results' / 'rules' / 'itsp_all.txt').write_text(
    '\n'.join(r.fmt(f'R{i + 1}', cls_fmt=lambda c: f'Cụm {c}') for i, r in enumerate(rules)) + '\n')
print(f'ILA: {len(rules)} luật, TB {np.mean([len(r.conds) for r in rules]):.2f} điều kiện, uncovered {info["uncovered"]}')
for c in range(k_main):
    m = lb == c
    top = sorted(((W.loc[m, col] == v).mean() - (W[col] == v).mean(), col, v)
                 for col in cols for v in W.loc[m, col].unique() if v not in ('F', 'none', 'n/a', '0')
                 and (W.loc[m, col] == v).mean() >= 0.5)[::-1][:4]
    labs = pd.Series(W.label_true[m]).dropna().value_counts().to_dict()
    print(f'Cụm {c} ({m.sum()} bài) nhãn={labs}: ' + '; '.join(f'{col}={v}' for _, col, v in top))
