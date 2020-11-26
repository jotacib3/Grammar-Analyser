import graphviz as graphviz
import streamlit as st

from cmp.grammarbuilder import GrammarBuilder
from cmp.utils import ContainerSet
from cmp.parsers.firsts_follows import compute_firsts, compute_follows

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

            grammar_clone = G.copy()
            is_not_null, acepted_symbols = GrammarBuilder.is_not_null(grammar_clone)
            GrammarBuilder.remove_bad_items(grammar_clone, keep_symbols=acepted_symbols)
            GrammarBuilder.remove_left_recursion(grammar_clone)
            GrammarBuilder.factorize_grammar(grammar_clone)
            st.write("Gramática sin prefijos comunes, recursión izquierda inmediata ni producciones inalcanzables")
            st.write(grammar_clone)            

    else:
        st.write("No se ha insertado gramática para analizar")
