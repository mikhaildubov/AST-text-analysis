# -*- coding: utf-8 -*

import getopt
import sys

from east.synonyms import synonyms

def main(args):
    opts, args = getopt.getopt(args, "")

    path = args[0]

    synonimizer = synonyms.SynonymExtractor(path)
    print "Prepared synonimizer\n"

    synonym_dicts = synonimizer.get_synonyms(threshold=0.3, return_similarity_measure=True)
    synonym_tuples = []
    for w1 in synonym_dicts:
        for w2, sim in synonym_dicts[w1]:
            synonym_tuples.append((w1, w2, sim))
    synonym_tuples.sort(key=lambda (w1, w2, sim): -sim)
    for w1, w2, sim in synonym_tuples:
        print "%.2f %s <-> %s" % (sim, w1, w2)


if __name__ == "__main__":
    main(sys.argv[1:])
