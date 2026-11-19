"""P4: Quét k = 2..12 cho 3 phương pháp, mọi (dataset, problem); trọng số khởi điểm (DP3).

Ghi data/processed/clusters.parquet (dataset, problem, sub_id, method, k, cluster_id)
    results/tables/p4_k_sweep.csv  (silhouette, cost K-modes; synthetic thêm ARI/NMI/Purity — tham khảo E1)
"""
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd

import bench
import cluster as cl
import config
import schema

warnings.filterwarnings('ignore')
K_RANGE = range(2, 13)
rows, assign = [], []
datasets = [('real', p) for p in config.PROBLEMS] + [('synthetic', p) for p in bench.SYNTH_PROBLEMS]
for ds, p in datasets:
    t0 = time.time()
    W = schema.load_wide(config.PROCESSED / 'oav_wide' / f'{ds}_{p}.parquet')
    X, w, cols = cl.feature_matrix(W)
    D = cl.weighted_hamming(X, w)
    y = W.label_true.values if ds == 'synthetic' else None
    for k in K_RANGE:
        if k >= len(W):
            break
        res = {}
        res['kmodes'], cost = cl.kmodes(X, w, k)
        res['agglo'], _ = cl.agglomerative(D, k)
        res['kmeans1h'] = cl.kmeans_onehot(X, w, k)
        for m, lab in res.items():
            r = dict(dataset=ds, problem=p, n=len(W), d=len(cols), method=m, k=k,
                     n_clusters=len(set(lab)), silhouette=cl.silhouette(D, lab),
                     cost=cost if m == 'kmodes' else None,
                     min_size=pd.Series(lab).value_counts().min())
            if y is not None:
                r.update(cl.external(y, lab))
            rows.append(r)
            assign += [dict(dataset=ds, problem=p, sub_id=s, method=m, k=k, cluster_id=int(c))
                       for s, c in zip(W.sub_id, lab)]
    print(f'[{ds}/{p}] n={len(W)} d={len(cols)} {time.time() - t0:.0f}s', flush=True)

R = pd.DataFrame(rows)
R.to_csv(config.TABLES / 'p4_k_sweep.csv', index=False)
pd.DataFrame(assign).to_parquet(config.PROCESSED / 'clusters.parquet', index=False)
print('DONE')
