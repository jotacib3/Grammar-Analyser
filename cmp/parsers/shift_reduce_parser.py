class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'
    
    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()
    
    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [ 0 ]
        cursor = 0
        output = []
        
        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, w[cursor:])            
            
            try:
                action, tag = self.action[state, lookahead]
               
                if action == self.SHIFT:
                    cursor += 1
                    stack.append(tag)
                
                elif action == self.REDUCE:
                    if not tag.Right.IsEpsilon:
                        for _ in tag.Right:                        
                            stack.pop()
                    stack.append(self.goto[stack[-1], tag.Left])
                    output.append(tag)
                
                elif action == self.OK:
                    return output
                
                else:
                    assert False, "La tabla Action está mal implementada"
                    
            except KeyError:
                raise Exception(f"La cadena {w} no pertenece al lenguage generado por la gramatica {self.G}")

    def AnalyseTable(self):
        
        dic = { }

        for (state, symb), value in self.action.items():
            for i in range(len(value)):
                for j in range(i + 1, len(value)):
                    action1, _ = value[i]
                    action2, _ = value[j]

                    if ((action1 == self.SHIFT and action2 == self.REDUCE) or
                        (action2 == self.REDUCE and action1 == self.SHIFT)):
                        try:
                            if 'SHIFT-REDUCE' not in dic[state, symb]: 
                                dic[state, symb].append('SHIFT-REDUCE')
                        except:
                            dic[state, symb] = ['SHIFT-REDUCE']

                    if action1 == self.REDUCE and action2 == self.REDUCE:
                        try:
                            if 'REDUCE-REDUCE' not in dic[state, symb]: 
                                dic[state, symb].append('REDUCE-REDUCE')
                        except:
                            dic[state, symb] = ['REDUCE-REDUCE']
        
        return dic

class Item:

    def __init__(self, production, pos, lookaheads=[]):
        self.production = production
        self.pos = pos
        self.lookaheads = tuple(look for look in lookaheads)

    def __str__(self):
        s = str(self.production.Left) + " -> "
        if len(self.production.Right) > 0:
            for i,c in enumerate(self.production.Right):
                if i == self.pos:
                    s += "."
                s += str(self.production.Right[i])
            if self.pos == len(self.production.Right):
                s += "."
        else:
            s += "."
        s += ", " + str(self.lookaheads)
        return s

    def __repr__(self):
        return str(self)


    def __eq__(self, other):
        return (
            (self.pos == other.pos) and
            (self.production == other.production) and
            (self.lookaheads == other.lookaheads)
        )

    def __hash__(self):
        return hash((self.production,self.pos,self.lookaheads))

    def Preview(self, skip=1):
        unseen = self.production.Right[self.pos+skip:]
        return [ unseen + (lookahead,) for lookahead in self.lookaheads ]

    def Center(self):
        return Item(self.production, self.pos)

    @property
    def IsReduceItem(self):
        return len(self.production.Right) == self.pos

    @property
    def NextSymbol(self):
        if self.pos < len(self.production.Right):
            return self.production.Right[self.pos]
        else:
            return None
    @property
    def NextItem(self):
        if self.pos < len(self.production.Right):
            return Item(self.production,self.pos+1,self.lookaheads)
        else:
            return None