# -*- coding: utf-8 -*

from east.asts import ast
from east.asts import utils

class NaiveAnnotatedSuffixTree(ast.AnnotatedSuffixTree):

    __algorithm__ = "ast_naive"

    def _construct(self, strings_collection):
        '''
        Naive generalized suffix tree construction algorithm,
        with quadratic [O(n_1^2 + ... + n_m^2)] worst-case time complexity,
        where m is the number of strings in collection.
        
        '''
        
        # 0. Add a unique character to each string in the collection,
        #    to preserve simplicity while building the tree
        strings_collection = utils.make_unique_endings(strings_collection)
        
        root = ast.AnnotatedSuffixTree.Node()
        root.strings_collection = strings_collection
        
        # For each string in the collection...
        for string_ind in xrange(len(strings_collection)):
            string = strings_collection[string_ind]
            # For each suffix of that string...
            # (do not handle unique last characters as suffixes)
            for suffix_start in xrange(len(string)-1):
                suffix = string[suffix_start:]
                # ... first try to find maximal matching path
                node = root
                child_node = node.chose_arc(suffix)
                while child_node:
                    (str_ind, substr_start, substr_end) = child_node.arc()
                    match = utils.match_strings(
                                suffix, strings_collection[str_ind][substr_start:substr_end])
                    if match == substr_end-substr_start:
                        # matched the arc, proceed with child node
                        suffix = suffix[match:]
                        suffix_start += match
                        node = child_node
                        node.weight += 1
                        child_node = node.chose_arc(suffix)
                    else:
                        # ... then, where the matching path ends;
                        # create new inner node
                        # (that's the only possible alternative
                        #  since we have unique string endings)
                        node.remove_child(child_node)
                        new_node = node.add_new_child(string_ind, suffix_start,
                                                      suffix_start+match)
                        new_leaf = new_node.add_new_child(string_ind, suffix_start+match,
                                                          len(string))
                        (osi, oss, ose) = child_node._arc
                        child_node._arc = (osi, oss+match, ose)
                        new_node.add_child(child_node)
                        new_leaf.weight = 1
                        new_node.weight = 1 + child_node.weight
                        suffix = ''
                        break
                        
                # ... or create new leaf if there was no appropriate arc to proceed
                if suffix:
                    new_leaf = node.add_new_child(string_ind, suffix_start, len(string))
                    new_leaf.weight = 1
                    
        # Root will also be annotated by the weight of its children,
        # to preserve simplicity while calculating string matching
        for k in root.children:
            root.weight += root.children[k].weight
        
        return root
