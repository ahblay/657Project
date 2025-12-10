import re
from pprint import pp

def xxo_conjecture(position, q):
    left_index = position.index('_')
    right_index = left_index - len(position) + 1
    #print(f"\nleft index : {left_index}")
    #print(f"right index: {right_index}")
    position = position.replace('_', q*4)
    for i, piece in enumerate(position):
        if piece == "x":
            label = list(position)
            label[i] = piece.upper()
            #print(''.join(label))

            left_move, right_move = make_move(position, i)
            #print(f"left move: {left_move}")
            #print(f"right move: {right_move}")
            if right_move:
                simplified_position = sorted([
                    reduce(right_move[0], q, left_index, left_index+len(q)*4), 
                    reduce(right_move[1], q, right_index-len(q)*4, right_index)])
                #print(simplified_position)
                return clean({tuple(simplified_position)})
    return ()


def find_moves(position, q):
    children = {"x": set(), "o": set()}
    left_index = position.index('_')
    right_index = left_index - len(position) + 1
    #print(f"\nleft index : {left_index}")
    #print(f"right index: {right_index}")
    position = position.replace('_', q*4)
    for i, piece in enumerate(position):
        label = list(position)
        label[i] = piece.upper()
        #print(''.join(label))

        left_move, right_move = make_move(position, i)
        #print(f"left move: {left_move}")
        #print(f"right move: {right_move}")

        for move in make_move(position, i):
            if move:
                simplified_position = sorted([
                    reduce(move[0], q, left_index, left_index+len(q)*4), 
                    reduce(move[1], q, right_index-len(q)*4, right_index)])
                #print(simplified_position)
                children[piece].add(tuple(simplified_position))
    return children

def clean(children):
    groups = {}

    for tup in children:
        tup = tuple(sorted(tup, key=lambda s: (len(s), s)))

        # Normalize: remove underscores + sort the items
        key = tuple(sorted(s.replace('_', '') for s in tup))

        # Count underscores in original tuple
        underscore_count = sum(s.count('_') for s in tup)

        # Keep only tuple with max underscore count for each group
        if key not in groups or underscore_count > groups[key][1]:
            groups[key] = (tup, underscore_count)

    # Extract the best representative of each group
    return {item for item, _ in groups.values()}

def simplify(children, symmetry_dict):
    result = set()
    for child in children:
        new_child = []
        for game in child:
            if game in symmetry_dict.keys():
                new_child.append(symmetry_dict[game])
            else:
                new_child.append(game)
        new_child.sort(key=lambda s: (len(s), s))
        result.add(tuple(new_child))
    return result

# TODO: there's a problem when q is contained within a prefix or suffix
def reduce(s, term, lb, ub):
    """Takes a string s and a term and removes the first occurrence of (term)^n for n > 0."""
    lowerbound = lb #if (lb is None or lb >= 0) else len(s) + lb
    upperbound = ub #if (ub is None or ub >= 0) else len(s) + ub
    if upperbound == 0: upperbound = len(s)
    
    # TODO: catching the case where we try to simplify the position q?
    if not s or s == term:
        return s
    #print(f"\nlower bound: {lowerbound}")
    #print(f"upper bound: {upperbound}")
    substring = s[lowerbound: upperbound]
    #print(f"s: {s}")
    #print(f"substring: {substring}")
    #print(f"{s[:lowerbound]} + {substring} + {s[upperbound:]}")
    # defines the pattern to match as a repeated occurrence of term
    pattern = f"({re.escape(term)})+"
    # finds the first instance of pattern in s
    match = re.search(pattern, substring)
    if match:
        # all characters in s before the matched string
        prefix = s[:lowerbound] + substring[:match.start()]
        #print(f"prefix: {prefix}")
        # all characters in s after the matched string
        suffix = substring[match.end():] + s[upperbound:]
        #print(f"suffix: {suffix}")
        return f"{prefix}_{suffix}"
    else:
        #print(f"no removal: {s}")
        return s
    
def make_move(pattern, index):
    """Given a pattern string representing a game and a piece index to move, supply the games 
    resulting from moving that piece left and right."""
    if index not in range(len(pattern)):
        return [None, None], None
    # piece to move
    piece = pattern[index]
    # everything to the left of piece
    left = pattern[:index]
    # everything to the right of piece
    right = pattern[index + 1:]

    # if there is a piece to the left of the active piece that is a different color
    if left[-1:] and piece != left[-1:]:
        # tuple representing the position after the active piece captures to the left
        move_left = (left[:-1] + piece, right)
    else:
        # no move possible
        move_left = None
    # if there is a piece to the right of the active piece that is a different color
    if right[:1] and piece != right[:1]:
        # tuple representing the position after the active piece captures to the right
        move_right = (left, piece + right[1:])
    else:
        # no move possible
        move_right = None
    return [move_left, move_right]

def main():
    children = xxo_conjecture('xo_', 'xxo')
    pp(children)
    #pp(clean(children['o']))

if __name__ == "__main__":
    main()