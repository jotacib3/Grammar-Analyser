from cmp.parsers.shift_reduce_parser import ShiftReduceParser, Item
from cmp.automata import State, multiline_formatter
from cmp.utils import ContainerSet
from cmp.parsers.firsts_follows import compute_firsts, compute_follows, compute_local_first

class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        
        automaton = build_LR1_automaton(G)
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i
        
        self.automaton = automaton

        for node in automaton:
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


def build_LR1_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])

    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)

    pending = [ start ]
    visited = { start: automaton }

    while pending:
        current = pending.pop()
        current_state = visited[current]

        for symbol in G.terminals + G.nonTerminals:
            # Your code here!!! (Get/Build `next_state`)
            dest = goto_lr1(current_state.state, symbol, just_kernel=True)

            if not dest:
                continue

            if dest in visited:
                next_state = visited[dest]
            else:
                items = goto_lr1(current_state.state, symbol, firsts, just_kernel=False)
                next_state = State(frozenset(items), True)
                visited[dest] = next_state
                pending.append(dest)

            current_state.add_transition(symbol.Name, next_state)

    automaton.set_formatter(multiline_formatter)
    return automaton


def expand(item, firsts, with_lookaheads = True):
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []
    
    if with_lookaheads:
        lookaheads = ContainerSet()
        # Your code here!!! (Compute lookahead for child items)
        preview = item.Preview()
        for sentence in preview:
            lookaheads.update(compute_local_first(firsts, sentence))
            assert not lookaheads.contains_epsilon

    return [Item(production, 0, [l for l in lookaheads]) for production in next_symbol.productions]

def compress(items):
    centers = {}

    for item in items:
        center = item.Center()
        try:
            lookaheads = centers[center]
        except KeyError:
            centers[center] = lookaheads = set()
        lookaheads.update(item.lookaheads)

    return { Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items() }

def closure_lr1(items, firsts, with_lookaheads = True):
    closure = ContainerSet(*items)

    changed = True
    while changed:
        changed = False

        new_items = ContainerSet()
        # Your code here!!!
        for item in closure:
            new_items.extend(expand(item, firsts))

        changed = closure.update(new_items)
    if with_lookaheads:
        return compress(closure)
    else:
        return closure



def goto_lr1(items, symbol, firsts=None, just_kernel=False):
    assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
    items = frozenset(item.NextItem for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(items, firsts)