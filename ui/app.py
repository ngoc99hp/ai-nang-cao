"""Demo: Phát hiện và gom nhóm lỗi hiểu sai (misconception) trong bài lập trình C — giao diện Streamlit.

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
PNAME = {'digits': 'Tách chữ số (digits)', 'grade': 'Xếp loại điểm (grade)',
         'median': 'Tìm số trung vị (median)', 'smallest': 'Tìm số nhỏ nhất (smallest)',
         'average': 'Tính trung bình (average — bài phụ)'}
TAXO = {'M1': 'biên vòng lặp', 'M2': 'truyền tham trị / tham chiếu', 'M3': 'nhầm = và ==', 'M4': 'chia nguyên',
        'M5': 'khởi tạo biến', 'M6': 'vị trí return/break', 'M7': 'biên so sánh trong if', 'M8': 'xử lý số âm'}

# ----------------------------------------------------------------------------- diễn giải thuộc tính OAV
FLAG = {   # thuộc tính đúng/sai → câu mô tả khi giá trị = T
    'D:diff.cmp_if': 'đổi phép so sánh trong điều kiện if',
    'D:diff.cmp_loop': 'đổi phép so sánh ở điều kiện vòng lặp',
    'D:diff.eq_assign': 'nhầm phép gán = với phép so sánh ==',
    'D:diff.logic_op': 'đổi toán tử logic && / ||',
    'D:diff.loop_init': 'khởi tạo biến chạy vòng lặp khác',
    'D:diff.init_value': 'khởi tạo biến bằng giá trị khác',
    'D:diff.literal_other': 'dùng hằng số khác',
    'D:diff.ptr_missing': 'thiếu con trỏ hoặc toán tử & / *',
    'D:diff.ptr_extra': 'thừa con trỏ hoặc toán tử & / *',
    'D:diff.cast_missing': 'thiếu ép kiểu',
    'D:diff.neg_missing': 'thiếu đoạn xử lý số âm',
    'D:diff.neg_extra': 'xử lý dấu âm thừa hoặc sai chỗ',
    'D:diff.moved_into_loop': 'đưa câu lệnh vào trong vòng lặp',
    'D:diff.moved_out_of_loop': 'đưa câu lệnh ra ngoài vòng lặp',
    'D:diff.extra_break': 'thừa lệnh break / return',
    'D:diff.missing_break': 'thiếu lệnh break / return',
    'D:diff.extra_output': 'thừa lệnh in',
    'D:diff.missing_output': 'thiếu lệnh in (thiếu nhánh in kết quả)',
    'D:diff.var_changed': 'dùng nhầm biến',
    'D:diff.arith_changed': 'dùng phép toán số học khác',
    'D:diff.stmt_missing': 'thiếu câu lệnh',
    'D:diff.stmt_extra': 'thừa câu lệnh',
    'O:output.missing_answer': 'không in ra đáp án',
    'O:output.multiple_answers': 'in ra nhiều đáp án',
    'O:output.off_by_one': 'đáp án lệch 1 đơn vị',
    'O:output.output_zero': 'in ra số 0',
    'O:output.wrong_input_elem': 'in ra một số có trong input nhưng không phải đáp án',
    'O:output.not_input_elem': 'in ra số không có trong input',
    'O:output.sign_error': 'đáp án sai dấu',
    'O:output.missing_items': 'in thiếu chữ số',
    'O:output.extra_items': 'in thừa chữ số',
    'O:output.missing_last': 'thiếu chữ số cuối',
    'O:output.wrong_digit': 'in sai chữ số',
    'O:output.digits_reversed': 'in chữ số theo thứ tự ngược',
    'O:output.adjacent_grade': 'xếp loại lệch 1 bậc',
    'O:output.far_grade': 'xếp loại lệch nhiều bậc',
    'O:output.grade_too_low': 'xếp loại thấp hơn đúng',
    'O:output.grade_too_high': 'xếp loại cao hơn đúng',
    'O:output.timeout': 'chạy quá thời gian (có thể lặp vô hạn)',
    'O:output.crash': 'chương trình bị dừng do lỗi khi chạy',
    'O:output.output_limit': 'in ra quá nhiều',
    'O:run.format_only_any': 'có test chỉ sai câu chữ / định dạng',
    'O:run.uninit_dependent': 'kết quả phụ thuộc biến chưa khởi tạo',
    'O:run.nondet_dataset': 'kết quả không ổn định giữa các lần chạy',
    'A:loop.output_in_loop': 'có lệnh in bên trong vòng lặp',
    'A:loop.return_in_loop': 'có return bên trong vòng lặp',
    'A:loop.break_in_loop': 'có break bên trong vòng lặp',
    'A:condition.assign_in_cond': 'có phép gán trong điều kiện',
    'A:function.has_ptr_param': 'có hàm nhận tham số con trỏ',
    'A:division.int_div_float_ctx': 'chia hai số nguyên rồi dùng như số thực',
    'A:division.has_cast': 'có ép kiểu khi chia',
    'A:negation.uses_abs': 'dùng hàm abs()',
    'A:negation.unary_minus': 'dùng phép đổi dấu (-x)',
}
TESTS = {'tie': 'có các số bằng nhau', 'negative': 'có số âm', 'zero': 'có số 0', 'sorted': 'input đã sắp xếp',
         'single_digit': 'số chỉ có 1 chữ số', 'inner_zero': 'số có chữ số 0 ở giữa',
         'boundary': 'điểm đúng bằng ngưỡng', 'failing': 'điểm dưới ngưỡng D', 'top': 'điểm loại A'}
QTY = {'some': 'một số', 'all': 'tất cả', 'none': 'không'}
FRAC = {'low': 'trượt ít test (dưới 1/3)', 'mid': 'trượt khoảng 1/3–2/3 số test',
        'high': 'trượt phần lớn test', 'all': 'trượt toàn bộ test'}
CMP_KIND = {'strictness': 'đổi giữa so sánh "chặt" và "không chặt" (< ↔ <=, > ↔ >=)',
            'reversed': 'đảo chiều phép so sánh (< ↔ >)', 'mixed': 'đổi phép so sánh theo nhiều kiểu',
            'none': 'không đổi phép so sánh nào'}
SIZE = {'1': 'chỉ khác bản đúng 1 ký hiệu', '2-5': 'khác bản đúng 2–5 ký hiệu',
        '6-20': 'khác bản đúng 6–20 ký hiệu', '21+': 'khác bản đúng hơn 20 ký hiệu'}
IF_CMP = {'strict': 'các điều kiện if chỉ dùng < hoặc > (so sánh chặt)',
          'nonstrict': 'các điều kiện if dùng <= hoặc >=', 'mixed': 'điều kiện if dùng cả hai kiểu so sánh',
          'none': 'không có so sánh trong if'}
INIT = {'zero': 'bằng 0', 'literal': 'bằng một hằng số', 'expr': 'bằng một biến / biểu thức',
        'none': 'không khởi tạo', 'n/a': 'không có'}


def describe(attr: str, v: str) -> str:
    """Thuộc tính OAV + giá trị → một câu tiếng Việt."""
    v = str(v).strip()
    if attr in FLAG:
        return FLAG[attr][0].upper() + FLAG[attr][1:] if v == 'T' else f'Không {FLAG[attr]}'
    m = re.fullmatch(r'O:tests_(\w+)\.fail', attr)
    if m and m.group(1) in TESTS:
        t = TESTS[m.group(1)]
        return {'none': f'Không trượt test nào {t}', 'all': f'Trượt tất cả test {t}'}.get(
            v, f'Trượt một số test {t}')
    if attr == 'O:tests.fail_frac':
        return FRAC.get(v, v).capitalize()
    if attr == 'D:diff.cmp_kind':
        return CMP_KIND.get(v, v).capitalize()
    if attr == 'D:diff.size':
        return SIZE.get(v, v).capitalize()
    if attr == 'A:condition.if_cmp':
        return IF_CMP.get(v, v).capitalize()
    if attr == 'A:loop.cmp_op':
        return 'Không có vòng lặp so sánh' if v == 'none' else f'Vòng lặp dùng phép so sánh {v}'
    if attr == 'A:extremum.init':
        return f'Biến min/max khởi tạo {INIT.get(v, v)}'
    if attr == 'A:accumulator.init':
        return f'Biến tích lũy khởi tạo {INIT.get(v, v)}'
    return f'{attr} = {v}'


def rule_to_text(text: str) -> tuple[str, str]:
    """'NẾU [a = v] VÀ ... THÌ Cụm k [coverage x/y, accuracy z]' → (câu, ghi chú độ phủ)."""
    m = re.match(r'(?:R\d+: )?NẾU (.*) THÌ Cụm (\d+) \[coverage (\d+)/(\d+), accuracy ([\d.]+)\]', text)
    if not m:
        return text, ''
    conds = [describe(a.strip(), v) for a, v in re.findall(r'\[([^\]=]+?) = ([^\]]+)\]', m.group(1))]
    cond = ' **và** '.join(c[0].lower() + c[1:] for c in conds)
    acc = float(m.group(5))
    note = f'đúng với {m.group(3)}/{m.group(4)} bài của nhóm' + ('' if acc == 1 else f', chính xác {acc:.0%}')
    return f'**Nếu** bài {cond} **thì** thuộc nhóm C{m.group(2)}', note


def taxo(t: str) -> str:
    return '—' if t in ('-', '', None) else ', '.join(f'{x} ({TAXO.get(x, "")})' for x in t.split('+'))


# ----------------------------------------------------------------------------- đề bài (IntroClass)
PROBLEM_DOC = {
    'digits': dict(
        task='Nhập một số nguyên **n**. In ra từng chữ số của n, **mỗi chữ số một dòng**, bắt đầu từ chữ số hàng '
             'đơn vị (tức là in **ngược** từ phải sang trái). Cuối cùng in dòng `That\'s all, have a nice day!`',
        rules=['Nếu n **âm**: các chữ số in ra không có dấu, riêng chữ số **cuối cùng** (chữ số đầu của n) mang '
               'dấu `-`.',
               'Nếu n = **0**: in ra `0`.',
               'Chữ số 0 nằm giữa hoặc cuối số vẫn phải được in.'],
        io='**Input:** một số nguyên.  \n**Output:** lời nhắc `Enter an integer >`, các chữ số mỗi số một dòng, '
           'rồi dòng kết thúc.',
        examples=[('1234', '4\n3\n2\n1\nThat\'s all, have a nice day!'),
                  ('-9876', '6\n7\n8\n-9\nThat\'s all, have a nice day!'),
                  ('0', '0\nThat\'s all, have a nice day!'),
                  ('3520', '0\n2\n5\n3\nThat\'s all, have a nice day!')]),
    'grade': dict(
        task='Nhập **4 ngưỡng điểm** cho loại A, B, C, D (giảm dần, theo %), sau đó nhập **điểm** của sinh viên. '
             'In ra loại mà sinh viên đạt được.',
        rules=['Điểm **≥ ngưỡng A** → `Student has an A grade`; tương tự với B, C, D.',
               'Điểm **bằng đúng ngưỡng** vẫn đạt loại đó (ví dụ ngưỡng A = 80, điểm 80 → loại A).',
               'Điểm **dưới ngưỡng D** → `Student has failed the course`.'],
        io='**Input:** 4 số ngưỡng A B C D, rồi 1 số điểm.  \n**Output:** sau các lời nhắc, đúng một câu xếp loại.',
        examples=[('80 70 60 50\n85', 'Student has an A grade'),
                  ('80 70 60 50\n80', 'Student has an A grade'),
                  ('80 70 60 50\n75', 'Student has an B grade'),
                  ('80 70 60 50\n45', 'Student has failed the course')]),
    'median': dict(
        task='Nhập **3 số nguyên**. In ra **số trung vị** — số đứng giữa khi xếp 3 số theo thứ tự tăng dần.',
        rules=['Các số có thể nhập theo **bất kỳ thứ tự nào**.',
               'Các số có thể **bằng nhau** (ví dụ 9 9 9 → trung vị là 9).'],
        io='**Input:** 3 số nguyên cách nhau bởi dấu cách.  \n**Output:** lời nhắc '
           '`Please enter 3 numbers separated by spaces >` rồi `<số> is the median`.',
        examples=[('2 6 8', '6 is the median'), ('8 2 6', '6 is the median'), ('9 9 9', '9 is the median')]),
    'smallest': dict(
        task='Nhập **4 số nguyên**. In ra **số nhỏ nhất**.',
        rules=['Các số có thể **bằng nhau** (ví dụ 1 1 1 1 → 1).', 'Các số có thể **âm** hoặc bằng 0.'],
        io='**Input:** 4 số nguyên cách nhau bởi dấu cách.  \n**Output:** lời nhắc '
           '`Please enter 4 numbers separated by spaces >` rồi `<số> is the smallest`.',
        examples=[('1 2 3 4', '1 is the smallest'), ('3 2 4 1', '1 is the smallest'),
                  ('2 2 2 3', '2 is the smallest'), ('0 -1 0 0', '-1 is the smallest')]),
}


def show_problem(p, expanded=True):
    d = PROBLEM_DOC[p]
    with st.expander(f'📄 Đề bài: {PNAME[p]}', expanded=expanded):
        st.markdown(d['task'])
        st.markdown('**Lưu ý:**\n' + '\n'.join(f'- {r}' for r in d['rules']))
        st.markdown(d['io'])
        st.markdown('**Ví dụ** (bỏ qua lời nhắc nhập):')
        def _cell(s):                               # giữ nguyên khoảng trắng, xuống dòng → ⏎
            return '`' + s.replace('\n', '` ⏎ `') + '`'
        st.markdown('| Nhập vào | Kết quả in ra |\n|---|---|\n' +
                    '\n'.join(f'| {_cell(i)} | {_cell(o)} |' for i, o in d['examples']))
        st.caption('Bài tập từ bộ dữ liệu IntroClass (UC Davis). Khi chấm, hệ thống chỉ so phần đáp án, '
                   'không bắt lỗi chính tả trong lời nhắc.')


@st.cache_data(ttl=60)
def load_dash():
    return json.loads((RES / 'demo' / 'dashboard.json').read_text(encoding='utf-8'))


def img(name, caption=None):
    f = FIG / name
    if f.exists():
        st.image(str(f), caption=caption, use_container_width=True)


st.set_page_config(page_title='Phát hiện lỗi hiểu sai — Demo', page_icon='🧩', layout='wide')
D = load_dash()
st.title('Tự động phát hiện và gom nhóm lỗi hiểu sai trong bài lập trình C')
st.caption('Đề tài 5 — môn AI nâng cao')

PAGES = ['① Giới thiệu', '② Dành cho giảng viên', '③ Thử nộp bài', '④ Kết quả thực nghiệm']
# Giữ lựa chọn bài tập / code đã dán khi chuyển trang (Streamlit xóa state của widget không được vẽ)
for _k in list(st.session_state):
    if _k in ('gv_p', 'sv_p', 'exp_p') or _k.startswith(('code_', 'sample_')):
        st.session_state[_k] = st.session_state[_k]
page = st.radio('Trang', PAGES, horizontal=True, key='page', label_visibility='collapsed')
st.divider()

# =============================================================================================== ① Giới thiệu
if page == PAGES[0]:
    st.markdown('''
### Bài toán
Lớp lập trình đông, mỗi bài tập có hàng trăm bài làm sai. Giảng viên không thể đọc hết, nhưng muốn biết:
**sinh viên đang hiểu sai điều gì, và bao nhiêu người hiểu sai như vậy** — để giảng lại cho cả lớp
(*macro-feedback*).

Nhiều bài sai trông khác nhau nhưng thực ra cùng một **lỗi hiểu sai** (misconception). Ví dụ: dùng `<` thay vì `<=`
khi tìm số nhỏ nhất → chương trình sai khi có hai số bằng nhau.

### Hệ thống làm gì
''')
    cols = st.columns(4)
    steps = [('1. Chấm bài', 'Chạy bài C với bộ test trong môi trường cách ly, ghi lại test nào trượt và in ra gì.'),
             ('2. Mô tả bài sai', 'Mỗi bài sai được mô tả bằng các **dấu hiệu** dạng *Đối tượng – Thuộc tính – Giá trị*: '
                                  'kết quả in ra sai kiểu gì, cấu trúc code ra sao, khác bài đúng ở chỗ nào.'),
             ('3. Gom nhóm', 'Các bài có dấu hiệu giống nhau được gom vào cùng một **nhóm lỗi** '
                             '(không cần ai gán nhãn trước).'),
             ('4. Giải thích', 'Với mỗi nhóm, hệ thống tự viết **luật "Nếu … thì …"** để giải thích vì sao các bài '
                               'đó cùng nhóm; con người đặt tên lỗi dựa trên luật.')]
    for c, (h, t) in zip(cols, steps):
        c.markdown(f'#### {h}')
        c.markdown(t)
    P = D['problems']
    st.markdown('### Dữ liệu')
    c = st.columns(4)
    c[0].metric('Bài làm sai thật', sum(v['n_sub'] for v in P.values()))
    c[1].metric('Sinh viên', sum(v['n_students'] for v in P.values()))
    c[2].metric('Bài tập', len(P))
    c[3].metric('Nhóm lỗi tìm được', sum(v['k'] for v in P.values()))
    st.markdown('''
- **Bài thật**: bộ dữ liệu IntroClass (ĐH UC Davis) — bài nộp của sinh viên cho 4 bài tập C nhập môn.
- **Bài cấy lỗi**: 480 bài do nhóm tự tạo bằng cách cố ý đưa 8 loại lỗi quen thuộc vào bài đúng.
  Vì biết trước mỗi bài mắc lỗi gì, ta **chấm được** hệ thống gom nhóm đúng đến đâu.
- **Bài kiểm chứng thêm**: bộ ITSP (IIT Kanpur, Ấn Độ) — 602 bài sai kèm bản sinh viên tự sửa đúng.

### Kết quả tóm tắt
- Trên bài cấy lỗi, các nhóm tìm được **khớp khá tốt** với loại lỗi đã cấy (điểm khớp 0.48–0.73 trên thang 0 → 1).
- Dấu hiệu quan trọng nhất là **"bài sai khác bài đúng ở đâu"**; chỉ nhìn test trượt thì gần như không phân biệt được lỗi.
- Trên bài thật, hệ thống tìm ra các nhóm lỗi có ý nghĩa — xem trang **② Dành cho giảng viên**.
- Hạn chế: chưa tách tốt các lỗi kiểu "nhầm biến" hay "sai công thức"; một số nhóm còn lẫn nhiều kiểu lỗi.
''')

# =============================================================================================== ② Giảng viên
if page == PAGES[1]:
    st.markdown('Chọn một bài tập để xem **sinh viên đang mắc những lỗi hiểu sai nào, bao nhiêu người mắc**, '
                'kèm giải thích và bài làm minh họa.')
    p = st.selectbox('Bài tập', list(D['problems']), format_func=PNAME.get, key='gv_p')
    info = D['problems'][p]
    show_problem(p, expanded=False)
    c = st.columns(3)
    c[0].metric('Bài làm sai', info['n_sub'])
    c[1].metric('Sinh viên làm sai', info['n_students'])
    c[2].metric('Nhóm lỗi', info['k'])
    st.markdown('#### Các lỗi phổ biến (nhiều sinh viên mắc nhất ở trên)')
    tbl = pd.DataFrame([{'Nhóm': f'C{x["id"]}', 'Lỗi hiểu sai': x['name'], 'Số sinh viên': x['n_students'],
                         'Số bài': x['n_sub'], 'Ứng với loại lỗi chuẩn': taxo(x['taxonomy'])}
                        for x in info['clusters']])
    st.dataframe(tbl, hide_index=True, use_container_width=True, column_config={
        'Số sinh viên': st.column_config.ProgressColumn('Số sinh viên', format='%d', min_value=0,
                                                        max_value=int(tbl['Số sinh viên'].max()))})
    st.caption('Một sinh viên có thể nộp nhiều lần, nên "số bài" có thể lớn hơn "số sinh viên". '
               'Tên lỗi do người đặt sau khi đọc luật và bài minh họa.')
    st.markdown('#### Chi tiết từng nhóm')
    for x in info['clusters']:
        with st.expander(f'C{x["id"]} · {x["name"]} — {x["n_students"]} sinh viên'):
            st.markdown('**Dấu hiệu đặc trưng của nhóm:**')
            for f in x['features'][:5]:
                st.markdown(f'- {describe(f["attr"], f["value"])} — **{f["in_cluster"]:.0%}** bài trong nhóm '
                            f'(so với {f["overall"]:.0%} ở toàn bộ bài sai)')
            st.markdown('**Luật do hệ thống tự sinh:**')
            for r in x['rules'][:3]:
                s, note = rule_to_text(r)
                st.markdown(f'- {s}  \n  <span style="color:gray">↳ {note}</span>', unsafe_allow_html=True)
            ex = x['examples'][0]
            src = 'bản sinh viên đó tự sửa đúng sau này' if ex['ref_kind'] == 'own_fix' else 'một bài đúng tương tự'
            st.markdown(f'**Bài minh họa** — so với {src}. Dòng đỏ (–) là code đúng, dòng xanh (+) là code sai:')
            st.code(ex['diff'][:3000] or '(không có khác biệt)', language='diff')
            if st.toggle('Hiện chi tiết kỹ thuật', key=f'tech_{p}_{x["id"]}'):
                st.dataframe(pd.DataFrame(x['features']), hide_index=True, use_container_width=True)
                st.code('\n'.join(x['rules'][:5]), language=None)
    st.markdown('#### Bản đồ nhiệt: nhóm lỗi × dấu hiệu')
    st.caption('Mỗi hàng là một nhóm lỗi, mỗi cột là một dấu hiệu; ô càng đậm thì càng nhiều bài trong nhóm có dấu '
               'hiệu đó.')
    img(f'heatmap_real_{p}.png')

# =============================================================================================== ③ Nộp bài
if page == PAGES[2]:
    st.markdown('Dán một bài làm C (hoặc chọn bài mẫu có sẵn) rồi bấm **Chấm và chẩn đoán**. Hệ thống sẽ chạy test, '
                'và nếu bài sai thì cho biết bài **giống nhóm lỗi nào nhất** và vì sao.')
    p = st.selectbox('Bài tập', [k for k in D['problems']], format_func=PNAME.get, key='sv_p')
    show_problem(p)
    samples = {f'Bài tự viết — {f.stem}': f.read_text() for f in sorted(SAMPLES.glob(f'{p}_*.c'))}
    for x in D['problems'][p]['clusters']:
        samples[f'Bài thật của sinh viên — ví dụ nhóm C{x["id"]} ({x["name"][:40]})'] = x['examples'][0]['code']

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
        with st.spinner('Đang chạy test trong môi trường cách ly... (thường dưới 2 giây; bài bị lặp vô hạn '
                        'có thể mất ~30 giây vì mỗi test được chạy tới giới hạn thời gian)'):
            for _ in range(180):
                if out.exists():
                    break
                time.sleep(0.5)
        if not out.exists():
            st.error('Không nhận được kết quả sau 90 giây. Bộ chấm có thể chưa chạy — chạy lại ./demo/start.sh trên server.')
            st.stop()
        st.session_state['result'] = (p, json.loads(out.read_text(encoding='utf-8')))
        out.unlink(missing_ok=True)

    if 'result' in st.session_state and st.session_state['result'][0] == p:
        R = st.session_state['result'][1]
        names = {x['id']: x for x in D['problems'][p]['clusters']}
        st.divider()
        if R['status'] == 'compile_error':
            st.error('Chương trình **không biên dịch được** — kiểm tra lỗi cú pháp:')
            st.code(R['stderr'], language=None)
        elif R['status'] == 'error':
            st.error(f'Không xử lý được bài này: {R["message"]}')
        else:
            tests = pd.DataFrame(R['tests'])
            if R['status'] == 'correct':
                st.success(f'✅ **Bài đúng** — qua cả {len(tests)}/{len(tests)} test. Không phát hiện lỗi hiểu sai.')
                if R.get('format_fail'):
                    st.info(f'Có {R["format_fail"]} test chỉ khác câu chữ (ví dụ lời nhắc nhập), không tính là sai.')
            else:
                cl = names[R['cluster']]
                st.error(f'❌ Bài **trượt {R["n_fail"]}/{len(tests)} test**.')
                st.markdown(f'### Chẩn đoán: giống nhất nhóm **C{R["cluster"]} — {cl["name"]}**')
                st.caption(f'Trong dữ liệu, {cl["n_students"]} sinh viên đã mắc lỗi này.')
                st.markdown('**Vì sao hệ thống nghĩ vậy?** Bài này có chung các dấu hiệu sau với nhóm đó:')
                st.markdown('\n'.join(f'- {describe(w["attr"], w["value"])}' for w in R['why'][:6]))
                own = [r for r in R['rules'] if r['cls'] == R['cluster']]
                other = [r for r in R['rules'] if r['cls'] != R['cluster']]
                if own:
                    st.markdown('**Luật khớp với bài này:**')
                    for r in own[:3]:
                        st.markdown(f'- {rule_to_text(r["text"])[0]}')
                if other:
                    st.warning('Bài cũng khớp luật của nhóm khác — có thể bài mắc nhiều kiểu lỗi cùng lúc: ' +
                               '; '.join(f'C{r["cls"]} ({names[r["cls"]]["name"]})' for r in other))
                st.markdown('**Mức giống với từng nhóm lỗi** (1 = giống hoàn toàn):')
                dist = pd.DataFrame([{'Nhóm lỗi': f'C{k} — {names[int(k)]["name"]}', 'Mức giống': 1 - v}
                                     for k, v in sorted(R['distances'].items(), key=lambda kv: kv[1])])
                st.dataframe(dist, hide_index=True, use_container_width=True, column_config={
                    'Mức giống': st.column_config.ProgressColumn('Mức giống', format='%.2f',
                                                                 min_value=0.0, max_value=1.0)})
                st.markdown('**So với một bài đúng tương tự** — dòng đỏ (–) là code đúng, dòng xanh (+) là code '
                            'của bài này:')
                st.code(R['ref']['diff'][:4000], language='diff')
                with st.expander('Chi tiết kỹ thuật (bộ ba Đối tượng – Thuộc tính – Giá trị, bài giống nhất)'):
                    st.dataframe(pd.DataFrame(R['oav']).rename(columns={
                        'group': 'Nhóm dấu hiệu', 'object': 'Đối tượng', 'attribute': 'Thuộc tính',
                        'value': 'Giá trị'}), hide_index=True, use_container_width=True)
                    st.dataframe(pd.DataFrame([{'Bài thật': n['sub_id'], 'Thuộc nhóm': f'C{n["cluster"]}',
                                                'Khoảng cách': n['distance']} for n in R['neighbors']]),
                                 hide_index=True, use_container_width=True)
                    st.caption(f'Bài đúng dùng để so: {R["ref"]["id"]} (giống {R["ref"]["similarity"]:.0%}) · '
                               f'thời gian chấm {R["elapsed"]} s')
            with st.expander('Kết quả từng test', expanded=R['status'] == 'correct'):
                st.dataframe(tests.assign(status=tests.status.map(lambda s: '✅ Đạt' if s == 'PASS' else f'❌ {s}'))
                             .rename(columns={'test_id': 'Test', 'status': 'Kết quả', 'input': 'Dữ liệu vào',
                                              'expected': 'Kết quả mong đợi', 'output': 'Bài in ra'})
                             .drop(columns='strict'), hide_index=True, use_container_width=True)

# =============================================================================================== ④ Thực nghiệm
if page == PAGES[3]:
    T = D['tables']
    st.markdown('''
**Cách đọc điểm khớp (ARI):** so sánh các nhóm hệ thống tìm được với loại lỗi thật đã cấy vào bài.
**1** = khớp hoàn toàn, **0** = không hơn chia nhóm ngẫu nhiên.
''')
    st.markdown('### 1. Hệ thống có tìm lại đúng các lỗi đã cấy không?')
    st.markdown('Dùng 480 bài cấy lỗi (biết trước đáp án), cho hệ thống gom nhóm rồi so với loại lỗi đã cấy.')
    if 'E1_E2_synthetic' in T:
        e = pd.DataFrame(T['E1_E2_synthetic'])
        e['Bài tập'] = e.problem.map(PNAME)
        tb = e.pivot_table(index='Bài tập', columns='method', values='ari').rename(columns={
            'kmodes': 'K-modes (phương pháp chính)', 'agglo': 'Phân cấp (Agglomerative)',
            'kmeans1h': 'K-means (đối chứng)'})
        st.dataframe(tb.round(2), use_container_width=True)
        st.success('**Kết luận:** điểm khớp 0.48–0.73 với phương pháp chính — các nhóm phần lớn trùng với loại lỗi '
                   'thật. Ba phương pháp gom nhóm cho kết quả gần nhau, không phương pháp nào luôn thắng.')
    p = st.selectbox('Xem hình cho bài tập', ['digits', 'grade', 'median', 'smallest', 'average'],
                     format_func=PNAME.get, key='exp_p')
    c = st.columns(2)
    with c[0]:
        img(f'confusion_syn_{p}.png', 'Hàng: loại lỗi đã cấy · Cột: nhóm tìm được. Ô đậm tập trung = gom đúng.')
    with c[1]:
        img(f'mds_synthetic_{p}.png', 'Mỗi chấm là một bài; bài càng giống nhau càng nằm gần nhau.')

    st.markdown('### 2. Loại dấu hiệu nào quan trọng?')
    st.markdown('Thử gom nhóm chỉ với từng loại dấu hiệu: **O** = kết quả in ra sai kiểu gì, **A** = cấu trúc code, '
                '**D** = khác bài đúng ở đâu, **T** = test nào trượt.')
    img('ablation_E3.png')
    st.success('**Kết luận:** có dấu hiệu **D** thì điểm khớp tăng mạnh; chỉ dùng O hoặc A thì thấp. '
               'Thêm "test nào trượt" (T) không giúp ích, thậm chí làm giảm ở 3/5 bài.')
    if 'E3_ablation' in T:
        with st.expander('Bảng số liệu'):
            e = pd.DataFrame(T['E3_ablation'])
            e = e[e.method == 'kmodes']
            e['Bài tập'] = e.problem.map(PNAME)
            st.dataframe(e.pivot_table(index='Bài tập', columns='groups', values='ari').round(2),
                         use_container_width=True)

    st.markdown('### 3. Trên bài làm thật của sinh viên')
    st.markdown('Bài thật không có đáp án sẵn, nên đánh giá bằng **độ tách nhóm** (silhouette: -1 → 1, càng cao '
                'các nhóm càng tách bạch) và bằng cách đọc lại bài trong từng nhóm.')
    if 'E4_real' in T:
        e = pd.DataFrame(T['E4_real'])
        st.dataframe(pd.DataFrame({'Bài tập': e.problem.map(PNAME), 'Số bài sai': e.n, 'Số nhóm': e.k,
                                   'Độ tách nhóm': e.silhouette.round(2), 'Số bài từng nhóm': e.sizes,
                                   'Số sinh viên từng nhóm': e.students}),
                     hide_index=True, use_container_width=True)
        st.info('**Nhận xét:** grade và smallest tách nhóm tốt (≈ 0.5); digits và median kém hơn. '
                'Thường có một nhóm lớn chiếm đa số — lỗi phổ biến nhất.')
    st.markdown('**Kiểm chứng thêm trên ITSP** (602 bài; 41 bài được gán nhãn lỗi bằng tay để đối chiếu): '
                'điểm khớp **0.20**. Hệ thống nhận ra tốt lỗi biên so sánh, biên vòng lặp, thiếu câu lệnh; '
                'chưa tách được lỗi nhầm biến và sai công thức.')

    st.markdown('### 4. Luật sinh ra có dễ hiểu và đáng tin không?')
    st.markdown('So sánh thuật toán **ILA** (tự cài đặt) với cây quyết định **ID3** khi viết luật giải thích các nhóm.')
    if 'E5_rules' in T:
        e = pd.DataFrame(T['E5_rules'])
        st.dataframe(pd.DataFrame({
            'Dữ liệu': e.dataset.map({'real': 'Bài thật', 'synthetic': 'Bài cấy lỗi'}),
            'Bài tập': e.problem.map(PNAME),
            'ILA: số luật': e.ila_rules, 'ILA: điều kiện / luật': e.ila_avg_conds.round(1),
            'ILA: độ chính xác': e.ila_cv_acc.round(2),
            'ID3: số luật': e.id3_rules, 'ID3: điều kiện / luật': e.id3_avg_conds.round(1),
            'ID3: độ chính xác': e.id3_cv_acc.round(2)}), hide_index=True, use_container_width=True)
        st.success('**Kết luận:** luật của ILA **ngắn hơn** (1–2 điều kiện so với 3–5 của ID3) nên dễ đọc hơn, '
                   'độ chính xác tương đương (0.70–0.92 so với 0.72–0.97).')
