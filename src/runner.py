"""Compile & chạy bài C của sinh viên an toàn, có giới hạn tài nguyên.

Status:
  PASS / FAIL    : chạy xong, so khớp hoặc không khớp output mong đợi
  TIMEOUT        : vượt CPU time (thường do vòng lặp vô hạn)
  CRASH          : bị signal kill (segfault, abort, FPE...)
  OUTPUT_LIMIT   : in quá MAX_OUTPUT_BYTES
  COMPILE_ERROR  : không biên dịch được (chỉ xuất hiện trong run_batch)
"""
import math
import os
import signal
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import config

MAX_OUTPUT_BYTES = 1 << 20          # 1 MB
MAX_MEMORY_KB    = 256 * 1024       # 256 MB
WALL_FACTOR      = 3                # wall timeout = CPU limit * 3 (lưới an toàn)
DEFAULT_WORKERS  = (os.cpu_count() or 2) * 2

# Giới hạn đặt bằng ulimit trong bash rồi exec -> an toàn với thread (không dùng preexec_fn)
_LIMIT_SH = 'ulimit -t {cpu} -f {fsize} -v {mem} -c 0; exec "$0"'

_TIMEOUT_SIGNALS = {-signal.SIGXCPU, -signal.SIGKILL}


def compile_c(src, exe) -> tuple[bool, str]:
    """Trả về (thành_công, stderr rút gọn)."""
    cmd = ['gcc', *config.GCC_FLAGS, str(src), '-o', str(exe), *config.GCC_LIBS]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=config.COMPILE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return False, 'COMPILE_TIMEOUT'
    return r.returncode == 0, r.stderr[-2000:]


@dataclass
class RunResult:
    status: str
    stdout: str
    returncode: int | None


def run_once(exe, input_path, cpu_limit: float | None = None) -> RunResult:
    """Chạy exe với stdin từ file; chưa so sánh output."""
    cpu = math.ceil(cpu_limit or config.RUN_TIMEOUT)
    sh = _LIMIT_SH.format(cpu=cpu, fsize=MAX_OUTPUT_BYTES // 1024, mem=MAX_MEMORY_KB)
    with open(input_path, 'rb') as fin, tempfile.TemporaryFile() as fout:
        try:
            p = subprocess.run(['bash', '-c', sh, str(Path(exe).resolve())],
                               stdin=fin, stdout=fout, stderr=subprocess.DEVNULL,
                               timeout=cpu * WALL_FACTOR)
        except subprocess.TimeoutExpired:
            return RunResult('TIMEOUT', '', None)
        fout.seek(0)
        out = fout.read(MAX_OUTPUT_BYTES).decode('utf-8', errors='replace')

    rc = p.returncode
    if rc in _TIMEOUT_SIGNALS:
        return RunResult('TIMEOUT', out, rc)
    if rc == -signal.SIGXFSZ:
        return RunResult('OUTPUT_LIMIT', out, rc)
    if rc < 0:
        return RunResult('CRASH', out, rc)
    return RunResult('OK', out, rc)


def normalize_output(s: str) -> list[str]:
    """Chuẩn hóa tối thiểu. Sẽ được thay bằng src/normalize.py ở Phase 1 (theo DP0)."""
    return s.split()


def judge(exe, input_path, expected_path, cpu_limit: float | None = None) -> RunResult:
    r = run_once(exe, input_path, cpu_limit)
    if r.status != 'OK':
        return r
    expected = Path(expected_path).read_text(errors='replace')
    r.status = 'PASS' if normalize_output(r.stdout) == normalize_output(expected) else 'FAIL'
    return r


def run_batch(subs, tests, workdir, max_workers: int | None = None) -> list[dict]:
    """
    subs : [(sub_id, src_path), ...]   sub_id phải hợp lệ làm tên file
    tests: [(test_id, in_path, out_path), ...]
    Trả về list dict khớp schema test_results: sub_id, test_id, status, stdout.
    Song song hóa ở mức (bài × test) để cân bằng tải.
    """
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    max_workers = max_workers or DEFAULT_WORKERS

    def _compile(item):
        sub_id, src = item
        exe = workdir / f'{sub_id}.out'
        ok, err = compile_c(src, exe)
        return sub_id, (exe if ok else None), err

    with ThreadPoolExecutor(max_workers) as ex:
        compiled = list(ex.map(_compile, subs))

    rows, jobs = [], []
    for sub_id, exe, err in compiled:
        if exe is None:
            rows.append(dict(sub_id=sub_id, test_id=None, status='COMPILE_ERROR', stdout=err))
        else:
            jobs.extend((sub_id, exe, t) for t in tests)

    def _run(job):
        sub_id, exe, (tid, inp, exp) = job
        r = judge(exe, inp, exp)
        return dict(sub_id=sub_id, test_id=tid, status=r.status, stdout=r.stdout[:2000])

    with ThreadPoolExecutor(max_workers) as ex:
        rows.extend(ex.map(_run, jobs))
    return rows
