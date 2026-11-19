"""P1.7: Lọc + khử trùng + thống kê dữ liệu IntroClass.

Ghi:
  data/interim/submissions/<problem>.parquet   (schema.SUBMISSIONS; is_correct = pass toàn bộ test semantic)
  data/interim/flags/<problem>.parquet         (schema.SUB_FLAGS)
  results/tables/p1_stats.csv
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd

import ast_utils
import config
import introclass as ic
import schema

stats = []
for p in ic.problems():
    v = ic.load_versions(p)
    tr = schema.load(config.INTERIM / 'test_results' / f'{p}.parquet', schema.TEST_RESULTS)
    ub = pd.read_parquet(config.INTERIM / 'uninit' / f'{p}.parquet').groupby('sub_id').differs.any()
    n_tests = len(ic.tests_of(p))

    ce = set(tr.loc[tr.status == 'COMPILE_ERROR', 'sub_id'])
    t = tr[tr.test_id.notna()]
    g = t.groupby('sub_id')
    agg = pd.DataFrame({
        'n_fail_strict': g.status.apply(lambda s: (s != 'PASS').sum()),
        'n_fail_sem': g.status_sem.apply(lambda s: (s != 'PASS').sum()),
        'format_only_any': g.apply(lambda d: ((d.status != 'PASS') & (d.status_sem == 'PASS')).any(),
                                   include_groups=False),
    })
    f = v[['sub_id', 'problem', 'repo', 'code_path', 'nondeterministic', 'is_unique']].merge(
        agg, left_on='sub_id', right_index=True, how='left')
    f['compiled'] = ~f.sub_id.isin(ce)
    f['n_tests'] = n_tests
    f[['n_fail_strict', 'n_fail_sem']] = f[['n_fail_strict', 'n_fail_sem']].fillna(n_tests)
    f['format_only_any'] = f.format_only_any.fillna(False).astype(bool)
    f['fails_all_sem'] = f.n_fail_sem == n_tests
    f['nondet_dataset'] = f.nondeterministic
    f['uninit_dependent'] = f.sub_id.map(ub).fillna(False).astype(bool)
    f['code_hash'] = [ast_utils.code_hash((config.ROOT / c).read_bytes()) for c in f.code_path]

    # Khử trùng: đại diện = sub_id nhỏ nhất trong nhóm cùng code_hash
    f = f.sort_values('sub_id')
    f['dup_of'] = f.groupby('code_hash').sub_id.transform('first')
    f['n_dups'] = f.groupby('code_hash').sub_id.transform('size')
    buggy = f.compiled & (f.n_fail_sem > 0)
    f['keep'] = buggy & (f.dup_of == f.sub_id)
    schema.save(f, schema.SUB_FLAGS, config.INTERIM / 'flags' / f'{p}.parquet')

    sub = v.assign(is_correct=v.sub_id.map(f.set_index('sub_id').n_fail_sem.eq(0)))
    schema.save(sub, schema.SUBMISSIONS, config.INTERIM / 'submissions' / f'{p}.parquet')

    k = f[f.keep]
    stats.append(dict(
        problem=p, versions=len(f), students=f.repo.nunique(), compiled=int(f.compiled.sum()),
        correct_sem=int((f.compiled & (f.n_fail_sem == 0)).sum()),
        buggy_strict=int((f.compiled & (f.n_fail_strict > 0)).sum()),
        buggy_sem=int(buggy.sum()),
        format_only_versions=int((f.compiled & (f.n_fail_strict > 0) & (f.n_fail_sem == 0)).sum()),
        buggy_unique_dataset=int((buggy & f.is_unique).sum()),
        kept=len(k), kept_students=k.repo.nunique(),
        kept_fails_all=int(k.fails_all_sem.sum()), kept_uninit=int(k.uninit_dependent.sum()),
        kept_nondet_dataset=int(k.nondet_dataset.sum()),
        distinct_fail_patterns=t[t.sub_id.isin(k.sub_id)].pivot(index='sub_id', columns='test_id', values='status_sem')
                                .apply(tuple, axis=1).nunique(),
    ))
    print(f'[{p}] xong', flush=True)

S = pd.DataFrame(stats)
S.to_csv(config.TABLES / 'p1_stats.csv', index=False)
pd.set_option('display.width', 250)
print(S.set_index('problem').T.to_string())
