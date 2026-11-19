"""P1.3: Đọc logic chấm của IntroClass + thống kê metadata."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import config

LOCAL = config.RAW / 'introclass'
problems = sorted(p.name for p in LOCAL.iterdir() if p.is_dir() and (p / 'tests').is_dir())


def versions_of(prob):
    return sorted(v for r in (LOCAL / prob).iterdir() if r.is_dir() and r.name != 'tests'
                  for v in r.iterdir() if v.is_dir())


def section(t):
    print(f'\n{"=" * 70}\n{t}\n{"=" * 70}')


section('1. bin/genprog_tests.py')
print((LOCAL / 'bin' / 'genprog_tests.py').read_text())

ver = versions_of('checksum')[0]
section(f'2. metadata.json pass/fail: {ver.relative_to(LOCAL)}')
m = json.loads((ver / 'metadata.json').read_text())
print('blackbox:', m['blackbox'])
print('whitebox:', m['whitebox'])
print('blackbox_test.sh:\n' + (ver / 'blackbox_test.sh').read_text())

section('3. defect-classification.json: phân bố')
dc = json.loads((LOCAL / 'defect-classification.json').read_text())
print('Số nhãn / phiên bản :', dict(Counter(len(d['bugclasses']) for d in dc)))
print('isReferenceDefect   :', dict(Counter(d['isReferenceDefect'] for d in dc)))
for c, n in Counter(c for d in dc for c in d['bugclasses']).most_common():
    print(f'  {n:5d}  {c}')

section('4. Thống kê theo bài')
print(f'{"problem":10s} {"vers":>5s} {"uniq":>5s} {"nondet":>7s} {"bb_all_pass":>12s} {"wb_all_pass":>12s}')
for p in problems:
    pm = json.loads((LOCAL / p / 'program-metadata.json').read_text())
    vs = versions_of(p)
    nondet = bb_ok = wb_ok = 0
    for v in vs:
        mm = json.loads((v / 'metadata.json').read_text())
        nondet += bool(mm.get('nondeterministic'))
        bb_ok += len(mm['blackbox']['fail']) == 0
        wb_ok += len(mm['whitebox']['fail']) == 0
    print(f'{p:10s} {len(vs):5d} {pm["nbUniqueDefects"]:5d} {nondet:7d} {bb_ok:12d} {wb_ok:12d}')
