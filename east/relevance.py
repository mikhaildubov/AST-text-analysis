# -*- coding: utf-8 -*

from collections import defaultdict
import math
import sys

from nltk.stem import snowball
import numpy as np

from east.asts import base
from east import consts
from east import logging
from east import utils


class RelevanceMeasure(object):

    def set_text_collection(self, texts, language=consts.Language.ENGLISH):
        raise NotImplemented()

    def relevance(self, keyphrase, text, synonimizer=None):
        # text is the index of the text to measure the relevance to
        # TODO(mikhaildubov): Add detailed docstrings
        raise NotImplemented()


class ASTRelevanceMeasure(RelevanceMeasure):

    def __init__(self, ast_algorithm=consts.ASTAlgorithm.EASA, normalized=True):
        super(ASTRelevanceMeasure, self).__init__()
        self.ast_algorithm = ast_algorithm
        self.normalized = normalized

    def set_text_collection(self, texts, language=consts.Language.ENGLISH):
        self.texts = texts
        self.language = language

        self.asts = []
        total_texts = len(texts)

        for i in xrange(total_texts):
            # NOTE(mikhaildubov): utils.text_to_strings_collection()
            #                     does utils.prepare_text() as well.
            self.asts.append(base.AST.get_ast(
                                    utils.text_to_strings_collection(texts[i]),
                                    self.ast_algorithm))
            logging.progress("Indexing texts with ASTs", i + 1, total_texts)

        logging.clear()

    def relevance(self, keyphrase, text, synonimizer=None):
        return self.asts[text].score(keyphrase, normalized=self.normalized,
                                     synonimizer=synonimizer)


class CosineRelevanceMeasure(RelevanceMeasure):

    def __init__(self, vector_space=consts.VectorSpace.STEMS,
                 term_weighting=consts.TermWeighting.TF_IDF):
        super(CosineRelevanceMeasure, self).__init__()
        self.vector_space = vector_space
        self.term_weighting = term_weighting
        

    def set_text_collection(self, texts, language=consts.Language.ENGLISH):
        self.language = language
        if self.vector_space == consts.VectorSpace.STEMS:
            self.stemmer = snowball.SnowballStemmer(self.language)
        raw_tokens = []
        total_texts = len(texts)
        for i in xrange(total_texts):
            raw_tokens.append(utils.tokenize_and_filter(utils.prepare_text(texts[i])))
            logging.progress("Preparing texts", i + 1, total_texts)

        logging.clear()

        # Convert to stems or lemmata, depending on the vector space type
        preprocessed_tokens = self._preprocess_tokens(raw_tokens)

        # Terms define the vector space (they can be words, stems or lemmata). They should be
        # defined once here because they will be reused when we compute td-idf for queries
        self.terms = list(set(utils.flatten(preprocessed_tokens)))
        self.tf, self.idf = self._tf_idf(preprocessed_tokens)


    def _preprocess_tokens(self, tokens_in_texts):
        if self.vector_space == consts.VectorSpace.WORDS:
            return tokens_in_texts
        if self.vector_space == consts.VectorSpace.STEMS:
            # TODO(mikhaildubov): If the user does not specify the language, can we do some
            #                     auto language detection here?
            stemmed_tokens = []
            total_texts = len(tokens_in_texts)
            for i in xrange(total_texts):
                stemmed_tokens.append([self.stemmer.stem(token) for token in tokens_in_texts[i]])
                logging.progress("Stemming tokens in texts", i + 1, total_texts)
            return stemmed_tokens
        elif self.vector_space == consts.VectorSpace.LEMMATA:
            # TODO(mikhaildubov): Implement this (what lemmatizer to use here?)
            raise NotImplemented()

        logging.clear()


    def _tf_idf(self, tokens_in_texts):
        # Calculate the inverted term index to facilitate further calculations
        # This is a mapping from a token to its position in the vector
        term_index = {}
        for i in xrange(len(self.terms)):
            term_index[self.terms[i]] = i

        total_texts = len(tokens_in_texts)
        terms_count = len(self.terms)

        # Calculate TF and IDF
        tf = [np.zeros(terms_count) for _ in xrange(total_texts)]
        idf_per_ferm = defaultdict(int)
        for i in xrange(total_texts):
            logging.progress("Processing texts for TF-IDF", i + 1, total_texts)
            # NOTE(mikhaildubov): For TF, we want to count each term as many time as it appears
            for term in tokens_in_texts[i]:
                if term in term_index:
                    tf[i][term_index[term]] += 1
            # NOTE(mikhaildubov): For IDF, we want to count each document once for each term
            if self.term_weighting == consts.TermWeighting.TF_IDF:
                for term in set(tokens_in_texts[i]):
                    if term in term_index:
                        idf_per_ferm[term] += 1
            # TF Normalization
            tf[i] = [freq * 1.0 / max(len(tokens_in_texts[i]), 1) for freq in tf[i]]
        # Actual IDF metric calculation
        if self.term_weighting == consts.TermWeighting.TF_IDF:
            idf = np.zeros(len(self.terms))
            for term in idf_per_ferm:
                idf[term_index[term]] = 1 + math.log(total_texts * 1.0 / idf_per_ferm[term])
        else:
            idf = None

        logging.clear()

        return tf, idf


    def _cosine_similarity(self, u, v):
        u_norm = math.sqrt(np.dot(u, u)) if np.count_nonzero(u) else 1.0
        v_norm = math.sqrt(np.dot(v, v)) if np.count_nonzero(v) else 1.0
        return np.dot(u, v) / (u_norm * v_norm)


    def relevance(self, keyphrase, text, synonimizer=None):
        # Based on: https://janav.wordpress.com/2013/10/27/tf-idf-and-cosine-similarity/,
        # but query vectors are defined here in the same vector space as document vectors
        # (not in the reduced one as in the article).

        # TF-IDF for query tokens
        query_tokens = self._preprocess_tokens([utils.tokenize_and_filter(keyphrase)])
        query_tf, query_idf = self._tf_idf(query_tokens)
        query_tf = query_tf[0]

        # Weighting for both text and query (either TF or TF-IDF)
        if self.term_weighting == consts.TermWeighting.TF:
            text_vector = self.tf[text]
            query_vector = query_tf
        elif self.term_weighting == consts.TermWeighting.TF_IDF:
            text_vector = np.multiply(self.tf[text], self.idf)
            query_vector = np.multiply(query_tf, query_idf)

        return self._cosine_similarity(text_vector, query_vector)
