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
    
    :param keyphrases: list of strings
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
        if not utils.output_is_redirected():
            sys.stdout.write("\rConstructing ASTs: %i/%i" % (i, total_texts))
            sys.stdout.flush()
        asts[text] = base.AST.get_ast(utils.text_to_strings_collection(texts[text]), ast_algorithm)

    i = 0
    keyphrases_prepared = {keyphrase: utils.prepare_text(keyphrase)
                           for keyphrase in keyphrases}
    total_keyphrases = len(keyphrases)
    total_scores = total_texts * total_keyphrases
    res = {}
    for keyphrase in keyphrases:
        if not keyphrase:
            continue
        res[keyphrase] = {}
        for text in texts:
            i += 1
            if not utils.output_is_redirected():
                sys.stdout.write("\rCalculating matching scores: %i/%i" % (i, total_scores))
                sys.stdout.flush()
            res[keyphrase][text] = asts[text].score(keyphrases_prepared[keyphrase],
                                                    normalized=normalized, synonimizer=synonimizer)

    if not utils.output_is_redirected():
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    return res


def keyphrases_graph(keyphrases, texts, referral_confidence=0.6, relevance_threshold=0.25,
                     support_threshold=1, ast_algorithm="easa", normalized=True, synonimizer=None):
    """
    Constructs the keyphrases relation graph based on the given texts corpus.

    The graph construction algorithm is based on the analysis of co-occurrences of key phrases
    in the text corpus. A key phrase is considered to imply another one if that second phrase
    occurs frequently enough in the same texts as the first one (that frequency is controlled
    by the referral_confidence). A keyphrase counts as occuring in a text if its matching score
    for that text ecxeeds some threshold (Mirkin, Chernyak, & Chugunova, 2012).

    :param keyphrases: list of unicode strings
    :param texts: dictionary of form {text_name: text}
    :param referral_confidence: significance level of the graph in [0; 1], 0.6 by default
    :param relevance_threshold: threshold for the matching score in [0; 1] where a keyphrase starts
                                to be considered as occuring in the corresponding text, 0.25 by default
    :param support_threshold: threshold for the support of a node (the number of documents containing
                              the corresponding keyphrase) such that it can be included into the graph
    :param synonimizer: SynonymExtractor object to be used

    :returns: graph dictionary in a the following format:
                {
                    "nodes": [
                        {
                            "id": <id>,
                            "label": "keyphrase",
                            "support": <# of documents containing the keyphrase>
                        },
                        ...
                    ]
                    "edges": [
                        {
                            "source": "node_id",
                            "target": "node_id",
                            "confidence": <confidence_level>
                        },
                        ...
                    ]
                }
    """

    # Keyphrases table
    table = keyphrases_table(keyphrases, texts, ast_algorithm, normalized, synonimizer)
    
    # Dictionary { "keyphrase" => set(names of texts containing "keyphrase") }
    keyphrase_texts = {keyphrase: set([text for text in texts
                                       if table[keyphrase][text] >= relevance_threshold])
                       for keyphrase in keyphrases}

    # Initializing the graph object with nodes
    graph = {
        "nodes": [
            {
                "id": i,
                "label": keyphrase,
                "support": len(keyphrase_texts[keyphrase])
            } for i, keyphrase in enumerate(keyphrases)
        ],
        "edges": []
    }

    # Removing nodes with small support after we've numbered all nodes
    graph["nodes"] = [n for n in graph["nodes"]
                      if len(keyphrase_texts[n["label"]]) >= support_threshold]
    
    # Creating edges
    # NOTE(msdubov): permutations(), unlike combinations(), treats (1,2) and (2,1) as different
    for i1, i2 in itertools.permutations(range(len(graph["nodes"])), 2):
        node1 = graph["nodes"][i1]
        node2 = graph["nodes"][i2]
        confidence = (float(len(keyphrase_texts[node1["label"]] &
                                keyphrase_texts[node2["label"]])) /
                      max(len(keyphrase_texts[node1["label"]]), 1))
        if confidence >= referral_confidence:
            graph["edges"].append({
                "source": node1["id"],
                "target": node2["id"],
                "confidence": confidence
            })
            
    return graph
