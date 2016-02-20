# -*- coding: utf-8 -*

import getopt
import os
import sys

from east import applications
from east import consts
from east import formatting
from east.synonyms import synonyms
from east import relevance
from east import utils


def main():
    args = sys.argv[1:]
    opts, args = getopt.getopt(args, "s:a:w:v:l:f:c:r:p:dy")
    opts = dict(opts)

    # Default values for non-boolean options
    # Language of the text collection / keyphrases ("english" / "german" / "french" /...)
    opts.setdefault("-l", consts.Language.ENGLISH)

    # Relevance measures
    # Similarity measure to use ("ast" / "cosine")
    opts.setdefault("-s", consts.RelevanceMeasure.AST)
    # Algorithm to use for computing ASTs ("easa" / "ast_linear" / "ast_naive")
    opts.setdefault("-a", consts.ASTAlgorithm.EASA)
    # Term weighting scheme used for computing the cosine similarity ("tf-idf" / "tf")
    opts.setdefault("-w", consts.TermWeighting.TF_IDF)
    # Elements of the vector space for the cosine similarity ("stems" / "lemmata" / "words")
    opts.setdefault("-v", consts.VectorSpace.STEMS)

    # Graph construction
    opts.setdefault("-c", "0.6")    # Referral confidence for graph construction
    opts.setdefault("-r", "0.25")   # Relevance threshold of the matching score
    opts.setdefault("-p", "1")      # Support threshold for graph nodes
    # NOTE(mikhaildubov): Default value of '-f' (output format) depends on the subcommand.

    if len(args) < 2:
        print("Invalid syntax: EAST should be called as:\n\n"
              "    east [options] <command> <subcommand> args\n\n"
              "Commands available: keyphrases.\n"
              "Subcommands available: table/graph.")
        return 1

    command = args[0]
    subcommand = args[1]

    if command == "keyphrases":

        if len(args) < 4:
            print('Invalid syntax. For keyphrases analysis, EAST should be called as:\n\n'
                  '    east [options] keyphrases <subcommand> "path/to/keyphrases.txt" '
                  '"path/to/texts/dir"')
            return 1

        # Keywords
        keyphrases_file = os.path.abspath(args[2])
        with open(keyphrases_file) as f:
            # NOTE(mikhaildubov): utils.prepare_text() should not be called in clients like this
            #                     one; it is already called in the applications module. Note that
            #                     the double-calling of this method results in errors.
            keyphrases = f.read().splitlines()

        # Text collection (either a directory or a single file)
        text_collection_path = os.path.abspath(args[3])

        if os.path.isdir(text_collection_path):
            text_files = [os.path.abspath(text_collection_path) + "/" + filename
                          for filename in os.listdir(text_collection_path)
                          if filename.endswith(".txt")]
        else:
            # TODO(mikhaildubov): Check that this single file ends with ".txt".
            text_files = [os.path.abspath(text_collection_path)]

        texts = {}
        for filename in text_files:
            with open(filename) as f:
                text_name = os.path.basename(filename).decode("utf-8")[:-4]
                texts[text_name] = f.read()

        language = opts["-l"]

        # Similarity measure
        similarity_measure = opts["-s"]
        if similarity_measure == "ast":
            ast_algorithm = opts["-a"]
            normalized_scores = "-d" not in opts
            similarity_measure = relevance.ASTRelevanceMeasure(ast_algorithm, normalized_scores)
        elif similarity_measure == "cosine":
            vector_space = opts["-v"]
            term_weighting = opts["-w"]
            similarity_measure = relevance.CosineRelevanceMeasure(vector_space, term_weighting)

        # Synomimizer
        use_synonyms = "-y" in opts
        synonimizer = synonyms.SynonymExtractor(text_collection_path) if use_synonyms else None

        if subcommand == "table":

            keyphrases_table = applications.keyphrases_table(
                                    keyphrases, texts, similarity_measure_factory,
                                    synonimizer, language)

            opts.setdefault("-f", "xml")  # Table output format ("csv" is the other option)
            table_format = opts["-f"].lower()

            try:
                res = formatting.format_table(keyphrases_table, table_format)
                print res
            except Exception as e:
                print e
                return 1

        elif subcommand == "graph":

            # Graph construction parameters: Referral confidence, relevance and support thresholds            
            referral_confidence = float(opts["-c"])
            relevance_threshold = float(opts["-r"])
            support_threshold = float(opts["-p"])

            graph = applications.keyphrases_graph(keyphrases, texts, referral_confidence,
                                                  relevance_threshold, support_threshold,
                                                  similarity_measure, synonimizer, language)

            opts.setdefault("-f", "edges")  # Graph output format (also "gml" possible)
            graph_format = opts["-f"].lower()

            try:
                res = formatting.format_graph(graph, graph_format)
                print res
            except Exception as e:
                print e
                return 1

        else:
            print "Invalid subcommand: '%s'. Please use one of: 'table', 'graph'." % subcommand
            return 1

    else:
        print "Invalid command: '%s'. Please use one of: 'keyphrases'." % command
        return 1



if __name__ == "__main__":
    main()
