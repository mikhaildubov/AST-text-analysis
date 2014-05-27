# -*- coding: utf-8 -*

import itertools
import sys

from east.asts import base
from east import utils

def keyphrases_table(keyphrases, texts, ast_algorithm="easa", normalized=True, synonimizer=None):
    """
    Constructs the keyphrases table, containing their matching scores in a set of texts.

    The resulting table is stored as a dictionary of dictionaries,
    where the entry table["keyphrase"]["text"] corresponds
    to the matching score (0 <= score <= 1) of keyphrase "keyphrase"
    in the text named "text".
    
    :param keyphrases: list of unicode strings
    :param texts: dictionary of form {text_name: text}
    :param ast_algorithm: AST implementation to use
    :param normalized: whether the scores should be normalized
    :param synonimizer: SynonymExtractor object to be used

    :returns: dictionary of dictionaries, having keyphrases on its first level and texts
              on the second level.  
    """

    i = 0
    total_texts = len(texts)
    asts = {}
    for text in texts:
        i += 1
        sys.stdout.write("\rConstructing ASTs: %i/%i" % (i, total_texts))
        sys.stdout.flush()
        asts[text] = base.AST.get_ast(ast_algorithm, utils.text_to_strings_collection(texts[text]))

    i = 0
    total_keyphrases = len(keyphrases)
    total_scores = total_texts * total_keyphrases
    res = {}
    for keyphrase in keyphrases:
        res[keyphrase] = {}
        for text in texts:
            i += 1
            sys.stdout.write("\rCalculating matching scores: %i/%i" % (i, total_scores))
            sys.stdout.flush()
            res[keyphrase][text] = asts[text].score(keyphrase, normalized=normalized,
                                                    synonimizer=synonimizer)

    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

    return res


def keyphrases_graph(keyphrases, texts, significance_level=0.6, score_treshold=0.25,
                     ast_algorithm="easa", normalized=True, synonimizer=None):
    """
    Constructs the keyphrases relation graph based on the given texts corpus.

    The graph construction algorithm is based on the analysis of co-occurrences of key phrases
    in the text corpus. A key phrase is considered to imply another one if that second phrase
    occurs frequently enough in the same texts as the first one (that frequency is controlled
    by the significance_level). A keyphrase counts as occuring in a text if its matching score
    for that text ecxeeds some threshold (Mirkin, Chernyak, & Chugunova, 2012).

    :param keyphrases: list of unicode strings
    :param texts: dictionary of form {text_name: text}
    :param significance_level: significance level of the graph in [0; 1], 0.6 by default
    :param score_treshold: threshold for the matching score in [0; 1] where a keyphrase starts
                           to be considered as occuring in the corresponding text, 0.25 by default
    :param synonimizer: SynonymExtractor object to be used

    :returns: graph in a dictionary format: dictionary keys are node labels, while each key points
              to a list of adjacent node labels ({"A": ["B", "C"], "B": ["A"], "C": []})
    """

    # Keyphrases table
    table = keyphrases_table(keyphrases, texts, ast_algorithm, normalized, synonimizer)
    
    # Dictionary { "keyphrase" => set(names of texts containing "keyphrase") }
    keyphrase_texts = {keyphrase: set([text for text in texts
                                       if table[keyphrase][text] >= score_treshold])
                       for keyphrase in keyphrases}
    
    # Initializing the graph object with nodes
    graph = {k: [] for k in keyphrases}
    
    # Creating arcs
    # NOTE(msdubov): permutations(), unlike combinations(), treats (1,2) and (2,1) as different
    for (k1, k2) in itertools.permutations(keyphrases, 2):
        if (len(keyphrase_texts[k1]) > 0 and 
            float(len(keyphrase_texts[k1] & keyphrase_texts[k2])) /
            len(keyphrase_texts[k1]) >= significance_level):
            graph[k1].append(k2)
            
    return graph
