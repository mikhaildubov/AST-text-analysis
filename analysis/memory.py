# -*- coding: utf-8 -*

import gc
import getopt
import os
import psutil
import sys
import time

from analysis import utils
from east.asts import base


def memory_usage():
    # return the memory usage in MB
    process = psutil.Process(os.getpid())
    mem = process.get_memory_info()[0] / float(2 ** 20)
    return mem


def main(args):
    opts, args = getopt.getopt(args, "")

    ast_algorithm = args[0]
    n_from = int(args[1])
    n_to = int(args[2])
    n_step = int(args[3]) if len(args) >= 4 else 1
    m = int(args[4]) if len(args) >= 5 else 100

    repeats = 2  # for each n

    print ast_algorithm
    for n in xrange(n_from, n_to + 1, n_step):
        asts = []
        for _ in xrange(repeats):
            strings_collection = utils.worst_case_strings_collection(m, n)
            ast = base.AST.get_ast(strings_collection, ast_algorithm)
            asts.append(ast)
        print("%i\t%.2f" % (n, memory_usage() / repeats))
        for ast in asts:
            del ast
        gc.collect()
    print ""


if __name__ == '__main__':
    main(sys.argv[1:])
