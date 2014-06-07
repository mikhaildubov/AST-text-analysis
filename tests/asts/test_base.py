# -*- coding: utf-8 -*

import itertools
import testtools

from east.asts import base


class BASEAstTestCase(testtools.TestCase):

    def setUp(self):
        super(BASEAstTestCase, self).setUp()
        self.strings_collection = ["abcd efg ops", "xyzq", "test"]
        self.queries = ["aqcb", "efgp", "mn4"]

    def test_matching_scores_equality(self):
        algorithms = ["easa", "ast_linear", "ast_naive"]
        for normalized in [True, False]:
            for alg1, alg2 in itertools.combinations(algorithms, 2):
                ast1 = base.AST.get_ast(self.strings_collection, alg1)
                ast2 = base.AST.get_ast(self.strings_collection, alg2)
                for query in self.queries:
                    self.assertEqual(ast1.score(query, normalized=normalized),
                                     ast2.score(query, normalized=normalized))
