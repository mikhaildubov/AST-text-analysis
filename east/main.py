# -*- coding: utf-8 -*

import getopt
import os
import sys

from east.asts import base
from east.synonyms import synonyms
from east import utils


def main(args):
    opts, args = getopt.getopt(args, "a:sd")
    opts = dict(opts)
    opts.setdefault("-a", "easa")

    input_text_file = os.path.abspath(args[0])
    keyphrases_file = os.path.abspath(args[1])
    use_synonyms = "-s" in opts
    normalized_scores = "-d" not in opts
    ast_algorithm = opts["-a"]

    with open(input_text_file) as f:
        text_collection = utils.text_to_strings_collection(f.read())

    with open(keyphrases_file) as f:
        keyphrases = map(lambda k: utils.prepare_text(k), f.read().splitlines())

    if use_synonyms:
        synonimizer = synonyms.SynonymExtractor(input_text_file)
    else:
        synonimizer = None

    ast = base.AST.get_ast(ast_algorithm, text_collection)
    scores = {keyphrase: ast.score(keyphrase, normalized=normalized_scores,
                                   synonimizer=synonimizer)
              for keyphrase in keyphrases}

    for keyphrase in keyphrases:
        print "%(keyphrase)s -> %(score).2f" % {"keyphrase": keyphrase,
                                                "score": scores[keyphrase]}


if __name__ == '__main__':
    main(sys.argv[1:])
