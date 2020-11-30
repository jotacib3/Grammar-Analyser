 <p align="center">Grammar Analyser. Primer Projecto de la asignatura Compilación</p>
    <p align="center">

## Descripción
La aplicación permite realizar determinados prrocesamientos sobre gramáticas libres del contexto:
* Calcualar los conjuntos First y Follow y se muestra la gramática sin prefijos comunes, sin recursión izquierda inmediata
y sn producciones inecesarias.
* Determinar si la gramática es LL(1), LR(0), SLR(1), LR(1), LALR(1). Para cada una de ellas se muestra la tabla método
predictivo recursivo en el caso de las LL(1), y las tablas de action y goto junto con el autómata en las de parser ascendente.
Se muestra además el árbol de derivación de las cadenas que se inserten par aanalizar así como el análisis del parser.(shift-reduce) de la cadena si la gramática se parsea con algún parser ascendente.
* Si la gramática es regular muestra su autómata y expresión regular equivalente. 

## Instalción
```bash
$ pip3 install graphviz

$ pip3 install streamlit
```


# Ejecutando app
`$ streamlit run main.py`

## The grammar must be free of context and is written in the following format:

```
S -> A | B
A -> to A | epsilon
B -> b B | epsilon
```

* Usa '->' para indicar una producción, y '|' para indicar multiples producciones con la misma cabecera.
* Usa 'epsilon' para indicar el simbolo terminal especial de el grafo.
* Todos los symboles que están en la cabecera de alguna producción deben ser No Terminales.
* Entre dos símbolos continuos debe haber un espacio en blanco.

## GRACIAS POR USAR GRAMMAR ANALYSER!