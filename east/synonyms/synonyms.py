# -*- coding: utf-8 -*

import codecs
import collections
import itertools
import math
import os
import subprocess
from xml.dom import minidom


from east import consts
from east import exceptions
from east import utils as common_utils
from east.synonyms import utils


class SynonymExtractor(object):

    def __init__(self, input_path):
        self.tomita_path, self.tomita_binary = self._get_tomita_path()
        if self.tomita_binary is None:
            raise exceptions.TomitaNotInstalledException()
        self.text = self._retrieve_text(input_path)
        self.dependency_triples = self._retrieve_dependency_triples(self.text)
        self.word_frequencies = self._calculate_word_frequencies(self.text)
        self.frequencies = self._calculate_dt_frequencies(self.dependency_triples)
        self.words = set([dt[0] for dt in self.dependency_triples] +
                         [dt[2] for dt in self.dependency_triples])
        self.relations = set([dt[1] for dt in self.dependency_triples])
        self.I_memoized = {}
        self.T_memoized = {}
        self.synonyms_memoized = {}

    def _retrieve_text(self, input_path):
        j = 0
        if os.path.isdir(input_path):
            text = ""
            for file_name in os.listdir(input_path):
                if file_name.endswith(".txt"):
                    if j == 25:
                        break
                    with open(os.path.abspath(input_path) + "/" + file_name) as f:
                        text += f.read()
                    j += 1
        else:
            with open(input_path) as f:
                text = f.read()
        return text

    def _retrieve_dependency_triples(self, text):

        dependency_triples = []

        cwd = os.getcwd()
        os.chdir(self.tomita_path)

        p = subprocess.Popen([self.tomita_binary, "config.proto"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate(input=text)

        xmldoc = minidom.parseString(out)
        relations = xmldoc.getElementsByTagName('Relation') 
        for rel in relations:
            r = rel.childNodes[0].nodeName
            w1, w2 = rel.childNodes[0].attributes['val'].value.split(' ', 1)
            dependency_triples.append((w1, r, w2))
            # NOTE(msdubov): Also add inversed triples.
            if r.endswith("_of"):
                dependency_triples.append((w2, r[:-3], w1))
            else:
                dependency_triples.append((w2, r + "_of", w1))

        os.chdir(cwd)

        return dependency_triples

    def _get_tomita_path(self):
        tomita_path = (os.path.dirname(os.path.abspath(__file__)) +
                       "/../../tools/tomita/")

        current_os = utils.determine_operating_system()
        if current_os == consts.OperatingSystem.LINUX_64:
            tomita_binary = "./tomita-linux64"
        elif current_os == consts.OperatingSystem.LINUX_32:
            tomita_binary = "./tomita-linux32"
        elif current_os == consts.OperatingSystem.WINDOWS:
            tomita_binary = "./tomita.exe"

        if not os.access(tomita_path + tomita_binary, os.F_OK):
            tomita_binary = None

        return tomita_path, tomita_binary

    def _calculate_word_frequencies(self, text):
        text = common_utils.prepare_text(text)
        words = common_utils.tokenize(text)
        res = collections.defaultdict(int)
        for word in words:
            res[word] += 1
        return res

    def _calculate_dt_frequencies(self, dependency_triples):
        res = collections.defaultdict(int)
        for dt in dependency_triples:
            res[dt] += 1
        return res

    def I(self, w1, r, w2):
        if (w1, r, w2) in self.I_memoized:
            return self.I_memoized[(w1, r, w2)]
        fr_w1rw2 = self.frequencies[w1, r, w2]
        if not fr_w1rw2:
            return 0.0
        fr__r_ = sum(self.frequencies[triple] for triple in self.frequencies.iterkeys()
                     if triple[1] == r)
        fr_w1r_ = sum(self.frequencies[triple] for triple in self.frequencies.iterkeys()
                      if triple[0] == w1 and triple[1] == r)
        fr__rw2 = sum(self.frequencies[triple] for triple in self.frequencies.iterkeys()
                      if triple[1] == r and triple[2] == w2)
        res = max(math.log(float(fr_w1rw2) * fr__r_ / fr_w1r_ / fr__rw2), 0.0)
        self.I_memoized[(w1, r, w2)] = res
        return res

    def T(self, w):
        if w in self.T_memoized:
            return self.T_memoized[w]
        res = set(filter(lambda (r, w_): self.I(w, r, w_) > 0,
                         itertools.product(self.relations, self.words)))
        self.T_memoized[w] = res
        return res

    def similarity(self, w1, w2):
        numerator = sum(self.I(w1, r, w) + self.I(w2, r, w)
                        for (r, w) in self.T(w1) & self.T(w2))
        denominator = (sum(self.I(w1, r, w) for (r, w) in self.T(w1)) +
                       sum(self.I(w2, r, w) for (r, w) in self.T(w2)))
        if denominator:
            return numerator / denominator
        else:
            return 0.0

    def get_synonyms(self, threshold=0.5, return_similarity_measure=False):
        synonyms = collections.defaultdict(list)
        words = filter(lambda w: len(w) > 3 and self.word_frequencies[w] > 3, self.words)
        combs = list(itertools.combinations(words, 2))
        for w1, w2 in combs:
            sim = self.similarity(w1, w2)
            if sim > threshold:
                if return_similarity_measure:
                    synonyms[w1].append((w2, sim))
                    synonyms[w2].append((w1, sim))
                else:
                    synonyms[w1].append(w2)
                    synonyms[w2].append(w1)
        return synonyms
