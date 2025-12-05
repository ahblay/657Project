from pprint import pp
from collections import defaultdict
from json import dumps, dump
from node import Node
from itertools import product

# TODO: start by simply traversing all game patterns and stopping when each has been seen twice

def jsonify(positions, small_games, start, json, depth, SEEN, PROVEN, MAX_DEPTH=0):
    MAX_DEPTH = max(depth, MAX_DEPTH)
    if start in SEEN or start not in positions.keys():
        return json, MAX_DEPTH
    SEEN.add(start)
    piece = 'x' if depth % 2 == 0 else 'o'
    for subgame in positions[start][piece]:
        for idx in range(len(subgame)):
            component = subgame[idx]
            if component in PROVEN:
                continue
            d = defaultdict(dict)
            child_dict, MAX_DEPTH = jsonify(positions, small_games, component, d, depth+1, SEEN, PROVEN, MAX_DEPTH)
            json[start][component] = child_dict
            if component in small_games.keys():
                for small_game in small_games[component]:
                    # TODO: small_game should be tuple with other component
                    small_game_tuple = subgame[:idx] + (small_game,) + subgame[idx+1:]
                    json[start][small_game] = {}
            readable_json = dumps(json)
    SEEN.remove(start)
    #PROVEN.add(start)
    return json[start], MAX_DEPTH

def prover(positions, small_games, start, values, depth, SEEN, PROVEN, MAX_DEPTH=0):
    MAX_DEPTH = max(depth, MAX_DEPTH)
    if start in small_games.keys():
        return small_games[start], MAX_DEPTH
    if start in SEEN or start not in positions.keys():
        if start in values.keys():
            return values[start], MAX_DEPTH
        else:
            return "U", MAX_DEPTH
    SEEN.add(start)
    piece = 'x' if depth % 2 == 0 else 'o'
    total = "P"
    best = ''
    # iterate over every subgame pair resulting from a move in start
    for subgame in positions[start][piece]:
        # outcome class of each sumgame pair
        sumgame = ""
        for idx in range(len(subgame)):
            component = subgame[idx]
            if component in PROVEN:
                continue
            value, MAX_DEPTH = prover(positions, small_games, component, values, depth+1, SEEN, PROVEN, MAX_DEPTH)
            sumgame = outcome_add(sumgame, value)
        best = best_outcome(best, sumgame, piece)
    total = outcome_add(total, best)
    SEEN.remove(start)
    #PROVEN.add(start)
    return best, MAX_DEPTH

def evaluate(state, game_dict, base_cases, depth, memo=None, path_visited=None):
    if memo is None:
        memo = {}
    if path_visited is None:
        path_visited = set()

    if state in memo:
        return Node(state, memo[state])
    
    if "_" not in state:
        return Node(state, base_cases[state])

    # apply inductive hypothesis
    if state in path_visited:
        return Node(state, base_cases[state])

    # mark this node as visited along the current path
    path_visited.add(state)

    # recursively evaluate all options
    left_children_x = []
    right_children_x = []
    x_values = []
    for sub1, sub2 in game_dict[state].get('x', []):
        child1 = evaluate(sub1, game_dict, base_cases, depth+1, memo, path_visited)
        child2 = evaluate(sub2, game_dict, base_cases, depth+1, memo, path_visited)
        x_values.append(outcome_add(child1.value, child2.value))
        left_children_x.append(child1)
        right_children_x.append(child2)

    left_children_o = []
    right_children_o = []
    o_values = []
    for sub1, sub2 in game_dict[state].get('o', []):
        child1 = evaluate(sub1, game_dict, base_cases, depth+1, memo, path_visited)
        child2 = evaluate(sub2, game_dict, base_cases, depth+1, memo, path_visited)
        o_values.append(outcome_add(child1.value, child2.value))
        left_children_o.append(child1)
        right_children_o.append(child2)

    # compute outcoem class
    values = []
    #print(f"o_vals: {o_values}")
    #print(f"x_vals: {x_values}")
    for expanded_x_values in expand_outcomes(x_values):
        for expanded_o_values in expand_outcomes(o_values):
            position = {'left': expanded_x_values, 'right': expanded_o_values}
            value = compute_value(position)
            values.append(value)
    #print(values)

    # temporary for testing
    if len(set(values)) == 1:
        value = values[0]
    else:
        value = "U"

    proof_node = Node(state, value)
    proof_node.left_children_x = left_children_x
    proof_node.right_children_x = right_children_x
    proof_node.left_children_o = left_children_o
    proof_node.right_children_o = right_children_o

    memo[state] = value

    path_visited.remove(state)

    return proof_node

def expand_outcomes(outcome_list):
    normalized_list = [outcome if type(outcome) == list else [outcome] for outcome in outcome_list]
    return [list(outcome) for outcome in product(*normalized_list)]

def compute_value(position):
    if "L" in position["left"] or "P" in position["left"]:
        left_can_win = True
    elif "U" in position["left"]:
        left_can_win = None
    else:
        left_can_win = False
    if "R" in position["right"] or "P" in position["right"]:
        right_can_win = True
    elif "U" in position["right"]:
        right_can_win = None
    else:
        right_can_win = False

    if left_can_win is None or right_can_win is None:
        return "U"
    if left_can_win and right_can_win:
        return "N"
    if left_can_win and not right_can_win:
        return "L"
    if not left_can_win and right_can_win:
        return "R"
    if not left_can_win and not right_can_win:
        return "P"
    else:
        return "U"

# best outcome depends on player to move
def best_outcome(a, b, player):
    if player == "x":
        order = ["L", "P", "U", "N", "R", ""]
    else:
        order = ["R", "P", "U", "N", "L", ""]
    if order.index(a) < order.index(b):
        return a
    else:
        return b

# L, N, P, R
def outcome_add(a, b):    
    summands = sorted([a, b])
    #print(summands)
    if summands == ["L", "N"]:
        return summands
    if summands == ["N", "R"]:
        return summands
    if summands[0] == "":
        return summands[1]
    if summands[0] == "P":
        return summands[1]
    if summands[0] == "L":
        if summands[1] in ["P", "L"]:
            return "L"
        else: return "U"
    if summands[0] == "R":
        if summands[1] in ["P", "R"]:
            return "R"
        else: return "U"
    if summands[0] == "N":
        if summands[1] == "P":
            return "N"
        else:
            return "U"
    else:
        return "U"


if __name__ == "__main__":
    game_data = {
        '_': {
            'x': {('_x', 'x_'), ('o_x', '_xxx')}, 
            'o': {('_', '_xo'), ('_xo','xxo'), ('_xx', 'o_xo')}}, 
        'o_o': {
            'x': {('x_', 'oo_x'), ('x', 'oo_x'), ('o_x', 'x_o')}, 
            'o': {('_', 'oo_xo'), ('_o', 'o_xo'), ('', 'oo_xo')}}, 
        'x_': {
            'x': {('o_x', 'x_xxx'), ('x_', 'x_x')}, 
            'o': {('xxo', 'x_xo'), ('_', 'x_xo'), ('_xxx', 'o_xo')}}
        }
    
    d = defaultdict(dict)
    json_game = jsonify(game_data, '_', d, 0, set())

    with open('data.json', 'w', encoding='utf-8') as f:
        dump(json_game, f, ensure_ascii=False, indent=4)