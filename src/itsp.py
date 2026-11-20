"""Parser cho ITSP (Yi et al., FSE 2017): dataset/Lab-*/<pid>/<prog>_{buggy,correct}.c, test ở dataset/test.

Mỗi bài sai có bản sửa đúng của chính sinh viên → tham chiếu own_fix cho nhóm D.
problem = 'itsp_<pid>'; sub_id = 'itsp_<pid>_<prog>_<buggy|correct>'.
"""
import re

import pandas as pd

import config

ROOT = config.RAW / 'itsp' / 'dataset'
TEST = ROOT / 'test'


def problems() -> list[tuple[str, str]]:
    """→ [(lab, pid), ...]"""
    return sorted((lab.name, p.name) for lab in ROOT.glob('Lab-*') for p in lab.iterdir() if p.is_dir())


def tests_of(pid: str) -> list[tuple]:
    """→ [(test_id 't<N>', in_path, out_path)] theo thứ tự N."""
    out = []
    for f in TEST.glob(f'in.{pid}.*.txt'):
        n = int(f.name.split('.')[2])
        out.append((f't{n}', f, TEST / f'out.{pid}.{n}.txt'))
    return sorted(out, key=lambda t: int(t[0][1:]))


def pairs() -> pd.DataFrame:
    """Mỗi dòng: 1 cặp buggy/correct (bỏ cặp thiếu một bên)."""
    rows = []
    for lab, pid in problems():
        d = ROOT / lab / pid
        for b in sorted(d.glob('*_buggy.c')):
            prog = b.name[:-len('_buggy.c')]
            c = d / f'{prog}_correct.c'
            if not c.exists() or not re.fullmatch(r'\w+', prog):
                continue
            rows.append(dict(lab=lab, pid=pid, prog=prog, problem=f'itsp_{pid}',
                             buggy_id=f'itsp_{pid}_{prog}_buggy', correct_id=f'itsp_{pid}_{prog}_correct',
                             buggy_path=str(b.relative_to(config.ROOT)),
                             correct_path=str(c.relative_to(config.ROOT))))
    return pd.DataFrame(rows)
