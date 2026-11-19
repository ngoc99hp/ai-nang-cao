"""Chấm output theo DP0 — hai chế độ.

strict   : port nguyên văn bin/genprog_tests.py của IntroClass (kể cả bug của nó).
           Dùng để kiểm định runner với metadata.json. Exception trong checker → FAIL
           (script gốc crash → exit ≠ 0 → test fail). Exit code của bài KHÔNG tính (khớp metadata).
semantic : trích đáp án lỏng — không phân biệt hoa/thường, chịu sai chính tả từ khóa
           và câu nhắc, bỏ qua khoảng trắng/xuống dòng, sửa bug checker gốc.
           Status dùng cho clustering. format_only = strict FAIL & semantic PASS.

problem None hoặc không phải bài IntroClass (vd 'average') → so token (`str.split`) cho cả hai chế độ.
"""
import re
import string

MODES = ('strict', 'semantic')


def tokens(s: str) -> list[str]:
    return s.split()


# ---------------------------------------------------------------- strict (nguyên văn)
# Giữ nguyên chuỗi regex của genprog_tests.py; chỉ đổi '\d' → r'\d' để tránh SyntaxWarning
# (cùng ngữ nghĩa).

def _strict_checksum(out, ref, inp):
    truth_rgx = re.compile("Check[ ]?sum[ ]+is[ ]+([{}])".format(string.printable), re.IGNORECASE)
    truth = truth_rgx.search(ref).group(1)
    return (truth_rgx.search(out) is not None
            and re.compile('Check[ ]?sum is {}'.format(truth), re.IGNORECASE).search(out) is not None
            and re.compile("Check[ ]?sum is [^{}]".format(truth), re.IGNORECASE).search(out) is None)


def _strict_digits(out, ref, inp):
    rgx = re.compile('[-]?\\d\n')
    return rgx.findall(out) == rgx.findall(ref)


def _strict_grade(out, ref, inp):
    def get_ans(o):
        m = re.compile('Student has an ([A-D]) grade', re.IGNORECASE).search(o)
        if m is None:
            m2 = re.compile('Student has (failed) the course', re.IGNORECASE).search(o)
            if m2 is None:
                raise Exception('GRADE: no answer found')
            return m2.group(1)
        return m.group(1)
    truth = get_ans(ref)
    grades = set('ABCD')
    pats = {g: re.compile('Student has an {} grade'.format(g), re.IGNORECASE) for g in grades}
    if truth in grades:
        no_neg = all(r.search(out) is None for g, r in pats.items() if g != truth)
        pos = pats[truth].search(out)
    elif truth == 'failed':
        no_neg = all(r.search(out) is None for r in pats.values())
        pos = re.compile('Student has failed the course', re.IGNORECASE).search(out)
    else:
        raise ValueError(truth)
    return pos is not None and no_neg


def _strict_median(out, ref, inp):
    rgx = re.compile(r'([-]?\d+) is the median')
    truth = rgx.search(ref).group(1)
    ans = rgx.search(out)
    neg = [re.compile('{} is the median'.format(n)) for n in inp.split(' ') if n != truth]
    return (ans is not None and int(ans.group(1)) == int(truth)
            and all(r.search(out) is None for r in neg))


def _strict_smallest(out, ref, inp):
    rgx = re.compile(r'([-]?\d+) is the smallest', re.IGNORECASE)
    truth = rgx.search(ref).group(1)
    ans = rgx.search(out)
    neg = (re.compile('{} is the smallest'.format(n)) for n in inp.split(' ') if n != truth)
    return (ans is not None and int(ans.group(1)) == int(truth)
            and all(r.search(inp) is None for r in neg))      # bug gốc: tìm trong input


def _strict_syllables(out, ref, inp):
    truth = re.compile(r'syllables is (\d+)', re.IGNORECASE).search(ref).group(1)
    right = re.compile('syllables is {}'.format(truth), re.IGNORECASE).search(out) is not None
    other = re.compile('syllables is [^{}]'.format(truth)).search(out) is None
    return right and other


# ---------------------------------------------------------------- semantic
# Mỗi bài: hàm trích danh sách "đáp án" từ một output. PASS ⇔ output có ≥ 1 đáp án
# và mọi đáp án đều bằng đáp án đúng (không in thêm đáp án mâu thuẫn).

def _ans_checksum(o):
    # "Check sum is K" / "checksum is K" / "Check sum is: K" ... ký tự ngay sau 'is'
    return re.findall(r'(?i)\bis[ \t]?:?[ \t]?([^\n])', o)


def _ans_grade(o):
    o = o.lower()
    ans = re.findall(r'\b([a-f])\s+grade\b', o)
    ans = ['failed' if a == 'f' else a.upper() for a in ans]   # "an F grade" ≡ failed (khác chữ, cùng nghĩa)
    if re.search(r'\bfail', o):
        ans.append('failed')
    return ans


def _ans_num(keyword):
    rgx = re.compile(r'(-?\d+)\D{0,20}?' + keyword, re.IGNORECASE)   # "N is the median", "N is teh median"...
    return lambda o: [int(x) for x in rgx.findall(o)]


_SEM_ANS = {
    'checksum': _ans_checksum,
    'grade': _ans_grade,
    'median': _ans_num('med'),
    'smallest': _ans_num('small'),
    'syllables': lambda o: [int(x) for x in re.findall(r'(?i)syl\w*\D{0,20}?(\d+)', o)],
}


def _semantic(problem, out, ref, inp):
    if problem == 'digits':
        # dãy chữ số có dấu, không phụ thuộc xuống dòng / câu nhắc (câu nhắc không chứa chữ số);
        # cho phép in lại số đã nhập phía trước ("The digits for the 89374 are: 4 7 3 9 8")
        got, truth = re.findall(r'-?\d', out), re.findall(r'-?\d', ref)
        k = len(got) - len(truth)
        return got == truth or (k > 0 and got[k:] == truth and got[:k] == re.findall(r'-?\d', inp))
    f = _SEM_ANS[problem]
    truth = f(ref)
    assert len(set(truth)) == 1, (problem, ref, truth)
    got = f(out)
    return bool(got) and set(got) == set(truth)


_STRICT = {'checksum': _strict_checksum, 'digits': _strict_digits, 'grade': _strict_grade,
           'median': _strict_median, 'smallest': _strict_smallest, 'syllables': _strict_syllables}


def check(problem: str | None, out: str, expected: str, test_input: str, mode: str) -> bool:
    if problem is None or problem not in _STRICT:      # bench/synthetic tự viết → so token
        return tokens(out) == tokens(expected)
    if mode == 'strict':
        if '�' in out:          # bản gốc .decode() utf-8 → UnicodeDecodeError → fail
            return False
        try:
            return bool(_STRICT[problem](out, expected, test_input))
        except Exception:
            return False
    if mode == 'semantic':
        return _semantic(problem, out, expected, test_input)
    raise ValueError(mode)
