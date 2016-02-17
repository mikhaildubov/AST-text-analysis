# -*- coding: utf-8 -*

import abc

from east.asts import base
from east.asts import utils
from east import consts


class AnnotatedSuffixTree(base.AST):
    __metaclass__ = abc.ABCMeta

    def __init__(self, strings_collection):
        super(AnnotatedSuffixTree, self).__init__(strings_collection)
        self.strings_collection = strings_collection
        self.root = self._construct(strings_collection)
        self._update_node_depth()

    def score(self, query, normalized=True, synonimizer=None, return_suffix_scores=False):
        """
        Matches the string against the GAST using
        the algorithm described in [Chernyak, sections 1.3 & 1.4].
        
        Expects the input string to consist of
        alphabet letters only (no whitespaces etc.)
        
        Returns the score (a float in [0, 1]).
        
        query -- Unicode
        
        """
        
        query = query.replace(" ", "")
        result = 0
        suffix_scores = {}
    
        # For each suffix of the string:
        for suffix_start in xrange(len(query)):
            
            suffix = query[suffix_start:]
            suffix_score = 0
            suffix_result = 0
            matched_chars = 0
            nodes_matched = 0
            
            child_node = self.root.chose_arc(suffix)
            while child_node:
                nodes_matched += 1
                (str_ind, substr_start, substr_end) = child_node.arc()
                match = utils.match_strings(
                            suffix, self.strings_collection[str_ind][substr_start:substr_end])
                suffix_score += child_node.conditional_probability()
                matched_chars += match
                suffix = suffix[match:]
                if suffix and match == substr_end - substr_start:
                    child_node = child_node.chose_arc(suffix)
                else:
                    break
            
            if matched_chars:
                suffix_result = (suffix_score + matched_chars - nodes_matched)
                if normalized:
                    suffix_result /= matched_chars
                result += suffix_result

            suffix_scores[query[suffix_start:]] = suffix_result
                    
        result /= len(query)

        if return_suffix_scores:
            result = result, suffix_scores
        
        return result

    def traverse_depth_first_pre_order(self, callback):
        """Traverses the annotated suffix tree in depth-first pre-order."""
        self.root.traverse_depth_first_pre_order(callback)

    def traverse_depth_first_post_order(self, callback):
        """Traverses the annotated suffix tree in depth-first post-order."""
        self.root.traverse_depth_first_post_order(callback)

    def traverse_breadth_first(self, callback):
        """Traverses the annotated suffix tree in breadth-first order."""
        self.root.traverse_breadth_first(callback, [])

    @abc.abstractmethod
    def _construct(self, strings_collection):
        """Constructs the annotated suffix tree and returns the pointer to its root."""
    
    def _update_node_depth(self):
        self.root.depth = 0
        def _calculate_depth(node):
            for k in node.children:
                node.children[k].depth = node.depth + 1
        self.traverse(_calculate_depth, consts.TraversalOrder.DEPTH_FIRST_PRE_ORDER)

    class Node:
        """
        Implementation of a Generalized Annotated Suffix Tree node.
        
        """ 
            
        def __init__(self):
            """ Hash table to store child nodes """
            self.children = {}
            """ Node weight """
            self.weight = 0
            """ Parent """
            self.parent = None
            """ Suffix link """
            self.suffix_link = None
            """ Arc that points to the node; Triple of form
                (string_index, substring_start_index[inclusive], substring_end_index[exclusive]) """
            self._arc = None
            """ Used in Ukkonen's algorithm """
            self._e = []
            """ Pointer to the strings collection """
            self.strings_collection = []
            # No sense in initializing node weight here
            # it is not possible to update it quickly while
            # constructing the tree; that's made later in one single pass
                
        
        def add_new_child(self, str_ind, substr_start, substr_end):
            """
            Creates and returns new child node.
            str_ind, substr_start, substr_end and parameters describe
            the substring that the new child should contain;
            for the given strings_collection that will be
            strings_collection[str_ind][substr_start:substr_end]
            
            """
            child_node = AnnotatedSuffixTree.Node()
            child_node.parent = self
            child_node.strings_collection = self.strings_collection
            child_node._arc = (str_ind, substr_start, substr_end)
            child_node._e = self._e
            self.children[self.strings_collection[str_ind][substr_start]] = child_node
            return child_node
        
        
        def add_child(self, child_node):
            """
            Adds an existing node as a new child
            for the current node.
            
            """
            (str_ind, substr_start, _) = child_node.arc()
            child_node.strings_collection = self.strings_collection
            self.children[self.strings_collection[str_ind][substr_start]] = child_node
            child_node.parent = self
        
        
        def remove_child(self, child_node):
            """
            Removes a child node from the current node.
            
            """
            (str_ind, substr_start, _) = child_node.arc()
            del self.children[self.strings_collection[str_ind][substr_start]]
            
            
        def conditional_probability(self):
            """
            Calculates the conditional probability
            of the first character in the node's substring;
            see [Chernyak, section 2.3] for details
            
            """
            return float(self.weight) / self.parent.weight
            
            
        def arc(self):
            """
            Returns a tuple of form (str_ind, substr_start, substr_end)
            that describes the substring that the current node contains
            (can be also imagined as the label of the arc that poins to this node).
            For the given strings_collection that will be
            strings_collection[str_ind][substr_start:substr_end]
            
            """
            (str_ind, substr_start, substr_end) = self._arc
            if substr_end == -1:
                substr_end = self._e[str_ind]
            return (str_ind, substr_start, substr_end)
        
        
        def arc_label(self):
            (str_ind, substr_start, substr_end) = self.arc()
            return self.strings_collection[str_ind][substr_start:substr_end]
        
            
        def chose_arc(self, string):
            """
            Returns the child node, the arc to which is
            labeled with a string that starts with the same
            character as the 'string' parameter.
            Returns None if no such arc exisits.
            O(1) amortized time complexity
            (since we use hash tables for storing children).
            
            """
            if string[0] in self.children:
                return self.children[string[0]]
            elif not string[0]:
                return self
                
            return None
        
        
        def is_leaf(self):
            """
            Returns whether the node is a leaf.
            
            """
            return not self.children and not self.is_root()
            
            
        def is_root(self):
            """
            Returns whether the node is a root of the tree.
            
            """
            return not self.parent
        
        
        def path(self):
            """
            Returns a string that represents the path to the current node.
            
            """
            res = ''
            node = self
            while not node.is_root():
                (str_ind, substr_start, substr_end) = node.arc()
                res = self.strings_collection[str_ind][substr_start:substr_end] + res
                node = node.parent
            return res
        
        
        def equals(self, other):
            """
            Determines whether the current node equals to the other node;
            that is, whether they have the same weight and equal children.
            
            """
            if self.weight != other.weight:
                return False
            
            if set(self.children.keys()) != set(other.children.keys()):
                return False
                
            for k in self.children.keys():
                if not self.children[k].equals(other.children[k]):
                    return False
                
            return True
            
            
        #######################################################
        ######             T R A V E R S A L S           ######
        #######################################################
        
        def traverse_depth_first_pre_order(self, callback):
            """
            Traverses the tree in depth-first top-down order,
            calling the callback function in each node.
            The callback function should take the node as its parameter.
    
            """
            callback(self)
            for k in self.children:
                self.children[k].traverse_depth_first_pre_order(callback)
                
        def traverse_depth_first_post_order(self, callback):
            """
            Traverses the tree in depth-first bottom-up order,
            calling the callback function in each node.
            The callback function should take the node as its parameter.
    
            """
            for k in self.children:
                self.children[k].traverse_depth_first_post_order(callback)
            callback(self)
        
        def traverse_breadth_first(self, callback, queue):
            """
            Traverses the tree in breadth-first top-down order,
            calling the callback function in each node.
            The callback function should take the node as its parameter.
    
            """
            callback(self)
            for k in self.children:
                queue.append(self.children[k])
            if queue:
                queue[0].traverse_breadh_first_top_down(callback, queue[1:])
            
            
        def __str__(self): 
            """
            Returns just the node annotation (for networkx graph drawing)
            
            """
            return str(self.weight)
            