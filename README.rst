EAST
----

**EAST** stands for *Enhanced Annotated Suffix Tree* method for text analysis.


How to
------

Keyphrases table
~~~~~~~~~~~~~~~~

The basic use case for the AST method is to calculate matching scores for a set of keyphrases against a set of text files (the so-called **keyphrase table**). To do that with **east**, launch it as follows:

*$ east [-s] [-d] [-a <ast_algorithm>] keyphrases table <keyphrases_file> <directory_with_txt_files>*

- The *-s* option stands for *synonyms* and determines whether the matching score should be computed taking into account the synonyms extracted from the text file.
- The *-d* option stands for *denormalized* and specifies whether the the matching score should be computed in the denormalized form (normalized by default, see *[Mirkin, Chernyak & Chugunova, 2012]*.
- The *-a* option stands for *algorithm* and defines the actual AST method implementation to be used. Possible arguments are *"easa"* (Enhanced Annotated Suffix Arrays) and *"ast_linear"* (Linear-time and -memory implementation of Annotated Suffix Trees).
- Please note that you can also specify the path to a single text file instead of that for a directory. In case of the path to a directory, only *.txt* files will be processed.

The output is in an XML-like format:

::

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

    

Keyphrases graph
~~~~~~~~~~~~~~~~

The *east* software also allows to construct a **keyphrases relation graph**, which indicates implications between different keyphrases according to the text corpus being analysed. The graph construction algorithm is based on the analysis of co-occurrences of keyphrases in the text corpus. A keyphrase is considered to imply another one if that second phrase occurs frequently enough in the same texts as the first one (that frequency is controlled by the significance level parameter). A keyphrase counts as occuring in a text if its presence score for that text ecxeeds some threshold *[Mirkin, Chernyak, & Chugunova, 2012]*.

*$ east [-s] [-d] [-a <ast_algorithm>] [-l significance_level] [-t score_threshold] keyphrases graph <keyphrases_file> <directory_with_txt_files>*

- The *-s*, *-d* and *-a* options configure the algorithm of computing the matching scores (exactly as for the *keyphrases table* command).
- The *-l* option stands for *level of significance* and controls the significance level above which the implications between keyphrases are considered to be strong enough to be added as graph arcs. The significance level should be a float in [0; 1] and is 0.6 by default.
- The *-t* option stands for *threshold of the matching score* and controls the minimum matching score value where keyphrases start to be counted as occuring in the corresponding texts. It should be a float in [0; 1] and is 0.25 by default.


The output is the set of arcs of the graph, which are essentially implications between keyphrases:

::

    KEYPHRASE_1 -> KEYPHRASE_3
    KEYPHRASE_2 -> KEYPHRASE_3
    KEYPHRASE_2 -> KEYPHRASE_4
    KEYPHRASE_4 -> KEYPHRASE_1
