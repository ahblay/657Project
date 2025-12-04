class Node:
    def __init__(self, state, value):
        self.state = state
        self.value = value
        #self.player = player
        self.left_children_x = []
        self.right_children_x = []
        self.left_children_o = []
        self.right_children_o = []
    
    def merge_children(self):
        x_moves = zip(self.left_children_x, self.right_children_x)
        o_moves = zip(self.left_children_o, self.right_children_o)
        return {"LEFT": list(x_moves), "RIGHT": list(o_moves)}
    
    def to_json(self):
        child_sums = self.merge_children()
        children = {}
        for player, sumgame_list in child_sums.items():
            for sumgame in sumgame_list:
                children[f"{player}: {sumgame[0].state} + {sumgame[1].state}"] = [sumgame[0].to_json(), sumgame[1].to_json()]
        

        return {
            "label": self.state,
            "value": self.value,
            "children": children
        }

    """
    def __repr__(self, level=0):
        indent = "  " * level
        s = f"{indent}{self.state} : {self.value}\n"
        for child in self.merge_children():
            child_indent = "  " * (level + 1)
            s += f"{child_indent}{child[0].state}+{child[1].state}\n"
            for subgame in child:
                s += subgame.__repr__(level + 2)
        return s
    """