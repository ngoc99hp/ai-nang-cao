"""ILA — Inductive Learning Algorithm (Tolun & Abu-Soud, 1998), tự cài đặt.

Học có giám sát: quy nạp luật NẾU–THÌ từ bảng thuộc tính rời rạc; ở đây lớp = cluster_id.
Với từng lớp j (bảng con), tăng dần số thuộc tính c = 1..max_c:
  - xét mọi tổ hợp c thuộc tính; tìm tổ hợp GIÁ TRỊ xuất hiện ở các dòng CHƯA ĐÁNH DẤU của lớp j
    nhưng KHÔNG xuất hiện ở bất kỳ dòng nào của lớp khác; chọn tổ hợp xuất hiện nhiều nhất;
  - sinh luật, đánh dấu các dòng của lớp j khớp luật; lặp lại với cùng c đến khi không còn tổ hợp;
  - dừng khi mọi dòng của lớp j đã được đánh dấu.
Theo cấu tạo, mọi luật nhất quán 100% trên tập huấn luyện. Dòng không phủ được với c ≤ max_c
được báo là 'uncovered'.
"""
from dataclasses import dataclass
from itertools import combinations

import numpy as np
import pandas as pd


@dataclass
class Rule:
    conds: tuple            # ((attr, value), ...)
    cls: object
    n_cls: int              # số dòng của lớp khớp luật (toàn bộ, không chỉ dòng chưa đánh dấu)
    n_match: int            # số dòng (mọi lớp) khớp luật
    cls_size: int

    @property
    def coverage(self) -> float:
        return self.n_cls / self.cls_size

    @property
    def accuracy(self) -> float:
        return self.n_cls / self.n_match if self.n_match else 0.0

    def matches(self, X: pd.DataFrame) -> np.ndarray:
        m = np.ones(len(X), bool)
        for a, v in self.conds:
            m &= (X[a].values == v)
        return m

    def fmt(self, name=None, attr_fmt=str, cls_fmt=str) -> str:
        lhs = ' VÀ '.join(f'[{attr_fmt(a)} = {v}]' for a, v in self.conds)
        return (f'{name + ": " if name else ""}NẾU {lhs} THÌ {cls_fmt(self.cls)} '
                f'[coverage {self.n_cls}/{self.cls_size}, accuracy {self.accuracy:.2f}]')


def _keys(codes: np.ndarray, attrs: tuple, radix: np.ndarray) -> np.ndarray:
    """Mã hóa tổ hợp giá trị trên attrs thành 1 số nguyên/dòng."""
    k = np.zeros(codes.shape[0], np.int64)
    for a in attrs:
        k = k * radix[a] + codes[:, a]
    return k


def fit(X: pd.DataFrame, y, max_c: int = 3) -> tuple[list[Rule], dict]:
    """→ (rules, info). X: thuộc tính categorical (chuỗi); y: nhãn lớp."""
    y = np.asarray(y)
    cols = list(X.columns)
    enc = [pd.factorize(X[c]) for c in cols]
    codes = np.column_stack([e[0] for e in enc]).astype(np.int64)
    radix = np.array([len(e[1]) + 1 for e in enc], np.int64)
    rules, uncovered = [], {}
    for cls in pd.unique(y):
        in_cls = y == cls
        unmarked = in_cls.copy()
        for c in range(1, max_c + 1):
            if not unmarked.any():
                break
            combos = list(combinations(range(len(cols)), c))
            # khóa của lớp khác (cố định cho mỗi tổ hợp) — tính một lần cho mức c
            other_keys = {at: set(_keys(codes[~in_cls], at, radix).tolist()) for at in combos}
            while unmarked.any():
                best = None                                   # (count, attrs, key)
                for at in combos:
                    k = _keys(codes[unmarked], at, radix)
                    ok = ~np.isin(k, list(other_keys[at])) if other_keys[at] else np.ones(len(k), bool)
                    if not ok.any():
                        continue
                    vals, cnt = np.unique(k[ok], return_counts=True)
                    i = int(np.argmax(cnt))
                    if best is None or cnt[i] > best[0]:
                        best = (int(cnt[i]), at, vals[i])
                if best is None:
                    break
                _, at, key = best
                hit_all = _keys(codes, at, radix) == key
                row = np.flatnonzero(hit_all & unmarked)[0]
                conds = tuple((cols[a], X.iloc[row, a]) for a in at)
                rules.append(Rule(conds, cls, int((hit_all & in_cls).sum()), int(hit_all.sum()),
                                  int(in_cls.sum())))
                unmarked &= ~hit_all
        if unmarked.any():
            uncovered[cls] = int(unmarked.sum())
    return rules, {'uncovered': uncovered, 'n_rules': len(rules)}


def predict(rules: list[Rule], X: pd.DataFrame, default=None) -> np.ndarray:
    """Luật đầu tiên khớp (theo thứ tự sinh); không khớp → default."""
    out = np.full(len(X), default, dtype=object)
    done = np.zeros(len(X), bool)
    for r in rules:
        m = r.matches(X) & ~done
        out[m] = r.cls
        done |= m
    return out
