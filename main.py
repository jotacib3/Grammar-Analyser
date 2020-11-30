import graphviz as graphviz
import streamlit as st

from cmp.grammarbuilder import GrammarBuilder
from cmp.utils import ContainerSet
from cmp.parsers import *
from cmp.derivation_tree import DerivationTree

import os

def printDerivationTree(parser, parser_type, words):
    derivations = []
    for word in words:
        try:
            derivations.append(parser(word))
            print(len(derivations))
        except Exception as ex:
            st.error(ex)
            print(word)  

    parser_derivations = parser.derivations
    derivations_tree = [DerivationTree.get_tree(derivation, parser_type).graph() if derivation else None for derivation in derivations]
    
    name = "Análisis shift-reduce y Árboles de derivación" if parser_type == "right" else "Árboles de derivación"
    st.write(name)

    if parser_type == "right":
        col1, col2, col3, col4, col5 = st.beta_columns([1, 1, 0.2 , 1, 2])        
        for index, derivation in enumerate(parser_derivations):
            col1.write(str(derivation[0]))
            col2.write(str(derivation[1]))
            col3.write("|")
            col4.write(str(derivation[2]) + " " + str(derivation[3]))
            
            try:
                col5.write(derivations_tree[index])
            except:
                pass
       
    else: 
        for derivation_graph in derivations:
            st.write(derivation_graph)

def printLL1Table(table):
    data={}              
    for t in table:
        aux={}          
        for n in table:                        
            if n[1]==t[1]:
                aux[n[0]]=table[n]                    
        data[t[1]]=aux
    st.write("LL(1) Table")
    st.table(data)

def printTable(items, table_name):
    table = {}
    for key, value in items:
        table[key] = set(value) 
    data={}              
    for t in table:
        aux={}          
        for n in table:                        
            if n[1]==t[1]:
                aux[n[0]]=table[n]                    
        data[t[1]]=aux
    st.write(table_name)
    st.table(data)

st.set_page_config('Analizador de Gramáticas', None, "wide")

with st.beta_container():
    col1, col2, col3 = st.beta_columns([0.2, 1, 0.2])
    col2.header("Welcome to Grammar Analyzer")

    col2.subheader("Ingrese la gramática que desea analizar")
    grammar_txt=col2.text_area("Gramática","", 200)

    col2.subheader("Ingrese las cadenas que desea reconocer")
    words_txt=col2.text_area("Cadenas","", 100)

    if col2.button("Analizar"):
        if(grammar_txt!=""):
            G = GrammarBuilder.build_grammar(grammar_txt)
            # TODO: Arreglar manejo de errores el item esta mal formado, cunaod se ingresan cadenas que no son de la gramatica   
            words = [GrammarBuilder.tokenizer(G, word) for word in words_txt.split('\n')]

            if G is not None:
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
                gb.eliminate_DLR()
                GDLR = GrammarBuilder.build_grammar(f'{gb}') if f'{gb}' != original else original                            
                st.write("Gramática sin recursión izquierda directa")
                st.text(GDLR)            

                # Eliminating common prefixes
                gb = GrammarBuilder(G)    
                gb.eliminate_common_prefixes()
                GCP = GrammarBuilder.build_grammar(f'{gb}') if f'{gb}' != original else original
                st.write("Gramática sin prefijos comunes")
                st.text(GCP)

                # Eliminating unreachable productions
                gb = GrammarBuilder(G)    
                gb.eliminate_unreachable_prod()
                GURP =  GrammarBuilder.build_grammar(f'{gb}') if f'{gb}' != original else original
                st.write("Gramática sin producciones inalcanzables")
                st.text(GURP)

                # Eliminating unfinished productions
                gb = GrammarBuilder(G)      
                gb.eliminate_unfinished_prod()
                GUFP = GrammarBuilder.build_grammar(f'{gb}') if f'{gb}' != original else original
                st.write("Gramática sin producciones sin terminar")
                st.text(GUFP)   
                
                st.subheader("Análisis LL(1)")   
                try:
                    conflict, TableLL1 = build_LL1_table(G, firsts, follows)
                except:
                    pass

                if conflict is not None:
                    st.warning("La gramática no es LL(1)")
                    st.write("En la posición " + f'{conflict}' + " hay conflicto")
                else:
                    st.success("La gramática es LL(1)")
                    printLL1Table(TableLL1)
                    printDerivationTree(metodo_predictivo_no_recursivo(G, TableLL1, firsts, follows), 'left', words)

                # LR(0)
                st.subheader('LR(0) Analisis')
                parser = None
                try:        
                    parserLR0 = LR0Parser(G)
                    conflicLR0 = parserLR0.AnalyseTable()

                    if conflicLR0.__len__() != 0:
                        st.warning("La gramática no es LR(0)")
                        for v in conflicLR0:
                            st.write("En la posición " + f'{v}' + " hay conflicto")
                    else:
                        parser = parserLR0

                        st.success("La gramática es LR(0)")
                        printTable(parserLR0.action.items(), 'Action Table LR(0)')   
                        printTable(parserLR0.goto.items(), 'Goto Table LR(0)')

                        st.write("Autómata LR(0)")                    
                        st.graphviz_chart(parserLR0.automaton.graph())  

                except Exception as error:
                    st.error(error)

                st.subheader("Análisis LALR(1)")
                try:
                    parserLALR1 = LALR1_DummyParser(G)  

                    conflicLALR1 = parserLALR1.AnalyseTable() 
                    if conflicLALR1.__len__() != 0:
                        st.warning("La gramática no es LALR(1)")
                        for v in conflicLALR1:
                            st.write("En la posición " + f'{v}' + " hay conflicto")
                    else:
                        parser = parserLALR1

                        st.success("La gramática es LALR(1)")
                        printTable(parserLALR1.action.items(), 'Action Table LALR(1)')   
                        printTable(parserLALR1.goto.items(), 'Goto Table LALR(1)') 

                        st.write("Autómata LALR(1)")    
                        st.graphviz_chart(parserLALR1.automaton.graph())
                        
                except Exception as error:
                    st.error(error) 

                st.subheader("Análisis LR(1)")
                try: 
                    parserLR1 = LR1Parser(G)
                
                    conflicLR1 = parserLR1.AnalyseTable() 
                    if conflicLR1.__len__() != 0:
                        st.warning("La gramática no es LR(1)")
                        for v in conflicLR1:
                            st.write("En la posición " + f'{v}' + " hay conflicto")
                    else:
                        parser = parserLR1

                        st.success("La gramática es LR(1)")
                        printTable(parserLR1.action.items(), 'Action Table LR(1)')   
                        printTable(parserLR1.goto.items(), 'Goto Table LR(1)') 

                        st.write("Autómata LR(1)")    
                        st.graphviz_chart(parserLR1.automaton.graph())

                except Exception as error:
                    st.error(error)

                st.subheader("Análisis SLR(1)")
                try:
                    parserSLR1 = SLR1Parser(G)            

                    conflicSLR1 = parserSLR1.AnalyseTable()
                    if conflicSLR1.__len__() != 0:
                        st.warning("La gramática no es SLR(1)")
                        for v in conflicSLR1:
                            st.write("En la posición " + f'{v}' + " hay conflicto")
                    else:
                        parser = parserSLR1

                        st.success("La gramática es SLR(1)")
                        printTable(parserSLR1.action.items(), 'Action Table SLR(1)')   
                        printTable(parserSLR1.goto.items(), 'Goto Table SLR(1)') 

                        st.write("Autómata SLR(1)")    
                        st.graphviz_chart(parserSLR1.automaton.graph())

                except Exception as error:
                    st.error(error)

                if parser is not None:
                    printDerivationTree(parser, 'right', words)

                st.subheader("Análisis Regular")  

                regular_automaton, is_regular = GrammarBuilder.build_automaton(G) 

                if is_regular:
                    st.success("La gramática es regular")    
                    st.write("Autómata Regular")
                    st.graphviz_chart(regular_automaton.graph(False))
                    try:
                        regular_expersion = GrammarBuilder.regexp_from_automaton(regular_automaton)
                        st.write("Expresion regular")
                        st.text(regular_expersion)
                    except Exception as ex:
                        st.error(ex)
                    

                else:
                    st.warning("La gramática no es regular")                 

        else:
            st.write("No se ha insertado gramática para analizar")
