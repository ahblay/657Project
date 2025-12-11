import re
from pprint import pp

def xxo_conjecture(position, q):
    '''
    Returns the sumgame tuple resulting from making the leftmost move by x, capturing to the right.

    :param position: a position of the form "p_s"
    :param q: the repeating pattern
    :returns sumgame: a set containing a tuple with the two resulting subgames
    '''
    left_index = position.index('_')
    right_index = left_index - len(position) + 1
    position = position.replace('_', q*4)
    for i, piece in enumerate(position):
        if piece == "x":

            left_move, right_move = make_move(position, i)
            if right_move:
                simplified_position = sorted([
                    reduce(right_move[0], q, left_index, left_index+len(q)*4), 
                    reduce(right_move[1], q, right_index-len(q)*4, right_index)])
                return {tuple(simplified_position)}
    return ()


def find_moves(position, q):
    '''
    Returns set of sumgame tuples resulting from all moves in position.

    :param position: a position of the form "p_s"
    :param q: the repeating pattern
    :returns children: a set containing tuples of all resulting sumgames
    '''
    children = {"x": set(), "o": set()}
    left_index = position.index('_')
    right_index = left_index - len(position) + 1

    position = position.replace('_', q*4)
    for i, piece in enumerate(position):

        left_move, right_move = make_move(position, i)

        for move in make_move(position, i):
            if move:
                simplified_position = sorted([
                    reduce(move[0], q, left_index, left_index+len(q)*4), 
                    reduce(move[1], q, right_index-len(q)*4, right_index)])
                children[piece].add(tuple(simplified_position))
    return children

def clean(children):
    '''
    Takes a list of sumgame tuples. If both subgames contain underscores, replace 
    all other sumgames that are equivalent if underscores are removed.

    :param children: list of sumgame tuples
    :returns result: children with all duplicated sumgames removed
    '''
    def is_equiv(sumgame1, sumgame2):
        for g1, g2 in zip(sumgame1, sumgame2):
            if not compare(g1, g2):
                return False
        return True
    
    def compare(main, g):
        underscore_index = main.index("_")
        if g.count("_") == 0:
            return True
        if g.index("_") == underscore_index:
            return True
        return False

    to_remove = set()
    result = set()
    for sumgame in children:
        total_underscores = sum(s.count("_") for s in sumgame)
        if total_underscores == 2:
            result.add(sumgame)
            for child in children:
                if is_equiv(sumgame, child):
                    to_remove.add(child)

    result.update(children - to_remove)
    return result

def simplify(children, symmetry_dict):
    '''
    Replaces each subgame with its symmetric representation, if smaller.

    :param children: sumgame tuples
    :param symmetry_dict: dictionary of all symmetric positions
    :returns result: canonical symmetric representation
    '''
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

def reduce(s, term, lowerbound, upperbound):
    """
    Takes a string s and a term and removes the first occurrence of 
    (term)^n for n > 0, within provide bounds.

    :param s: string
    :param term: repeating term to remove
    :param lb: index in string to start searching
    :param up: index in string to stop searching 
    """
    if upperbound == 0: upperbound = len(s)
    
    # TODO: catching the case where we try to simplify the position q?
    if not s or s == term:
        return s

    substring = s[lowerbound: upperbound]

    # defines the pattern to match as a repeated occurrence of term
    pattern = f"({re.escape(term)})+"
    # finds the first instance of pattern in s
    match = re.search(pattern, substring)
    if match:
        # all characters in s before the matched string
        prefix = s[:lowerbound] + substring[:match.start()]
        # all characters in s after the matched string
        suffix = substring[match.end():] + s[upperbound:]
        return f"{prefix}_{suffix}"
    else:
        return s
    
def make_move(pattern, index):
    """
    Given a pattern string representing a game and a piece index to move, supply the games 
    resulting from moving that piece left and right.
    """
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
    #children = xxo_conjecture('xo_', 'xxo')
    children = clean({('_x', 'xxx'), ('_x', '_xxx'), ('x', '_xxx')})
    pp(children)
    #pp(clean(children['o']))

if __name__ == "__main__":
    main()