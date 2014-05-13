# -*- coding: utf-8 -*

from east import consts


def index(array, key, start=0):
    # NOTE(msdubov): No boundary check for optimization purposes.
    i = start
    while array[i] != key:
        i += 1
    return i


def match_strings(str1, str2):
    '''
    Returns the largest index i such that str1[:i] == str2[:i]
    
    '''
    i = 0
    min_len = len(str1) if len(str1) < len(str2) else len(str2)
    while i < min_len and str1[i] == str2[i]: i += 1
    return i


def make_unique_endings(strings_collection):
    '''
    Make each string in the collection end with a unique character.
    Essential for correct builiding of a generalized annotated suffix tree.
    Returns the updated strings collection, encoded in Unicode.

    max strings_collection ~ 1.100.000
    
    '''
    res = []
    for i in range(len(strings_collection)):
        # NOTE(msdubov): a trick to handle 'narrow' python installation issues.
        hex_code = hex(consts.String.UNICODE_SPECIAL_SYMBOLS_START+i)
        hex_code = r"\U" + "0" * (8 - len(hex_code) + 2) + hex_code[2:]
        res.append(strings_collection[i] + hex_code.decode("unicode-escape"))
    return res
