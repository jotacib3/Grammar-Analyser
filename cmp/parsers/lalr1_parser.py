from cmp.parsers.shift_reduce_parser import Item, ShiftReduceParser
from cmp.pycompiler import Grammar, Production, Symbol, Sentence
from cmp.parsers.firsts_follows import compute_firsts, compute_follows
from cmp.parsers.lr1_parser import expand, closure_lr1, goto_lr1, compress, build_LR1_automaton
from cmp.parsers.lr0_parser import build_LR0_automaton
from cmp.utils import ContainerSet
from cmp.automata import State, multiline_formatter

def node_centers(state):
    return frozenset([item.Center() for item in state.state])

class LALR1_DummyParser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        automaton = build_LR1_automaton(G)
        centers = {}

        for i, node in enumerate(automaton):
            node.idx = i
            try:
                same_center = centers[node_centers(node)]
                centers[node_centers(node)] = State(compress(node.state.union(same_center.state)), True)
            except KeyError:
                centers[node_centers(node)] = node
            centers[node_centers(node)].idx = i
        
        self.automaton = automaton
        self.centers = centers

        Goto = {}
        firsts=compute_firsts(G)
        firsts[G.EOF] = ContainerSet(G.EOF)
        for node in centers.values():
            for symbol in G.terminals + G.nonTerminals:
                temp = goto_lr1(node.state, symbol, firsts)
                if not temp:
                    continue
                Goto[(node.idx, symbol)] = centers[node_centers(State(temp,True))]

        for node in centers.values():
            idx = node.idx
            for item in node.state:
                # Your code here!!!
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)
                if item.IsReduceItem:
                    production = item.production
                    if production.Left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), ("OK", None))
                    else:
                        for lookahead in item.lookaheads:
                            self._register(self.action, (idx, lookahead), ("REDUCE", production))
                else:
                    next_symbol = item.NextSymbol
                    if next_symbol.IsTerminal:
                        self._register(self.action, (idx, next_symbol), ("SHIFT", Goto[(node.idx, next_symbol)].idx))
                    else:
                        self._register(self.goto, (idx, next_symbol), Goto[(node.idx, next_symbol)].idx)
    
    @staticmethod
    def _register(table, key, value):
        # assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        try:
            table[key].append(value)
        except KeyError:
            table[key] = [value]
    






