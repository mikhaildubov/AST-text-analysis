# -*- coding: utf-8 -*

import itertools
import os
import random
import re
import sys

from nltk.corpus import stopwords as nltk_stopwords


class ImmutableMixin(object):
    _inited = False

    def __init__(self):
        self._inited = True

    def __setattr__(self, key, value):
        if self._inited:
            raise exceptions.ImmutableException()
        super(ImmutableMixin, self).__setattr__(key, value)


class EnumMixin(object):
    def __iter__(self):
        for k, v in itertools.imap(lambda x: (x, getattr(self, x)), dir(self)):
            if not k.startswith('_'):
                yield v


def prepare_text(text):
    text = unicode(text.decode('utf-8', errors='replace'))
    text = text.upper()
    return text


def tokenize(text):
    return re.findall(re.compile("[\w']+", re.U), text)


def tokenize_and_filter(text, min_word_length=3, stopwords=None):
    tokens = tokenize(text)
    # TODO(mikhaildubov): Add language detection
    stopwords = stopwords or set(word.upper() for word in nltk_stopwords.words("english"))
    return [token for token in tokens
            if len(token) >= min_word_length and token not in stopwords]


def text_to_strings_collection(text, words=3):
    """
    Splits the text to a collection of strings;
    a GAST for such a split collection usually produces
    better results in keyword matching that a GAST
    for the whole text. The word parameters determines
    how many words each string in the collection shall
    consist of (3 by default)
    
    return: Unicode
    """
    
    text = prepare_text(text)
    strings_collection = tokenize(text)
    strings_collection = filter(lambda s: len(s) > 2 and not s.isdigit(), strings_collection)
        
    i = 0
    strings_collection_grouped = []
    while i < len(strings_collection):
        group = ''
        for j in xrange(words):
            if i + j < len(strings_collection):
                group += strings_collection[i+j]
        strings_collection_grouped.append(group)
        i += words

    # Having an empty strings collection would lead to a runtime errors in the applications.
    if not strings_collection_grouped:
        strings_collection_grouped = [" "]
        
    return strings_collection_grouped


def text_collection_to_string_collection(text_collection, words=3):
    return flatten([text_to_strings_collection(text) for text in text_collection])


def random_string(length):
    string = "".join([unichr(ord("A") + random.randint(0, 25)) for _ in xrange(length - 2)])
    return string


def flatten(lst):
    # NOTE(mikhaildubov): This is the fastest implementation according to bit.ly/so_flat_list
    return list(itertools.chain.from_iterable(lst))


def output_is_redirected():
    return os.fstat(0) != os.fstat(1)


def itersubclasses(cls, _seen=None):
    """Generator over all subclasses of a given class in depth first order."""

    if not isinstance(cls, type):
        raise TypeError(_('itersubclasses must be called with '
                          'new-style classes, not %.100r') % cls)
    _seen = _seen or set()
    try:
        subs = cls.__subclasses__()
    except TypeError:   # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


def import_modules_from_package(package):
    """Import modules from package and append into sys.modules

    :param package: full package name, e.g. east.asts
    """
    path = [os.path.dirname(__file__), '..'] + package.split('.')
    path = os.path.join(*path)
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.startswith('__') or not filename.endswith('.py'):
                continue
            new_package = ".".join(root.split(os.sep)).split("....")[1]
            module_name = '%s.%s' % (new_package, filename[:-3])
            if module_name not in sys.modules:
                __import__(module_name)
