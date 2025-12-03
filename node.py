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
        return list(x_moves) + list(o_moves)
    
    def to_json(self):
        child_sums = self.merge_children()
        return {
            "label": self.state,
            "value": self.value,
            "children": {f"{child[0].state}+{child[1].state}": [child[0].to_json(), child[1].to_json()] for child in child_sums}
        }

    def __repr__(self, level=0):
        indent = "  " * level
        s = f"{indent}{self.state} : {self.value}\n"
        for child in self.merge_children():
            child_indent = "  " * (level + 1)
            s += f"{child_indent}{child[0].state}+{child[1].state}\n"
            for subgame in child:
                s += subgame.__repr__(level + 2)
        return s