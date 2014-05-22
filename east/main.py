# -*- coding: utf-8 -*

import getopt
import os
import sys

from east import applications
from east.synonyms import synonyms
from east import utils


def main(args):
    opts, args = getopt.getopt(args, "a:sd")
    opts = dict(opts)
    opts.setdefault("-a", "easa")

    input_path = os.path.abspath(args[0])
    keyphrases_file = os.path.abspath(args[1])
    use_synonyms = "-s" in opts
    normalized_scores = "-d" not in opts
    ast_algorithm = opts["-a"]

    if os.path.isdir(input_path):
        input_files = [os.path.abspath(input_path) + "/" + file_name
                       for file_name in os.listdir(input_path)
                       if file_name.endswith(".txt")]
    else:
        input_files = [os.path.abspath(input_path)]

    publications = {}
    for filename in input_files:
        with open(filename) as f:
            publications[os.path.basename(filename)[:-4]] = f.read()

    with open(keyphrases_file) as f:
        keyphrases = map(lambda k: utils.prepare_text(k), f.read().splitlines())

    if use_synonyms:
        synonimizer = synonyms.SynonymExtractor(input_path)
    else:
        synonimizer = None

    pk_table = applications.pk_table(publications, keyphrases, ast_algorithm,
                                     normalized_scores, synonimizer)

    res = u""
    for publication in sorted(pk_table.keys()):
        res += '<publication name="%s">\n' % publication
        for keyphrase in pk_table[publication]:
            res += '  <keyphrase text="%s">' % keyphrase
            res += '%.3f' % pk_table[publication][keyphrase]
            res += '</keyphrase>\n'
        res += '</publication>\n'

    print res.encode("utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
