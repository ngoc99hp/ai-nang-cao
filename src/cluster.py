"""Gom cụm trên ma trận OAV (Phase 4).

Khoảng cách: Hamming có trọng số. Trọng số cột = FEATURE_WEIGHTS[nhóm] / số cột của nhóm
(chuẩn hóa theo nhóm → mỗi nhóm đóng góp đúng trọng số của nó, không phụ thuộc số cột).
"""
import numpy as np
import pandas as pd
from kmodes.kmodes import KModes
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score

import config
import schema

GROUP_KEY = {'T': 'test', 'O': 'outdiff', 'A': 'ast', 'D': 'diff'}


def feature_matrix(W: pd.DataFrame, groups=('T', 'O', 'A', 'D'), weights=None, normalize_groups=True):
    """→ (X_codes int[n, d], w float[d], cols). Bỏ cột hằng."""
    weights = weights or config.FEATURE_WEIGHTS
    cols = [c for c in W.columns if c not in schema.WIDE_KEYS and c[0] in groups and W[c].nunique() > 1]
    X = np.column_stack([pd.factorize(W[c])[0] for c in cols]) if cols else np.zeros((len(W), 0), int)
    n_g = {g: sum(c[0] == g for c in cols) for g in groups}
    w = np.array([weights[GROUP_KEY[c[0]]] / (n_g[c[0]] if normalize_groups else 1) for c in cols])
    return X, w, cols


def weighted_hamming(X_codes: np.ndarray, w: np.ndarray) -> np.ndarray:
    """X_codes: ma trận mã hóa số nguyên theo cột; w: trọng số theo cột."""
    D = np.zeros((X_codes.shape[0],) * 2)
    for j in range(X_codes.shape[1]):              # vector hóa theo cột, nhanh hơn lambda trong pdist
        col = X_codes[:, j]
        D += w[j] * (col[:, None] != col[None, :])
    return D / w.sum()


def kmodes(X, w, k, seed=config.SEED):
    def dissim(a, b, **_):
        return np.sum((a != b) * w, axis=1)
    km = KModes(n_clusters=k, init='Cao', n_init=5, random_state=seed, cat_dissim=dissim)
    labels = km.fit_predict(X)
    return labels, km.cost_


def agglomerative(D, k):
    Z = linkage(squareform(D, checks=False), method='average')
    return fcluster(Z, k, criterion='maxclust') - 1, Z


def kmeans_onehot(X, w, k, seed=config.SEED):
    blocks = [np.sqrt(w[j]) * (X[:, [j]] == np.unique(X[:, j])[None, :]) for j in range(X.shape[1])]
    Z = np.hstack(blocks).astype(float)
    return KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(Z)


def silhouette(D, labels):
    if len(set(labels)) < 2 or len(set(labels)) >= len(labels):
        return np.nan
    return silhouette_score(D, labels, metric='precomputed')


def purity(y_true, y_pred) -> float:
    ct = pd.crosstab(pd.Series(y_pred, name='c'), pd.Series(y_true, name='y'))
    return ct.max(axis=1).sum() / len(y_true)


def external(y_true, y_pred) -> dict:
    return dict(ari=adjusted_rand_score(y_true, y_pred), nmi=normalized_mutual_info_score(y_true, y_pred),
                purity=purity(y_true, y_pred))
