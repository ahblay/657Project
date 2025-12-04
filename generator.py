from itertools import product
from utilities import generate_test_sequence, write_to_file, clear_file
import tree
from pprint import pp
from prover import prover, jsonify, evaluate
from collections import defaultdict
import json
import random

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

    # finds +q and -q
    for piece in x: # all pieces that could be to the left of q
        if piece != q[0]: # if a move is possible
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
    x.add(q[-1]) # q could be to the left of q
    for prefix in prefixes: # any prefix could be to the left of q
        if prefix: x.add(prefix[-1]) 
        result.update(simulate_move(prefix, [])) # to avoid multiple loops, get all positions resulting from moving in prefix
        result.add(prefix)
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
    y.add(q[0]) # q could be to the right of q
    for suffix in suffixes: # any suffix could be to the right of q
        if suffix: y.add(suffix[0])
        # suffixes resulting from moving in a suffix are equivalent to prefixes resulting from moving in reversed suffix
        moves_in_suffix_reversed = simulate_move(suffix[::-1], []) # all positions resulting from moving in suffix
        # reverse results back
        result.update([s[::-1] for s in moves_in_suffix_reversed])
        result.add(suffix)
    # simulating move in suffix is same as simulating move in reversed prefix and reversing the result
    suffixes = simulate_move(q[::-1], list(y))
    result.update([suffix[::-1] for suffix in suffixes])
    return result

def get_small_positions(pattern, q):
    small = set()
    if pattern and pattern[-1] != q[0]: # if pattern is non-empty and a move is possible
        small.add(pattern[:-1]) # capturing to the right
        small.add(pattern[:-1] + (q[0],)) # capturing to the left
    for i, item in enumerate(pattern): 
        if pattern[i+1:] and item != pattern[i+1]: # if a move is possible
            small.add(pattern[:i]) # capturing to the right
            small.add(pattern[:i] + (pattern[i+1],)) # capturing to the left
    return small

def generate_small_patterns(prefixes, suffixes, q):
    small = set()
    for prefix in prefixes:
        small.update(get_small_positions(prefix, q))
    for suffix in suffixes:
        reversed_small_suffixes = get_small_positions(suffix[::-1], q[::-1])
        small.update([s[::-1] for s in reversed_small_suffixes])
    small.update(get_small_positions(q, q))
    reversed_small_q = get_small_positions(q[::-1], q[::-1])
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
    patterns = list(product(prefixes, suffixes))
    result = []
    for pattern in patterns:
        p = pattern[0]
        s = pattern[1]
        new_p = s[::-1] + ('o',)
        new_p = "".join(list(new_p)).removesuffix(''.join(q))
        new_s = ('x', 'x',) + p[::-1]
        new_s = "".join(list(new_s)).removeprefix(''.join(q))
        #TODO: Is this necessary?
        if (tuple(new_p), tuple(new_s)) in patterns:
            result.append([(tuple(new_p), tuple(new_s)), pattern])
    return result

# returns a formatted symmetries list that does not identify symmetries
def empty_symmetries(prefixes, suffixes, q):
    patterns = list(product(prefixes, suffixes))
    result = []
    for pattern in patterns:
        result.append([pattern, pattern])
    return result

def get_symmetries_dict(symmetries):
    result = {}
    for pair in symmetries:
        simple_pair = []
        for i in pair:
            simple_pair.append("_".join("".join(inner) for inner in i))
        #sorted_pair = sorted(simple_pair, key=len)
        simple_pair.sort(key=lambda s: (len(s), s))
        result[simple_pair[1]] = simple_pair[0]
    return result 

def delete_symmetries(symmetries):
    result = set()
    for pair in symmetries:
        simple_pair = []
        for i in pair:
            simple_pair.append("_".join("".join(inner) for inner in i))
        result.add(min(sorted(simple_pair), key=len))
    return result    

def print_patterns(p):
    result = []
    for i in p:
        result.append("_".join("".join(inner) for inner in i))
    print(result)
    #print(len(result))
    return

def add_small_positions(game_dict, small_positions):
    pieces = ["x", "o"]
    output = {}
    for k, v in game_dict.items():
        output[k] = {}
        for piece in pieces:
            sumgames = v[piece]
            new_sumgames = set()
            for sumgame in sumgames:
                new_sumgames.add(sumgame)
                for idx in range(2):
                    subgame = sumgame[idx % 2]
                    base_cases = small_positions[subgame] if subgame in small_positions else []
                    for position in base_cases:
                        new_sumgames.add((sumgame[(idx + 1) % 2], position))
            output[k][piece] = new_sumgames
    return output

def create_cgs_file(pattern_list, q, filename):
    clear_file(f"/Users/abel/CGScript/{filename}")
    for pattern in pattern_list:
        test_sequence = generate_test_sequence(pattern, q, 24)
        write_to_file(test_sequence, f"/Users/abel/CGScript/{filename}")

def run(pattern, p, s, name, state, moves=False):
    q = tuple(pattern)
    
    if moves:
        with open(f'json/{name}/{name}_game_dict.json', 'r') as f:
            game_dict = json.load(f)
    
    else:
        prefixes, suffixes, small = generate_patterns(p, s, q)
        print_set(prefixes)
        print_set(suffixes)
        print_set(small)

        if pattern == "xxo":
            symmetries = find_symmetries_xxo(prefixes, suffixes, q)
        else:
            symmetries = empty_symmetries(prefixes, suffixes, q)

        symmetries_dict = get_symmetries_dict(symmetries)
        all_subgames = sorted(list(symmetries_dict.values()))
        print(all_subgames)

        game_dict = {}
        for subgame in all_subgames:
            children = tree.find_moves(subgame, pattern)
            x_cleaned = tree.clean(children['x'])
            x_simplified = tree.simplify(x_cleaned, symmetries_dict)
            o_cleaned = tree.clean(children['o'])
            o_simplified = tree.simplify(o_cleaned, symmetries_dict)

            game_dict[subgame] = {'x': x_simplified, 'o': o_simplified}
    
        create_cgs_file(all_subgames, pattern, 'cmds')
    
    if pattern =="xxo":
        with open('json/small_games.json', 'r') as f:
            small_games = json.load(f)
        game_dict = add_small_positions(game_dict, small_games)
    
    print("&" * 40)
    pp(game_dict)
    
    with open(f'json/{name}/{name}_base_cases.json', 'r') as f:
        base_cases = json.load(f)

    proof_node = evaluate(state, game_dict, base_cases, 0)

    with open(f'json/{name}/{name}_proof_node.json', 'w', encoding='utf-8') as f:
        json.dump(proof_node.to_json(), f, ensure_ascii=False, indent=4)

def main():
    main_pattern = 'xxo'
    q = tuple(main_pattern)

    prefixes, suffixes, small = generate_patterns(set(), set(), q)
    print_set(prefixes)
    print_set(suffixes)
    print_set(small)

    symmetries = find_symmetries_xxo(prefixes, suffixes, q)
    symmetries_dict = get_symmetries_dict(symmetries)
    all_patterns = sorted(list(symmetries_dict.values()))

    print(symmetries_dict)
    print(len(all_patterns))
    print(all_patterns)

    create_cgs_file(all_patterns, main_pattern, 'cmds')

    game_dict = {}

    for pattern in all_patterns:
        children = tree.find_moves(pattern, main_pattern)
        print("*" * 100)
        print(f"all children of {pattern}\n")
        pp(children)
        print('-------CLEANED-------')
        print('=====x=====')
        x_cleaned = tree.clean(children['x'])
        x_simplified = tree.simplify(x_cleaned, symmetries_dict)
        pp(x_cleaned)
        pp(x_simplified)
        print('=====o=====')
        o_cleaned = tree.clean(children['o'])
        o_simplified = tree.simplify(o_cleaned, symmetries_dict)
        pp(o_cleaned)
        pp(o_simplified)

        game_dict[pattern] = {'x': x_simplified, 'o': o_simplified}

    with open('json/small_games.json', 'r') as f:
        small_games = json.load(f)

    with open('json/small_game_values.json', 'r') as f:
        small_game_values = json.load(f)
    
    with open('json/base_cases.json', 'r') as f:
        base_cases = json.load(f)

    with open('json/xoxn/xoxn_base_cases.json', 'r') as f:
        oxn_base_cases = json.load(f)

    with open('json/xoxn/xoxn_game_dict.json', 'r') as f:
        oxn_game_dict = json.load(f)
    
    new_game_dict = add_small_positions(game_dict, small_games)
    pp(oxn_game_dict)
    print("&" * 100)

    proof_node = evaluate("xo_", oxn_game_dict, oxn_base_cases, 0)
    print(proof_node)

    with open('json/xoxn/xoxn_proof_node.json', 'w', encoding='utf-8') as f:
        json.dump(proof_node.to_json(), f, ensure_ascii=False, indent=4)
    

if __name__ == "__main__":
    state = "o_"
    pattern = "x"
    p = {("o",)}
    s = {()}
    name = "oxn"
    run(pattern, p, s, name, state, False)

# xo xxo xxo xxo x

# xo xxo x.x xxo x
# xo xxx .xo xxo x