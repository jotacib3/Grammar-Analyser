import graphviz as graphviz
import streamlit as st

from cmp.grammarbuilder import GrammarBuilder
from cmp.utils import ContainerSet
from cmp.parsers import *

import os

def get_words(text):
    try:
        for line in text.strip().split('\n'):
            if line.strip() != '':
                yield line.split()
    except:
        pass

st.header("Welcome to Grammar Analyzer")

st.subheader("Ingrese la gramática que desea analizar")
grammar_txt=st.text_area("Gramática","")

st.subheader("Ingrese las cadenas que desea reconocer")
words_txt=st.text_area("Cadenas","")

if st.button("Analizar"):
    if(grammar_txt!=""):
        G = GrammarBuilder.build_grammar(grammar_txt)
        if G is not None:
            words = get_words(words_txt)
            firsts = compute_firsts(G)
            follows = compute_follows(G, firsts)

            st.subheader("Conjunto First")
            st.write(ContainerSet.getStreamlitObject(firsts))

            st.subheader("Conjunto Follows")
            st.write(ContainerSet.getStreamlitObject(follows))
            
             # Eliminating indirect left recursion
            gb = GrammarBuilder(G)
            original = f'{gb}'
            gb.eliminate_LR()
            GILR = GrammarBuilder.build_grammar(f'{gb}') if f'{gb}' != original else original
            st.write("Gramática sin recursión izquierda indirecta")
            st.text(GILR)            

            # Eliminating direct left recursion
            gb = GrammarBuilder(G)
            original = f'{gb}'
            gb.eliminate_DLR()
            GDLR = GrammarBuilder.build_grammar(f'{gb}') if f'{gb}' != original else original                            
            st.write("Gramática sin recursión izquierda directa")
            st.text(GDLR)            

            # Eliminating common prefixes
            gb = GrammarBuilder(G)
            original = f'{gb}'            
            gb.eliminate_common_prefixes()
            GCP = GrammarBuilder.build_grammar(f'{gb}') if f'{gb}' != original else original
            st.write("Gramática sin prefijos comunes")
            st.text(GCP)

            # Eliminating unreachable productions
            gb = GrammarBuilder(G)
            original = f'{gb}'            
            gb.eliminate_unreachable_prod()
            GURP =  GrammarBuilder.build_grammar(f'{gb}') if f'{gb}' != original else original
            st.write("Gramática sin producciones inalcanzables")
            st.text(GURP)

            # Eliminating unfinished productions
            gb = GrammarBuilder(G)
            original = f'{gb}'            
            gb.eliminate_unfinished_prod()
            GUFP = GrammarBuilder.build_grammar(f'{gb}') if f'{gb}' != original else original
            st.write("Gramática sin producciones sin terminar")
            st.text(GUFP)

            # TODO: Falta aarreglar simbolo inicial que no s epone bien al aplicar estos cambios, ni      

            st.subheader("Análisis LL(1)")   
            conflict, dic = build_LL1_table(G, firsts, follows)

            if conflict is not None:
                st.warning("La gramática no es LL(1)")
                st.write("En la posición " + f'{conflict}' + " hay conflicto")
            
            # # else:
            # #     st.success("La gramática es LL(1)")
            #     data={}              
            #     for t in dic:  
            #         aux={}          
            #         for n in dic:                        
            #             if n[1]==t[1]:
            #                 aux[n[0]]=dic[n]                    
            #         data[t[1]]=aux
            #     st.write("Tabla LL(1)")
            #     st.table(data)

    else:
        st.write("No se ha insertado gramática para analizar")
