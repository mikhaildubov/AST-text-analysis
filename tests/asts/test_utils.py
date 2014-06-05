# -*- coding: utf-8 -*

import testtools

from east.asts import utils


class AstUtilsTestCase(testtools.TestCase):

    def test_match_strings_empty(self):
        self.assertEqual(utils.match_strings("abc", "bc"), 0)
        self.assertEqual(utils.match_strings("", ""), 0)

    def test_match_strings_partial(self):
        self.assertEqual(utils.match_strings("abc", "ac"), 1)
        self.assertEqual(utils.match_strings("mnc", "mnd"), 2)

    def test_match_strings_full(self):
        self.assertEqual(utils.match_strings("abc", "abc"), 3)
        self.assertEqual(utils.match_strings("abc", "abcd"), 3)

    def test_index_int(self):
        self.assertEqual(utils.index([0, 2, 4, 6], 0), 0)
        self.assertEqual(utils.index([0, 2, 4, 6], 4), 2)
        self.assertEqual(utils.index([0, 2, 4, 6], 6), 3)

    def test_index_string(self):
        self.assertEqual(utils.index(["a", "b", "c", "d"], "a"), 0)
        self.assertEqual(utils.index(["a", "b", "c", "d"], "c"), 2)
        self.assertEqual(utils.index(["a", "b", "c", "d"], "d"), 3)
