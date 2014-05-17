Runtime & memory analysis
-------------------------

There are special scripts which can be used to analyse the performance of the basic AST construction algorithms in terms of runtime & memory consumption and print the results.

Runtime analysis
~~~~~~~~~~~~~~~~
*python -m analysis.runtime <n_from> <n_to> <n_step> <m>*

- *n_from, n_to, n_step* - Determine the lengths of strings in auto-generated string collections during analysis. These generated collections are "worst-case" ones.
- *m* - Number of strings in each collections (100 by default).

The script will compare the performances of all the 3 basic algorithms ("easa", "ast_linear", "ast_naive").

Memory analysis
~~~~~~~~~~~~~~~
*python -m analysis.memory <algorithm> <n_from> <n_to> <n_step> <m>*

- *algorithm* - "easa"/"ast_linear"/"ast_naive". Note that this script can analyse only one algorithm at a time.
- *n_from, n_to, n_step, m* - Auto-generated string collections paratemers, as in runtime analysis.
