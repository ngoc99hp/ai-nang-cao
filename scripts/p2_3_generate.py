"""P2.3: Sinh mutant có nhãn (M1–M8), chạy test, kiểm định, chọn mẫu.

Nguồn bản đúng: IntroClass (pass toàn bộ test semantic, unique, không phụ thuộc UB) + bench/.
Mutant hợp lệ: compile được, fail ≥ 1 test (semantic), hành vi khác bản gốc.
Chọn ≤ MAX_PER_LABEL mutant đơn / nhãn / bài (xoay vòng theo nguồn) + ~15% mutant kép.
Ghi data/interim/synthetic/{src,submissions,test_results,mutants}/ và results/tables/p2_mutants.csv.
Chạy: docker exec -d aai-lab bash -c 'python scripts/p2_3_generate.py > work/logs/p2_3.log 2>&1'
"""
import random
import sys
import time
from collections import defaultdict
from itertools import zip_longest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd

import ast_utils
import bench
import config
import mutators as mu
import runner
import schema

MAX_PER_LABEL = 50
CAND_PER_LABEL = 150          # ứng viên đơn / nhãn (nhiều mutant M7 tương đương → cần dư)
COMBO_FRAC = 0.15
CAND_COMBO = 120
OUT = config.INTERIM / 'synthetic'


def round_robin(groups: dict, rng) -> list:
    """Trộn các nhóm (theo nguồn) rồi lấy xoay vòng → không nguồn nào áp đảo."""
    lists = [rng.sample(v, len(v)) for _, v in sorted(groups.items())]
    rng.shuffle(lists)
    return [x for tup in zip_longest(*lists) for x in tup if x is not None]


def sources_of(p):
    out = []
    if p in config.PROBLEMS:
        f = schema.load(config.INTERIM / 'flags' / f'{p}.parquet', schema.SUB_FLAGS)
        sub = schema.load(config.INTERIM / 'submissions' / f'{p}.parquet', schema.SUBMISSIONS).set_index('sub_id')
        ok = f[f.compiled & (f.n_fail_sem == 0) & (f.dup_of == f.sub_id) & ~f.uninit_dependent]
        out += [(s, config.ROOT / sub.loc[s, 'code_path']) for s in ok.sub_id]
    return out + bench.sources(p)


def main(problems):
    summary = []
    for p in problems:
        if (OUT / 'mutants' / f'{p}.parquet').exists():
            print(f'[{p}] đã có, bỏ qua', flush=True)
            continue
        t0 = time.time()
        rng = random.Random(config.SEED)
        srcs = sources_of(p)
        code = {s: f.read_bytes() for s, f in srcs}
        seen = {ast_utils.code_hash(c) for c in code.values()}

        # --- ứng viên đơn, theo nhãn, xoay vòng theo nguồn
        by_label = defaultdict(lambda: defaultdict(list))
        all_muts = {}
        for s, c in code.items():
            ms = mu.find_all(c)
            all_muts[s] = ms
            for m in ms:
                by_label[m.label][s].append((m,))
        cands = []
        for lab in sorted(by_label):
            cands += [(lab, s_m) for s_m in round_robin(
                {s: [(s, ms) for ms in v] for s, v in by_label[lab].items()}, rng)][:CAND_PER_LABEL * 2]
        # --- ứng viên kép: 2 nhãn khác nhau, cùng nguồn, không chồng lấn
        combos = []
        for s, ms in all_muts.items():
            for _ in range(20):
                if len({m.label for m in ms}) < 2:
                    break
                a, b = rng.sample(ms, 2)
                if a.label != b.label and not mu.overlaps(a, b):
                    combos.append((s, (a, b)))
        combos = rng.sample(combos, min(len(combos), CAND_COMBO * 3))

        # --- hiện thực hóa, khử trùng theo code_hash
        rows, per_label_n = [], defaultdict(int)
        src_dir = OUT / 'src' / p
        src_dir.mkdir(parents=True, exist_ok=True)

        def add(s, muts, cap_key, cap):
            if per_label_n[cap_key] >= cap:
                return
            try:
                new = mu.apply(code[s], muts)
            except ValueError:
                return
            h = ast_utils.code_hash(new)
            if h in seen:
                return
            seen.add(h)
            per_label_n[cap_key] += 1
            sid = f'syn_{p}_{len(rows):05d}'
            path = src_dir / f'{sid}.c'
            path.write_bytes(new)
            rows.append(dict(sub_id=sid, problem=p, parent_id=s, label_true=mu.label_of(muts),
                             ops='+'.join(m.op for m in muts), desc=' | '.join(m.desc for m in muts),
                             line=muts[0].line, code_path=str(path.relative_to(config.ROOT))))

        for lab, (s, muts) in cands:
            add(s, muts, lab, CAND_PER_LABEL)
        for s, muts in combos:
            add(s, list(muts), 'combo', CAND_COMBO)
        M = pd.DataFrame(rows)
        print(f'[{p}] {len(srcs)} nguồn, {len(M)} ứng viên: {M.label_true.str.len().gt(2).sum()} kép', flush=True)

        # --- chạy: ứng viên + bản gốc bench (IntroClass gốc đã có kết quả từ P1.6)
        tests = bench.tests_of(p)
        run_subs = [(r.sub_id, config.ROOT / r.code_path) for r in M.itertuples()] + bench.sources(p)
        tr = pd.DataFrame(runner.run_batch(run_subs, tests, config.WORK / 'bin_syn' / p, problem=p)).assign(problem=p)
        if p in config.PROBLEMS:
            orig = schema.load(config.INTERIM / 'test_results' / f'{p}.parquet', schema.TEST_RESULTS)
            orig = pd.concat([orig[orig.sub_id.isin(code)], tr[tr.sub_id.str.startswith('bench_')]])
        else:
            orig = tr[tr.sub_id.str.startswith('bench_')]
        tr = tr[tr.sub_id.str.startswith('syn_')]

        # --- kiểm định
        ce = set(tr.loc[tr.status == 'COMPILE_ERROR', 'sub_id'])
        t = tr[tr.test_id.notna()]
        nfail = t.groupby('sub_id').status_sem.apply(lambda s: int((s != 'PASS').sum()))
        o = orig.set_index(['sub_id', 'test_id'])[['status_sem', 'stdout']]
        tt = t.merge(M[['sub_id', 'parent_id']], on='sub_id')
        po = o.reindex(list(zip(tt.parent_id, tt.test_id)))
        tt['diff'] = (tt.status_sem.values != po.status_sem.values) | (tt.stdout.values != po.stdout.values)
        differs = tt.groupby('sub_id')['diff'].any()
        M['compiled'] = ~M.sub_id.isin(ce)
        M['n_fail_sem'] = M.sub_id.map(nfail).fillna(len(tests)).astype(int)
        M['differs'] = M.sub_id.map(differs).astype('boolean').fillna(True).astype(bool)
        M['valid'] = M.compiled & (M.n_fail_sem > 0) & M.differs

        # --- chọn: đơn ≤ MAX_PER_LABEL / nhãn (xoay vòng nguồn), kép ≈ 15% tổng
        sel = []
        V = M[M.valid]
        for lab, g in V[~V.label_true.str.contains(r'\+')].groupby('label_true'):
            grp = {s: list(gg.sub_id) for s, gg in g.groupby('parent_id')}
            sel += round_robin(grp, rng)[:MAX_PER_LABEL]
        n_combo = round(len(sel) * COMBO_FRAC / (1 - COMBO_FRAC))
        vc = V[V.label_true.str.contains(r'\+')]
        sel += round_robin({s: list(gg.sub_id) for s, gg in vc.groupby('parent_id')}, rng)[:n_combo]
        M['selected'] = M.sub_id.isin(sel)

        schema.save(M, schema.MUTANTS, OUT / 'mutants' / f'{p}.parquet')
        S = M[M.selected].assign(source='synthetic', is_correct=False)
        schema.save(S, schema.SUBMISSIONS, OUT / 'submissions' / f'{p}.parquet')
        schema.save(tr[tr.sub_id.isin(sel)], schema.TEST_RESULTS, OUT / 'test_results' / f'{p}.parquet')
        for lab, g in M.groupby('label_true'):
            summary.append(dict(problem=p, label=lab, candidates=len(g), compiled=int(g.compiled.sum()),
                                fail_ge1=int((g.compiled & (g.n_fail_sem > 0)).sum()),
                                valid=int(g.valid.sum()), selected=int(g.selected.sum()),
                                parents=g[g.selected].parent_id.nunique()))
        print(f'[{p}] xong {time.time() - t0:.0f}s, chọn {len(sel)} '
              f'({M[M.selected].label_true.value_counts().to_dict()})', flush=True)

    if summary:
        f = config.TABLES / 'p2_mutants.csv'
        old = pd.read_csv(f) if f.exists() else pd.DataFrame()
        pd.concat([old, pd.DataFrame(summary)]).drop_duplicates(['problem', 'label'], keep='last') \
            .to_csv(f, index=False)
    print('DONE', flush=True)


if __name__ == '__main__':
    main(sys.argv[1:] or bench.SYNTH_PROBLEMS)
