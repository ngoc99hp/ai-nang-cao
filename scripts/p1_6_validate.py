"""P1.6: Kiểm định runner (status strict) với metadata.json — chỉ phiên bản deterministic.

Xuất results/tables/p1_6_validation.csv (theo problem) và p1_6_mismatches.csv (chi tiết lệch).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd

import config
import introclass as ic
import schema

summ, mism = [], []
for p in ic.problems():
    f = config.INTERIM / 'test_results' / f'{p}.parquet'
    if not f.exists():
        continue
    tr = schema.load(f, schema.TEST_RESULTS)
    v = ic.load_versions(p)
    meta = v.explode('meta_pass')[['sub_id', 'meta_pass']].dropna().rename(columns={'meta_pass': 'test_id'}).assign(meta='PASS')
    meta = pd.concat([meta, v.explode('meta_fail')[['sub_id', 'meta_fail']].dropna()
                      .rename(columns={'meta_fail': 'test_id'}).assign(meta='FAIL')])
    nd = v.set_index('sub_id')['nondeterministic']
    ce = tr[tr.status == 'COMPILE_ERROR']
    # COMPILE_ERROR → mọi test coi như FAIL
    ce_rows = meta[meta.sub_id.isin(ce.sub_id)].assign(status='COMPILE_ERROR', status_sem='COMPILE_ERROR', returncode=pd.NA)
    j = meta.merge(tr[tr.test_id.notna()], on=['sub_id', 'test_id'], how='inner')
    if len(ce_rows):
        j = pd.concat([j, ce_rows], ignore_index=True)
    j['nondet'] = j.sub_id.map(nd)
    j['ok'] = (j.status == 'PASS') == (j.meta == 'PASS')
    ubf = config.INTERIM / 'uninit' / f'{p}.parquet'          # từ scripts/p1_6b_uninit_probe.py
    ub = pd.read_parquet(ubf).groupby('sub_id').differs.any() if ubf.exists() else pd.Series(dtype=bool)
    j['ub'] = j.sub_id.map(ub).fillna(False).astype(bool)
    d = j[~j.nondet]
    c = d[~d.ub]
    summ.append(dict(problem=p, versions=len(v), compile_error=ce.sub_id.nunique(),
                     det_tests=len(d), match_det=d.ok.mean(), match_det_noUB=c.ok.mean(),
                     match_all=j.ok.mean(), ub_versions=int(ub.sum()),
                     mism_det=int((~d.ok).sum()), mism_det_noUB=int((~c.ok).sum()),
                     rc_nonzero_det=int(((d.returncode.fillna(0) != 0) & d.status.isin(['PASS', 'FAIL'])).sum()),
                     sem_pass=float((tr.status_sem == 'PASS').mean()),
                     format_only=int(((tr.status != 'PASS') & (tr.status_sem == 'PASS')).sum())))
    mm = d[~d.ok].drop(columns='stdout', errors='ignore').merge(tr[['sub_id', 'test_id', 'stdout']], on=['sub_id', 'test_id'], how='left')
    mism.append(mm.assign(problem=p))

S = pd.DataFrame(summ)
config.TABLES.mkdir(parents=True, exist_ok=True)
S.to_csv(config.TABLES / 'p1_6_validation.csv', index=False)
M = pd.concat(mism, ignore_index=True)
M.to_csv(config.TABLES / 'p1_6_mismatches.csv', index=False)
pd.set_option('display.width', 200)
print(S.to_string(index=False, float_format=lambda x: f'{x:.4f}'))
print('\nLệch (deterministic) theo (meta, runner status):')
print(M.groupby(['problem', 'meta', 'status']).size().to_string())
