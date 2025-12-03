from pprint import pp

data = {
    "_": [""],
    "_o": ["o", "xxoo"],
    "_x": ["x", "xxox", "xxoxxox", "xxoxxoxxox", "xxoxxoxxoxxox", "xxoxxoxxoxxoxxox"],
    "_xo": ["xo", "xxoxo", "xxoxxoxo", "xxoxxoxxoxo"],
    "_xx": ["xx"],
    "_xxx": ["xxx"],
    "o_": ["o", "oxxo"],
    "o_o": ["oo", "oxxoxxoo"],
    "o_x": ["ox", "oxxoxxox", "oxxoxxoxxoxxox"],
    "o_xo": ["oxo", "oxxoxo", "oxxoxxoxo"],
    "oo_o": ["ooo", "ooxxoo", "ooxxoxxoxxoo"],
    "oo_x": ["oox", "ooxxox", "ooxxoxxox", "ooxxoxxoxxox", "ooxxoxxoxxoxxoxxox"],
    "oo_xo": ["ooxo", "ooxxoxo", "ooxxoxxoxo", "ooxxoxxoxxoxo"],
    "oxo_x": ["oxox", "oxoxxoxxox"],
    "oxo_xo": ["oxoxxoxo"],
    "x_": ["x"],
    "x_o": ["xo", "xxxoo"],
    "x_x": ["xx", "xxxox"],
    "x_xo": ["xxxoxo", "xxxoxxoxxoxo"],
    "x_xxx": ["xxxx"],
    "xo_x": ["xox", "xoxxox", "xoxxoxxox", "xoxxoxxoxxox", "xoxxoxxoxxoxxox"]
}

result = {}

for key, values in data.items():
    result[key] = ""

pp(result)