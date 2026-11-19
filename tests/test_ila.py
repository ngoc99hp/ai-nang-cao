import pandas as pd

import ila

# Bộ dữ liệu "object classification" trong bài báo ILA gốc (Tolun & Abu-Soud 1998)
X = pd.DataFrame({
    'size':  ['medium', 'small', 'small', 'large', 'large', 'large', 'medium'],
    'color': ['blue', 'red', 'red', 'red', 'green', 'red', 'green'],
    'shape': ['brick', 'wedge', 'sphere', 'wedge', 'pillar', 'pillar', 'sphere'],
})
y = ['yes', 'no', 'yes', 'no', 'yes', 'no', 'yes']


def test_rules_consistent_and_complete():
    rules, info = ila.fit(X, y)
    assert info['uncovered'] == {}
    assert all(r.accuracy == 1.0 for r in rules)          # nhất quán trên tập huấn luyện
    assert (ila.predict(rules, X) == y).all()


def test_paper_rules():
    rules, _ = ila.fit(X, y)
    got = {(r.conds, r.cls) for r in rules}
    # Kết quả trong bài báo: size=medium→yes, color=green→yes, shape=sphere→yes, shape=wedge→no,
    #                        size=large & color=red→no (5 luật)
    assert ((('shape', 'wedge'),), 'no') in got
    assert ((('color', 'green'),), 'yes') in got
    assert ((('size', 'large'), ('color', 'red')), 'no') in got
    assert len(rules) == 5


def test_fmt():
    rules, _ = ila.fit(X, y)
    s = rules[0].fmt('R1')
    assert s.startswith('R1: NẾU [') and 'THÌ' in s and 'coverage' in s
