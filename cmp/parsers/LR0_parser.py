from cmp.parsers.shift_reduce_parser import ShiftReduceParser, Item
from cmp.parsers.firsts_follows import compute_firsts, compute_follows
from cmp.automata import State, multiline_formatter, lr0_formatter, multiline_formatter_lr0

class LR0Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        firsts = compute_firsts(G)
        # follows = compute_follows(G, firsts)       
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
                        for c in G.terminals + [G.EOF]:                            
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
            # table[key].add(value)
        except KeyError:
            table[key] = [value]
            # table[key] = set(value)

def build_LR0_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)

    automaton = State(start_item, True)

    pending = [ start_item ]
    visited = { start_item: automaton }

    while pending:
        current_item = pending.pop()
        if current_item.IsReduceItem:
            continue
        
        if current_item.NextSymbol.IsTerminal:
            if not current_item.NextItem in visited:
                visited[current_item.NextItem] = State(current_item.NextItem, True)
                pending.append(current_item.NextItem)                
        else:
            for production in current_item.NextSymbol.productions:
                item = Item(production, 0)
                if not item in visited:
                    visited[item] = State(item, True)
                    pending.append(item)
            if not current_item.NextItem in visited:
                visited[current_item.NextItem] = State(current_item.NextItem,True)
                pending.append(current_item.NextItem)
            
        current_state = visited[current_item]
        # Your code here!!! (Add the decided transitions)                
        current_state.add_transition(current_item.NextSymbol.Name, visited[current_item.NextItem])
        
        if current_item.NextSymbol.IsNonTerminal:
            for production in current_item.NextSymbol.productions:
                current_state.add_epsilon_transition(visited[Item(production,0)])
    
    automaton.set_formatter(multiline_formatter_lr0)
    return automaton