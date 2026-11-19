"""Lời giải tự viết (bench/) + truy cập test thống nhất cho mọi problem (IntroClass hoặc bench)."""
from pathlib import Path

import config
import introclass as ic

BENCH = config.ROOT / 'bench'
SYNTH_PROBLEMS = [*config.PROBLEMS, 'average']        # average: bài phụ cho M4 (DP2)


def tests_of(problem: str) -> list[tuple[str, Path, Path]]:
    if (ic.LOCAL / problem / 'tests').is_dir():
        return ic.tests_of(problem)
    d = BENCH / problem / 'tests' / 'blackbox'
    nums = sorted(int(f.stem) for f in d.glob('*.in'))
    return [(f'bb{n}', d / f'{n}.in', d / f'{n}.out') for n in nums]


def sources(problem: str) -> list[tuple[str, Path]]:
    """[(sub_id, path)] các lời giải tự viết."""
    return [(f'bench_{problem}_{f.stem}', f) for f in sorted((BENCH / problem).glob('*.c'))]
