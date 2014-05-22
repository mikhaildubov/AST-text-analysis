# -*- coding: utf-8 -*

from east.asts import base
from east import utils

def pk_table(publications, keyphrases, ast_algorithm="easa", normalized=True, synonimizer=None):
    """
    Constructs the "Publication-Keyword" table for the input data.

    The resulting table is stored as a dictionary of dictionaries,
    where the entry table['publication']['keyphrase'] corresponds
    to the matching score (0 <= score <= 1) of keyphrase 'keyphrase'
    in publication named 'publication'.
    
    :param publications: dictionary of form {publication_name: text}
    :param keyphrases: list of strings
    :param ast_algorithm: AST implementation to use
    :param normalized: whether the scores should be normalized
    :param synonimizer: SynonymExtractor object to be used

    :returns: dictionary of dictionaries   
    """
    asts = {p: base.AST.get_ast(ast_algorithm, utils.text_to_strings_collection(publications[p]))
            for p in publications}

    return {p: {keyphrase: asts[p].score(keyphrase, normalized=normalized,
                                         synonimizer=synonimizer) for keyphrase in keyphrases}
            for p in publications}
