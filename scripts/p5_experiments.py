"""P5: Thí nghiệm E1–E5 + sinh luật (ILA tự cài, so với ID3).

Cấu hình chính: trọng số DP3 (config.FEATURE_WEIGHTS), K-modes; k thật = config.K_REAL (DP4),
k synthetic = số nhãn đơn. Ghi results/tables/E1..E5*.csv, results/rules/*.txt,
data/processed/clusters_main.parquet.
"""
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import numpy as np
import pandas as pd
from sklearn.metrics import davies_bouldin_score
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier

import bench
import cluster as cl
import config
import ila
import schema

warnings.filterwarnings('ignore')
T = config.TABLES
RULES = config.ROOT / 'results' / 'rules'
RULES.mkdir(parents=True, exist_ok=True)
SYN = bench.SYNTH_PROBLEMS


def wide(ds, p):
    return schema.load_wide(config.PROCESSED / 'oav_wide' / f'{ds}_{p}.parquet')


def k_syn(W):
    return W.label_true[~W.label_true.str.contains(r'\+')].nunique()


def run_methods(W, k, groups=('T', 'O', 'A', 'D'), weights=None):
    X, w, cols = cl.feature_matrix(W, groups=groups, weights=weights)
    D = cl.weighted_hamming(X, w)
    return {'kmodes': cl.kmodes(X, w, k)[0], 'agglo': cl.agglomerative(D, k)[0],
            'kmeans1h': cl.kmeans_onehot(X, w, k)}, X, w, cols, D


t0 = time.time()
# ------------------------------------------------------------ E1 + E2: synthetic, 3 phương pháp
rows = []
for p in SYN:
    W = wide('synthetic', p)
    res, *_ , D = run_methods(W, k_syn(W))
    for m, lab in res.items():
        rows.append(dict(problem=p, n=len(W), k=k_syn(W), method=m, **cl.external(W.label_true, lab),
                         silhouette=cl.silhouette(D, lab)))
E1 = pd.DataFrame(rows)
E1.to_csv(T / 'E1_E2_synthetic.csv', index=False)
print('E1/E2\n', E1.pivot(index='problem', columns='method', values='ari').round(2).to_string(), flush=True)

# E1b: leave-one-problem-out cho trọng số (tránh tối ưu trên chính tập đánh giá)
G = pd.read_csv(T / 'p4_weight_grid.csv')
lopo = []
for p in SYN:
    others = [f'ARI_{q}' for q in SYN if q != p]
    best = G.assign(m=G[others].mean(axis=1)).sort_values('m', ascending=False).iloc[0]
    lopo.append(dict(problem=p, T=best['T'], O=best['O'], A=best['A'], D=best['D'],
                     ari_heldout=best[f'ARI_{p}'], ari_dp3=G[(G['T'] == 0) & (G.O == 0.5) & (G.A == 0.5)
                                                            & (G.D == 3)][f'ARI_{p}'].iloc[0]))
pd.DataFrame(lopo).to_csv(T / 'E1b_lopo_weights.csv', index=False)
print('E1b LOPO\n', pd.DataFrame(lopo).round(2).to_string(index=False), flush=True)

# ------------------------------------------------------------ E3: ablation nhóm thuộc tính
ABL = [('O',), ('A',), ('D',), ('O', 'A'), ('O', 'D'), ('A', 'D'), ('O', 'A', 'D'), ('T', 'O', 'A', 'D')]
rows = []
for p in SYN:
    W = wide('synthetic', p)
    for gs in ABL:
        wts = dict(config.FEATURE_WEIGHTS)
        if 'T' in gs:
            wts['test'] = 1.0                                   # T bị tắt trong DP3 → bật lại để so sánh
        res, X, w, cols, D = run_methods(W, k_syn(W), groups=gs, weights=wts)
        for m in ('kmodes', 'agglo'):
            rows.append(dict(problem=p, groups='+'.join(gs), d=len(cols), method=m,
                             **cl.external(W.label_true, res[m])))
E3 = pd.DataFrame(rows)
E3.to_csv(T / 'E3_ablation.csv', index=False)
print('E3 (K-modes ARI)\n', E3[E3.method == 'kmodes'].pivot(index='groups', columns='problem', values='ari')
      .round(2).to_string(), flush=True)

# ------------------------------------------------------------ cụm chính + E4
main, e4 = [], []
for ds, probs in (('real', config.PROBLEMS), ('synthetic', SYN)):
    for p in probs:
        W = wide(ds, p)
        k = config.K_REAL[p] if ds == 'real' else k_syn(W)
        X, w, cols = cl.feature_matrix(W)
        lab, _ = cl.kmodes(X, w, k)
        main += [dict(dataset=ds, problem=p, sub_id=s, cluster_id=int(c)) for s, c in zip(W.sub_id, lab)]
        if ds == 'real':
            D = cl.weighted_hamming(X, w)
            Z = np.hstack([np.sqrt(w[j]) * (X[:, [j]] == np.unique(X[:, j])[None, :]) for j in range(X.shape[1])])
            sizes = pd.Series(lab).value_counts().sort_index()
            stud = pd.Series(W.repo.values).groupby(lab).nunique()
            e4.append(dict(problem=p, n=len(W), k=k, silhouette=cl.silhouette(D, lab),
                           davies_bouldin=davies_bouldin_score(Z, lab),
                           sizes='/'.join(map(str, sizes)), students='/'.join(map(str, stud))))
M = pd.DataFrame(main)
M.to_parquet(config.PROCESSED / 'clusters_main.parquet', index=False)
E4 = pd.DataFrame(e4)
E4.to_csv(T / 'E4_real.csv', index=False)
print('E4\n', E4.round(3).to_string(index=False), flush=True)


# ------------------------------------------------------------ E5: luật ILA vs ID3
def id3_rules(F, y):
    Xo = pd.get_dummies(F).astype(int)
    t = DecisionTreeClassifier(criterion='entropy', random_state=config.SEED).fit(Xo, y)
    depth = t.decision_path(Xo).sum(axis=1).A1 - 1           # số điều kiện trên đường đi tới lá
    leaves = t.apply(Xo)
    per_leaf = pd.Series(depth).groupby(leaves).first()
    return t, Xo.columns, len(per_leaf), per_leaf.mean()


def cv_acc(F, y, model):
    y = np.asarray(y)
    vc = pd.Series(y).value_counts()
    kf = StratifiedKFold(5, shuffle=True, random_state=config.SEED) if vc.min() >= 5 else \
        KFold(5, shuffle=True, random_state=config.SEED)
    acc = []
    for tr, te in kf.split(F, y):
        if model == 'ila':
            r, _ = ila.fit(F.iloc[tr], y[tr], max_c=3)
            pred = ila.predict(r, F.iloc[te], default=pd.Series(y[tr]).mode()[0])
        else:
            Xo = pd.get_dummies(F).astype(int)
            pred = DecisionTreeClassifier(criterion='entropy', random_state=config.SEED) \
                .fit(Xo.iloc[tr], y[tr]).predict(Xo.iloc[te])
        acc.append((pred == y[te]).mean())
    return float(np.mean(acc))


rows = []
for ds, probs in (('real', config.PROBLEMS), ('synthetic', SYN)):
    for p in probs:
        W = wide(ds, p)
        _, _, cols = cl.feature_matrix(W)
        F = W[cols].reset_index(drop=True)
        y = M[(M.dataset == ds) & (M.problem == p)].set_index('sub_id').loc[W.sub_id, 'cluster_id'].values
        rules, info = ila.fit(F, y, max_c=3)
        rules.sort(key=lambda r: (r.cls, -r.n_cls))
        with open(RULES / f'{ds}_{p}.txt', 'w') as fh:
            fh.write(f'# {ds}/{p}: {len(W)} bài, {len(set(y))} cụm, {len(cols)} thuộc tính (O/A/D)\n')
            fh.write(f'# uncovered: {info["uncovered"]}\n')
            for i, r in enumerate(rules, 1):
                fh.write(r.fmt(f'R{i}', cls_fmt=lambda c: f'Cụm {c}') + '\n')
        _, _, n_leaf, d_leaf = id3_rules(F, y)
        rows.append(dict(dataset=ds, problem=p, n=len(W), k=len(set(y)), attrs=len(cols),
                         ila_rules=len(rules), ila_avg_conds=np.mean([len(r.conds) for r in rules]),
                         ila_train_cover=1 - sum(info['uncovered'].values()) / len(W),
                         ila_cv_acc=cv_acc(F, y, 'ila'),
                         id3_rules=n_leaf, id3_avg_conds=d_leaf, id3_cv_acc=cv_acc(F, y, 'id3')))
        print(f'[E5 {ds}/{p}] {time.time() - t0:.0f}s', flush=True)
E5 = pd.DataFrame(rows)
E5.to_csv(T / 'E5_rules.csv', index=False)
print('E5\n', E5.round(2).to_string(index=False))
print('DONE', flush=True)
