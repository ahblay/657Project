from pprint import pp
from collections import defaultdict
from json import dumps, dump
from node import Node
from itertools import product
from functools import lru_cache

def evaluate(state, game_dict, base_cases, depth, nodes, path_visited=None):
    nodes += 1
    if nodes % 500 == 0:
        print(nodes)

    if path_visited is None:
        path_visited = {}

    if "_" not in state:
        return Node(state, base_cases[state]), nodes

    # apply inductive hypothesis
    if state in path_visited:
        depth_diff = depth - path_visited[state]
        #print(f"state: {state}")
        #print(f"difference in depth: {depth_diff}")
        return Node(state, base_cases[state]), nodes

    # mark this node as visited along the current path
    path_visited[state] = depth

    # recursively evaluate all options
    left_children_x = []
    right_children_x = []
    x_values = set()
    for sub1, sub2 in game_dict[state].get('x', []):
        child1, nodes = evaluate(sub1, game_dict, base_cases, depth+1, nodes, path_visited)
        child2, nodes = evaluate(sub2, game_dict, base_cases, depth+1, nodes, path_visited)
        x_values.add(outcome_add_cached(child1.value, child2.value))
        left_children_x.append(child1)
        right_children_x.append(child2)

    left_children_o = []
    right_children_o = []
    o_values = set()
    for sub1, sub2 in game_dict[state].get('o', []):
        child1, nodes = evaluate(sub1, game_dict, base_cases, depth+1, nodes, path_visited)
        child2, nodes = evaluate(sub2, game_dict, base_cases, depth+1, nodes, path_visited)
        o_values.add(outcome_add_cached(child1.value, child2.value))
        left_children_o.append(child1)
        right_children_o.append(child2)

    # compute outcoem class
    values = []
    #print(f"o_vals: {o_values}")
    #print(f"x_vals: {x_values}")
    for expanded_x_values in expand_outcomes_cached(tuple(x_values)):
        for expanded_o_values in expand_outcomes_cached(tuple(o_values)):
            #position = {'left': expanded_x_values, 'right': expanded_o_values}
            value = compute_value_cached(tuple(expanded_x_values), tuple(expanded_o_values))
            values.append(value)
    #print(values)

    if len(set(values)) == 1:
        value = values[0]
    else:
        value = "U"

    proof_node = Node(state, value)
    proof_node.left_children_x = left_children_x
    proof_node.right_children_x = right_children_x
    proof_node.left_children_o = left_children_o
    proof_node.right_children_o = right_children_o

    #with open(f'json/all_nodes/{state}_proof_node.json', 'w', encoding='utf-8') as f:
    #    dump(proof_node.to_json(), f, ensure_ascii=False, indent=4)

    path_visited.pop(state)

    return proof_node, nodes

@lru_cache(None)
def outcome_add_cached(a, b):
    return outcome_add(a, b)

@lru_cache(None)
def expand_outcomes_cached(values_tuple):
    return expand_outcomes(list(values_tuple))

@lru_cache(None)
def compute_value_cached(left, right):
    position = {"left": list(left), "right": list(right)}
    return compute_value(position)

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
        return tuple(summands)
    if summands == ["N", "R"]:
        return tuple(summands)
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
    