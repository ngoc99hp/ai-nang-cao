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
