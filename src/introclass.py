"""Parser cho dataset IntroClass (data/raw/introclass, chỉ đọc).

Quy ước:
  sub_id  = f'ic_{problem}_{repo[:12]}_{revision}'   (revision = tên thư mục '000', '001', ...)
  test_id = 'bb<N>' / 'wb<N>'  với N = số file tests/{blackbox,whitebox}/N.{in,out}
  metadata.json: pass/fail ghi trực tiếp số file test (chuỗi '5'), KHÔNG phải pN/nN.
  defect-classification.json: revision dạng 'N_<commit sha>' ↔ thư mục f'{N:03d}',
                              sha == metadata.json['revision'].
"""
import json
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

import config

LOCAL = config.RAW / 'introclass'
SUITES = {'bb': 'blackbox', 'wb': 'whitebox'}
_SH_LINE = re.compile(r'^([pn])(\d+)\).*?tests/(blackbox|whitebox)/(\d+)\.out', re.M)


def problems() -> list[str]:
    return sorted(p.name for p in LOCAL.iterdir() if p.is_dir() and (p / 'tests').is_dir())


def sub_id(problem: str, repo: str, revision: str) -> str:
    return f'ic_{problem}_{repo[:12]}_{revision}'


def tests_of(problem: str) -> list[tuple[str, Path, Path]]:
    """[(test_id, in_path, out_path)] sắp theo suite rồi số."""
    out = []
    for pre, suite in SUITES.items():
        d = LOCAL / problem / 'tests' / suite
        nums = sorted(int(f.stem) for f in d.glob('*.in'))
        out += [(f'{pre}{n}', d / f'{n}.in', d / f'{n}.out') for n in nums]
    return out


def versions(problem: str) -> list[Path]:
    root = LOCAL / problem
    return sorted(v for r in root.iterdir() if r.is_dir() and r.name != 'tests'
                  for v in r.iterdir() if v.is_dir())


def parse_test_sh(path: Path) -> dict[str, str]:
    """{'p1': 'bb5', 'n1': 'bb3', ...} từ blackbox_test.sh / whitebox_test.sh."""
    return {f'{pn}{i}': f'{suite[0]}b{num}'
            for pn, i, suite, num in _SH_LINE.findall(path.read_text())}


@lru_cache(maxsize=None)
def _unique_defects(problem: str) -> frozenset:
    pm = json.loads((LOCAL / problem / 'program-metadata.json').read_text())
    return frozenset((u['repo'], u['revision']) for u in pm['uniqueDefects'])


@lru_cache(maxsize=1)
def _bugclasses() -> dict:
    """(program, repo, '00N') -> list bugclasses; kiểm tra sha khớp metadata."""
    dc = json.loads((LOCAL / 'defect-classification.json').read_text())
    out = {}
    for d in dc:
        n, sha = d['revision'].split('_', 1)
        out[(d['program'], d['repo'], f'{int(n):03d}')] = (sha, d['bugclasses'], d['isReferenceDefect'])
    return out


def load_versions(problem: str) -> pd.DataFrame:
    """Một dòng / phiên bản: các cột của schema.SUBMISSIONS + metadata phụ trợ.

    is_correct lấy theo metadata.json của dataset (pass toàn bộ bb + wb);
    Bước 1.6 sẽ đối chiếu với kết quả runner.
    """
    tids = {t for t, _, _ in tests_of(problem)}
    bc = _bugclasses()
    rows = []
    for v in versions(problem):
        repo, rev = v.parent.name, v.name
        m = json.loads((v / 'metadata.json').read_text())
        meta_fail = {f'{pre}{n}' for pre, s in SUITES.items() for n in m[s]['fail']}
        meta_pass = {f'{pre}{n}' for pre, s in SUITES.items() for n in m[s]['pass']}
        sha, classes, is_ref = bc.get((problem, repo, rev), (None, None, None))
        code = v / f'{problem}.c'
        rows.append(dict(
            sub_id=sub_id(problem, repo, rev), source='introclass', problem=problem,
            code_path=str(code.relative_to(config.ROOT)) if code.exists() else None,
            is_correct=not meta_fail, label_true=None,
            repo=repo, revision=rev, commit=m['revision'],
            nondeterministic=bool(m.get('nondeterministic')),
            is_unique=(repo, rev) in _unique_defects(problem),
            meta_pass=sorted(meta_pass), meta_fail=sorted(meta_fail),
            meta_complete=(meta_pass | meta_fail) == tids and not (meta_pass & meta_fail),
            bugclasses=classes, is_reference_defect=is_ref,
            bc_sha_ok=(sha == m['revision']) if sha else None,
        ))
    return pd.DataFrame(rows)
