# -*- coding: utf-8 -*

from east import utils

def worst_case_strings_collection(m, n):
    # NOTE(msdubov): strings differ only in their last 2 symbols.
    prefix = utils.random_string(n - 2)
    strings_collection = [prefix + utils.random_string(2) for _ in xrange(m)]
    return strings_collection
