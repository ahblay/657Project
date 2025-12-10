import subprocess
from pathlib import Path
from pprint import pp
import os

def segclobber(position, player):
    binary_path = os.environ.get(
        "SEGCLOBBER_BINARY",
        str(Path(__file__).parent / "bin" / "segclobber")
    )
    binary = Path(binary_path)
    cwd = binary.parent

    result = subprocess.run(
        [str(binary), str(position), str(player)],
        capture_output=True,
        text=True,
        check=True,
        timeout=100,
        cwd=cwd
    )

    winning_player = result.stdout[0]
    return winning_player

def get_outcome_class(position):
    if position == "":
        return "P"
    position = position.replace("x", "B").replace("o", "W")
    left_can_win = True if segclobber(position, "B") == "B" else False
    right_can_win = True if segclobber(position, "W") == "W" else False

    if left_can_win and right_can_win:
        return "N"
    if left_can_win and not right_can_win:
        return "L"
    if not left_can_win and right_can_win:
        return "R"
    if not left_can_win and not right_can_win:
        return "P"

def compute_base_cases(pattern, q, length):
    prefix, suffix = pattern.split("_")
    result = {}
    for i in range(length):
        g = f"{prefix}{q*i}{suffix}"
        result[g] = get_outcome_class(g)
    return result

def evaluate_base_cases(pattern, base_cases):
    result = {}
    games = sorted(base_cases.keys(), key=len)
    for g in games:
        if len(set(base_cases.values())) == 1:
            result[pattern] = base_cases[g]
            break
        result[g] = base_cases[g]
        base_cases.pop(g)
    return result

def compute_all_base_cases(patterns, small_games, q, amount):
    result = {}
    small = {}
    for pattern in patterns:
        small[pattern] = []
        base_cases = compute_base_cases(pattern, q, amount)
        simplified_base_cases = evaluate_base_cases(pattern, base_cases)
        #result.update(simplified_base_cases)
        inductive_hypothesis = simplified_base_cases[pattern]
        for game, outcome in simplified_base_cases.items():
            if game == pattern:
                result[game] = outcome
            if outcome != inductive_hypothesis:
                result[game] = outcome
                small[pattern].append(game)
    for small_game in small_games:
        result[small_game] = get_outcome_class(small_game)
    return result, small

if __name__ == "__main__":
    g = "o_o"
    q = "xxo"
    all_states = ['_', '_o', '_x', '_xo', '_xx', '_xxx', 'o_', 'o_o', 'o_x', 'o_xo', 'oo_o', 'oo_x', 'oo_xo', 'oxo_x', 'oxo_xo', 'x_', 'x_o', 'x_x', 'x_xo', 'x_xxx', 'xo_x']
    #bc, sbc = compute_all_base_cases(all_states, [], q, 10)    
    #pp(bc)    
    #pp(sbc)

    print(get_outcome_class("xooxxxxxxxxxxxxxxxxxxxxxxxxox"))