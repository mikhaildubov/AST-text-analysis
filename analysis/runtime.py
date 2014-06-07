# -*- coding: utf-8 -*

import gc
import getopt
import sys
import time

from analysis import utils
from east.asts import base

def main(args):
    opts, args = getopt.getopt(args, "")

    n_from = int(args[0])
    n_to = int(args[1])
    n_step = int(args[2]) if len(args) >= 3 else 1
    m = int(args[3]) if len(args) >= 4 else 100

    repeats = 5  # for each n

    for ast_algorithm in ["ast_naive", "ast_linear", "easa"]:
        print ast_algorithm
        for n in xrange(n_from, n_to + 1, n_step):
            t = 0
            for _ in xrange(repeats):
                strings_collection = utils.worst_case_strings_collection(m, n)
                start = time.clock()
                base.AST.get_ast(strings_collection, ast_algorithm)
                t += time.clock() - start
            gc.collect()
            print("%i\t%.2f" % (n, t / repeats))
        print ""


if __name__ == '__main__':
    main(sys.argv[1:])
