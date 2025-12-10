from itertools import product
from utilities import generate_test_sequence, write_to_file, clear_file
import tree
from pprint import pp
from prover import evaluate, proof_tree, write_status
import json
import segclobber
import os

def simulate_move(q, x):
    '''
    Given a sequence q and a set of pieces x, find all subgames prefixes 
    resulting from a move in q or between x and q. 
    This function *only* determines prefixes of larger positions. Small positions 
    are calculated elsewhere.

    :param q: tuple representing linear clobber position (e.g. ('x', 'x', 'o'))
    :param x: list of clobber pieces (e.g. ['x', 'o'])
    :returns: set of tuples representing all subgame prefixes
    '''
    result = set()

    if not q:
        return result

    # finds +q and -q
    for piece in x: # all pieces that could be to the left of q
        if piece != q[0] and len(piece) == 1: # if a move is possible
            result.add((piece,) + q[1:]) # capturing to the right (+q)
            result.add(q[1:]) # capturing to the left (-q)
   
   # finds q1 (p1)
    for i, item in enumerate(q): # all pieces in q
        if q[i+1:] and item != q[i+1]: # if the subgame to the right of the piece exists and the piece can capture to the right
            result.add((item,) + q[i+2:]) # capturing to the right
            result.add(q[i+2:]) # capturing to the left 
    return result

def get_prefixes(prefixes, q):
    '''
    Given a set of prefix patterns and a repeating pattern q, determine 
    all new prefixes resulting from a move in a prefix, in q, or between 
    the two of them.

    :param prefixes: set of tuples representing all known prefix patterns
    :param q: tuple representing repeating pattern
    :returns: set of tuples each corresponding to a unique prefix pattern
    '''
    result = set()

    x = set() # all pieces that could be to the left of q
    
    for prefix in prefixes: # any prefix could be to the left of q
        if prefix: x.add(prefix[-1]) 
        result.update(simulate_move(prefix, [])) # to avoid multiple loops, get all positions resulting from moving in prefix
        result.add(prefix)
    
    if q:    
        x.add(q[-1]) # q could be to the left of q
        result.update(simulate_move(q, list(x))) # get all positions resulting from moving in q, and between q and x
    return result

def get_suffixes(suffixes, q):
    '''
    Given a set of suffix patterns and a repeating pattern q, returns 
    all suffixes resulting from a move in q, or between a suffix and q.

    :param suffixes: set of tuples representing all known suffix patterns
    :param q: tuple representing repeating pattern
    :returns: set of tuples each corresponding to a unique prefix pattern
    '''
    result = set()
    # get all values that could contribute to q+ and q-
    y = set() # all pieces that could be to the right of q
    
    for suffix in suffixes: # any suffix could be to the right of q
        if suffix: y.add(suffix[0])
        # suffixes resulting from moving in a suffix are equivalent to prefixes resulting from moving in reversed suffix
        moves_in_suffix_reversed = simulate_move(suffix[::-1], []) # all positions resulting from moving in suffix
        # reverse results back
        result.update([s[::-1] for s in moves_in_suffix_reversed])
        result.add(suffix)
   
    if q:
        y.add(q[0]) # q could be to the right of q
        # simulating move in suffix is same as simulating move in reversed prefix and reversing the result
        suffixes = simulate_move(q[::-1], list(y))
        result.update([suffix[::-1] for suffix in suffixes])
    return result

def get_small_positions(pattern, q):
    '''
    Given a prefix and a repeating pattern q, find all of the small positions resulting from 
    a move in the prefix or between the prefix and q.

    :param pattern: tuple representing prefix
    :param q: tuple representing repeating pattern
    :returns small: set of tuples representing all small positions
    '''
    #print(f"pattern: {pattern}")
    #print(f"q: {q}")
    small = set()
    if q and q[-1] != q[0]: # if a move can be made between copies of q
        small.add(pattern + q[:-1]) # capturing to the right
        small.add(pattern + q[:-1] + (q[0],)) # capturing to the left
    pattern = pattern + q
    for i, item in enumerate(pattern): 
        if pattern[i+1:] and item != pattern[i+1]: # if a move is possible
            small.add(pattern[:i]) # capturing to the right
            small.add(pattern[:i] + (pattern[i+1],)) # capturing to the left
    return small

def generate_small_patterns(prefixes, suffixes, q):
    '''
    Given a set of prefixes and suffixes and a repeating pattern q, find 
    all small positions.

    :param prefixes: set of tuples representing suffix patterns
    :param suffixes: set of tuples representing prefix patterns
    :param q: tuple representing repeating pattern
    :returns small: set of tuples representing all small positions
    '''
    small = set()
    for prefix in prefixes:
        small.update(get_small_positions(prefix, q))
    for suffix in suffixes:
        reversed_small_suffixes = get_small_positions(suffix[::-1], q[::-1])
        small.update([s[::-1] for s in reversed_small_suffixes])
    small.update(get_small_positions(tuple(), q))
    reversed_small_q = get_small_positions(tuple(), q[::-1])
    small.update([s[::-1] for s in reversed_small_q])
    return small

def generate_patterns(prefixes, suffixes, q):
    '''
    Determine all prefixes and suffixes from a given set of prefixes, 
    suffixes, and repeating pattern.

    :param prefixes: set of tuples of prefix patterns
    :param suffixes: set of tuples of suffix patterns
    :param q: tuple representing repeating pattern
    :returns prefixes, suffixes: sets of tuples representing complete set of all prefixes and suffixes
    '''
    while True:
        p = get_prefixes(prefixes, q)
        s = get_suffixes(suffixes, q)

        if p == prefixes and s == suffixes:
            break
        else:
            prefixes.update(p)
            suffixes.update(s)
    small = generate_small_patterns(prefixes, suffixes, q)
    return prefixes, suffixes, small

def print_set(s):
    result = []
    for item in s:
        result.append("".join(list(item)))
    print(sorted(result, key=len))

# THIS FUNCTION IS SPECFIC TO THE GAME (xxo)^n
def find_symmetries_xxo(prefixes, suffixes, q):
    '''
    Given a list of prefixes, suffixes and repeating pattern q, find all 
    symmetric positions.

    :param prefixes: set of tuples of prefix patterns
    :param suffixes: set of tuples of suffix patterns
    :param q: tuple representing repeating pattern
    :return result: list of lists of (prefix, suffix) tuples, where each internal list catalogues symmetric positions
    '''
    patterns = list(product(prefixes, suffixes))
    result = []
    for pattern in patterns:
        p = pattern[0]
        s = pattern[1]

        new_p = s[::-1] + ('o',)        
        if new_p[-len(q):] == q:
            new_p = new_p[:-len(q)]

        new_s = ('x', 'x',) + p[::-1]
        if new_s[:len(q)] == q:
            new_s = new_s[len(q):]
        
        if (tuple(new_p), tuple(new_s)) in patterns:
            result.append([(tuple(new_p), tuple(new_s)), pattern])
    return result

# returns a formatted symmetries list that does not identify symmetries
def empty_symmetries(prefixes, suffixes, q):
    '''
    Given a list of prefixes, suffixes and repeating pattern q,
    return a dummy formatted symmetries list, mapping positions to themselves.

    :param prefixes: set of tuples of prefix patterns
    :param suffixes: set of tuples of suffix patterns
    :param q: tuple representing repeating pattern
    :return result: list of lists of (prefix, suffix) tuples, where each internal list catalogues symmetric positions
    '''
    patterns = list(product(prefixes, suffixes))
    result = []
    for pattern in patterns:
        result.append([pattern, pattern])
    return result

def get_symmetries_dict(symmetries):
    '''
    Given a list of symmetric position pairs, return a dictionary mapping 
    longer symmetries to their shorter pairs.

    :param symmetries: list of lists of (prefix, suffix) tuples, where each internal list catalogues symmetric positions
    :returns result: dictionary with keys and values corresponding to symmetric positions (e.g. {"_": "o_xx"})
    '''
    result = {}
    for pair in symmetries:
        simple_pair = []
        for i in pair:
            simple_pair.append("_".join("".join(inner) for inner in i))
        #sorted_pair = sorted(simple_pair, key=len)
        simple_pair.sort(key=lambda s: (len(s), s))
        result[simple_pair[1]] = simple_pair[0]
    return result  

def print_patterns(p):
    '''
    Pretty-printer for pairs of tuples representing prefixes and suffixes.
    '''
    result = []
    for i in p:
        result.append("_".join("".join(inner) for inner in i))
    print(result)
    return

def add_small_positions(game_dict, small_positions):
    '''
    Given a dictionary representing moves from one pattern to another, and a 
    set of irregular small positions for each pattern, add positions corresponding 
    to moves to each irregular position.

    :param game_dict: nested dictionary with positional patterns as keys and subgames as values 
    (e.g. {"_": {
                "x": {
                    ("o_x", "_xxx"), 
                    ("_x", "x_")}, 
                "o": {
                    ("_", "_xo"), 
                    ("_xx", "o_xo")}
                }
            })
    :param small_positions: dictionary with positional patterns as keys, and small irregular
    positions as values (e.g. {"o_x": ["ox", "oxxoxxox", "oxxoxxoxxoxxox"]})        
    :param output: game_dict with small irregular positions included
    (e.g. {"_": {
                "x": {
                    ("o_x", "_xxx"),
                    ("ox", "_xxx"),
                    ("oxxoxxox", "_xxx"),
                    ("oxxoxxoxxoxxox", "_xxx"), 
                    ("_x", "x_")}, 
                "o": {
                    ("_", "_xo"), 
                    ("_xx", "o_xo")}
                }
            })
    '''
    pieces = ["x", "o"]
    output = {}
    for k, v in game_dict.items():
        output[k] = {}
        for piece in pieces:
            sumgames = v[piece] # set of all positions resulting from a move by {piece}
            new_sumgames = set()
            for sumgame in sumgames:
                new_sumgames.add(sumgame)
                for idx in range(2): # iterate through subgames and replace positional patterns with irregular small games
                    if "_" in sumgame[(idx + 1) % 2]:
                        subgame = sumgame[idx % 2]
                        base_cases = small_positions[subgame] if subgame in small_positions else []
                        for position in base_cases:
                            new_sumgames.add((sumgame[(idx + 1) % 2], position))
            output[k][piece] = tuple(new_sumgames)
    return output

def create_cgs_file(pattern_list, q, filename):
    '''
    Deprecated function for writing a .cgs file to calculate outcome 
    classes for small games
    '''
    clear_file(f"/Users/abel/CGScript/{filename}")
    for pattern in pattern_list:
        test_sequence = generate_test_sequence(pattern, q, 12)
        write_to_file(test_sequence, f"/Users/abel/CGScript/{filename}")

def run(state, pattern, p, s, name=None, moves=False):
    '''
    Main function for calculating outcome class.

    :param state: the starting position (e.g. "_")
    :param pattern: the repeating pattern that "_" stands for (e.g. "xxo")
    :param p: a set of prefixes that the position starts with (can be empty)
    :param s: a set of suffixes that the position starts with (can be empty)
    :param name: the name of the folder to save the output to (optional)
    :param moves: flag to optionally load dictionary of moves (optional)
    :returns value: the outcome class of the game
    '''
    q = tuple(pattern)
    
    if moves:
        with open(f'json/{name}/{name}_game_dict.json', 'r') as f:
            game_dict = json.load(f)
    
    else:
        prefixes, suffixes, small = generate_patterns(p, s, q)

        # handle symmetries if input position is "xxo"
        if pattern == "xxo":
            symmetries = find_symmetries_xxo(prefixes, suffixes, q)
        # otherwise use empty symmetries
        else:
            symmetries = empty_symmetries(prefixes, suffixes, q)

        symmetries_dict = get_symmetries_dict(symmetries)
        all_subgames = sorted(list(symmetries_dict.values()))

        # build dictionary of moves from symmetries
        game_dict = {}
        for subgame in all_subgames:
            children = tree.find_moves(subgame, pattern)
            x_cleaned = tree.clean(children['x'])
            x_simplified = tree.simplify(x_cleaned, symmetries_dict)
            o_cleaned = tree.clean(children['o'])
            o_simplified = tree.simplify(o_cleaned, symmetries_dict)

            xxo_conj_simplified = tree.simplify(tree.xxo_conjecture(subgame, pattern), symmetries_dict)

            game_dict[subgame] = {'x': tuple(x_simplified), 'o': tuple(o_simplified)}
   
    # compute small game values automatically with SEGClobber
    base_cases, small = segclobber.compute_all_base_cases(all_subgames, 
                                                   ["".join(s) for s in small], 
                                                   pattern, 
                                                   10)
    
    # update game dictionary with small irregular games
    game_dict = add_small_positions(game_dict, small)
    pp(game_dict)

    # call inductive search
    value, nodes = evaluate(state, game_dict, base_cases, 0, 0)

    # periodically write status to file to log long runtimes
    write_status("result.txt", nodes, value)

    # optionally save state space tree as a JSON file
    if name:
        folder = f"json/{name}"
        os.makedirs(folder, exist_ok=True)
        proof_node = proof_tree(state, game_dict, base_cases)
        with open(f'folder/{name}_proof_node.json', 'w', encoding='utf-8') as f:
            json.dump(proof_node.to_json(0, 3), f, ensure_ascii=False, indent=4)
    
    return value

if __name__ == "__main__":
    test = ["xxoo_"]
    all_states = ['_', '_o', '_x', '_xo', '_xx', '_xxx', 'o_', 'o_o', 'o_x', 'o_xo', 'oo_o', 'oo_x', 'oo_xo', 'oxo_x', 'oxo_xo', 'x_', 'x_o', 'x_x', 'x_xo', 'x_xxx', 'xo_x']
    for state in test:
        print("=" * 50 + "(" + state + ")" + "=" * 50)
        #state = "_"
        pattern = "x"
        prefix = state.split("_")[0]
        suffix = state.split("_")[1]
        p = {tuple(prefix)}
        s = {tuple(suffix)}
        name = "xxooxn"
        run(state, pattern, p, s, name, False)
