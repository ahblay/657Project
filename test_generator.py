import pytest
import generator

def normalize(obj):
    """
    Recursively convert lists to frozensets so ordering does not matter.
    """
    if isinstance(obj, list):
        return frozenset(normalize(x) for x in obj)
    return obj

def split_p_s(item: str):
    p, s = item.split("_", 1)
    return tuple(p), tuple(s)

@pytest.mark.parametrize("q, pieces, expected", [
    ("", [], set()),
    ("", ["x"], set()),
    ("x", [], set()),
    ("x", ["x"], set()),
    ("x", ["o"], {"o", ""}),
    ("x", ["oo"], set()),
    ("xoxo", [], {"xxo", "oo", "xo", "x", "o", ""}),
    ("xoxo", ["x", "o"], {"xxo", "oo", "xo", "x", "o", "ooxo", "oxo", ""})
])
def test_simulate_move(q, pieces, expected):
    q = tuple(q)
    expected = {tuple(p) for p in expected}
    assert generator.simulate_move(q, pieces) == expected

@pytest.mark.parametrize("prefixes, q, expected", [
    ({"", "xoxo", "o", "xo"}, "x", {"", "xoxo", "xxo", "xo", "oo", "o", "x"}),
    (set(), "xxo", {"", "x", "xo", "oxo"}),
    ({"x", "o"}, "xxo", {"", "x", "xo", "oxo", "o"}),
    ({"xxoo", "xoxo"}, "", {"o", "xo", "xxo", "oo", "xo", "x", "xxoo", "xoxo", ""}),
    ({"xxo"}, "ox", {"o", "x", "xx", "xxo", ""}),
    ({"xo"}, "", {"x", "", "xo"}),
    (set(), "", {})
])
def test_get_prefixes(prefixes, q, expected):
    q = tuple(q)
    prefixes = {tuple(p) for p in prefixes}
    expected = {tuple(p) for p in expected}
    assert generator.get_prefixes(prefixes, q) == expected

@pytest.mark.parametrize("suffixes, q, expected", [
    ({"", "xoxo", "o", "xo"}, "x", {"", "xoxo", "o", "xo", "xx", "xoo", "x"}),
    (set(), "xxo", {"x", "xo", "xxx", "xx"}),
    ({"x", "o"}, "xxo", {"x", "o", "x", "xo", "xxx", "xx"}),
    ({"xxoo", "xoxo"}, "", {"xo", "x", "xx", "o", "xxoo", "xoxo", "xoo", ""}),
    ({"xxo"}, "ox", {"", "oo", "x", "xxo", "o", "xo"}),
    ({"xo"}, "", {"o", "", "xo"}),
    (set(), "", {})
])
def test_get_suffixes(suffixes, q, expected):
    q = tuple(q)
    suffixes = {tuple(p) for p in suffixes}
    expected = {tuple(p) for p in expected}
    assert generator.get_suffixes(suffixes, q) == expected

@pytest.mark.parametrize("pattern, q, expected", [
    ("o", "x", {"x", ""}),
    ("xxox", "x", {"xx", "x", "xo", "xxx"}),
    ("xoxoxo", "xxo", {"xoxoo", "xoxo", "xoxx", "xox", "xoo", "xo", "xx", "x", "o", "", "xoxox", "xoxoxx", "xoxoxox", "xoxoxoxo", "xoxoxoxx", "xoxoxoxxx"}),
    ("xxxooo", "x", {"xxxoox", "xxxoo", "xxo", "xx"}),
    ("", "", {})
])
def test_get_small_positions(pattern, q, expected):
    q = tuple(q)
    pattern = tuple(pattern)
    expected = {tuple(p) for p in expected}
    assert generator.get_small_positions(pattern, q) == expected

@pytest.mark.parametrize("prefixes, suffixes, q, expected", [
    ({"o"}, {"o"}, "x", {"x", ""}),
    ({"xxox"}, {"oxxo"}, "x", {"xx", "x", "xo", "xxx", "xxxo", "xxo", "oxo", "xo", ""}),
    ({"x", "o"}, {}, "xxo", {"xxo", "xx", "xxx", "xxxx", "", "x", "ox", "oxo", "oxx", "oxxx", "xo"}),
    ({}, {}, "", {}),
    ({}, {}, "xxo", {"x", "xo", "xx", "xxx", "", "oxo"}),
    ({}, {"o"}, "ox", {"", "x", "o", "oo", "xxo", "xo", "xx"})
])
def test_generate_small_patterns(prefixes, suffixes, q, expected):
    q = tuple(q)
    prefixes = {tuple(p) for p in prefixes}
    suffixes = {tuple(s) for s in suffixes}
    expected = {tuple(p) for p in expected}
    assert generator.generate_small_patterns(prefixes, suffixes, q) == expected

@pytest.mark.parametrize("prefixes, suffixes, q, p, s", [
    ({}, {}, "xxo", {"", "x", "o", "xo", "oo", "oxo"}, {"", "x", "o", "xo", "xx", "xxx"})
])
def test_generate_patterns(prefixes, suffixes, q, p, s):
    q = tuple(q)
    prefixes = {tuple(p) for p in prefixes}
    suffixes = {tuple(s) for s in suffixes}
    p = {tuple(i) for i in p}
    s = {tuple(i) for i in s}
    pfxs, sfxs, sm = generator.generate_patterns(prefixes, suffixes, q)
    small = generator.generate_small_patterns(pfxs, sfxs, q)
    assert generator.generate_patterns(prefixes, suffixes, q) == (p, s, small)

@pytest.mark.parametrize("prefixes, suffixes, q, expected", [
    ({"o"}, {""}, "xxo", [["o_", "o_"]])
    #({"x", "oo"}, {"o", "xxx"}, "xxo", [["oo_o", "oo_o"], ["oo_xxx", "x_o"], ["x_xxx", "x_xxx"], ["x_o", "oo_xxx"]])
])
def test_find_symmetries_xxo(prefixes, suffixes, q, expected):
    q = tuple(q)
    prefixes = {tuple(p) for p in prefixes}
    suffixes = {tuple(s) for s in suffixes}
    expected = [[split_p_s(item) for item in group] for group in expected]
    assert generator.find_symmetries_xxo(prefixes, suffixes, q) == expected

@pytest.mark.parametrize("state, pattern, prefixes, suffixes, expected", [
    ("xo_ox", "x", {"xo"}, {"ox"}, "P"),
    ("xoxoo_", "x", {"xoxoo"}, {""}, "N"),
    ("o_", "x", {"o"}, {""}, "L"),
    ("_", "x", {""}, {""}, "P")
])
def test_run(state, pattern, prefixes, suffixes, expected):
    prefixes = {tuple(p) for p in prefixes}
    suffixes = {tuple(s) for s in suffixes}
    assert generator.run(state, pattern, prefixes, suffixes, None) == expected 
  