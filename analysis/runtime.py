# -*- coding: utf-8 -*

import gc
import getopt
import sys
import time

from east.asts import base
from east import utils


def worst_case_strings_collection(m, n):
    # NOTE(msdubov): strings differ only in their last 2 symbols.
    prefix = utils.random_string(n - 2)
    strings_collection = [prefix + utils.random_string(n - 2) for _ in xrange(m)]
    return strings_collection


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
                strings_collection = worst_case_strings_collection(m, n)
                start = time.clock()
                base.AST.get_ast(ast_algorithm, strings_collection)
                t += time.clock() - start
            gc.collect()
            print("%i\t%.2f" % (n, t / repeats))
        print ""


if __name__ == '__main__':
    main(sys.argv[1:])
