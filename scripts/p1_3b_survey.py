"""P1.3b: Thống kê bổ sung cho DP0/DP1 — quan hệ bugclasses ↔ test fail, isReferenceDefect, số bài sai."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import config

LOCAL = config.RAW / 'introclass'
dc = json.loads((LOCAL / 'defect-classification.json').read_text())

rows = []
for d in dc:
    # defect-classification dùng revision dạng 'N_<commit sha>' ↔ thư mục '{N:03d}', sha = metadata['revision']
    n, sha = d['revision'].split('_', 1)
    v = LOCAL / d['program'] / d['repo'] / f'{int(n):03d}'
    m = json.loads((v / 'metadata.json').read_text())
    assert m['revision'] == sha, (v, sha)
    nf = len(m['blackbox']['fail']) + len(m['whitebox']['fail'])
    nt = nf + len(m['blackbox']['pass']) + len(m['whitebox']['pass'])
    rows.append(dict(d, dir=v.name, nfail=nf, ntest=nt, nondet=bool(m.get('nondeterministic')),
                     has_c=(v / f"{d['program']}.c").exists()))

print('len(bugclasses) == số test fail:', Counter(len(r['bugclasses']) == r['nfail'] for r in rows))
print('isReferenceDefect × (nfail==0):', Counter((r['isReferenceDefect'], r['nfail'] == 0) for r in rows))
print('"human fix - not a defect" × nfail==0:',
      Counter(r['nfail'] == 0 for r in rows if 'human fix - not a defect' in r['bugclasses']))

pm = {p: {(u['repo'], u['revision']) for u in
          json.loads((LOCAL / p / 'program-metadata.json').read_text())['uniqueDefects']}
      for p in sorted({r['program'] for r in rows})}

print(f'\n{"problem":10s} {"vers":>5s} {"allpass":>7s} {"fail>=1":>7s} {"&det":>5s} {"&det&uniq":>9s} {"failALL&det":>11s}')
for p in sorted(pm):
    R = [r for r in rows if r['program'] == p]
    bad = [r for r in R if r['nfail'] > 0]
    det = [r for r in bad if not r['nondet']]
    uq = [r for r in det if (r['repo'], r['dir']) in pm[p]]
    fall = [r for r in det if r['nfail'] == r['ntest']]
    print(f'{p:10s} {len(R):5d} {len(R)-len(bad):7d} {len(bad):7d} {len(det):5d} {len(uq):9d} {len(fall):11d}')

# Mẫu output đã ghi nhận: so expected vs output thực của 1 test fail (để thấy kiểu lỗi định dạng)
print('\nMẫu output fail (test đầu tiên bị fail của 2 phiên bản deterministic / bài):')
for p in sorted(pm):
    shown = 0
    for r in rows:
        if r['program'] != p or r['nondet'] or r['nfail'] == 0 or shown >= 2:
            continue
        v = LOCAL / p / r['repo'] / r['dir']
        m = json.loads((v / 'metadata.json').read_text())
        if not m['blackbox']['fail']:
            continue
        t = m['blackbox']['fail'][0]
        exp = (LOCAL / p / 'tests' / 'blackbox' / f'{t}.out').read_text()
        got = m['output']['blackbox'].get(t, ['?'])
        print(f'  [{p} bb{t}] in ={(LOCAL / p / "tests/blackbox" / f"{t}.in").read_text()!r}')
        print(f'           exp={exp!r}\n           got={str(got[0])[:160]!r}')
        shown += 1
