import pytest
import tree

def normalize(l):
    result = []
    for item in l:
        result.append(sorted(list(set(item))))
    return sorted(result)

@pytest.mark.parametrize("position, q, expected", [
    ("_", "xxo", {('x', 'x_')}),
    ("xx_", "xxo", {('xxx', 'x_')}),
    ("o_o", "xxo", {('ox', 'x_o')}),
    ("xo_", "xxo", {('', 'x_')})
])
def test_xxo_conjecture(position, q, expected):
    assert normalize(tree.xxo_conjecture(position, q)) == normalize(expected)

@pytest.mark.parametrize("children, expected", [
    ({('x_', 'xxx'), ('_xxx', '_x'), ('x', '_xxx')}, {('_x', '_xxx'), ('x_', 'xxx')}),
    ({('xxx', '_x'), ('_x', '_xxx'), ('x', '_xxx')}, {('_x', '_xxx')}),
    ({('x_', 'xx_oo'), ('x', 'xxoo'), ('x', 'xx_oo'), ('x_', 'xxoo')}, {('x_', 'xx_oo')}),
    ({('_', 'x_x'), ('xx_', '_')}, {('_', 'x_x'), ('xx_', '_')}),
    ({('x', 'x'), ('x_', 'x_')}, {('x_', 'x_')})
])
def test_clean(children, expected):
    assert normalize(tree.clean(children)) == normalize(expected)

@pytest.mark.parametrize("s, term, lb, ub, expected", [
    ("xxoxxo", "xxo", 0, 6, "_"),
    ("xxoxoxxxoxxoxxoooxxo", "xxo", 6, 15, "xxoxox_ooxxo"),
    ("xoxxxoxxoxxoooxxo", "xxo", 3, 12, "xox_ooxxo")
])
def test_reduce(s, term, lb, ub, expected):
    assert tree.reduce(s, term, lb, ub) == expected