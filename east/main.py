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
    opts, args = getopt.getopt(args, "s:a:f:c:r:p:dy")
    opts = dict(opts)

    # Default values for non-boolean options
    opts.setdefault("-s", "ast")    # Similarity measure to use ("cosine" / "ast")
    opts.setdefault("-a", "easa")   # Algorithm to use for computing ASTs
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
            keyphrases = map(lambda k: utils.prepare_text(k), f.read().splitlines())

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

        # Similarity measure
        similarity_measure = opts["-s"]
        if similarity_measure == "ast":
            ast_algorithm = opts["-a"]
            normalized_scores = "-d" not in opts
            similarity_measure = relevance.ASTRelevanceMeasure(ast_algorithm, normalized_scores)
        elif similarity_measure == "cosine":
            # TODO(mikhaildubov): add options fot this measure
            similarity_measure = relevance.CosineRelevanceMeasure()

        # Synomimizer
        use_synonyms = "-y" in opts
        synonimizer = synonyms.SynonymExtractor(text_collection_path) if use_synonyms else None

        if subcommand == "table":

            keyphrases_table = applications.keyphrases_table(
                                    keyphrases, texts, similarity_measure_factory,
                                    synonimizer)

            opts.setdefault("-f", "xml")  # Table output format ("csv" is the other option)
            table_format = opts["-f"].lower()

            try:
                res = formatting.format_table(keyphrases_table, table_format)
                print res.encode("utf-8", "ignore")
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
                                                  similarity_measure, synonimizer)

            opts.setdefault("-f", "edges")  # Graph output format (also "gml" possible)
            graph_format = opts["-f"].lower()

            try:
                res = formatting.format_graph(graph, graph_format)
                print res.encode("utf-8", "ignore")
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
