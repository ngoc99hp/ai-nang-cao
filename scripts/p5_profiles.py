"""P5: Hồ sơ cụm (dữ liệu thật) để người dùng đặt tên misconception (DP5).

Ghi results/tables/p5_cluster_profiles.md
"""
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import numpy as np
import pandas as pd

import cluster as cl
import config
import schema

M = pd.read_parquet(config.PROCESSED / 'clusters_main.parquet')
out = ['# Hồ sơ cụm — dữ liệu thật IntroClass (K-modes, trọng số DP3, k theo DP4)', '',
       'Đặc trưng: cặp thuộc tính = giá trị có tần suất trong cụm ≥ 50% và cao hơn toàn bài rõ nhất '
       '(cụm% / toàn bài%). Bỏ qua giá trị F / none / n/a / 0.', '']
SKIP = {'F', 'none', 'n/a', '0'}
for p in config.PROBLEMS:
    W = schema.load_wide(config.PROCESSED / 'oav_wide' / f'real_{p}.parquet')
    X, w, cols = cl.feature_matrix(W)
    D = cl.weighted_hamming(X, w)
    lab = M[(M.dataset == 'real') & (M.problem == p)].set_index('sub_id').loc[W.sub_id, 'cluster_id'].values
    refs = pd.read_parquet(config.PROCESSED / 'refs' / f'real_{p}.parquet').set_index('sub_id')
    sub = schema.load(config.INTERIM / 'submissions' / f'{p}.parquet', schema.SUBMISSIONS).set_index('sub_id')
    rules = Path(config.ROOT / 'results' / 'rules' / f'real_{p}.txt').read_text().splitlines()
    out += [f'## {p} — {len(W)} bài, {W.repo.nunique()} SV, k = {len(set(lab))}', '']
    for c in sorted(set(lab)):
        idx = np.flatnonzero(lab == c)
        Wc = W.iloc[idx]
        out += [f'### {p} / Cụm {c} — {len(idx)} bài, {Wc.repo.nunique()} SV', '']
        feats = []
        for col in cols:
            for v, pc in Wc[col].value_counts(normalize=True).items():
                if v in SKIP or pc < 0.5:
                    continue
                pa = (W[col] == v).mean()
                feats.append((pc - pa, col, v, pc, pa))
        feats.sort(reverse=True)
        out += ['**Đặc trưng:** ' + '; '.join(f'`{col}={v}` ({pc:.0%}/{pa:.0%})' for _, col, v, pc, pa in feats[:6])]
        rr = [l for l in rules if re.search(rf'THÌ Cụm {c} \[', l)]
        rr.sort(key=lambda l: -int(re.search(r'coverage (\d+)/', l).group(1)))
        out += ['', '**Luật ILA (coverage cao nhất):**', ''] + [f'- `{l}`' for l in rr[:3]]
        med = idx[np.argmin(D[np.ix_(idx, idx)].sum(axis=1))]
        sid = W.sub_id.iloc[med]
        ref = refs.loc[sid]
        a = (config.ROOT / sub.loc[sid, 'code_path']).read_text(errors='replace').splitlines()
        ref_path = sub.loc[ref.ref_id, 'code_path'] if ref.ref_id in sub.index else \
            f'bench/{p}/{ref.ref_id.split("_", 2)[2]}.c'
        b = (config.ROOT / ref_path).read_text(errors='replace').splitlines()
        diff = [l for l in difflib.unified_diff(b, a, 'đúng', 'sai', n=0, lineterm='')
                if not l.startswith(('---', '+++', '@@'))]
        out += ['', f'**Bài đại diện** `{sid}` vs bản đúng `{ref.ref_id}` ({ref.ref_kind}, sim {ref.similarity:.2f}) '
                f'— `-` bản đúng, `+` bài sai:', '', '```diff', *[l.rstrip()[:110] for l in diff[:14]],
                *(['… (' + str(len(diff) - 14) + ' dòng nữa)'] if len(diff) > 14 else []), '```', '']
Path(config.TABLES / 'p5_cluster_profiles.md').write_text('\n'.join(out))
print('\n'.join(out))
