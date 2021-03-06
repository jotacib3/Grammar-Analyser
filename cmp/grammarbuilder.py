
from queue import Queue
from cmp.pycompiler import Grammar, NonTerminal, Terminal, Sentence, Epsilon
from cmp.automata import State
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
            # print(data)
            G.startSymbol = G.nonTerminals[0]

            return G
        except:
            return None

    @staticmethod
    def tokenizer(G: Grammar, text):
        return [G[word] for word in text.split()] + [G.EOF]
        
    def __init__(self, G):
        self._G = G
        self.startSymbol = f'{G.startSymbol}'
        
        self.Productions = {f'{nt}':set() for nt in G.nonTerminals}

        for p in G.Productions:
            self.Productions[f'{p.Left}'].add(f'{p.Right}')
    
    def __str__(self):
        ans = ''
        
        for head in self.Productions:
            for body in self.Productions[head]:
                ans += f'{head} -> {body}\n\t'

        return ans.strip()

    def copy(self):
        clone = GrammarBuilder(self._G)
        
        clone.Productions = { key:set() for key in self.Productions }
        
        for key in self.Productions:
            clone.Productions[key] = set([value for value in self.Productions[key]])

        clone.startSymbol = f'{self._G.startSymbol}'
        
        return clone

    # Ai -> Aj alpha
    def get_prods_with_head_and_body_beginning(self, Ai:str, Aj:str):
        return [body for body in self.Productions[Ai] if body.strip()[0] == Aj]
    
    # Aj -> beta
    def get_prods_with_head(self, Aj:str):
        return [body for body in self.Productions[Aj]]
    
    def eliminate_LR_and_CP(self):
        self.eliminate_DLR()
        self.eliminate_common_prefixes()

    def get_new_nonTerminal(self, nt, sym = ''):
        ans = nt
        count = 1
        while ans in self.Productions:
            ans = nt + sym + f'{count}'
            count += 1

        return ans

    def get_common_pref_descomp(self, productions):
        head, bodies = productions
        bodies = [body for body in bodies]
        alphas, betas = [], []
        
        t = Trie()
        for body in bodies:
            t.Insert(body.split())
        
        prefixes, matched = [], set()

        for child in t.post_order():
            if child.prefix != '' and child._words >= 2:
                prefixes.append(child.prefix)
        
        # Con esta ordenacion se garantiza que los prefijos comunes que
        # se encuentren entre al menos 2 produciones sean maximos
        prefixes.sort(key = str.__len__, reverse = True) # Sort descending by the sentence length
        
        for prefix in prefixes:
            alphas.append(prefix)
            betas.append([])
            for body in bodies:
                if body not in matched and body.startswith(prefix):
                    beta = body.replace(prefix, '', 1).strip()
                    beta = beta if beta != '' else 'epsilon'
                    betas[-1].append(beta)
                    matched.add(body)
                   
            # Las producciones con el mismo prefijo ya fueron 
            # procesadas con un prefijo comun mas grande
            if len(betas[-1]) < 2:
                alphas.remove(alphas[-1])
                betas.remove(betas[-1])

        return alphas, betas

    def eliminate_common_prefixes(self):
        clone = self.copy()
        
        for A in clone.Productions:
            alphas, betas = clone.get_common_pref_descomp((A, clone.Productions[A]))

            for i in range(len(alphas)):
                alpha = alphas[i]
                Ap = self.get_new_nonTerminal(A, 'X')
                self.Productions[Ap] = set()
                self.Productions[A].add(f'{alpha} {Ap}')
                for beta in betas[i]:
                    beta = beta if beta != 'epsilon' else ''
                    old_prod = f'{alpha} {beta}'.strip()
                    beta = beta if beta != '' else 'epsilon'
                    
                    self.Productions[A].remove(old_prod)
                    self.Productions[Ap].add(beta)

        self._G = GrammarBuilder.build_grammar(f'{self}')

    # Eliminating direct left recursion
    def eliminate_DLR(self):
        clone = self.copy()

        for A in clone.Productions:
            Ap = clone.get_new_nonTerminal(A)

            prods_DLR = clone.get_prods_with_head_and_body_beginning(A, A) 
            
            if len(prods_DLR) == 0:
                continue

            self.Productions[Ap] = set()

            for p in prods_DLR: 
                self.Productions[A].remove(p)
                alpha = None

                try:
                # _, alpha = p.split(' ', 1)                
                    _, alpha = p.split(' ', 1)
                except:
                    alpha = p

                self.Productions[Ap].add(alpha)
                self.Productions[Ap].add(alpha + ' ' + Ap)

            prods_nonDLR = [body for body in clone.Productions[A] if body not in prods_DLR]
            for beta in prods_nonDLR:
                if beta != 'epsilon':
                    self.Productions[A].add(beta + ' ' + Ap)

        self._G = GrammarBuilder.build_grammar(f'{self}')

    # Eliminating direct left recursion
    def eliminate_DLR2(self):
        clone = self.copy()

        for A in clone.Productions:
            N = clone.get_new_nonTerminal(A, 'N')
            T = clone.get_new_nonTerminal(A, 'T')

            prods_DLR = clone.get_prods_with_head_and_body_beginning(A, A) 
            
            if len(prods_DLR) == 0:
                continue

            self.Productions[N] = set()
            self.Productions[T] = set()
            self.Productions[A].add(f'{N} {T}')

            for p in prods_DLR: 
                self.Productions[A].remove(p)
                _, alpha = p.split(' ', 1)

                self.Productions[T].add(f'{alpha} {T}')
                self.Productions[T].add('epsilon')

            prods_nonDLR = [body for body in clone.Productions[A] if body not in prods_DLR]
            for beta in prods_nonDLR:
                self.Productions[N].add(beta)

        self._G = GrammarBuilder.build_grammar(f'{self}')

    # Using Paull's Algorithm
    def eliminate_LR(self):
        clone = self.copy()
        n = len(clone.Productions)

        A = [head for head in clone.Productions]
        #A.reverse()
       
        for i in range(n):
            for j in range(i): 
                for p in clone.get_prods_with_head_and_body_beginning(A[i], A[j]):
                    self.Productions[A[i]].remove(p)
                    _, alpha = p.split(' ', 1) if ' ' in p else (p, '')

                    for beta in clone.get_prods_with_head(A[j]):
                        self.Productions[A[i]].add(f'{beta} {alpha}'.strip())

        # Eliminating direct left recursion
        # self.eliminate_DLR()
    
        self._G = GrammarBuilder.build_grammar(f'{self}')

    def _dfs_visit(self, graph, u, vars):
        pi, color, CCG, cc = vars
        color[u] = 1

        for v in graph[u]:
            if color[v] == 0:
                pi[v] = u
                self._dfs_visit(graph, v, (pi, color, CCG, cc))

        CCG[u] = cc

    def _dfs(self, graph):
        n = len(graph)
        CCG, color, pi = [0] * n, [0] * n, [-1] * n
        cc = 0

        for u in range(n):
            if color[u] == 0:
                self._dfs_visit(graph, u, (pi, color, CCG, cc))
                cc += 1
        
        return CCG, pi
    
    def _build_graph(self):
        n = len(self._G.nonTerminals)
        graph = [[] for _ in range(n)]

        dic = {self._G.nonTerminals[i]:i for i in range(n)}

        for p in self._G.Productions:
            head, body = p.Left, p.Right

            for term in body:
                if term in dic and term != head:
                    u, v = dic[head], dic[term]
                    if v not in graph[u]:
                        graph[u].append(v)
        
        return graph, dic[self._G.startSymbol]

    def _build_path(self, v, pi):
        path = [v]
        while pi[v] != -1:
            v = pi[v]
            path.append(v)

        path.reverse()
        return path

    def get_unreachable_symbols(self):
        graph, s = self._build_graph()
        CCG, _ = self._dfs(graph)
        
        n = len(self._G.nonTerminals)
        dic = {i:self._G.nonTerminals[i] for i in range(n)}
        
        for u in range(n):
            if CCG[u] != CCG[s]:
                yield f'{dic[u]}' 

    def eliminate_unreachable_prod(self):
        clone = self.copy()
        unreachable_symbols = self.get_unreachable_symbols()

        unreachable_symbols = [v for v in unreachable_symbols]

        for head in clone.Productions:
            if head in unreachable_symbols:
                self.Productions.pop(head)
        
        self._G = GrammarBuilder.build_grammar(f'{self}')

    def sentence_finish(self, sentence, nt_info):
        for symb in sentence:
            if symb in self._G.nonTerminals:
                finish, _ = nt_info[symb]
                
                if not finish:
                    finish = self.nt_finish(symb, nt_info)
                
                if not finish:
                    return False
        
        return True 

    def nt_finish(self, nt, nt_info):
        finish, start = nt_info[nt]

        if finish:
            return True

        for i in range(start, len(nt.productions)):
            p = nt.productions[i]
            nt_info[nt] = (False, i + 1) 
            if self.sentence_finish(p.Right, nt_info):
                nt_info[nt] = (True, i + 1)
                return True
        
        return False

    def eliminate_unfinished_prod(self):
        for nt in self._G.nonTerminals:
            for p in nt.productions:
                nt_finish = { nt:(False,0) for nt in self._G.nonTerminals }
                if not self.sentence_finish(p.Right, nt_finish):
                    self.Productions[f'{nt}'].remove(f'{p.Right}')
        
        self._G = GrammarBuilder.build_grammar(f'{self}')

    def eliminate_unecessary_productions(self):
        self.eliminate_unreachable_prod()
        self.eliminate_unfinished_prod()

    epsilon = 'ε'
    
    @staticmethod
    def build_automaton(G: Grammar):
        """
        Build the finite automaton for
        a regular grammar
        """
        states = { nonTerminal: State(nonTerminal.Name) for nonTerminal in G.nonTerminals }
        final_state = State('F\'', True)

        start_in_right = False
        epsilon_production = False

        for nonTerminal in G.nonTerminals:
            for production in nonTerminal.productions:
                right = production.Right

                # Start Symbol produces epsilon
                if isinstance(right, Epsilon) and nonTerminal == G.startSymbol:
                    epsilon_production = True
                    continue
                    
                start_in_right |= G.startSymbol in right
                n = len(right)

                # X --> w
                if n == 1 and isinstance(right[0], Terminal):
                    states[nonTerminal].add_transition(right[0].Name, final_state)
                    continue

                # X --> w Y
                if n == 2 and isinstance(right[0], Terminal) and isinstance(right[1], NonTerminal):
                    states[nonTerminal].add_transition(right[0].Name, states[right[1]])
                    continue

                return states[G.startSymbol], False

        states[G.startSymbol].final = epsilon_production
        return states[G.startSymbol], not (start_in_right and epsilon_production)

    @staticmethod 
    def regex_union(regex, other):
        if regex is None:
            return other

        if other is None:
            return regex

        if regex == other:
            return regex

        return f'({regex}|{other})'

    @staticmethod 
    def regex_concat(regex, other):
        if regex is None or other is None:
            return None

        if regex is GrammarBuilder.epsilon:
            return other

        if other is GrammarBuilder.epsilon:
            return regex

        return f'{regex}{other}'

    @staticmethod 
    def regex_star(regex):
        if regex is None or regex is GrammarBuilder.epsilon:
            return regex

        return f'({regex})*'

    @staticmethod
    def regexp_from_automaton(automaton):
        """
        Build the  regular expresion for
        a NFA
        """
        states = list(automaton)
        states_index = {state: i for i, state in enumerate(states)}
        n = len(states)

        R = [[[None for k in range(n + 1)] for j in range(n)] for i in range(n)]

        for i in range(n):
            R[i][i][0] = GrammarBuilder.epsilon

        for i, state in enumerate(states):
            for symbol, transitions in state.transitions.items():
                for state2 in transitions:
                    j = states_index[state2]
                    R[i][j][0] = GrammarBuilder.regex_union(R[i][j][0], symbol)

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    R[i][j][k + 1] = GrammarBuilder.regex_union(R[i][j][k], GrammarBuilder.regex_concat(R[i][k][k], GrammarBuilder.regex_concat(GrammarBuilder.regex_star(R[k][k][k]), R[k][j][k])))

        e = None
        for i in range(n):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
            if states[i].final:
                e = GrammarBuilder.regex_union(e, R[0][i][n])
        return e