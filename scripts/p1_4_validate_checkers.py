"""P1.4: Kiểm định checker offline trên output đã ghi trong metadata.json.

- strict(recorded output) phải khớp pass/fail của metadata (kiểm port nguyên văn).
- Thống kê strict→semantic: format_only (strict FAIL, semantic PASS) và ngược lại (semantic FAIL, strict PASS).
Chỉ dùng phiên bản deterministic.
"""
import ast
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import introclass as ic
import normalize

stats = defaultdict(Counter)
examples = defaultdict(list)
for p in ic.problems():
    tests = {t: (i.read_text(), o.read_text()) for t, i, o in ic.tests_of(p)}
    for v in ic.versions(p):
        m = json.loads((v / 'metadata.json').read_text())
        if m.get('nondeterministic'):
            continue
        for pre, suite in ic.SUITES.items():
            meta_pass = set(m[suite]['pass'])
            for n, outs in m['output'][suite].items():
                if not outs:
                    stats[p]['no_output'] += 1
                    continue
                raw = outs[0]
                try:
                    out = ast.literal_eval(raw).decode('utf-8', errors='replace')
                except Exception:
                    out = str(raw)
                inp, exp = tests[f'{pre}{n}']
                s = normalize.check(p, out, exp, inp, 'strict')
                sem = normalize.check(p, out, exp, inp, 'semantic')
                mp = n in meta_pass
                stats[p]['n'] += 1
                stats[p]['strict==meta'] += (s == mp)
                stats[p]['format_only'] += (not s and sem)
                stats[p]['sem_stricter'] += (s and not sem)
                stats[p]['meta_fail'] += (not mp)
                key = 'sem_stricter' if (s and not sem) else 'mismatch' if s != mp else 'format_only' if (not s and sem) else None
                if key and len(examples[(p, key)]) < 3:
                    examples[(p, key)].append((f'{pre}{n}', exp, out[:200]))

print(f'{"problem":10s} {"outputs":>7s} {"strict==meta":>13s} {"meta_fail":>9s} {"format_only":>11s} {"sem_stricter":>12s}')
for p, c in stats.items():
    print(f'{p:10s} {c["n"]:7d} {c["strict==meta"] / c["n"]:12.2%} {c["meta_fail"]:9d} {c["format_only"]:11d} {c["sem_stricter"]:12d}'
          + (f'  (no_output {c["no_output"]})' if c['no_output'] else ''))
for (p, key), ex in sorted(examples.items()):
    print(f'\n--- {p} / {key}')
    for t, exp, out in ex:
        print(f'  {t}: exp={exp!r}\n       out={out!r}')
