"""P3: Trích xuất OAV cho dữ liệu thật (IntroClass, bài giữ lại ở P1.7) và synthetic (P2).

Ghi data/processed/oav_long/<dataset>_<problem>.parquet (schema.OAV_LONG)
    data/processed/oav_wide/<dataset>_<problem>.parquet (schema.save_wide)
    results/tables/p3_features.csv (số thuộc tính / nhóm, số cột hằng)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd

import bench
import config
import features as ft
import schema


def build(dataset, p, subs, tr, extra_flags=None):
    tests = {t: (i.read_text(), o.read_text()) for t, i, o in bench.tests_of(p)}
    tr = tr[tr.test_id.notna()]
    trg = dict(tuple(tr.groupby('sub_id')))
    long_rows, wide_rows = [], []
    for r in subs.itertuples():
        code = (config.ROOT / r.code_path).read_bytes()
        fl = extra_flags.get(r.sub_id) if extra_flags else None
        F = ft.extract(p, code, trg[r.sub_id], tests, fl)
        long_rows += [dict(sub_id=r.sub_id, problem=p, source=r.source, group=g, object=o, attribute=a, value=v)
                      for (g, o, a), v in F.items()]
        wide_rows.append({'sub_id': r.sub_id, 'problem': p, 'source': r.source,
                          'label_true': r.label_true, 'repo': getattr(r, 'repo', None),
                          **{ft.key(k): v for k, v in F.items()}})
    L = pd.DataFrame(long_rows)
    W = pd.DataFrame(wide_rows)
    feats = [c for c in W.columns if c not in schema.WIDE_KEYS]
    # thuộc tính Output-diff dạng cờ vắng mặt → 'F'
    W[[c for c in feats if c.startswith('O:output.')]] = W[[c for c in feats if c.startswith('O:output.')]].fillna('F')
    W[feats] = W[feats].fillna('n/a')
    schema.save(L, schema.OAV_LONG, config.PROCESSED / 'oav_long' / f'{dataset}_{p}.parquet')
    schema.save_wide(W, config.PROCESSED / 'oav_wide' / f'{dataset}_{p}.parquet')
    const = [c for c in feats if W[c].nunique() == 1]
    return dict(dataset=dataset, problem=p, n=len(W), **{f'n_{g}': sum(c.startswith(g + ':') for c in feats)
                                                        for g in 'TOA'},
                n_const=len(const), n_triples=len(L))


stats = []
for p in config.PROBLEMS:                                   # dữ liệu thật
    fl = schema.load(config.INTERIM / 'flags' / f'{p}.parquet', schema.SUB_FLAGS)
    keep = fl[fl.keep]
    sub = schema.load(config.INTERIM / 'submissions' / f'{p}.parquet', schema.SUBMISSIONS)
    sub = sub[sub.sub_id.isin(keep.sub_id)].merge(keep[['sub_id', 'repo']], on='sub_id')
    tr = schema.load(config.INTERIM / 'test_results' / f'{p}.parquet', schema.TEST_RESULTS)
    flags = {r.sub_id: {'uninit_dependent': r.uninit_dependent, 'nondet_dataset': r.nondet_dataset,
                        'format_only_any': r.format_only_any} for r in keep.itertuples()}
    stats.append(build('real', p, sub, tr, flags))
    print(stats[-1], flush=True)
for p in bench.SYNTH_PROBLEMS:                              # synthetic
    d = config.INTERIM / 'synthetic'
    sub = schema.load(d / 'submissions' / f'{p}.parquet', schema.SUBMISSIONS)
    tr = schema.load(d / 'test_results' / f'{p}.parquet', schema.TEST_RESULTS)
    stats.append(build('synthetic', p, sub, tr))
    print(stats[-1], flush=True)
pd.DataFrame(stats).to_csv(config.TABLES / 'p3_features.csv', index=False)
print(pd.DataFrame(stats).to_string(index=False))
