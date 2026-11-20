"""P1.8: Kiểm định runner trên ITSP bằng verdict ghi trong comment đầu mỗi file (hệ thống chấm gốc của IIT-K).

Ghép verdict ↔ test theo nội dung input. Lệch kiểu "gốc FAIL / ta PASS" mà output chỉ khác khoảng trắng
là do ta so theo token (lỗi định dạng, DP0) — tách riêng.
→ results/tables/p1_8_itsp_validation.csv
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd

import config
import itsp
import schema

V = re.compile(r'Verdict:(\w+), Visibility:\d, Input:"(.*?)", ExpOutput:"(.*?)", Output:"(.*?)"\n(?=Verdict|\*/)', re.S)
P = itsp.pairs()
TR = pd.concat([schema.load(f, schema.TEST_RESULTS) for f in (config.INTERIM / 'test_results').glob('itsp_*.parquet')])
TR = TR.set_index(['sub_id', 'test_id'])
rows = []
for pid, g in P.groupby('pid'):
    by_in = {t[1].read_text(errors='replace').strip(): t[0] for t in itsp.tests_of(pid)}
    for r in g.itertuples():
        for kind in ('buggy', 'correct'):
            sid, path = getattr(r, f'{kind}_id'), getattr(r, f'{kind}_path')
            head = (config.ROOT / path).read_text(errors='replace').split('*/', 1)[0] + '*/'
            for verdict, inp, exp, out in V.findall(head):
                tid = by_in.get(inp.strip())
                if tid is None or (sid, tid) not in TR.index:
                    rows.append(dict(sub_id=sid, kind=kind, test_id=tid, orig=verdict, ours=None, ws_only=None))
                    continue
                ours = TR.loc[(sid, tid), 'status']
                rows.append(dict(sub_id=sid, kind=kind, test_id=tid, orig=verdict, ours=ours,
                                 ws_only=out.split() == exp.split() and out != exp))
D = pd.DataFrame(rows)
D['orig_pass'] = D.orig == 'ACCEPTED'
D['ours_pass'] = D.ours == 'PASS'
m = D[D.ours.notna()]
print(f'verdict đọc được: {len(D)}, ghép được test: {len(m)} ({len(m) / len(D):.1%})')
print('verdict gốc:', D.orig.value_counts().to_dict())
agree = m.orig_pass == m.ours_pass
print(f'khớp PASS/FAIL: {agree.mean():.2%}')
lech = m[~agree]
print('lệch:', len(lech), '| gốc FAIL & ta PASS:', ((~lech.orig_pass) & lech.ours_pass).sum(),
      '(trong đó chỉ khác khoảng trắng:', int(lech.ws_only.fillna(False).sum()), ') | gốc PASS & ta FAIL:',
      (lech.orig_pass & ~lech.ours_pass).sum())
print(lech.groupby(['orig', 'ours']).size().to_string())
ws = lech.ws_only.fillna(False)
print(f'khớp sau khi bỏ lệch do khoảng trắng: {(agree | (m.ws_only.fillna(False) & m.ours_pass)).mean():.2%}')
s = m.groupby(['sub_id', 'kind']).agg(all_orig=('orig_pass', 'all'), all_ours=('ours_pass', 'all')).reset_index()
for k in ('correct', 'buggy'):
    x = s[s.kind == k]
    print(f'{k}: pass hết test theo gốc {x.all_orig.mean():.1%}, theo ta {x.all_ours.mean():.1%}')
D.to_csv(config.TABLES / 'p1_8_itsp_validation.csv', index=False)
print(lech[~ws].head(15).to_string())
