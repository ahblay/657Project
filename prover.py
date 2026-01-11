from pprint import pp
from collections import defaultdict
from json import dumps, dump
from node import Node
from itertools import product
from functools import lru_cache

def proof_tree(state, game_dict, base_cases, path_visited=None):
    '''
    Compute the actual tree searched by the solver.

    :param state: starting position (e.g. "_")
    :param game_dict: dictionary of all positions and their children after all possible x and o-moves
    :param base_cases: dictionary of all values of small positions, and inductive hypotheses for patterns
    :returns node: root node of search tree
    '''
    if path_visited is None: 
        path_visited = set() # this will track whether we have already visited a node on our search

    if "_" not in state: # if state is a small position, get its value
        return Node(state, base_cases[state])

    # apply inductive hypothesis--we have already seen this node on our current path
    if state in path_visited:
        return Node(state, base_cases[state])

    # mark this node as visited along the current path
    path_visited.add(state)

    # recursively evaluate all options
    left_children_x = [] # child nodes
    right_children_x = [] # child nodes
    x_values = set() # all outcome classes resulting from x-moves

    # iterate through all subgames resulting from an x-move
    for sub1, sub2 in game_dict[state].get('x', []):
        child1 = proof_tree(sub1, game_dict, base_cases, path_visited) 
        child2 = proof_tree(sub2, game_dict, base_cases, path_visited)
        result = outcome_add_cached(child1.value, child2.value) # compute the sum of outcome classes
        x_values.add(result)
        left_children_x.append(child1) 
        right_children_x.append(child2)
        if result in ["L", "P"]: # if we find a winning move, stop searching
            break

    left_children_o = [] # child nodes
    right_children_o = [] # child nodes
    o_values = set() # all outcome classes resulting from o-moves
    for sub1, sub2 in game_dict[state].get('o', []):
        child1 = proof_tree(sub1, game_dict, base_cases, path_visited)
        child2 = proof_tree(sub2, game_dict, base_cases, path_visited)
        result = outcome_add_cached(child1.value, child2.value)
        o_values.add(result)
        left_children_o.append(child1)
        right_children_o.append(child2)
        if result in ["R", "P"]:
            break

    # since L + N in {L, N}, we compute outcomes assuming each possibility
    values = []
    # expand all possible outcome combinations
    for expanded_x_values in expand_outcomes_cached(tuple(x_values)): 
        for expanded_o_values in expand_outcomes_cached(tuple(o_values)):
            value = compute_value_cached(tuple(expanded_x_values), tuple(expanded_o_values))
            values.append(value)

    # if all combinations lead to the same outcome, return that outcome
    if len(set(values)) == 1:
        value = values[0]
    else:
        value = "U" # otherwise, return unknown

    # add children to node
    node = Node(state, value)
    node.left_children_x = left_children_x
    node.right_children_x = right_children_x
    node.left_children_o = left_children_o
    node.right_children_o = right_children_o

    path_visited.remove(state)

    return node

def evaluate(state, game_dict, base_cases, depth, nodes, good_moves, path_visited=None):
    '''
    Compute the outcome class.

    :param state: starting position (e.g. "_")
    :param game_dict: dictionary of all positions and their children after all possible x and o-moves
    :param base_cases: dictionary of all values of small positions, and inductive hypotheses for patterns
    :param depth: integer tracking the maximum depth
    :param nodes: total number of nodes visited
    :returns value: outcome class of position
    '''
    nodes += 1
    if nodes % 10000000 == 0:
        print(nodes)
        pp(good_moves)
        write_status("result.txt", nodes) # log status to file

    if path_visited is None:
        path_visited = {}

    if "_" not in state:
        return base_cases[state], nodes

    # if we visited this node, apply inductive hypothesis
    if state in path_visited:
        depth_diff = depth - path_visited[state]
        #print(f"state: {state}")
        #print(f"difference in depth: {depth_diff}")
        return base_cases[state], nodes

    # mark this node as visited along the current path
    path_visited[state] = depth

    # recursively evaluate all options (same functionality as above)
    x_values = set()
    if (state, 'x') not in good_moves.keys():
        good_moves[(state, 'x')] = set()
    sorted_subgames = sort_subgames(game_dict[state].get('x', []), good_moves[(state, 'x')])
    for sub1, sub2 in sorted_subgames:
        val1, nodes = evaluate(sub1, game_dict, base_cases, depth+1, nodes, good_moves, path_visited)
        val2, nodes = evaluate(sub2, game_dict, base_cases, depth+1, nodes, good_moves, path_visited)
        result = outcome_add_cached(val1, val2)
        x_values.add(result)
        if result in ["L", "P"]:
            good_moves[(state, 'x')].add((sub1, sub2))
            break

    o_values = set()
    if (state, 'o') not in good_moves:
        good_moves[(state, 'o')] = set()
    sorted_subgames = sort_subgames(game_dict[state].get('o', []), good_moves[(state, 'o')])
    for sub1, sub2 in sorted_subgames:
        val1, nodes = evaluate(sub1, game_dict, base_cases, depth+1, nodes, good_moves, path_visited)
        val2, nodes = evaluate(sub2, game_dict, base_cases, depth+1, nodes, good_moves, path_visited)
        result = outcome_add_cached(val1, val2)
        o_values.add(result)
        if result in ["R", "P"]:
            good_moves[(state, 'o')].add((sub1, sub2))
            break

    # compute outcome class (same as above)
    values = []
    for expanded_x_values in expand_outcomes_cached(tuple(x_values)):
        for expanded_o_values in expand_outcomes_cached(tuple(o_values)):
            value = compute_value_cached(tuple(expanded_x_values), tuple(expanded_o_values))
            values.append(value)

    if len(set(values)) == 1:
        value = values[0]
    else:
        value = "U"

    path_visited.pop(state)

    return value, nodes

def sort_subgames(all_moves, good_moves):
    all_moves = list(all_moves)
    all_moves.sort(key=lambda t: t not in good_moves)
    return all_moves

# caching specific, frequently used function calls to speed up runtime of evaluate()
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
    '''
    Given a list of outcomes, and possible outcomes (e.g. [L, N]), compute all possible 
    lists of outcomes.
    '''
    normalized_list = [list(outcome) if type(outcome) == tuple else [outcome] for outcome in outcome_list]
    return [list(outcome) for outcome in product(*normalized_list)]

def compute_value(position):
    '''
    Determine the outcome class of a game given the outcome classes of 
    all elements in its left and right sets.
    '''
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

    # uncomment this code for more specific handling of outcome evaluation
    '''
    if left_can_win and right_can_win is None:
        return "L"
    if left_can_win is None and right_can_win:
        return "N"
    '''
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

# DEPECRATED UNUSED FUNCTION
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

def outcome_add(a, b):  
    '''
    Compute the sum of two outcome classes.
    '''  
    summands = sorted([a, b])
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

def write_status(filename, nodes, outcome="incomplete"):
    '''
    Log eval status to file.
    '''
    with open(filename, "w") as f:
        f.write(f"nodes visited: {nodes}\n")
        f.write(f"outcome: {outcome}")


if __name__ == "__main__":
    print(outcome_add("P", "N"))
    