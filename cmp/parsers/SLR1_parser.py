from cmp.parsers.shift_reduce_parser import ShiftReduceParser, Item
from cmp.parsers.firsts_follows import compute_firsts, compute_follows
from cmp.automata import State
from cmp.parsers.LR0_parser import build_LR0_automaton

class SLR1Parser(ShiftReduceParser):

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        firsts = compute_firsts(G)
        follows = compute_follows(G, firsts)       
        automaton = build_LR0_automaton(G).to_deterministic()
        for i, node in enumerate(automaton):
            if self.verbose: print(i, node)
            node.idx = i

        self.automaton = automaton

        for node in automaton:
            idx = node.idx
            for state in node.state:
                item = state.state
                
                if item.IsReduceItem:
                    X = item.production.Left
                    
                    if X == G.startSymbol:                       
                        self._register(self.action, (idx, G.EOF), ("OK", None))
                        
                    else:    
                        for c in follows[X]:                            
                            self._register(self.action,(idx, c), ("REDUCE", item.production))
                
                else:
                    next_symbol = item.NextSymbol
                    
                    if next_symbol.IsTerminal:
                        
                        self._register(self.action, (idx, next_symbol), ("SHIFT", node[next_symbol.Name][0].idx))
                    else:                       
                        self._register(self.goto, (idx, next_symbol), node[next_symbol.Name][0].idx)
    
    @staticmethod
    def _register(table, key, value):
        # assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        try:
            table[key].append(value)
        except KeyError:
            table[key] = [value]