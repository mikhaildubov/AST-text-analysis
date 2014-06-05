# -*- coding: utf-8 -*

import testtools

from east import utils


class UtilsTestCase(testtools.TestCase):

    def test_tokenize(self):
        text = "Well, what a sunny day!"
        tokens = ["Well", "what", "a", "sunny", "day"]
        self.assertEqual(utils.tokenize(text), tokens)
