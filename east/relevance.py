# -*- coding: utf-8 -*

from collections import defaultdict
import math

import numpy as np

from east.asts import base
from east import consts
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
        # NOTE(mikhaildubov): utils.text_to_strings_collection() does utils.prepare_text() as well.
        self.asts = [base.AST.get_ast(utils.text_to_strings_collection(text), self.ast_algorithm)
                     for text in texts]

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
        raw_tokens = [utils.tokenize_and_filter(utils.prepare_text(text)) for text in texts]
        # Convert to stems or lemmata, depending on the vector space type
        preprocessed_tokens = self._preprocess_tokens(raw_tokens)
        # Terms define the vector space (they can be words, stems or lemmata). They should be
        # defined once here because they will be reused when we compute td-idf for queries
        self.terms = list(set(utils.flatten(preprocessed_tokens)))
        self.tf, self.idf = self._tf_idf(preprocessed_tokens)


    def _preprocess_tokens(self, tokens):
        if self.vector_space == consts.VectorSpace.WORDS:
            return tokens
        if self.vector_space == consts.VectorSpace.STEMS:
            # TODO(mikhaildubov): If the user does not specify the language, can we do some
            #                     auto language detection here?
            from nltk.stem import snowball
            stemmer = snowball.SnowballStemmer(self.language)
            return [[stemmer.stem(token) for token in tokens[i]] for i in xrange(len(tokens))]
        elif self.vector_space == consts.VectorSpace.LEMMATA:
            # TODO(mikhaildubov): Implement this (what lemmatizer to use here?)
            raise NotImplemented()


    def _tf_idf(self, tokens):
        # Calculate the inverted term index to facilitate further calculations
        term_index = {}
        for i in xrange(len(self.terms)):
            term_index[self.terms[i]] = i

        text_collection_size = len(tokens)

        # Calculate TF and IDF
        tf = [[0] * len(self.terms) for _ in xrange(text_collection_size)]
        idf_docs = defaultdict(set)
        for i in xrange(text_collection_size):
            for token in tokens[i]:
                if token in term_index:
                    tf[i][term_index[token]] += 1
                    idf_docs[token].add(i)
            # TF Normalization
            tf[i] = [freq * 1.0 / max(len(tokens[i]), 1) for freq in tf[i]]
        # Actual IDF metric calculation
        idf = [0] * len(self.terms)
        for term in idf_docs:
            idf[term_index[term]] = 1 + math.log(text_collection_size * 1.0 / len(idf_docs[term]))

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
