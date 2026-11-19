"""P1.6b: Phát hiện phiên bản phụ thuộc biến chưa khởi tạo (UB).

Compile 2 lần với -ftrivial-auto-var-init=zero và =pattern; output khác nhau ở ≥ 1 test
⇒ phụ thuộc giá trị rác ⇒ kết quả không tái lập giữa các môi trường.
Ghi data/interim/uninit/<problem>.parquet (sub_id, test_id, stdout_zero, stdout_pattern, differs).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd

import config
import introclass as ic
import runner

out_dir = config.INTERIM / 'uninit'
out_dir.mkdir(parents=True, exist_ok=True)
for p in sys.argv[1:] or ic.problems():
    f = out_dir / f'{p}.parquet'
    if f.exists():
        continue
    v = ic.load_versions(p)
    subs = [(r.sub_id, config.ROOT / r.code_path) for r in v.itertuples()]
    res = {}
    for mode in ('zero', 'pattern'):
        rows = runner.run_batch(subs, ic.tests_of(p), config.WORK / 'bin_uninit' / mode / p,
                                problem=p, extra_flags=[f'-ftrivial-auto-var-init={mode}'])
        res[mode] = pd.DataFrame(rows).set_index(['sub_id', 'test_id'])[['stdout', 'status']]
    df = res['zero'].join(res['pattern'], lsuffix='_zero', rsuffix='_pattern').reset_index()
    df['differs'] = (df.stdout_zero != df.stdout_pattern) | (df.status_zero != df.status_pattern)
    df.to_parquet(f)   # bảng phụ trợ chẩn đoán, không thuộc data contract của schema.py
    print(f'[{p}] versions phụ thuộc UB: {df.groupby("sub_id").differs.any().sum()}/{len(v)}', flush=True)
print('DONE', flush=True)
