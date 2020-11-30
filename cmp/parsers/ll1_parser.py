import streamlit as st
from cmp.parsers.firsts_follows import compute_firsts, compute_follows

def build_LL1_table(G, firsts, follows):
    # init parsing table
    M = {}
    conflict = None
    
    # P: X -> alpha
    for production in G.Productions:
        X = production.Left
        alpha = production.Right        
        
        for t in firsts[alpha]:
            try:
                M[X, t].append(production)
                if conflict is None:
                    conflict = (X, t)
            except KeyError:
                M[X, t] = [production]
                    
       
        if firsts[alpha].contains_epsilon:
            for t in follows[X]:
                try:
                    M[X, t].append(production)
                    if conflict is None:
                        conflict = (X, t)
                except KeyError:
                    M[X, t] = [production]               
                         
    
    # parsing table is ready!!!
    return conflict, M

def metodo_predictivo_no_recursivo(G, M, firsts, follows):       
    # parser construction...
    def parser(w):
        # w ends with $ (G.EOF)
        # init:
        stack = [G.startSymbol]
        cursor = 0
        output = []
        
        # parsing w...
        while len(stack) > 0: 
            top = stack.pop()
            a = w[cursor]
            
            if top.IsTerminal:
                if top == a:
                    cursor += 1
                else:
                    st.error(f"La cadena {w} no pertenece al lenguaje generado por la gramática:\n{G}\nSe esperaba {top} en la posición {cursor} y en su lugar está {a} ")
                    return None
            else:
                try:
                    production = M[top,a][0]
                except KeyError:
                    st.error(f"La cadena {w} no pertenece al lenguaje generado por la gramática:\n{G}\n")
                    return None
                alpha = production.Right
                output.append(production)               
                for i in range(len(alpha) - 1, -1, -1):
                    stack.append(alpha[i])
        
        # left parse is ready!!!
        return output
    
    # parser is ready!!!
    return parser