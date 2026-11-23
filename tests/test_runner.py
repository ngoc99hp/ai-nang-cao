import pytest
import runner

HEAD = '#include <stdio.h>\nint main(){int n,i,x,s=0;scanf("%d",&n);'
BODY = {
    'correct'      : 'for(i=0;i<n;i++){scanf("%d",&x);s+=x;} printf("%d\\n",s); return 0;}',
    'off_by_one'   : 'for(i=1;i<n;i++){scanf("%d",&x);s+=x;} printf("%d\\n",s); return 0;}',
    'infinite_loop': 'while(1){} return 0;}',
    'segfault'     : 'int *p=0; *p=1; return 0;}',
    'output_flood' : 'while(1) printf("x\\n"); return 0;}',
    'syntax_error' : 'printf("%d\\n",s) return 0;}',
    'nonzero_exit' : 'for(i=0;i<n;i++){scanf("%d",&x);s+=x;} printf("%d\\n",s); return 3;}',
}
EXPECTED = {
    'correct': 'PASS', 'off_by_one': 'FAIL', 'infinite_loop': 'TIMEOUT',
    'segfault': 'CRASH', 'output_flood': 'OUTPUT_LIMIT',
    'syntax_error': 'COMPILE_ERROR', 'nonzero_exit': 'PASS',
}


@pytest.fixture
def io_files(tmp_path):
    (tmp_path / 'in.txt').write_text('3\n1 2 3\n')
    (tmp_path / 'out.txt').write_text('6\n')
    return tmp_path


def test_all_statuses(io_files):
    subs = []
    for name, body in BODY.items():
        src = io_files / f'{name}.c'
        src.write_text(HEAD + body)
        subs.append((name, src))
    rows = runner.run_batch(subs, [('t0', io_files / 'in.txt', io_files / 'out.txt')],
                            io_files / 'bin')
    got = {r['sub_id']: r['status'] for r in rows}
    assert got == EXPECTED


def test_no_false_timeout_under_load(io_files):
    """Bài đúng không được TIMEOUT oan khi chạy song song với bài lặp vô hạn."""
    subs = []
    for i in range(12):
        kind = 'infinite_loop' if i < 3 else 'correct'
        src = io_files / f's{i:02d}_{kind}.c'
        src.write_text(HEAD + BODY[kind])
        subs.append((src.stem, src))
    rows = runner.run_batch(subs, [('t0', io_files / 'in.txt', io_files / 'out.txt')],
                            io_files / 'bin', max_workers=8)
    for r in rows:
        expected = 'TIMEOUT' if r['sub_id'].endswith('infinite_loop') else 'PASS'
        assert r['status'] == expected, r


MEDIAN = '#include <stdio.h>\nint main(){int a,b,c;scanf("%d%d%d",&a,&b,&c);printf(FMT);return RC;}'
MED_OUT = '"Please enter 3 numbers separated by spaces > %d is the median\\n",b'


@pytest.mark.parametrize('fmt, rc, strict, sem', [
    (MED_OUT, 0, 'PASS', 'PASS'),
    (MED_OUT, 3, 'PASS', 'PASS'),                                  # exit code không tính (P1.6)
    (MED_OUT.replace('is the', 'IS the'), 0, 'FAIL', 'PASS'),      # format_only
    (MED_OUT.replace(',b', ',a'), 0, 'FAIL', 'FAIL'),              # sai ngữ nghĩa
])
def test_problem_mode(tmp_path, fmt, rc, strict, sem):
    (tmp_path / 'in.txt').write_text('1 2 3\n')
    (tmp_path / 'out.txt').write_text('Please enter 3 numbers separated by spaces > 2 is the median\n')
    src = tmp_path / 'm.c'
    src.write_text(MEDIAN.replace('FMT', fmt).replace('RC', str(rc)))
    [row] = runner.run_batch([('m', src)], [('t0', tmp_path / 'in.txt', tmp_path / 'out.txt')],
                             tmp_path / 'bin', problem='median')
    assert (row['status'], row['status_sem'], row['returncode']) == (strict, sem, rc)


def test_uninit_reproducible(tmp_path):
    """GCC_FLAGS có -ftrivial-auto-var-init=zero → biến chưa khởi tạo luôn = 0."""
    (tmp_path / 'in.txt').write_text('')
    (tmp_path / 'out.txt').write_text('0\n')
    src = tmp_path / 'u.c'
    src.write_text('#include <stdio.h>\nint main(){int s; for(int i=0;i<0;i++) s=i; printf("%d\\n", s);}')
    rows = runner.run_batch([('u', src)], [('t0', tmp_path / 'in.txt', tmp_path / 'out.txt')], tmp_path / 'bin')
    assert rows[0]['status'] == 'PASS', rows


def test_no_orphan_processes(io_files):
    """Tiến trình con của bài nộp bị diệt sau khi chạy (cả khi cha đã thoát)."""
    import subprocess
    src = io_files / 'orphan.c'
    src.write_text('#include <unistd.h>\n#include <stdio.h>\n'
                   'int main(){ if(fork()==0){ execlp("sleep","sleep","77",(char*)0); } printf("6\\n"); return 0; }')
    rows = runner.run_batch([('orphan', src)], [('t0', io_files / 'in.txt', io_files / 'out.txt')],
                            io_files / 'bin')
    assert rows[0]['status'] == 'PASS'
    ps = subprocess.run(['pgrep', '-f', 'sleep 77'], capture_output=True, text=True).stdout
    assert ps.strip() == '', f'còn tiến trình mồ côi: {ps}'
