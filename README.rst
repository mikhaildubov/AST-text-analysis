EAST
----

**EAST** stands for *Enhanced Annotated Suffix Tree* method for text analysis.


How to
------

To calculate matching scores for a set of keyphrases against some text file, **launch** *east* using:

*python -m east.main [-s] [-d] [-a <ast_algorithm>] <text_file> <keyphrases_file>*

- The *-s* option stands for *synonyms* and determines whether the matching score should be computed taking into account the synonyms extracted from the text file.
- The *-d* option stands for *denormalized* and specifies whether the the matching score should be computed in the denormalized form (normalized by default, see *[Mirkin, Chernyak & Chugunova, 2012]*.
- The *-a* option stands for *algorithm* and defines the actual AST method implementation to be used. Possible arguments are *"easa"* (Enhanced Annotated Suffix Arrays) and *"ast_linear"* (Linear-time and -memory implementation of Annotated Suffix Trees).
