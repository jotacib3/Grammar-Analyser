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

def metodo_predictivo_no_recursivo(G, M=None, firsts=None, follows=None):
    
    # checking table...
    if M is None:
        if firsts is None:
            firsts = compute_firsts(G)
        if follows is None:
            follows = compute_follows(G, firsts)
        _, M = build_LL1_table(G, firsts, follows)   
   
    def parser(w):       
        stack = [G.startSymbol]
        cursor = 0
        output= []        
        
        while len(stack) > 0:           
            top = stack.pop()
            a = w[cursor]          
            
            if top.IsTerminal:
                if top != a:
                    st.error(f"La cadena {w} no pertenece al lenguaje generado por la gramática:\n{G}\nSe esperaba {top} en la posición {cursor} y en su lugar está {a} ")
                    return output
                cursor += 1
                
            else:              
                production = M[top,a][0]
                alpha = production.Right
                output.append(production)               
                for i in range(len(alpha) - 1, -1, -1):
                    stack.append(alpha[i])

        return output 
    
    return parser