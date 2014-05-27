# -*- coding: utf-8 -*

import getopt
import os
import sys

from east import applications
from east.synonyms import synonyms
from east import utils


def main():
    args = sys.argv[1:]
    opts, args = getopt.getopt(args, "a:l:t:sd")
    opts = dict(opts)
    opts.setdefault("-a", "easa")
    opts.setdefault("-l", "0.6")
    opts.setdefault("-t", "0.25")

    if len(args) < 2:
        print "Invalid syntax."
        return 1

    command_group = args[0]
    command = args[1]

    if command_group == "keyphrases":

        keyphrases_file = os.path.abspath(args[2])
        input_path = os.path.abspath(args[3])
        use_synonyms = "-s" in opts
        normalized_scores = "-d" not in opts
        ast_algorithm = opts["-a"]
        significance_level = float(opts["-l"])
        score_threshold = float(opts["-t"])

        if os.path.isdir(input_path):
            input_files = [os.path.abspath(input_path) + "/" + filename
                           for filename in os.listdir(input_path)
                           if filename.endswith(".txt")]
        else:
            input_files = [os.path.abspath(input_path)]

        texts = {}
        for filename in input_files:
            with open(filename) as f:
                text_name = os.path.basename(filename).decode("utf-8")[:-4]
                texts[text_name] = f.read()

        with open(keyphrases_file) as f:
            keyphrases = map(lambda k: utils.prepare_text(k), f.read().splitlines())

        if use_synonyms:
            synonimizer = synonyms.SynonymExtractor(input_path)
        else:
            synonimizer = None

        if command == "table":

            keyphrases_table = applications.keyphrases_table(keyphrases, texts, ast_algorithm,
                                                             normalized_scores, synonimizer)
            res = u""
            for keyphrase in sorted(keyphrases_table.keys()):
                res += u'<keyphrase value="%s">\n' % keyphrase
                for text in sorted(keyphrases_table[keyphrase].keys()):
                    res += u'  <text name="%s">' % text
                    res += u'%.3f' % keyphrases_table[keyphrase][text]
                    res += u'</text>\n'
                res += u'</keyphrase>\n'

            print res.encode("utf-8", "ignore")

        elif command == "graph":

            graph = applications.keyphrases_graph(keyphrases, texts, significance_level,
                                                  score_threshold, ast_algorithm,
                                                  normalized_scores, synonimizer)
            res = u""
            for node in graph:
                if graph[node]:
                    res += "%s -> %s\n" % (node, ", ".join(graph[node]))

            print res.encode("utf-8", "ignore")

        else:
            print "Invalid command."
            return 1

    else:
        print "Invalid command."
        return 1



if __name__ == "__main__":
    main()
