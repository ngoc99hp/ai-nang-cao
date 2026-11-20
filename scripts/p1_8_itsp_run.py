"""P1.8: Chạy test ITSP (buggy + correct) → data/interim/{submissions,test_results}/itsp_<lab>.parquet.

So sánh output theo token (normalize.check với problem ngoài IntroClass). Resume theo lab.
  docker exec -d aai-lab bash -c 'python scripts/p1_8_itsp_run.py > work/logs/p1_8.log 2>&1'
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd

import config
import itsp
import runner
import schema

P = itsp.pairs()
print(f'{len(P)} cặp, {P.pid.nunique()} bài, {P.lab.nunique()} lab', flush=True)
for lab, G in P.groupby('lab'):
    out = config.INTERIM / 'test_results' / f'itsp_{lab}.parquet'
    if out.exists():
        print(f'[{lab}] đã có, bỏ qua', flush=True)
        continue
    t0, rows, subs = time.time(), [], []
    for pid, g in G.groupby('pid'):
        tests = itsp.tests_of(pid)
        s = [(r.buggy_id, config.ROOT / r.buggy_path) for r in g.itertuples()] + \
            [(r.correct_id, config.ROOT / r.correct_path) for r in g.itertuples()]
        rr = runner.run_batch(s, tests, config.WORK / 'bin' / 'itsp' / pid)
        rows += [dict(r, problem=f'itsp_{pid}') for r in rr]
        for r in g.itertuples():
            subs += [dict(sub_id=r.buggy_id, code_path=r.buggy_path, problem=r.problem),
                     dict(sub_id=r.correct_id, code_path=r.correct_path, problem=r.problem)]
    tr = pd.DataFrame(rows)
    ok = tr[tr.test_id.notna()].groupby('sub_id').status.apply(lambda s: (s == 'PASS').all())
    sub = pd.DataFrame(subs).assign(source='itsp', label_true=None)
    sub['is_correct'] = sub.sub_id.map(ok).fillna(False).astype(bool)
    schema.save(sub, schema.SUBMISSIONS, config.INTERIM / 'submissions' / f'itsp_{lab}.parquet')
    schema.save(tr, schema.TEST_RESULTS, out)
    print(f'[{lab}] {len(G)} cặp, {time.time() - t0:.0f}s  {tr.status.value_counts().to_dict()}', flush=True)
print('DONE', flush=True)
