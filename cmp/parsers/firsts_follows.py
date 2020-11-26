from cmp.utils import ContainerSet

def compute_local_first(firsts, alpha):    
    """
    Computes First(alpha), given First(Vt) and First(Vn) 
    alpha in (Vt U Vn)*
    """
    first_alpha = ContainerSet()
    
    try:
        alpha_is_epsilon = alpha.IsEpsilon
    except:
        alpha_is_epsilon = False

    # alpha == epsilon ? First(alpha) = { epsilon }
    if alpha_is_epsilon:
        first_alpha.set_epsilon()

    # alpha = X1 ... XN
    # First(Xi) subset of First(alpha)
    # epsilon  in First(X1)...First(Xi) ? First(Xi+1) subset of First(X) & First(alpha)
    # epsilon in First(X1)...First(XN) ? epsilon in First(X) & First(alpha)
    else:
        for symbol in alpha:
            first_symbol = firsts[symbol]
            first_alpha.update(first_symbol)
            if not first_symbol.contains_epsilon:
                break
        else:
            first_alpha.set_epsilon()

    return first_alpha


# Computes First(Vt) U First(Vn) U First(alpha)
# P: X -> alpha
def compute_firsts(G):
    firsts = {}
    change = True
    
    # init First(Vt)
    for terminal in G.terminals:
        firsts[terminal] = ContainerSet(terminal)
        
    # init First(Vn)
    for nonterminal in G.nonTerminals:
        firsts[nonterminal] = ContainerSet()
    
    while change:
        change = False
        
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right
            
            # get current First(X)
            first_X = firsts[X]
                
            # init First(alpha)
            try:
                first_alpha = firsts[alpha]
            except:
                first_alpha = firsts[alpha] = ContainerSet()
            
            # CurrentFirst(alpha)???
            local_first = compute_local_first(firsts, alpha)
            
            # update First(X) and First(alpha) from CurrentFirst(alpha)
            change |= first_alpha.hard_update(local_first)
            change |= first_X.hard_update(local_first)
                    
    # First(Vt) + First(Vt) + First(RightSides)
    return firsts


def compute_follows(G, firsts):
    follows = { }
    change = True
    
    # init Follow(Vn)
    for nonterminal in G.nonTerminals:
        follows[nonterminal] = ContainerSet()
    follows[G.startSymbol] = ContainerSet(G.EOF)
    
    while change:
        change = False
        
        # P: X -> alpha
        for production in G.Productions:
            X = production.Left
            alpha = production.Right            
            follow_X = follows[X]
            
            ###################################################
            # X -> zeta Y beta
            # First(beta) - { epsilon } subset of Follow(Y)
            # beta ->* epsilon or X -> zeta Y ? Follow(X) subset of Follow(Y)
            ###################################################
            for i in range(len(alpha)):
                    if alpha[i].IsTerminal:
                        continue
                    follow_y = follows[alpha[i]]                    
                    first_beta = compute_local_first(firsts,alpha[i+1:])                     
                    change|=follow_y.update(first_beta)
                    if(first_beta).contains_epsilon or len(alpha[i+1:]) == 0:
                        change |= follow_y.update(follow_X)
                     
                                              
                
            ###################################################
                       
    # Follow(Vn)
    return follows
