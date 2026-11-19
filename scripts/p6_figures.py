"""P6: Hình cho báo cáo + bảng macro-feedback cho giảng viên.

Hình (results/figures/, PNG 200 dpi, nền sáng cho bản in):
  heatmap_real_<p>.png     cụm × đặc trưng (tần suất)          — hình chính cho macro-feedback
  confusion_syn_<p>.png    nhãn cấy × cụm (synthetic)
  mds_<ds>_<p>.png         MDS trên Hamming có trọng số, small multiples (mỗi panel 1 cụm)
  ksweep_real.png          silhouette theo k (K-modes / Agglomerative), k đã chốt đánh dấu
  ablation_E3.png          ARI theo nhóm thuộc tính × bài
Bảng: results/tables/macro_feedback.{csv,md}. Tên cụm đọc từ results/tables/p5_cluster_names.csv (DP5).
"""
import re
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from sklearn.manifold import MDS

import bench
import cluster as cl
import config
import schema

FIG = config.FIGURES
FIG.mkdir(parents=True, exist_ok=True)
# Bảng màu tham chiếu (dataviz skill, light mode)
SURFACE, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
S1, S2 = '#2a78d6', '#eb6834'
CONTEXT = '#c9c8c2'
BLUES = LinearSegmentedColormap.from_list('seq_blue', ['#f3f7fd', '#cde2fb', '#86b6ef', '#3987e5',
                                                      '#256abf', '#184f95', '#0d366b'])
plt.rcParams.update({
    'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
    'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
    'text.color': INK, 'axes.titlesize': 11, 'axes.titleweight': 'bold', 'font.size': 9,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': False,
})
M = pd.read_parquet(config.PROCESSED / 'clusters_main.parquet')
NAMES = pd.read_csv(config.TABLES / 'p5_cluster_names.csv').set_index(['problem', 'cluster_id'])
SKIP = {'F', 'none', 'n/a', '0'}


def load(ds, p):
    W = schema.load_wide(config.PROCESSED / 'oav_wide' / f'{ds}_{p}.parquet')
    lab = M[(M.dataset == ds) & (M.problem == p)].set_index('sub_id').loc[W.sub_id, 'cluster_id'].values
    return W, lab


def short(col, v):
    return f"{col.split(':', 1)[1].replace('diff.', '').replace('output.', 'out.')}={v}"


def ink_for(x, vmax=1.0):
    return '#ffffff' if x / vmax > 0.55 else INK


def save(fig, name):
    fig.savefig(FIG / name, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print('  ', name)


# ------------------------------------------------------------ 1. heatmap cụm × đặc trưng (thật)
for p in config.PROBLEMS:
    W, lab = load('real', p)
    _, _, cols = cl.feature_matrix(W)
    picks = []
    for c in sorted(set(lab)):
        Wc = W[lab == c]
        sc = []
        for col in cols:
            for v, pc in Wc[col].value_counts(normalize=True).items():
                if v not in SKIP and pc >= 0.5:
                    sc.append((pc - (W[col] == v).mean(), col, v))
        picks += [(col, v) for _, col, v in sorted(sc, reverse=True)[:4]]
    picks = list(dict.fromkeys(picks))
    H = np.array([[(W[lab == c][col] == v).mean() for col, v in picks] for c in sorted(set(lab))])
    ylab = []
    for c in sorted(set(lab)):
        nm = NAMES.loc[(p, c), 'name_draft'] if (p, c) in NAMES.index else f'Cụm {c}'
        ylab.append(f"C{c} · {(lab == c).sum()} bài/{W[lab == c].repo.nunique()} SV\n"
                    + textwrap.shorten(nm, 52, placeholder='…'))
    fig, ax = plt.subplots(figsize=(1.0 + 0.42 * len(picks), 0.9 + 0.62 * len(ylab)))
    ax.imshow(H, cmap=BLUES, vmin=0, vmax=1, aspect='auto')
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            ax.text(j, i, f'{H[i, j]:.0%}', ha='center', va='center', fontsize=6.5, color=ink_for(H[i, j]))
    ax.set_xticks(range(len(picks)), [short(c, v) for c, v in picks], rotation=55, ha='right', fontsize=7)
    ax.set_yticks(range(len(ylab)), ylab, fontsize=7.5)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(f'{p}: tần suất đặc trưng trong từng cụm (dữ liệu thật, K-modes k={len(ylab)})', loc='left')
    save(fig, f'heatmap_real_{p}.png')

# ------------------------------------------------------------ 2. confusion nhãn cấy × cụm (synthetic)
for p in bench.SYNTH_PROBLEMS:
    W, lab = load('synthetic', p)
    y = np.where(W.label_true.str.contains(r'\+'), 'kép', W.label_true)
    ct = pd.crosstab(pd.Series(y, name='nhãn'), pd.Series(lab, name='cụm'))
    order = sorted([r for r in ct.index if r != 'kép']) + (['kép'] if 'kép' in ct.index else [])
    ct = ct.loc[order]
    R = ct.div(ct.sum(axis=1), axis=0).values
    fig, ax = plt.subplots(figsize=(1.2 + 0.55 * ct.shape[1], 0.8 + 0.42 * ct.shape[0]))
    ax.imshow(R, cmap=BLUES, vmin=0, vmax=1, aspect='auto')
    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            if ct.values[i, j]:
                ax.text(j, i, ct.values[i, j], ha='center', va='center', fontsize=7, color=ink_for(R[i, j]))
    ax.set_xticks(range(ct.shape[1]), [f'C{c}' for c in ct.columns])
    ax.set_yticks(range(ct.shape[0]), [f'{r} (n={ct.loc[r].sum()})' for r in ct.index])
    ax.set_xlabel('cụm (K-modes)')
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ari = cl.external(W.label_true, lab)['ari']
    ax.set_title(f'{p}: nhãn cấy × cụm (synthetic, ARI {ari:.2f}); màu = tỷ lệ theo hàng', loc='left')
    save(fig, f'confusion_syn_{p}.png')

# ------------------------------------------------------------ 3. MDS small multiples
for ds, probs in (('real', config.PROBLEMS), ('synthetic', bench.SYNTH_PROBLEMS)):
    for p in probs:
        W, lab = load(ds, p)
        X, w, _ = cl.feature_matrix(W)
        D = cl.weighted_hamming(X, w)
        Y = MDS(n_components=2, dissimilarity='precomputed', random_state=config.SEED,
                normalized_stress='auto', n_init=4).fit_transform(D)
        cs = sorted(set(lab))
        n = len(cs)
        ncol = min(n, 4)
        nrow = int(np.ceil(n / ncol))
        fig, axes = plt.subplots(nrow, ncol, figsize=(2.4 * ncol, 2.3 * nrow), squeeze=False,
                                 sharex=True, sharey=True)
        for ax in axes.flat[n:]:
            ax.set_visible(False)
        for ax, c in zip(axes.flat, cs):
            m = lab == c
            ax.scatter(Y[~m, 0], Y[~m, 1], s=12, c=CONTEXT, linewidths=0)
            ax.scatter(Y[m, 0], Y[m, 1], s=18, c=S1, edgecolors=SURFACE, linewidths=0.8)
            ttl = f'C{c} · {m.sum()} bài'
            if ds == 'real' and (p, c) in NAMES.index:
                ttl += '\n' + textwrap.shorten(NAMES.loc[(p, c), 'name_draft'], 34, placeholder='…')
            elif ds == 'synthetic':
                top = pd.Series(W.label_true[m]).value_counts()
                ttl += f'\nnhãn chính {top.index[0]} ({top.iloc[0]}/{m.sum()})'
            ax.set_title(ttl, fontsize=7.5, loc='left', fontweight='normal')
            ax.set_xticks([])
            ax.set_yticks([])
        fig.suptitle(f'{p} ({"dữ liệu thật" if ds == "real" else "synthetic"}): MDS trên Hamming có trọng số',
                     x=0.01, ha='left', fontsize=10, fontweight='bold')
        fig.tight_layout()
        save(fig, f'mds_{ds}_{p}.png')

# ------------------------------------------------------------ 4. silhouette theo k (thật)
R = pd.read_csv(config.TABLES / 'p4_k_sweep.csv')
fig, axes = plt.subplots(1, 4, figsize=(11, 2.8), sharey=True)
for ax, p in zip(axes, config.PROBLEMS):
    for m, col, nm in (('kmodes', S1, 'K-modes'), ('agglo', S2, 'Agglomerative')):
        g = R[(R.dataset == 'real') & (R.problem == p) & (R.method == m)]
        ax.plot(g.k, g.silhouette, color=col, lw=2, marker='o', ms=4, label=nm)
    ax.axvline(config.K_REAL[p], color=INK2, lw=1, ls=':')
    ax.text(config.K_REAL[p] + 0.15, 0.62, f'k={config.K_REAL[p]}', fontsize=7, color=INK2)
    ax.set_title(p, loc='left')
    ax.set_xlabel('k')
    ax.grid(axis='y', color=GRID, lw=0.6)
axes[0].set_ylabel('silhouette')
axes[0].legend(frameon=False, fontsize=7, loc='lower left')
axes[0].set_ylim(0, 0.66)
fig.suptitle('Silhouette theo k — dữ liệu thật (đường chấm: k đã chốt, DP4)', x=0.01, ha='left',
             fontsize=10, fontweight='bold')
fig.tight_layout()
save(fig, 'ksweep_real.png')

# ------------------------------------------------------------ 5. ablation E3
E3 = pd.read_csv(config.TABLES / 'E3_ablation.csv')
A = E3[E3.method == 'kmodes'].pivot(index='groups', columns='problem', values='ari')
order = ['O', 'A', 'D', 'O+A', 'O+D', 'A+D', 'O+A+D', 'T+O+A+D']
A = A.loc[order, bench.SYNTH_PROBLEMS]
fig, ax = plt.subplots(figsize=(5.2, 3.6))
ax.imshow(A.values, cmap=BLUES, vmin=0, vmax=1, aspect='auto')
for i in range(A.shape[0]):
    for j in range(A.shape[1]):
        ax.text(j, i, f'{A.values[i, j]:.2f}', ha='center', va='center', fontsize=7.5,
                color=ink_for(A.values[i, j]))
ax.set_xticks(range(A.shape[1]), A.columns)
ax.set_yticks(range(A.shape[0]), A.index)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title('E3: ARI theo nhóm thuộc tính (synthetic, K-modes)', loc='left')
save(fig, 'ablation_E3.png')

# ------------------------------------------------------------ bảng macro-feedback
rows = []
for p in config.PROBLEMS:
    W, lab = load('real', p)
    rules = (config.ROOT / 'results' / 'rules' / f'real_{p}.txt').read_text().splitlines()
    X, w, _ = cl.feature_matrix(W)
    D = cl.weighted_hamming(X, w)
    for c in sorted(set(lab)):
        idx = np.flatnonzero(lab == c)
        rr = [l for l in rules if re.search(rf'THÌ Cụm {c} \[', l)]
        best = max(rr, key=lambda l: int(re.search(r'coverage (\d+)/', l).group(1))) if rr else ''
        med = W.sub_id.iloc[idx[np.argmin(D[np.ix_(idx, idx)].sum(axis=1))]]
        rows.append(dict(problem=p, cluster=c,
                         misconception=NAMES.loc[(p, c), 'name_draft'] if (p, c) in NAMES.index else '',
                         taxonomy=NAMES.loc[(p, c), 'taxonomy'] if (p, c) in NAMES.index else '',
                         students=W.repo.iloc[idx].nunique(), submissions=len(idx),
                         top_rule=re.sub(r'^R\d+: ', '', best), example=med))
MF = pd.DataFrame(rows)
MF.to_csv(config.TABLES / 'macro_feedback.csv', index=False)
md = ['# Macro-feedback cho giảng viên — IntroClass (dữ liệu thật)', '',
      'Số SV = số sinh viên khác nhau trong cụm (một SV có thể nộp nhiều phiên bản). '
      'Tên misconception: bản đề xuất (DP5), sửa trong `results/tables/p5_cluster_names.csv`.', '']
for p, g in MF.groupby('problem', sort=False):
    md += [f'## {p}', '', '| Cụm | Misconception | Taxonomy | SV | Bài | Luật tiêu biểu (ILA) | Bài minh họa |',
           '|---|---|---|---:|---:|---|---|']
    for r in g.sort_values('students', ascending=False).itertuples():
        md.append(f'| C{r.cluster} | {r.misconception} | {r.taxonomy} | {r.students} | {r.submissions} | '
                  f'`{r.top_rule}` | `{r.example}` |')
    md.append('')
(config.TABLES / 'macro_feedback.md').write_text('\n'.join(md))
print('DONE')
