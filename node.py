class Node:
    '''
    Node class for each linear Clobber game state.
    '''
    def __init__(self, state, value):
        self.state = state
        self.value = value
        self.left_children_x = [] # left subgames resulting from x moves
        self.right_children_x = [] # right subgames resulting from x moves
        self.left_children_o = [] # left subgames rsulting from o moves
        self.right_children_o = [] # right subgames resulting from o moves
    
    def merge_children(self):
        '''
        Combine child nodes into pairs corresponding to sumgames.
        '''
        x_moves = zip(self.left_children_x, self.right_children_x)
        o_moves = zip(self.left_children_o, self.right_children_o)
        return {"LEFT": list(x_moves), "RIGHT": list(o_moves)}
    
    def to_json(self, depth, depth_limit=None):
        '''
        Write the game tree to a JSON file. Depth can be limited for huge state spaces.
        '''
        children = {}
        if depth_limit and depth >= depth_limit:
            return {
                "label": self.state,
                "value": self.value,
                "children": children
            }
        child_sums = self.merge_children()
        for player, sumgame_list in child_sums.items():
            for sumgame in sumgame_list:
                children[f"{player}: {sumgame[0].state} + {sumgame[1].state}"] = [sumgame[0].to_json(depth+1, depth_limit), sumgame[1].to_json(depth+1, depth_limit)]
        

        return {
            "label": self.state,
            "value": self.value,
            "children": children
        }
