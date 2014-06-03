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
        self.current_os = utils.determine_operating_system()
        self.tomita_path, self.tomita_binary = self._get_tomita_path()
        if self.tomita_binary is None:
            raise exceptions.TomitaNotInstalledException()
        self.text, self.number_of_texts = self._retrieve_text(input_path)
        self.dependency_triples, self.dt_for_r, self.dt_for_w1r, self.dt_for_rw2 = \
            self._retrieve_dependency_triples(self.text)
        self.word_frequencies = self._calculate_word_frequencies(self.text)
        self.frequencies = self._calculate_dt_frequencies(self.dependency_triples)
        self.words = set([dt[0] for dt in self.dependency_triples] +
                         [dt[2] for dt in self.dependency_triples])
        self.relations = set([dt[1] for dt in self.dependency_triples])
        self.I_memoized = {}
        self.T_memoized = {}
        self.synonyms_memoized = {}

    def _retrieve_text(self, input_path):
        if os.path.isdir(input_path):
            text = ""
            number_of_texts = 0
            for file_name in os.listdir(input_path):
                if file_name.endswith(".txt"):
                    with open(os.path.abspath(input_path) + "/" + file_name) as f:
                        text += f.read()
                        number_of_texts += 1
        else:
            with open(input_path) as f:
                text = f.read()
                number_of_texts = 1
        return text, number_of_texts

    def _retrieve_dependency_triples(self, text):

        dependency_triples = []

        # Additional indexes to speed up the calculation of I(w1, r, w2)
        dt_for_r = collections.defaultdict(list)
        dt_for_w1r = collections.defaultdict(list)
        dt_for_rw2 = collections.defaultdict(list)

        p = subprocess.Popen([self.tomita_binary, "config.proto"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, cwd=self.tomita_path,
                             shell=(self.current_os == consts.OperatingSystem.WINDOWS))
        out, err = p.communicate(input=text)

        xmldoc = minidom.parseString(out)
        relations = xmldoc.getElementsByTagName('Relation') 
        
        for rel in relations:
            r = rel.childNodes[0].nodeName
            w1, w2 = rel.childNodes[0].attributes['val'].value.split(' ', 1)

            dt = (w1, r, w2)
            dependency_triples.append(dt)
            dt_for_r[r].append(dt)
            dt_for_w1r[(w1, r)].append(dt)
            dt_for_rw2[(r, w2)].append(dt)

            # NOTE(msdubov): Also add inversed triples.
            r_inv = r[:-3] if r.endswith("_of") else (r + "_of")
            dt_inv = (w2, r_inv, w1)
            dependency_triples.append(dt_inv)
            dt_for_r[r_inv].append(dt_inv)
            dt_for_w1r[(w2, r_inv)].append(dt_inv)
            dt_for_rw2[(r_inv, w1)].append(dt_inv)

        return dependency_triples, dt_for_r, dt_for_w1r, dt_for_rw2

    def _get_tomita_path(self):
        tomita_path = (os.path.dirname(os.path.abspath(__file__)) +
                       "/../../tools/tomita/")

        if self.current_os == consts.OperatingSystem.LINUX_64:
            tomita_binary = "./tomita-linux64"
        elif self.current_os == consts.OperatingSystem.LINUX_32:
            tomita_binary = "./tomita-linux32"
        elif self.current_os == consts.OperatingSystem.WINDOWS:
            tomita_binary = "tomitaparser.exe"
        elif self.current_os == consts.OperatingSystem.MACOS:
            tomita_binary = "./tomita-mac"

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
        fr__r_ = sum(self.frequencies[triple] for triple in self.dt_for_r[r])
        fr_w1r_ = sum(self.frequencies[triple] for triple in self.dt_for_w1r[(w1, r)])
        fr__rw2 = sum(self.frequencies[triple] for triple in self.dt_for_rw2[(r, w2)])
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

    def get_synonyms(self, threshold=0.3, return_similarity_measure=False):
        synonyms = collections.defaultdict(list)
        words = filter(lambda w: len(w) > 2 and
                                 self.word_frequencies[w] > self.number_of_texts / 50,
                       self.words)
        combs = itertools.combinations(words, 2)
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
