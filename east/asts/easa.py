# -*- coding: utf-8 -*

import itertools
import numpy as np

from east.asts import base
from east.asts import utils
from east import utils as common_utils

class EnhancedAnnotatedSuffixArray(base.AST):

    __algorithm__ = "easa"

    def __init__(self, strings_collection):
        super(EnhancedAnnotatedSuffixArray, self).__init__(strings_collection)
        self.strings_collection = strings_collection
        self.string = "".join(utils.make_unique_endings(strings_collection))
        self.suftab = self._compute_suftab(self.string)
        self.lcptab = self._compute_lcptab(self.string, self.suftab)
        self.childtab_up, self.childtab_down = self._compute_childtab(self.lcptab)
        self.childtab_next_l_index = self._compute_childtab_next_l_index(self.lcptab)
        self.anntab = self._compute_anntab(self.suftab, self.lcptab)

    def score(self, query, normalized=True, synonimizer=None):
        if synonimizer:
            synonyms = synonimizer.get_synonyms()
            query_words = common_utils.tokenize(query)
            for i in xrange(len(query_words)):
                query_words[i] = synonyms[query_words[i]] + [query_words[i]]
            possible_queries = map(lambda words: "".join(words),
                                   itertools.product(*query_words))
            return max(self._score(q) for q in possible_queries)
        else:
            return self._score(query.replace(" ", ""), normalized)

    def traverse_depth_first_pre_order(self, callback):
        """Visits the internal "nodes" of the enhanced suffix array in depth-first pre-order.

        Based on Abouelhoda et al. (2004).
        """
        n = len(self.suftab)
        root = [0, 0, n - 1, ""]  # <l, i, j, char>

        def _traverse_top_down(interval):  # TODO: Rewrite with stack? As in bottom-up
            callback(interval)
            i, j = interval[1], interval[2]
            if i != j:
                children = self._get_child_intervals(i, j)
                children.sort(key=lambda child: child[3])
                for child in children:
                    _traverse_top_down(child)

        _traverse_top_down(root)

    def traverse_depth_first_post_order(self, callback):
        """Visits the internal "nodes" of the enhanced suffix array in depth-first post-order.

        Kasai et. al. (2001), Abouelhoda et al. (2004).
        """
        # a. Reimplement without python lists?..
        # b. Interface will require it to have not internal nodes only?..
        #    (but actually this implementation gives a ~2x gain of performance)
        last_interval = None
        n = len(self.suftab)
        stack = [[0, 0, None, []]]  # <l, i, j, children>
        for i in xrange(1, n):
            lb = i - 1
            while self.lcptab[i] < stack[-1][0]:
                stack[-1][2] = i - 1
                last_interval = stack.pop()
                callback(last_interval)
                lb = last_interval[1]
                if self.lcptab[i] <= stack[-1][0]:
                    stack[-1][3].append(last_interval)
                    last_interval = None
            if self.lcptab[i] > stack[-1][0]:
                if last_interval:
                    stack.append([self.lcptab[i], lb, None, [last_interval]])
                    last_interval = None
                else:
                    stack.append([self.lcptab[i], lb, None, []])
        stack[-1][2] = n - 1
        callback(stack[-1])

    def traverse_breadth_first(self, callback):
        """Visits the internal "nodes" of the enhanced suffix array in breadth-first order."""
        raise NotImplementedError

    def _score(self, query, normalized=True):
        result = 0
        n = len(self.suftab)

        root_interval = (0, 0, n - 1)
    
        for suffix_start in xrange(len(query)):
            
            suffix = query[suffix_start:]
            suffix_score = 0
            matched_chars = 0
            nodes_matched = 0
            
            parent_node = root_interval
            child_node = self._get_child_interval(parent_node[1], parent_node[2], suffix[0])
            while child_node:
                nodes_matched += 1
                # TODO: Use structs??? child_node[1] is actually cn.i; parent_node[0] == pn.l
                substr_start = self.suftab[child_node[1]] + parent_node[0]
                if self._is_leaf(child_node):
                    substr_end = n
                else:
                    substr_end = substr_start + child_node[0] - parent_node[0]
                match = utils.match_strings(suffix, self.string[substr_start:substr_end])
                suffix_score += float(self._annotation(child_node)) / self._annotation(parent_node)
                matched_chars += match
                suffix = suffix[match:]
                if suffix and match == substr_end - substr_start:
                    parent_node = child_node
                    child_node = self._get_child_interval(parent_node[1], parent_node[2], suffix[0])
                else:
                    break

            if matched_chars:
                if normalized:
                    suffix_result = (suffix_score + matched_chars - nodes_matched) / matched_chars
                else:
                    suffix_result = (suffix_score + matched_chars - nodes_matched)
                result += suffix_result
            
        result /= len(query)
        return result

    def _compute_suftab(self, string):
        """Computes the suffix array of a string in O(n).

        The code is based on that from the pysuffix library (https://code.google.com/p/pysuffix/).

        Kärkkäinen & Sanders (2003).
        """
        n = len(string)
        string += (unichr(1) * 3)
        suftab = np.zeros(n, dtype=np.int)
        alpha = sorted(set(string))
        self._kark_sort(string, suftab, n, alpha)
        return suftab

    def _kark_sort(self, s, SA, n, alpha):
        n0 = (n + 2) / 3
        n1 = (n + 1) / 3
        n2 = n / 3
        n02 = n0 + n2

        SA12 = [0] * (n02 + 3)
        SA0 = [0] * n0
        s12 = [i for i in xrange(n + n0 - n1) if i % 3 != 0] + [0, 0, 0]

        self._radixpass(s12, SA12, s[2:], n02, alpha)
        self._radixpass(SA12, s12, s[1:], n02, alpha)
        self._radixpass(s12, SA12, s, n02, alpha)
  
        name = 0
        c0, c1, c2 = -1, -1, -1
        array_name = [0]
        for i in xrange(n02):
            if s[SA12[i]] != c0 or s[SA12[i] + 1] != c1 or s[SA12[i] + 2] != c2:
                name += 1
                array_name.append(name)
                c0 = s[SA12[i]]
                c1 = s[SA12[i]+1]
                c2 = s[SA12[i]+2]
            if SA12[i] % 3 == 1:
                s12[SA12[i] / 3] = name
            else:
                s12[SA12[i] / 3 + n0] = name

        if name < n02:
            self._kark_sort(s12, SA12, n02, array_name)
            for i in xrange(n02): 
                s12[SA12[i]] = i+1
        else:
            for i in xrange(n02): 
                SA12[s12[i]-1] = i

        s0 = [SA12[i] * 3 for i in xrange(n02) if SA12[i] < n0]

        self._radixpass(s0, SA0, s, n0, alpha)
  
        p = j = k = 0
        t = n0 - n1
        while k < n:
            i = SA12[t] * 3 + 1 if SA12[t] < n0 else (SA12[t] - n0) * 3 + 2
            j = SA0[p] if p < n0 else 0
 
            if SA12[t] < n0:
                test = (s12[SA12[t]+n0] <= s12[j/3]) if(s[i]==s[j]) else (s[i] < s[j])
            elif(s[i]==s[j]) :
                test = s12[SA12[t]-n0+1] <= s12[j/3 + n0] if(s[i+1]==s[j+1]) else s[i+1] < s[j+1]
            else:
                test = s[i] < s[j]

            if test:
                SA[k] = i
                t += 1
                if t == n02: 
                    k += 1
                    l = n0 - p
                    while p < n0:
                        SA[k] = SA0[p]
                        p += 1
                        k += 1          
            else: 
                SA[k] = j
                p += 1
                if p == n0:
                    k += 1
                    while t < n02:
                        SA[k] = (SA12[t] * 3) + 1 if SA12[t] < n0 else ((SA12[t] - n0) * 3) + 2
                        t += 1
                        k += 1
            k += 1

    def _radixpass(self, a, b, r, n, alpha):
        c = {}
        for letter in alpha:
            c[letter] = 0
        for i in xrange(n):
            c[r[a[i]]] += 1

        total = 0
        for letter in alpha:
            freq, c[letter] = c[letter], total
            total += freq
        for i in xrange(n):
            b[c[r[a[i]]]] = a[i]
            c[r[a[i]]] += 1

        return b

    def _compute_lcptab(self, string, suftab):
        """Computes the LCP array in O(n) based on the input string & its suffix array.

        Kasai et al. (2001).
        """
        n = len(suftab)
        rank = [0] * n
        for i in xrange(n):
            rank[suftab[i]] = i
        lcptab = np.zeros(n, dtype=np.int)
        h = 0
        for i in xrange(n):
            if rank[i] >= 1:
                j = suftab[rank[i] - 1]
                while string[i + h] == string[j + h]:
                    h += 1
                lcptab[rank[i]] = h
                if h > 0:
                    h -= 1
        return lcptab

    def _compute_childtab(self, lcptab):
        """Computes the child 'up' and 'down' arrays in O(n) based on the LCP table.

        Abouelhoda et al. (2004).
        """
        last_index = -1
        stack = [0]
        n = len(lcptab)
        childtab_up = np.zeros(n, dtype=np.int)  # Zeros / -1 ?
        childtab_down = np.zeros(n, dtype=np.int)
        for i in xrange(n):
            while lcptab[i] < lcptab[stack[-1]]:
                last_index = stack.pop()
                if lcptab[i] <= lcptab[stack[-1]] and lcptab[stack[-1]] != lcptab[last_index]:
                    childtab_down[stack[-1]] = last_index
            if last_index != -1:
                childtab_up[i] = last_index
                last_index = -1
            stack.append(i)
        return childtab_up, childtab_down

    def _compute_childtab_next_l_index(self, lcptab):
        """Computes the child 'next l index' array in O(n) based on the LCP table.

        Abouelhoda et al. (2004).
        """
        stack = [0]
        n = len(lcptab)
        childtab_next_l_index = np.zeros(n, dtype=np.int)  # Zeros / -1 ?
        for i in xrange(n):
            while lcptab[i] < lcptab[stack[-1]]:
                stack.pop()
            if lcptab[i] == lcptab[stack[-1]]:
                last_index = stack.pop()
                childtab_next_l_index[last_index] = i
            stack.append(i)
        return childtab_next_l_index

    def _compute_anntab(self, suftab, lcptab):
        """Computes the annotations array in O(n) by "traversing" the suffix array.

        Based on ideas from Abouelhoda et al. (2004) and Dubov & Chernyak (2013).
        """
        n = len(suftab)
        anntab = np.zeros(n, dtype=np.int)  # Zeros / -1 ?

        def process_node(node):
            # NOTE(msdubov): Assumes that child l-[i..j] lcp intervals come in the ascending
            #                order (by i). This allows to handle the leafs properly.
            i = node[1]
            for child_node in node[3]:
                if i < child_node[1]:
                    anntab[self._interval_index(node)] += child_node[1] - i
                anntab[self._interval_index(node)] += anntab[self._interval_index(child_node)]
                i = child_node[2] + 1
            if i <= node[2]:
                anntab[self._interval_index(node)] += node[2] - i + 1

        self.traverse_depth_first_post_order(process_node)
        # NOTE(msdubov): Removing the "degenerate" 1st-level leafs
        #                with the auxiliary symbol in the arc.
        anntab[0] -= len(self.strings_collection)

        return anntab

    def _interval_index(self, lcp_interval):
        """Maps an lcp interval to an index in [0..n-1].

        :param lcp_interval: <l, i, j>.
        """
        return utils.index(self.lcptab, lcp_interval[0], lcp_interval[1])

    def _annotation(self, lcp_interval):
        if self._is_leaf(lcp_interval):
            return 1
        else:
            return self.anntab[self._interval_index(lcp_interval)]

    def _is_leaf(self, lcp_interval):
        return lcp_interval[1] == lcp_interval[2]

    def _lcp_value(self, i, j):
        n = len(self.suftab)
        if (i == 0 or i == n - 1) and j == n - 1:
            return 0  # TODO: Verify the correctness of this step.
        elif i < self.childtab_up[j + 1] <= j:
            return self.lcptab[self.childtab_up[j + 1]]
        else:
            return self.lcptab[self.childtab_down[i]]

    def _get_child_intervals(self, i, j):
        if i == j:
            return []
        n = len(self.suftab)
        l = self._lcp_value(i, j)
        intervals = []
        if i == 0 and j == n - 1:
            i1 = 0  # TODO: Verify the correctness of this step.
        else:
            if i < self.childtab_up[j + 1]:
                i1 = self.childtab_up[j + 1]
            else:
                i1 = self.childtab_down[i]
            intervals.append((self._lcp_value(i, i1 - 1), i, i1 - 1, self.string[self.suftab[i] + l]))
        while self.childtab_next_l_index[i1] != 0:
            i2 = self.childtab_next_l_index[i1]
            intervals.append((self._lcp_value(i1, i2 - 1), i1, i2 - 1, self.string[self.suftab[i1] + l]))
            i1 = i2
        intervals.append((self._lcp_value(i1, j), i1, j, self.string[self.suftab[i1] + l]))
        return intervals

    def _get_child_interval(self, i, j, char):
        if i == j:
            return None
        n = len(self.suftab)
        l = self._lcp_value(i, j)
        if i == 0 and j == n - 1:
            i1 = 0
        else:
            if i < self.childtab_up[j + 1]:
                i1 = self.childtab_up[j + 1]
            else:
                i1 = self.childtab_down[i]
            if self.string[self.suftab[i] + l] == char:
                return (self._lcp_value(i, i1 - 1), i, i1 - 1, self.string[self.suftab[i] + l])
        while self.childtab_next_l_index[i1] != 0:
            i2 = self.childtab_next_l_index[i1]
            if self.string[self.suftab[i1] + l] == char:
                return (self._lcp_value(i1, i2 - 1), i1, i2 - 1, self.string[self.suftab[i1] + l])
            i1 = i2
        if self.string[self.suftab[i1] + l] == char:
            return (self._lcp_value(i1, j), i1, j, self.string[self.suftab[i1] + l])
        return None
