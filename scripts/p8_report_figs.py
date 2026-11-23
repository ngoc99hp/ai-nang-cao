"""P8: Hình cho báo cáo: sơ đồ quy trình tổng thể (results/figures/pipeline.png)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import config

INK, MUTED, EDGE = '#1f2937', '#4b5563', '#1F4E79'
FILL = {'data': '#e8eef6', 'step': '#ffffff', 'out': '#f2f2f2'}
fig, ax = plt.subplots(figsize=(11, 4.6), dpi=200)
ax.set_xlim(0, 110); ax.set_ylim(0, 46); ax.axis('off')


def box(x, y, w, h, title, sub, kind='step'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.4,rounding_size=1.2', linewidth=1.2,
                                edgecolor=EDGE, facecolor=FILL[kind]))
    ax.text(x + w / 2, y + h - 2.4, title, ha='center', va='top', fontsize=9.5, fontweight='bold', color=INK)
    ax.text(x + w / 2, y + h - 6.2, sub, ha='center', va='top', fontsize=7.6, color=MUTED, linespacing=1.35)


def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=11, linewidth=1.1,
                                 color=EDGE, shrinkA=2, shrinkB=2))


# hàng dữ liệu
box(1, 31, 20, 13, 'IntroClass', '1.143 phiên bản C\n6 bài, test blackbox\n+ whitebox', 'data')
box(1, 16, 20, 13, 'Bài cấy lỗi', 'lời giải đúng + 19 lời giải\ntự viết → đột biến AST\n480 mutant nhãn M1–M8', 'data')
box(1, 1, 20, 13, 'ITSP', '661 cặp bài sai /\nbản tự sửa đúng', 'data')
# chuỗi xử lý
box(26, 20, 18, 24, '① Chấm bài', 'container cách ly\n(không mạng, ulimit\nCPU/RAM/output)\n\nstrict + semantic\nlọc, khử trùng\n→ 279 bài sai thật')
box(48, 20, 18, 24, '② Trích OAV', 'Đối tượng–Thuộc tính\n–Giá trị\n\nT  test trượt\nO  kiểu sai output\nA  cấu trúc AST\nD  khác bản đúng')
box(70, 20, 18, 24, '③ Gom cụm', 'Hamming có trọng số\n(O 0.5 · A 0.5 · D 3)\n\nK-modes (chính)\nAgglomerative\nK-means one-hot')
box(92, 20, 17, 24, '④ Sinh luật', 'ILA (tự cài đặt)\nso sánh ID3\n\nNẾU … THÌ\nnhóm lỗi k')
# đầu ra
box(48, 1, 40, 11, 'Đánh giá', 'E1–E3: ARI/NMI/Purity trên bài cấy lỗi · E4: silhouette + đọc cụm\nE4b: ITSP đối chiếu nhãn tay · E5: chất lượng luật', 'out')
box(92, 1, 17, 11, '⑤ Macro-feedback', 'bảng cho giảng viên\n+ giao diện demo', 'out')
arrow(21.8, 37.5, 25.6, 37.5)
arrow(21.8, 22.5, 25.6, 26)
arrow(21.8, 7.5, 47.6, 7.5)
arrow(44.6, 32, 47.6, 32); arrow(66.6, 32, 69.6, 32); arrow(88.6, 32, 91.6, 32)
arrow(100.5, 19.6, 100.5, 12.6); arrow(79, 19.6, 72, 12.6)
fig.tight_layout()
out = config.FIGURES / 'pipeline.png'
fig.savefig(out, bbox_inches='tight', facecolor='white')
print(out)
