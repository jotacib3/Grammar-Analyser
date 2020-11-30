from cmp.pycompiler import Terminal
import graphviz as graphviz

class DerivationTree:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []

    def add_child(self, child_tree):
        self.children.append(child_tree)

    @staticmethod      
    def get_tree_at(parser, index, parser_type='left'):
        production = parser[index]
        tree = DerivationTree(production.Left)
        end = index + 1

        sentence = reversed(production.Right) if parser_type == 'right' else production.Right

        for symbol in sentence:
            if symbol.IsTerminal:
                tree.add_child(DerivationTree(symbol))
            else:
                ctree, end = DerivationTree.get_tree_at(parser, end, parser_type)
                tree.add_child(ctree)

        if parser_type == 'right': tree.children.reverse()
        
        return tree, end

    @staticmethod
    def get_tree(parser, parser_type='left'):
        return DerivationTree.get_tree_at(parser, 0, parser_type)[0]

    def graph(self):
        G = graphviz.Digraph()
        
        G.node('start', '',{ 'style': 'bold', 'shape': 'plaintext', 'width': '0', 'height': '0'})
        # G = pydot.Dot(rankdir='TD', margin=0.1)
        # G.add_node(pydot.Node('start', shape='plaintext', label='', width=0, height=0))

        visited = set()
        def visit(start):
            ids = id(start)
            if ids not in visited:
                visited.add(ids)
                G.node(str(ids), str(start.symbol) ,{ 'shape': 'circle', 'style': 'bold'})
                # G.add_node(pydot.Node(ids, label=start.symbol.Name, shape='circle', style='bold' if isinstance(start.symbol, Terminal) else ''))
                for tree in start.children:
                    visit(tree)
                    G.edge(str(ids), str(id(tree)), '', {'labeldistance': '2'})
                    # G.add_edge(pydot.Edge(ids, id(tree), labeldistance=2))

        visit(self)
        G.edge('start', str(id(self)), '', {'labeldistance': '2'})
        # G.add_edge(pydot.Edge('start', id(self), label='', style='dashed'))

        return G
