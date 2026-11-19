"""P1.6: Compile + chạy toàn bộ test IntroClass → data/interim/test_results/<problem>.parquet.

Resume được: bỏ qua problem đã có file. Chạy nền trong container:
  docker exec -d aai-lab bash -c 'python scripts/p1_6_run_tests.py > work/logs/p1_6.log 2>&1'
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd

import config
import introclass as ic
import runner
import schema

only = sys.argv[1:] or ic.problems()
for p in only:
    out = config.INTERIM / 'test_results' / f'{p}.parquet'
    if out.exists():
        print(f'[{p}] đã có {out.name}, bỏ qua', flush=True)
        continue
    t0 = time.time()
    vers = ic.load_versions(p)
    subs = [(r.sub_id, config.ROOT / r.code_path) for r in vers.itertuples()]
    tests = ic.tests_of(p)
    print(f'[{p}] {len(subs)} versions × {len(tests)} tests ...', flush=True)
    rows = runner.run_batch(subs, tests, config.WORK / 'bin' / p, problem=p)
    df = pd.DataFrame(rows).assign(problem=p)
    schema.save(df, schema.TEST_RESULTS, out)
    print(f'[{p}] xong {time.time() - t0:.0f}s  strict={df.status.value_counts().to_dict()}', flush=True)
print('DONE', flush=True)
