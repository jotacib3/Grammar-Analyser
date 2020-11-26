
from queue import Queue
from cmp.pycompiler import Grammar, NonTerminal, Terminal, Sentence
from cmp.utils import Trie

import json

class GrammarBuilder:
    
    @staticmethod
    def build_grammar(grammar_txt: str):
        """
        Transform a string in this format:

        S --> A B
        A --> a A | epsilon
        B --> b B | epsilon

        to a Grammar object
        """
        try:
            nonTerminals, terminals, P = [], [], []

            lines = [l.strip() for l in grammar_txt.splitlines() if l.strip() != '']

            head = None
            
            for l in lines:
                if '->' not in l:
                    l = f'{head} -> {l}'

                head, bodies = l.split('->')
                head = head.split()[0]            
                nonTerminals.append(head)

                for body in bodies.split('|'):
                    if body.strip() != '':
                        P.append({'Head': head, 'Body': list(body.split())})
                        terminals.extend(P[-1]['Body'])
            
            set_terminals, set_nonTerminals = set(terminals).difference(nonTerminals + ['epsilon']), set(nonTerminals)

            N, T = [], []

            for nt in nonTerminals:
                if nt in set_nonTerminals and set_nonTerminals.discard(nt) == None:
                    N.append(nt)
            
            for t in terminals:
                if t in set_terminals and set_terminals.discard(t) == None:
                    T.append(t)

            data = json.dumps({
                                    'Terminals': T,
                                    'NonTerminals': N,
                                    'Productions': P
                                })
            G = Grammar.from_json(data)
            G.startSymbol = G.nonTerminals[0]
            return G
        except:
            return None

    @staticmethod
    def is_not_null(G: Grammar):
        """
        Check if the given grammar genere
        the empty language, if not null
        return also return a set with
        true used symbols
        """
        accepted = set()
        visited = set()

        def dfs(symbol):
            visited.add(symbol)
            acc = False

            if isinstance(symbol, Terminal):
                acc = True
            else:
                for production in symbol.productions:
                    for s in production.Right:
                        if s not in visited:
                            dfs(s)
                    acc |= all(s in accepted for s in production.Right)

            if acc:
                accepted.add(symbol)

        dfs(G.startSymbol)

        pending = Queue()
        if G.startSymbol in accepted: pending.put(G.startSymbol)
        visited = set()

        while not pending.empty():
            symbol = pending.get()
            visited.add(symbol)

            if isinstance(symbol, NonTerminal):
                for production in symbol.productions:
                    if all(s in accepted for s in production.Right):
                        for s in production.Right:
                            if s not in visited:
                                pending.put(s)

        return (G.startSymbol in accepted), visited

    @staticmethod
    def remove_bad_items(G: Grammar, keep_symbols):
        """
        Transform G for remove all symbols
        not in keep_symbols
        """
        G.nonTerminals = [nonTerminal for nonTerminal in G.nonTerminals if nonTerminal in keep_symbols]
        G.terminals = [terminal for terminal in G.terminals if terminal in keep_symbols]
        G.productions = []

        for nonTerminal in G.nonTerminals:
            productions = nonTerminal.productions.copy()
            nonTerminal.productions = []

            for production in productions:
                if all(symbol in keep_symbols for symbol in production.Right):
                    nonTerminal %= production.Right
        
    @staticmethod
    def remove_left_recursion(G: Grammar):
        """
        Transform G for remove inmediate
        left recursion
        """
        G.Productions = []
        nonTerminals = G.nonTerminals.copy()

        for nonTerminal in nonTerminals:
            recursion = [p.Right[1:] for p in nonTerminal.productions if len(p.Right) > 0 and p.Right[0] == nonTerminal]
            no_recursion = [p.Right for p in nonTerminal.productions if len(p.Right) == 0 or p.Right[0] != nonTerminal]

            if len(recursion) > 0:
                nonTerminal.productions = []
                aux = G.NonTerminal(f'{nonTerminal.Name}0')

                for p in no_recursion:
                    nonTerminal %= Sentence(*p) + aux

                for p in recursion:
                    aux %= Sentence(*p) + aux

                aux %= G.Epsilon
            else:
                G.Productions.extend(nonTerminal.productions)

    @staticmethod
    def factorize_grammar(G: Grammar):
        """
        Transform G for remove common
        prefixes
        """
        G.Productions = []

        pending = Queue() 
        for nonTerminal in G.nonTerminals: pending.put(nonTerminal)

        while not pending.empty():
            nonTerminal = pending.get()

            productions = nonTerminal.productions.copy()
            nonTerminal.productions = []

            visited = set()

            for i, p in enumerate(productions):
                if p not in visited:
                    n = len(p.Right)
                    same_prefix = []

                    for p2 in productions[i:]:
                        m = 0

                        for s1, s2 in zip(p.Right, p2.Right):
                            if s1 == s2:
                                m += 1
                            else:
                                break
                        
                        if m > 0:
                            same_prefix.append(p2)
                            n = min(n, m)

                    if len(same_prefix) > 1:
                        visited.update(same_prefix)
                        aux = G.NonTerminal(f'{nonTerminal.Name}{i + 1}')

                        nonTerminal %= Sentence(*p.Right[:n]) + aux
                        for p2 in same_prefix:
                            if n == len(p2.Right):
                                aux %= G.Epsilon
                            else:
                                aux %= Sentence(*p2.Right[n:])

                        pending.put(aux)
                    else:
                        visited.add(p)
                        nonTerminal %= p.Right



    # def expand_sentence(self, head, sentence, nt_info, production):
    #     for symb in sentence:
    #         finish, pos, word = nt_info[symb]
    #         if symb in self.nonTerminals:
                
    #             if not finish:
    #                 finish, beta  = self.expand_nonTerminal(symb, nt_info)
                
    #             if not finish:
    #                 return False
    #             else:
    #                 nt_info[head] = finish, pos, f'{word} {beta}'.strip()
    #         else:
    #             nt_info[head] = finish, pos, f'{word} {symbol}'.strip()
                
    #     return True 

    # def expand_nonTerminal(self, nt, nt_info):
    #     finish, start, word = nt_info[nt]

    #     if finish and self._useProd:
    #         return True, word

    #     for i in range(start, len(nt.productions)):
    #         p = nt.productions[i]
    #         nt_info[nt] = (False, i + 1, word) 
    #         if self.expand_sentence(p.Left, p.Right, nt_info):
    #             _, _, word = nt_info[nt]
    #             nt_info[nt] = (True, i + 1, word)
    #             return True, word

    #     return False, None

    # def get_conflicted_word(self, production):
    #     graph = self._build_graph()
        
    #     nt_expansion = { nt:(False, 0, '') for nt in self.nonTerminals }
    #     word = ''
    #     for symbol in production.Right:
    #         if symbol in self._G.nonTerminals:
    #             word += self.expand_nonTerminal(nt_expansion)
    #         else:
    #             word = f' {symbol}'
    #             word = word.strip()