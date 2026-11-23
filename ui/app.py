"""Demo: Cụm hóa quan niệm sai lầm (misconception) trong bài lập trình C — giao diện Streamlit.

Chỉ đọc /data/results (dashboard.json, hình) và /data/demo (bài mẫu); bài nộp được ghi vào /data/queue/in,
worker trong container aai-lab (không mạng) chấm và trả /data/queue/out. Container này không chạy code C.
"""
import json
import os
import re
import time
import uuid
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path('/data')
RES, QUEUE, SAMPLES = DATA / 'results', DATA / 'queue', DATA / 'demo' / 'samples'
FIG = RES / 'figures'
PNAME = {'digits': 'digits — tách chữ số', 'grade': 'grade — xếp loại điểm',
         'median': 'median — số trung vị', 'smallest': 'smallest — số nhỏ nhất'}

# Diễn giải các thuộc tính OAV thường gặp (cho người xem không cần đọc tên kỹ thuật)
GLOSS = {
    'D:diff.cmp_if': 'Đổi phép so sánh trong điều kiện if',
    'D:diff.cmp_loop': 'Đổi phép so sánh ở điều kiện vòng lặp',
    'D:diff.cmp_kind': 'Kiểu đổi phép so sánh (strictness: < ↔ <=; reversed: < ↔ >)',
    'D:diff.eq_assign': 'Nhầm = và ==',
    'D:diff.logic_op': 'Đổi toán tử logic && / ||',
    'D:diff.loop_init': 'Khởi tạo biến vòng lặp khác',
    'D:diff.init_value': 'Giá trị khởi tạo khác',
    'D:diff.literal_other': 'Hằng số khác',
    'D:diff.ptr_missing': 'Thiếu con trỏ / toán tử &, *',
    'D:diff.ptr_extra': 'Thừa con trỏ / toán tử &, *',
    'D:diff.cast_missing': 'Thiếu ép kiểu',
    'D:diff.neg_missing': 'Thiếu xử lý số âm',
    'D:diff.neg_extra': 'Xử lý dấu âm thừa / sai chỗ',
    'D:diff.moved_into_loop': 'Câu lệnh bị đưa vào trong vòng lặp',
    'D:diff.moved_out_of_loop': 'Câu lệnh bị đưa ra ngoài vòng lặp',
    'D:diff.extra_break': 'Thừa break/return',
    'D:diff.missing_break': 'Thiếu break/return',
    'D:diff.extra_output': 'Thừa lệnh in',
    'D:diff.missing_output': 'Thiếu lệnh in (thiếu nhánh in kết quả)',
    'D:diff.var_changed': 'Dùng nhầm biến',
    'D:diff.arith_changed': 'Đổi phép toán số học',
    'D:diff.stmt_missing': 'Thiếu câu lệnh',
    'D:diff.stmt_extra': 'Thừa câu lệnh',
    'D:diff.size': 'Số token khác biệt so với bản đúng',
    'O:output.missing_answer': 'Không in ra đáp án',
    'O:output.multiple_answers': 'In nhiều đáp án',
    'O:output.off_by_one': 'Đáp án lệch 1',
    'O:output.output_zero': 'In ra 0',
    'O:output.wrong_input_elem': 'In một số trong input nhưng sai số',
    'O:output.not_input_elem': 'In số không có trong input',
    'O:output.sign_error': 'Sai dấu',
    'O:output.missing_items': 'Thiếu phần tử output',
    'O:output.extra_items': 'Thừa phần tử output',
    'O:output.missing_last': 'Thiếu phần tử cuối',
    'O:output.wrong_digit': 'Sai chữ số',
    'O:output.digits_reversed': 'Chữ số bị đảo thứ tự',
    'O:output.adjacent_grade': 'Xếp loại lệch 1 bậc',
    'O:output.far_grade': 'Xếp loại lệch nhiều bậc',
    'O:output.grade_too_low': 'Xếp loại thấp hơn đúng',
    'O:output.grade_too_high': 'Xếp loại cao hơn đúng',
    'O:output.timeout': 'Chạy quá thời gian',
    'O:output.crash': 'Chương trình bị lỗi khi chạy',
    'O:tests.fail_frac': 'Tỷ lệ test trượt',
    'O:tests_tie.fail': 'Trượt test có các giá trị bằng nhau',
    'O:tests_negative.fail': 'Trượt test có số âm',
    'O:tests_zero.fail': 'Trượt test có số 0',
    'O:tests_sorted.fail': 'Trượt test input đã sắp xếp',
    'O:tests_single_digit.fail': 'Trượt test số có 1 chữ số',
    'O:tests_inner_zero.fail': 'Trượt test số có chữ số 0 ở giữa',
    'O:tests_boundary.fail': 'Trượt test điểm đúng bằng ngưỡng',
    'O:tests_failing.fail': 'Trượt test điểm trượt',
    'O:tests_top.fail': 'Trượt test điểm cao nhất',
    'O:run.format_only_any': 'Có test chỉ sai định dạng',
    'A:condition.if_cmp': 'Kiểu so sánh trong if (strict <, > / nonstrict <=, >=)',
    'A:condition.assign_in_cond': 'Có phép gán trong điều kiện',
    'A:loop.cmp_op': 'Phép so sánh ở vòng lặp',
    'A:loop.output_in_loop': 'In bên trong vòng lặp',
    'A:loop.return_in_loop': 'return trong vòng lặp',
    'A:loop.break_in_loop': 'break trong vòng lặp',
    'A:function.has_ptr_param': 'Hàm có tham số con trỏ',
    'A:extremum.init': 'Cách khởi tạo biến min/max',
    'A:accumulator.init': 'Cách khởi tạo biến tích lũy',
    'A:negation.uses_abs': 'Dùng abs()',
    'A:negation.unary_minus': 'Dùng phép đổi dấu',
}
TAXO = {'M1': 'Biên vòng lặp', 'M2': 'Tham trị / tham chiếu', 'M3': 'Nhầm = và ==', 'M4': 'Chia nguyên',
        'M5': 'Khởi tạo biến', 'M6': 'Phạm vi return/break', 'M7': 'Biên so sánh trong if', 'M8': 'Số âm với % và /'}


def gloss(attr):
    return GLOSS.get(attr, attr)


def humanize_rule(text):
    """'NẾU [D:diff.cmp_if = T] VÀ ...' → thêm diễn giải tiếng Việt cho từng điều kiện."""
    m = re.match(r'NẾU (.*) THÌ (.*?) \[(.*)\]$', text)
    if not m:
        return text
    conds = re.findall(r'\[([^\]=]+?) = ([^\]]+)\]', m.group(1))
    parts = []
    for a, v in conds:
        v = v.strip()
        g = gloss(a.strip())
        parts.append(g if v == 'T' else f'KHÔNG {g[0].lower() + g[1:]}' if v == 'F' else f'{g} = {v}')
    return f'NẾU {" VÀ ".join(parts)} THÌ {m.group(2)}  ({m.group(3)})'


@st.cache_data(ttl=60)
def load_dash():
    return json.loads((RES / 'demo' / 'dashboard.json').read_text(encoding='utf-8'))


def img(name, caption=None):
    f = FIG / name
    if f.exists():
        st.image(str(f), caption=caption, use_container_width=True)


st.set_page_config(page_title='Misconception Clustering — Demo', page_icon='🧩', layout='wide')
D = load_dash()
st.title('Cụm hóa quan niệm sai lầm trong bài lập trình C')
st.caption('Đề tài 5 — AI nâng cao · OAV + K-modes (Hamming có trọng số) + ILA · dữ liệu IntroClass, ITSP, mutation')

tab_over, tab_gv, tab_sv, tab_exp = st.tabs(
    ['Tổng quan', 'Giảng viên: macro-feedback', 'Nộp bài: chẩn đoán lỗi', 'Thực nghiệm'])

# ------------------------------------------------------------------------------------------- Tổng quan
with tab_over:
    P = D['problems']
    c = st.columns(4)
    c[0].metric('Bài sai thật (IntroClass)', sum(v['n_sub'] for v in P.values()))
    c[1].metric('Sinh viên', sum(v['n_students'] for v in P.values()))
    c[2].metric('Cụm misconception', sum(v['k'] for v in P.values()))
    c[3].metric('Bài tập', len(P))
    st.subheader('Quy trình')
    st.markdown('''
| Bước | Làm gì | Kết quả |
|---|---|---|
| 1. Chấm bài an toàn | Compile + chạy bài C trong container cách ly (không mạng, giới hạn CPU/RAM) | Khớp kết quả chấm gốc 96–100% |
| 2. Hình thức hóa OAV | Mỗi bài sai → các bộ ba **Đối tượng – Thuộc tính – Giá trị**, 4 nhóm: **T** test trượt, **O** kiểu sai output, **A** cấu trúc code, **D** khác biệt so với bản đúng gần nhất | 40–60 thuộc tính / bài tập |
| 3. Gom cụm phi giám sát | K-modes, khoảng cách Hamming có trọng số (O 0.5, A 0.5, D 3) | Mỗi cụm ≈ một kiểu hiểu sai |
| 4. Sinh luật | ILA (tự cài đặt) học luật NẾU–THÌ mô tả từng cụm | Luật ngắn 1.5–2 điều kiện |
| 5. Macro-feedback | Bảng cho giảng viên: lỗi phổ biến, số sinh viên mắc, luật, bài minh họa | Tab "Giảng viên" |
''')
    st.subheader('Đánh giá')
    st.markdown('''
- **Dữ liệu sinh** (480 bài cấy lỗi có nhãn M1–M8): cụm khớp lỗi đã cấy, **ARI 0.48–0.73** (K-modes).
  Ablation: nhóm **D** là quyết định; chỉ dùng test/output: ARI 0.06–0.17.
- **Dữ liệu thật**: silhouette 0.25–0.50; nhiều cụm rõ ràng (vd. smallest: 36 SV dùng `<` thay vì `<=`).
- **ITSP** (602 cặp bài sai/bản tự sửa, nhãn gán tay cho 41 bài): ARI 0.20 — nhận ra được lỗi biên so sánh, biên vòng lặp,
  thiếu câu lệnh; chưa tách được nhầm biến / sai công thức.
''')

# ------------------------------------------------------------------------------------------- Giảng viên
with tab_gv:
    p = st.selectbox('Bài tập', list(D['problems']), format_func=PNAME.get, key='gv_p')
    info = D['problems'][p]
    st.markdown(f'**Đề:** {info["title"]}')
    c = st.columns(3)
    c[0].metric('Bài sai (đã khử trùng)', info['n_sub'])
    c[1].metric('Sinh viên', info['n_students'])
    c[2].metric('Số cụm', info['k'])
    tbl = pd.DataFrame([dict(Cụm=f'C{x["id"]}', Misconception=x['name'],
                             Taxonomy=', '.join(f'{t} ({TAXO.get(t, "")})' for t in x['taxonomy'].split('+'))
                             if x['taxonomy'] != '-' else '—',
                             **{'Sinh viên': x['n_students'], 'Bài': x['n_sub']}) for x in info['clusters']])
    st.dataframe(tbl, hide_index=True, use_container_width=True, column_config={
        'Sinh viên': st.column_config.ProgressColumn('Sinh viên', format='%d', min_value=0,
                                                     max_value=int(tbl['Sinh viên'].max()))})
    st.caption('Sắp theo số sinh viên mắc lỗi (một sinh viên có thể nộp nhiều phiên bản).')
    for x in info['clusters']:
        with st.expander(f'C{x["id"]} · {x["name"]} — {x["n_students"]} SV, {x["n_sub"]} bài'):
            st.markdown('**Đặc trưng nổi bật** (tỷ lệ trong cụm so với toàn bài):')
            st.dataframe(pd.DataFrame([dict(**{'Thuộc tính': gloss(f['attr']), 'Mã': f['attr'],
                                               'Giá trị': f['value'], 'Trong cụm': f['in_cluster'],
                                               'Toàn bài': f['overall']}) for f in x['features']]),
                         hide_index=True, use_container_width=True)
            st.markdown('**Luật ILA tiêu biểu:**')
            for r in x['rules'][:3]:
                st.markdown(f'- {humanize_rule(r)}')
                st.code(r, language=None)
            ex = x['examples'][0]
            st.markdown(f'**Bài minh họa** `{ex["sub_id"]}` — so với bản đúng `{ex["ref_id"]}` '
                        f'({"bản sửa của chính SV" if ex["ref_kind"] == "own_fix" else "bản đúng gần nhất"}):')
            st.code(ex['diff'][:3000] or '(không có khác biệt)', language='diff')
    st.subheader('Bản đồ nhiệt cụm × thuộc tính')
    img(f'heatmap_real_{p}.png')

# ------------------------------------------------------------------------------------------- Nộp bài
with tab_sv:
    st.markdown('Dán bài làm C (hoặc chọn bài mẫu). Hệ thống chấm test trong container cách ly, trích OAV, '
                'gán vào cụm misconception gần nhất và chỉ ra luật khớp.')
    p = st.selectbox('Bài tập', list(D['problems']), format_func=PNAME.get, key='sv_p')
    st.markdown(f'**Đề:** {D["problems"][p]["title"]}')
    samples = {f'Bài mẫu tự viết: {f.stem}': f.read_text() for f in sorted(SAMPLES.glob(f'{p}_*.c'))}
    for x in D['problems'][p]['clusters']:
        samples[f'Bài thật minh họa C{x["id"]}: {x["examples"][0]["sub_id"]}'] = x['examples'][0]['code']
    def _load_sample(p=p):
        st.session_state[f'code_{p}'] = samples.get(st.session_state[f'sample_{p}'], '')

    st.selectbox('Nạp bài mẫu', ['(tự nhập)'] + list(samples), key=f'sample_{p}', on_change=_load_sample)
    st.session_state.setdefault(f'code_{p}', '')
    code = st.text_area('Mã nguồn C', height=320, key=f'code_{p}')
    if st.button('Chấm và chẩn đoán', type='primary', disabled=not code.strip()):
        jid = uuid.uuid4().hex
        (QUEUE / 'in').mkdir(parents=True, exist_ok=True)
        tmp = QUEUE / 'in' / f'{jid}.tmp'
        tmp.write_text(json.dumps({'problem': p, 'code': code}, ensure_ascii=False))
        os.replace(tmp, QUEUE / 'in' / f'{jid}.json')
        out = QUEUE / 'out' / f'{jid}.json'
        with st.spinner('Đang chấm trong container cách ly...'):
            for _ in range(180):
                if out.exists():
                    break
                time.sleep(0.5)
        if not out.exists():
            st.error('Không nhận được kết quả sau 90 giây — worker trong aai-lab có đang chạy không?')
            st.stop()
        st.session_state['result'] = (p, json.loads(out.read_text(encoding='utf-8')))
        out.unlink(missing_ok=True)

    if 'result' in st.session_state and st.session_state['result'][0] == p:
        R = st.session_state['result'][1]
        names = {x['id']: x for x in D['problems'][p]['clusters']}
        st.divider()
        if R['status'] == 'compile_error':
            st.error('Lỗi biên dịch')
            st.code(R['stderr'], language=None)
        elif R['status'] == 'error':
            st.error(f'Lỗi xử lý: {R["message"]}')
        else:
            tests = pd.DataFrame(R['tests'])
            if R['status'] == 'correct':
                st.success(f'Bài đúng: pass {len(tests)}/{len(tests)} test — không phát hiện misconception.')
                if R.get('format_fail'):
                    st.info(f'{R["format_fail"]} test chỉ sai định dạng (câu chữ), không tính là sai.')
            else:
                cl = names[R['cluster']]
                c = st.columns([1, 3])
                c[0].metric('Test trượt', f'{R["n_fail"]}/{len(tests)}')
                c[1].markdown(f'#### Chẩn đoán: C{R["cluster"]} — {cl["name"]}')
                c[1].caption(f'{cl["n_students"]} sinh viên trong dữ liệu mắc lỗi này · '
                             f'khoảng cách tới cụm {R["distances"][str(R["cluster"])]:.3f} · '
                             f'chấm trong {R["elapsed"]} s')
                st.markdown('**Vì sao?** Bài nộp có chung các đặc trưng sau với cụm này:')
                st.markdown('\n'.join(f'- {gloss(w["attr"])} = `{w["value"]}`  ·  `{w["attr"]}`' for w in R['why']))
                own = [r for r in R['rules'] if r['cls'] == R['cluster']]
                other = [r for r in R['rules'] if r['cls'] != R['cluster']]
                if own:
                    st.markdown('**Luật ILA khớp (cùng cụm):**')
                    for r in own:
                        st.markdown(f'- {humanize_rule(r["text"])}')
                if other:
                    st.warning('Luật của cụm khác cũng khớp → bài có thể mang đặc điểm của nhiều kiểu lỗi: ' +
                               '; '.join(f'C{r["cls"]} ({names[r["cls"]]["name"]})' for r in other))
                if not R['rules']:
                    st.caption('Không có luật ILA nào khớp hoàn toàn — gán theo khoảng cách tới cụm.')
                dist = pd.DataFrame([dict(Cụm=f'C{k} · {names[int(k)]["name"]}', **{'Độ tương đồng': 1 - v})
                                     for k, v in sorted(R['distances'].items(), key=lambda kv: kv[1])])
                st.markdown('**Độ tương đồng với từng cụm** (1 − khoảng cách Hamming có trọng số):')
                st.dataframe(dist, hide_index=True, use_container_width=True, column_config={
                    'Độ tương đồng': st.column_config.ProgressColumn('Độ tương đồng', format='%.2f',
                                                                      min_value=0.0, max_value=1.0)})
                st.markdown(f'**So với bản đúng gần nhất** `{R["ref"]["id"]}` (tương đồng token '
                            f'{R["ref"]["similarity"]:.2f}):')
                st.code(R['ref']['diff'][:4000], language='diff')
                with st.expander('Bộ ba OAV trích được'):
                    st.dataframe(pd.DataFrame(R['oav']).assign(**{'Diễn giải': lambda d: [
                        gloss(f'{a[0]}:{o}.{t}') for a, o, t in zip(
                            d.group.map({'Output': 'O', 'Cấu trúc (AST)': 'A', 'Khác bản đúng': 'D'}),
                            d.object, d.attribute)]}), hide_index=True, use_container_width=True)
                with st.expander('Bài thật giống nhất trong dữ liệu'):
                    st.dataframe(pd.DataFrame([dict(Bài=n['sub_id'], Cụm=f'C{n["cluster"]} · '
                                                    f'{names[n["cluster"]]["name"]}', **{'Khoảng cách': n['distance']})
                                               for n in R['neighbors']]), hide_index=True, use_container_width=True)
            with st.expander('Kết quả từng test', expanded=R['status'] == 'correct'):
                st.dataframe(tests.rename(columns={'test_id': 'Test', 'status': 'Kết quả', 'input': 'Input',
                                                   'expected': 'Mong đợi', 'output': 'Output'})
                             .drop(columns='strict'), hide_index=True, use_container_width=True)

# ------------------------------------------------------------------------------------------- Thực nghiệm
with tab_exp:
    T = D['tables']
    st.subheader('E1/E2 — Khôi phục lỗi đã cấy (dữ liệu sinh)')
    if 'E1_E2_synthetic' in T:
        st.dataframe(pd.DataFrame(T['E1_E2_synthetic']), hide_index=True, use_container_width=True)
    p = st.selectbox('Bài tập (hình)', ['digits', 'grade', 'median', 'smallest', 'average'], key='exp_p')
    c = st.columns(2)
    with c[0]:
        img(f'confusion_syn_{p}.png', 'Nhãn cấy × cụm')
    with c[1]:
        img(f'mds_synthetic_{p}.png', 'MDS trên khoảng cách Hamming')
    st.subheader('E3 — Ablation nhóm thuộc tính')
    img('ablation_E3.png')
    if 'E3_ablation' in T:
        with st.expander('Bảng E3'):
            st.dataframe(pd.DataFrame(T['E3_ablation']), hide_index=True, use_container_width=True)
    st.subheader('E4 — Dữ liệu thật IntroClass')
    if 'E4_real' in T:
        st.dataframe(pd.DataFrame(T['E4_real']), hide_index=True, use_container_width=True)
    img('ksweep_real.png', 'Silhouette theo k')
    st.subheader('E4b — ITSP (602 cặp, đối chiếu 41 nhãn gán tay)')
    if 'E4b_itsp' in T:
        e = pd.DataFrame(T['E4b_itsp'])
        st.dataframe(e[e.method == 'kmodes'].pivot_table(index='groups', columns='k', values='ari'),
                     use_container_width=True)
        st.caption('ARI theo nhóm thuộc tính (hàng) và số cụm k (cột), K-modes.')
    st.subheader('E5 — Chất lượng luật: ILA vs ID3')
    if 'E5_rules' in T:
        st.dataframe(pd.DataFrame(T['E5_rules']), hide_index=True, use_container_width=True)
