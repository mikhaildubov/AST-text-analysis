EAST
====

**EAST** stands for the *Enhanced Annotated Suffix Tree* method for text analysis.


Installation
------------

To install EAST, run:

::

    $ pip install EAST

This may require admin permissions on your machine (and should then be run with *sudo*).

EAST comes both as a *CLI application* and as a *python library* (which can be imported and used in python code).


How to - CLI application
------------------------

Keyphrases table
~~~~~~~~~~~~~~~~

The basic use case for the AST method is to calculate matching scores for a set of keyphrases against a set of text files (the so-called **keyphrase table**). To do that with **east**, launch it as follows:

*$ east [-s] [-d] [-f <table_format>] [-a <ast_algorithm>] keyphrases table <keyphrases_file> <directory_with_txt_files>*

- The *-s* option stands for *synonyms* and determines whether the matching score should be computed taking into account the synonyms extracted from the text file.
- The *-d* option stands for *denormalized* and specifies whether the the matching score should be computed in the denormalized form (normalized by default, see *[Mirkin, Chernyak & Chugunova, 2012]*.
- The *-f* option specifies the format in which the table should be printed. The format is *XML* by default (see an example below); the *-f* option can also take *CSV* as its parameter.
- The *-a* option stands for *algorithm* and defines the actual AST method implementation to be used. Possible arguments are *"easa"* (Enhanced Annotated Suffix Arrays), *"ast_linear"* (Linear-time and -memory implementation of Annotated Suffix Trees) and *"ast_naive"* (a slow and memory-consumptive implementation, present just for comparison).
- Please note that you can also specify the path to a single text file instead of that for a directory. In case of the path to a directory, only *.txt* files will be processed.

If you want to print the output to some file, just redirect the *EAST* output (e.g. by appending *> filename.txt* to the command in Unix).

Sample output in the XML format:

::

    <table>
      <keyphrase value="KEYPHRASE_1">
        <text name="TEXT_1">0.250</text>
        <text name="TEXT_2">0.234</text>
      </keyphrase>
      <keyphrase value="KEYPHRASE_2">
        <text name="TEXT_1">0.121</text>
        <text name="TEXT_2">0.000</text>
      </keyphrase>
      <keyphrase value="KEYPHRASE_3">
        <text name="TEXT_1">0.539</text>
        <text name="TEXT_3">0.102</text>
      </keyphrase>
    </table>

    

Keyphrases graph
~~~~~~~~~~~~~~~~

The *east* software also allows to construct a **keyphrases relation graph**, which indicates implications between different keyphrases according to the text corpus being analysed. The graph construction algorithm is based on the analysis of co-occurrences of keyphrases in the text corpus. A keyphrase is considered to imply another one if that second phrase occurs frequently enough in the same texts as the first one (that frequency is controlled by the referral confidence parameter). A keyphrase counts as occuring in a text if its presence score for that text ecxeeds some threshold *[Mirkin, Chernyak, & Chugunova, 2012]*.

*$ east [-s] [-d] [-f <graph_format>] [-c <referral_confidence>] [-r <relevance_threshold>] [-p <support_threshold>] [-a <ast_algorithm>] keyphrases graph <keyphrases_file> <directory_with_txt_files>*

- The *-s*, *-d* and *-a* options configure the algorithm of computing the matching scores (exactly as for the *keyphrases table* command).
- The *-p* option configures the threshold for graph node support (the number of documents "containing" the corresponding keyphrase according to the AST method), starting with which the nodes get included into the graph.
- The *-f* option stands for *format* and determines in which format the resulting graph should come to the output. Possible values are:
    - *"GML"* (`Graph Modelling Language <http://en.wikipedia.org/wiki/Graph_Modelling_Language>`_, which can be used for graph visualization in tools like `Gephi <http://gephi.org>`_);
    - *"edges"*, which is just a list of edges in form *Some keyphrase -> <List of keyphrases it points to>* (simple but convenient for a quick analysis of implications between keyphrases).
- The *-c* option stands for *referral confidence* and controls the confidence level above which the implications between keyphrases are considered to be strong enough to be added as graph arcs. The confidence level should be a float in [0; 1] and is 0.6 by default.
- The *-r* option stands for *relevance threshold of the matching score* and controls the minimum matching score value where keyphrases start to be counted as occuring in the corresponding texts. It should be a float in [0; 1] and is 0.25 by default.


Sample output in the *edges* format:

::

    KEYPHRASE_1 -> KEYPHRASE_3
    KEYPHRASE_2 -> KEYPHRASE_3, KEYPHRASE_4
    KEYPHRASE_4 -> KEYPHRASE_1

The same graph in *GML*:

::

    graph
    [
      node
      [
        id 0
        label "KEYPHRASE_1"
      ]
      node
      [
        id 1
        label "KEYPHRASE_2"
      ]
      node
      [
        id 2
        label "KEYPHRASE_3"
      ]
      node
      [
        id 3
        label "KEYPHRASE_4"
      ]
      edge
      [
        source 0
        target 2
      ]
      edge
      [
        source 1
        target 2
      ]
      edge
      [
        source 1
        target 3
      ]
      edge
      [
        source 3
        target 0
      ]
    ]


How to - Python library
------------------------

The example below shows how to use the *EAST* package in code. Here, we build an Annotated suffix tree for a collection of two strings (*"XABXAC"* and *"HI"*) and then calculate matching scores for two queries (*"ABCI"* and *"NOPE"*):

.. parsed-literal::

    from east.asts import base

    ast = base.AST.get_ast(["XABXAC", "HI"])

    print ast.score("ABCI")   *# 0.1875*
    print ast.score("NOPE")   *# 0*


The *get_ast()* method takes the list of input strings and constructs an annotated suffix tree using suffix arrays by default as the underlying data structure (this is the most efficient implementation known). The algorithm used for AST construction can be optionally specified via the second parameter to *get_ast()* (along with *"easa"*, its possible values include *"ast_linear"* and *"ast_naive"*)

Working with real texts already requires some preprocessing, such as splitting a single input text into a collection of small-sized strings, which later enables matching scores for queries to be more precise. There is a special method *text_to_strings_collection()* in *EAST* which does that for you. The following example processes a real text collection and calculates matching scores for an input query:

.. parsed-literal::

    import itertools

    from east.asts import base
    from east import utils

    text_collection = [...]  *# e.g. retrieved from a set of *.txt files*
    strings_collection = itertools.chain.from_iterable(
                            [utils.text_to_strings_collection(text)
                             for text in text_collection])

    ast = base.AST.get_ast(strings_collection)

    print ast.score("Hello, world")  *# will be in [0; 1]*

