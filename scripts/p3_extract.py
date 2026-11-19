"""P3: Trích xuất OAV (T, O, A, D) cho dữ liệu thật (IntroClass, bài giữ lại ở P1.7) và synthetic (P2).

D: so với bản đúng gần nhất — bản sửa đúng về sau của chính SV (dữ liệu thật) hoặc bản gần nhất theo
token trong kho lời giải đúng (IntroClass unique + bench). Ghi bảng data/processed/refs/<dataset>_<problem>.parquet.

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
import diff_features as dfe
import features as ft
import schema


def ref_pool(p):
    """{ref_id: code} lời giải đúng (IntroClass unique, không phụ thuộc UB) + bench."""
    pool = {}
    if p in config.PROBLEMS:
        f = schema.load(config.INTERIM / 'flags' / f'{p}.parquet', schema.SUB_FLAGS)
        sub = schema.load(config.INTERIM / 'submissions' / f'{p}.parquet', schema.SUBMISSIONS).set_index('sub_id')
        ok = f[f.compiled & (f.n_fail_sem == 0) & (f.dup_of == f.sub_id) & ~f.uninit_dependent]
        pool = {s: (config.ROOT / sub.loc[s, 'code_path']).read_bytes() for s in ok.sub_id}
    pool.update({s: f.read_bytes() for s, f in bench.sources(p)})
    return pool


def own_fix(p):
    """{sub_id buggy: (ref_id, code)} bản đúng sớm nhất về sau của cùng SV (dữ liệu thật)."""
    f = schema.load(config.INTERIM / 'flags' / f'{p}.parquet', schema.SUB_FLAGS)
    sub = schema.load(config.INTERIM / 'submissions' / f'{p}.parquet', schema.SUBMISSIONS).set_index('sub_id')
    f['rev'] = f.sub_id.str[-3:]
    ok = f[f.compiled & (f.n_fail_sem == 0)].sort_values('rev')
    out = {}
    for r in f[f.keep].itertuples():
        later = ok[(ok.repo == r.repo) & (ok.rev > r.rev)]
        if len(later):
            s = later.sub_id.iloc[0]
            out[r.sub_id] = (s, (config.ROOT / sub.loc[s, 'code_path']).read_bytes())
    return out


def build(dataset, p, subs, tr, extra_flags=None, own=None):
    tests = {t: (i.read_text(), o.read_text()) for t, i, o in bench.tests_of(p)}
    tr = tr[tr.test_id.notna()]
    trg = dict(tuple(tr.groupby('sub_id')))
    long_rows, wide_rows, refs = [], [], []
    pool = ref_pool(p)
    pool_tok = {s: dfe.tokens(c) for s, c in pool.items()}
    for r in subs.itertuples():
        code = (config.ROOT / r.code_path).read_bytes()
        fl = extra_flags.get(r.sub_id) if extra_flags else None
        F = ft.extract(p, code, trg[r.sub_id], tests, fl)
        tok = dfe.tokens(code)
        if own and r.sub_id in own:
            ref_id, ref_code = own[r.sub_id]
            kind = 'own_fix'
        else:
            ref_id = max(pool_tok, key=lambda s: dfe.similarity(tok, pool_tok[s]))
            ref_code, kind = pool[ref_id], 'nearest'
        refs.append(dict(sub_id=r.sub_id, ref_id=ref_id, ref_kind=kind,
                         similarity=dfe.similarity(tok, dfe.tokens(ref_code))))
        F.update(dfe.diff_features(code, ref_code))
        long_rows += [dict(sub_id=r.sub_id, problem=p, source=r.source, group=g, object=o, attribute=a, value=v)
                      for (g, o, a), v in F.items()]
        wide_rows.append({'sub_id': r.sub_id, 'problem': p, 'source': r.source,
                          'label_true': r.label_true, 'repo': getattr(r, 'repo', None),
                          **{ft.key(k): v for k, v in F.items()}})
    R = pd.DataFrame(refs)
    (config.PROCESSED / 'refs').mkdir(parents=True, exist_ok=True)
    R.to_parquet(config.PROCESSED / 'refs' / f'{dataset}_{p}.parquet', index=False)   # bảng phụ trợ
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
                                                        for g in 'TOAD'},
                own_fix=int((R.ref_kind == 'own_fix').sum()), sim_median=round(R.similarity.median(), 3),
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
    stats.append(build('real', p, sub, tr, flags, own_fix(p)))
    print(stats[-1], flush=True)
for p in bench.SYNTH_PROBLEMS:                              # synthetic
    d = config.INTERIM / 'synthetic'
    sub = schema.load(d / 'submissions' / f'{p}.parquet', schema.SUBMISSIONS)
    tr = schema.load(d / 'test_results' / f'{p}.parquet', schema.TEST_RESULTS)
    stats.append(build('synthetic', p, sub, tr))
    print(stats[-1], flush=True)
pd.DataFrame(stats).to_csv(config.TABLES / 'p3_features.csv', index=False)
print(pd.DataFrame(stats).to_string(index=False))
