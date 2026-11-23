"""Dựng báo cáo Word theo file mẫu (giữ trang bìa + style của mẫu, thay toàn bộ nội dung).

Chạy trong container công cụ aai-doc (python-docx + LibreOffice):
  docker run --rm -v "$PWD":/w aai-doc:1 python -I report/build.py
Hai lượt: lượt 1 render PDF để lấy số trang của từng đầu mục → lượt 2 ghi mục lục có số trang.
"""
import copy
import re
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import docx
from docx.oxml import parse_xml
from docx.shared import Cm

ROOT = Path('/w')
sys.path.insert(0, str(ROOT / 'report'))
TEMPLATE = ROOT / 'BaoCao_BTL_HocMayNangCao_UIT-VSMEC.docx'
OUT = ROOT / 'report' / 'BaoCao_BTL_AINangCao_MisconceptionClustering.docx'
W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
CONTENT_W = 9071                                   # dxa, = 16 cm (A4, lề trái 3, phải 2)
HEAD_FILL, ALT_FILL = '1F4E79', 'F2F2F2'


# ============================================================================ mô hình nội dung
class Doc:
    """Các khối nội dung; đánh số chương/bảng/hình/công thức khi khai báo."""

    def __init__(self):
        self.blocks, self.tables, self.figures, self.labels = [], [], [], {}
        self.chap, self.nt, self.nf, self.ne = '0', 0, 0, 0

    def h1(self, text, chap=None):
        if chap is not None:
            self.chap, self.nt, self.nf, self.ne = str(chap), 0, 0, 0
        self.blocks.append(('h', 1, text))

    def h2(self, text):
        self.blocks.append(('h', 2, text))

    def h3(self, text):
        self.blocks.append(('h', 3, text))

    def p(self, text, indent=True):
        self.blocks.append(('p', text, indent))

    def bullets(self, items):
        for it in items:
            self.blocks.append(('li', it))

    def eq(self, text, label=None):
        self.ne += 1
        num = f'{self.chap}.{self.ne}'
        if label:
            self.labels[label] = num
        self.blocks.append(('eq', text, num))

    def table(self, header, rows, widths, caption, label=None, align=None, bold_last=False):
        self.nt += 1
        num = f'{self.chap}.{self.nt}'
        if label:
            self.labels[label] = num
        cap = f'Bảng {num}: {caption}'
        self.tables.append(cap)
        tot = sum(widths)
        widths = [round(w * CONTENT_W / tot) for w in widths]
        widths[-1] += CONTENT_W - sum(widths)
        self.blocks.append(('tbl', header, rows, widths, cap, align, bold_last))

    def figure(self, path, caption, width_cm=16, label=None):
        self.nf += 1
        num = f'{self.chap}.{self.nf}'
        if label:
            self.labels[label] = num
        cap = f'Hình {num}: {caption}'
        self.figures.append(cap)
        self.blocks.append(('fig', path, width_cm, cap))

    def code(self, text):
        self.blocks.append(('code', text))

    def pagebreak(self):
        self.blocks.append(('pb',))


# ============================================================================ sinh XML
RUN_RE = re.compile(r'(\*\*.+?\*\*|\*[^*\s][^*]*?\*|`[^`]+`|_\{[^}]*\}|\^\{[^}]*\})')


def runs(text, base='', size=None):
    """Markup nhẹ: **đậm**, *nghiêng*, `code`, _{chỉ số dưới}, ^{chỉ số trên}."""
    out = []
    sz = f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else ''
    for part in RUN_RE.split(text):
        if not part:
            continue
        rpr = base
        if part.startswith('**'):
            part, rpr = part[2:-2], rpr + '<w:b/><w:bCs/>'
        elif part.startswith('`'):
            part = part[1:-1]
            rpr += ('<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>'
                    '<w:sz w:val="22"/><w:szCs w:val="22"/>')
            out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
            continue
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            part, rpr = part[1:-1], rpr + '<w:i/><w:iCs/>'
        elif part.startswith('_{'):
            part, rpr = part[2:-1], rpr + '<w:vertAlign w:val="subscript"/>'
        elif part.startswith('^{'):
            part, rpr = part[2:-1], rpr + '<w:vertAlign w:val="superscript"/>'
        out.append(f'<w:r><w:rPr>{rpr}{sz}</w:rPr><w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return ''.join(out)


def body_p(text, indent=True):
    ind = '<w:ind w:firstLine="567"/>' if indent else ''
    return (f'<w:p {W}><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/>{ind}'
            f'<w:jc w:val="both"/></w:pPr>{runs(text)}</w:p>')


def li_p(text):
    return (f'<w:p {W}><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/>'
            f'</w:numPr><w:spacing w:after="80" w:line="276" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>'
            f'{runs(text)}</w:p>')


_bm = [500]


def heading_p(level, text, first=False):
    _bm[0] += 1
    br = '<w:r><w:br w:type="page"/></w:r>' if level == 1 and not first else ''
    return (f'<w:p {W}><w:pPr><w:pStyle w:val="Heading{level}"/><w:keepNext/><w:keepLines/></w:pPr>{br}'
            f'<w:bookmarkStart w:id="{_bm[0]}" w:name="_Toc9{_bm[0]:05d}"/><w:r><w:t xml:space="preserve">'
            f'{escape(text)}</w:t></w:r><w:bookmarkEnd w:id="{_bm[0]}"/></w:p>')


def eq_p(text, num):
    return (f'<w:p {W}><w:pPr><w:tabs><w:tab w:val="center" w:pos="4535"/><w:tab w:val="right" w:pos="9071"/>'
            f'</w:tabs><w:spacing w:before="60" w:after="120"/></w:pPr><w:r><w:tab/></w:r>'
            f'{runs(text, base="<w:i/><w:iCs/>")}<w:r><w:tab/></w:r><w:r><w:t>({num})</w:t></w:r></w:p>')


def caption_p(text):
    return (f'<w:p {W}><w:pPr><w:spacing w:before="80" w:after="160"/><w:jc w:val="center"/></w:pPr>'
            f'{runs(text, base="<w:i/><w:iCs/>", size=24)}</w:p>')


def code_p(line, first, last):
    sp = f'<w:spacing w:before="{80 if first else 0}" w:after="{80 if last else 0}" w:line="240" w:lineRule="auto"/>'
    return (f'<w:p {W}><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>{sp}'
            f'<w:ind w:left="284" w:right="284"/></w:pPr><w:r><w:rPr>'
            f'<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>'
            f'<w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr><w:t xml:space="preserve">{escape(line) or " "}</w:t>'
            f'</w:r></w:p>')


def cell(text, width, fill, header=False, align=None, bold=False):
    mar = 80 if header else 60
    jc = '<w:jc w:val="center"/>' if header or align == 'c' else '<w:jc w:val="right"/>' if align == 'r' else ''
    base = '<w:b/><w:bCs/><w:color w:val="FFFFFF"/>' if header else ('<w:b/><w:bCs/>' if bold else '')
    paras = ''.join(f'<w:p><w:pPr><w:keepNext/>{jc}</w:pPr>{runs(line, base=base, size=24)}</w:p>'
                    for line in str(text).split('\n'))
    return (f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/><w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
            f'<w:tcMar><w:top w:w="{mar}" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>'
            f'<w:bottom w:w="{mar}" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tcMar>'
            f'<w:vAlign w:val="center"/></w:tcPr>{paras}</w:tc>')


def table_xml(header, rows, widths, align, bold_last):
    b = ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="AAAAAA"/>'
                for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
    grid = ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    align = align or [None] * len(widths)
    trs = ['<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' +
           ''.join(cell(h, w, HEAD_FILL, header=True) for h, w in zip(header, widths)) + '</w:tr>']
    for i, r in enumerate(rows):
        fill = 'FFFFFF' if i % 2 == 0 else ALT_FILL
        bold = bold_last and i == len(rows) - 1
        trs.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>' +
                   ''.join(cell(c, w, fill, align=a, bold=bold) for c, w, a in zip(r, widths, align)) + '</w:tr>')
    return (f'<w:tbl {W}><w:tblPr><w:tblW w:w="{CONTENT_W}" w:type="dxa"/><w:jc w:val="center"/>'
            f'<w:tblBorders>{b}</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblLook w:val="04A0" '
            f'w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>'
            f'</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(trs)}</w:tbl>')


def plain_p(text, size=None, bold=False, center=False, after=80, page_break=False):
    base = '<w:b/><w:bCs/>' if bold else ''
    jc = '<w:jc w:val="center"/>' if center else ''
    br = '<w:r><w:br w:type="page"/></w:r>' if page_break else ''
    return f'<w:p {W}><w:pPr><w:spacing w:after="{after}"/>{jc}</w:pPr>{br}{runs(text, base=base, size=size)}</w:p>'


def toc_p(level, text, page, first=False, last=False):
    st = f'TOC{level}'
    b = '<w:b/><w:bCs/>' if level == 1 else ''
    fld = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" '
           '\\h \\z \\u </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>') if first else ''
    end = '<w:r><w:fldChar w:fldCharType="end"/></w:r>' if last else ''
    return (f'<w:p {W}><w:pPr><w:pStyle w:val="{st}"/><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9061"/>'
            f'</w:tabs></w:pPr>{fld}<w:r><w:rPr>{b}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'
            f'<w:r><w:rPr>{b}</w:rPr><w:tab/></w:r><w:r><w:rPr>{b}</w:rPr><w:t>{page}</w:t></w:r>{end}</w:p>')


# ============================================================================ dựng file
def resolve(text, labels):
    return re.sub(r'\{(?:T|F|E):(\w+)\}', lambda m: labels[m.group(1)], text)


def build(D, abbrev, cover, pages=None):
    pages = pages or {}
    d = docx.Document(str(TEMPLATE))
    body = d.element.body
    els = list(body.iterchildren())
    sect_final = els[-1]
    # giữ trang bìa (phần tử 0..21, có sectPr của section bìa), xóa phần còn lại
    for el in els[22:-1]:
        body.remove(el)
    # sửa chữ trên bìa
    for idx, new in cover.items():
        p = els[idx]
        rs = p.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
        ts = [t for r in rs for t in r.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')]
        ts[0].text = new
        for t in ts[1:]:
            t.getparent().remove(t)

    def add(xml):
        sect_final.addprevious(parse_xml(xml))

    # ---- mục lục
    add(plain_p('MỤC LỤC', size=30, bold=True, center=True, after=200))
    heads = [(b[1], b[2]) for b in D.blocks if b[0] == 'h']
    for i, (lvl, t) in enumerate(heads):
        add(toc_p(lvl, t, pages.get(t, ''), first=i == 0, last=i == len(heads) - 1))
    # ---- từ viết tắt
    add(plain_p('DANH MỤC TỪ VIẾT TẮT', size=28, bold=True, center=True, after=200, page_break=True))
    add(table_xml(['Viết tắt', 'Tiếng Anh', 'Ý nghĩa'], abbrev, [1500, 3700, 3871], None, False))
    # ---- danh mục hình, bảng
    add(plain_p('DANH MỤC HÌNH VẼ', size=28, bold=True, center=True, after=200, page_break=True))
    for f in D.figures:
        add(plain_p(f, size=24))
    add(plain_p('DANH MỤC BẢNG BIỂU', size=28, bold=True, center=True, after=200, page_break=True))
    for t in D.tables:
        add(plain_p(t, size=24))
    # ---- nội dung
    for b in D.blocks:
        kind = b[0]
        if kind == 'h':
            add(heading_p(b[1], b[2]))
        elif kind == 'p':
            add(body_p(resolve(b[1], D.labels), b[2]))
        elif kind == 'li':
            add(li_p(resolve(b[1], D.labels)))
        elif kind == 'eq':
            add(eq_p(b[1], b[2]))
        elif kind == 'tbl':
            _, header, rows, widths, cap, align, bold_last = b
            add(table_xml(header, rows, widths, align, bold_last))
            add(caption_p(cap))
        elif kind == 'fig':
            _, path, width, cap = b
            para = d.add_paragraph()                 # python-docx chèn trước sectPr cuối
            para.add_run().add_picture(str(ROOT / path), width=Cm(width))
            ppr = parse_xml(f'<w:pPr {W}><w:keepNext/><w:spacing w:before="120" w:after="0"/>'
                            f'<w:jc w:val="center"/></w:pPr>')
            para._p.insert(0, ppr)
            add(caption_p(cap))
        elif kind == 'code':
            lines = b[1].split('\n')
            for i, line in enumerate(lines):
                add(code_p(line, i == 0, i == len(lines) - 1))
        elif kind == 'ref':
            add(f'<w:p {W}><w:pPr><w:spacing w:after="100" w:line="276" w:lineRule="auto"/>'
                f'<w:ind w:left="567" w:hanging="567"/><w:jc w:val="both"/></w:pPr>{runs(b[1])}</w:p>')
        elif kind == 'pb':
            add(f'<w:p {W}><w:r><w:br w:type="page"/></w:r></w:p>')
    d.core_properties.title = 'Báo cáo BTL — Misconception Clustering'
    d.core_properties.author = ''
    d.save(str(OUT))
    return OUT


def page_map(D, pdf):
    """Số trang (đánh số liên tục từ bìa = 1) của từng đầu mục, tìm tuần tự trong PDF."""
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout)[1])
    texts = [re.sub(r'\s+', '', subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), '-layout', pdf, '-'],
                                                capture_output=True, text=True).stdout) for i in range(1, n + 1)]
    heads = [b[2] for b in D.blocks if b[0] == 'h']
    first = heads[0]
    start = max(i for i, t in enumerate(texts) if re.sub(r'\s+', '', first) in t)   # bỏ qua trang mục lục
    pages, cur = {}, start
    for h in heads:
        key = re.sub(r'\s+', '', h)
        for i in range(cur, n):
            if key in texts[i]:
                pages[h], cur = i + 1, i
                break
    return pages, n


def render_pdf(path):
    outdir = ROOT / 'work' / 'report'
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', str(outdir), str(path)],
                   check=True, capture_output=True)
    return str(outdir / (path.stem + '.pdf'))


if __name__ == '__main__':
    import content
    D = content.make()
    build(D, content.ABBREV, content.COVER)
    pages, n = page_map(D, render_pdf(OUT))
    build(D, content.ABBREV, content.COVER, pages)
    pdf = render_pdf(OUT)
    pages2, n2 = page_map(D, pdf)
    miss = [h for h in (b[2] for b in D.blocks if b[0] == 'h') if h not in pages2]
    diff = {h: (pages.get(h), p) for h, p in pages2.items() if pages.get(h) != p}
    print(f'{OUT.name}: {n2} trang, {len(D.tables)} bảng, {len(D.figures)} hình; '
          f'đầu mục không tìm thấy: {miss}; lệch số trang sau lượt 2: {diff}')
