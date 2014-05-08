# -*- coding: utf-8 -*

from east.asts import base
from east.asts import utils
from east import consts

class LinearAnnotatedSuffixTree(base.AST):

    __algorithm__ = "ast_linear"

    def __init__(self, strings_collection):
        self.strings_collection = strings_collection
        self.root = self._construct()
        self._update_node_depth()

    def score(self, query, normalized=True, synonimizer=None):
        """
        Matches the string against the GAST using
        the algorithm described in [Chernyak, sections 1.3 & 1.4].
        
        Expects the input string to consist of
        alphabet letters only (no whitespaces etc.)
        
        Returns the score (a float in [0, 1]).
        
        query -- Unicode
        
        """
        
        query = query.upper()
        result = 0
    
        # For each suffix of the string:
        for suffix_start in xrange(len(query)):
            
            suffix = query[suffix_start:]
            suffix_score = 0
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
                if suffix and match == substr_end-substr_start:
                    child_node = child_node.chose_arc(suffix)
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

    def traverse_depth_first_pre_order(self, callback):
        """Traverses the annotated suffix tree in depth-first pre-order."""
        self.root.traverse_depth_first_pre_order(callback)

    def traverse_depth_first_post_order(self, callback):
        """Traverses the annotated suffix tree in depth-first post-order."""
        self.root.traverse_depth_first_post_order(callback)

    def traverse_breadth_first(self, callback):
        """Traverses the annotated suffix tree in breadth-first order."""
        self.root.traverse_breadth_first(callback, [])

    def _construct(self):
        """
        Generalized suffix tree construction algorithm based on the
        Ukkonen's algorithm for suffix tree construction,
        with linear [O(n_1 + ... + n_m)] worst-case time complexity,
        where m is the number of strings in collection.
        
        """
        
        # 1. Add a unique character to each string in the collection
        strings_collection = utils.make_unique_endings(self.strings_collection)
    
        ############################################################
        # 2. Build the GST using modified Ukkonnen's algorithm     #
        ############################################################
        
        root = LinearAnnotatedSuffixTree.Node()
        root.strings_collection = strings_collection
        # To preserve simplicity
        root.suffix_link = root
        root._arc = (0,-1,0)
        # For constant updating of all leafs, see [Gusfield {RUS}, p. 139]
        root._e = [0 for _ in xrange(len(strings_collection))]
        
        
        def _ukkonen_first_phases(string_ind):
            """
            Looks for the part of the string which is already encoded.
            Returns a tuple of form
            ([length of already encoded string preffix],
             [tree node to start the first explicit phase with],
             [path to go down at the beginning of the first explicit phase]).
            
            """
            already_in_tree = 0
            suffix = strings_collection[string_ind]
            starting_path = (0, 0, 0)
            starting_node = root
            child_node = starting_node.chose_arc(suffix)
            while child_node:
                (str_ind, substr_start, substr_end) = child_node.arc()
                match = utils.match_strings(
                    suffix, strings_collection[str_ind][substr_start:substr_end])
                already_in_tree += match
                if match == substr_end-substr_start:
                    # matched the arc, proceed with child node
                    suffix = suffix[match:]
                    starting_node = child_node
                    child_node = starting_node.chose_arc(suffix)
                else:
                    # otherwise we will have to proceed certain path at the beginning
                    # of the first explicit phase
                    starting_path = (str_ind, substr_start, substr_start+match)
                    break
            # For constant updating of all leafs, see [Gusfield {RUS}, p. 139]
            root._e[string_ind] = already_in_tree
                
            return (already_in_tree, starting_node, starting_path)
        
        def _ukkonen_phase(string_ind, phase, starting_node, starting_path, starting_continuation):
            """
            Ukkonen's algorithm single phase.
            Returns a tuple of form:
            ([tree node to start the next phase with],
             [path to go down at the beginning of the next phase],
             [starting continuation for the next phase]).
            
            """
            current_suffix_end = starting_node
            suffix_link_source_node = None
            path_str_ind, path_substr_start, path_substr_end = starting_path
            # Continuations [starting_continuation..(i+1)]
            for continuation in xrange(starting_continuation, phase+1):
                # Go up to the first node with suffix link [no more than 1 pass]
                if continuation > starting_continuation:
                    path_str_ind, path_substr_start, path_substr_end = 0, 0, 0
                    if not current_suffix_end.suffix_link:
                        (path_str_ind, path_substr_start, path_substr_end) = current_suffix_end.arc()
                        current_suffix_end = current_suffix_end.parent
                    if current_suffix_end.is_root():
                        path_str_ind = string_ind
                        path_substr_start = continuation
                        path_substr_end = phase
                    else:
                        # Go through the suffix link
                        current_suffix_end = current_suffix_end.suffix_link
                        
                # Go down the path (str_ind, substr_start, substr_end)
                # NB: using Skip/Count trick,
                # see [Gusfield {RUS} p.134] for details
                g = path_substr_end - path_substr_start
                if g > 0:
                    current_suffix_end = current_suffix_end.chose_arc(strings_collection
                                         [path_str_ind][path_substr_start])
                (_, cs_ss_start, cs_ss_end) = current_suffix_end.arc()
                g_ = cs_ss_end - cs_ss_start
                while g >= g_:
                    path_substr_start += g_
                    g -= g_
                    if g > 0:
                        current_suffix_end = current_suffix_end.chose_arc(strings_collection
                                             [path_str_ind][path_substr_start])
                    (_, cs_ss_start, cs_ss_end) = current_suffix_end.arc()
                    g_ = cs_ss_end - cs_ss_start
                    
                # Perform continuation by one of three rules,
                # see [Gusfield {RUS} p. 129] for details
                if g == 0:
                    # Rule 1
                    if current_suffix_end.is_leaf():
                        pass
                    # Rule 2a
                    elif not current_suffix_end.chose_arc(strings_collection[string_ind][phase]):
                        if suffix_link_source_node:
                            suffix_link_source_node.suffix_link = current_suffix_end
                        new_leaf = current_suffix_end.add_new_child(string_ind, phase, -1)
                        new_leaf.weight = 1
                        if continuation == starting_continuation:
                            starting_node = new_leaf
                            starting_path = (0, 0, 0)
                    # Rule 3a
                    else:
                        if suffix_link_source_node:
                            suffix_link_source_node.suffix_link = current_suffix_end
                        starting_continuation = continuation
                        starting_node = current_suffix_end
                        starting_path = (string_ind, phase, phase+1)
                        break
                    suffix_link_source_node = None
                else:
                    (si, ss, se) = current_suffix_end._arc
                    # Rule 2b
                    if strings_collection[si][ss + g] != strings_collection[string_ind][phase]:
                        parent = current_suffix_end.parent
                        parent.remove_child(current_suffix_end)
                        current_suffix_end._arc = (si, ss+g, se)
                        new_node = parent.add_new_child(si, ss, ss + g)
                        new_leaf = new_node.add_new_child(string_ind, phase, -1)
                        new_leaf.weight = 1
                        if continuation == starting_continuation:
                            starting_node = new_leaf
                            starting_path = (0, 0, 0)
                        new_node.add_child(current_suffix_end)
                        if suffix_link_source_node:
                            # Define new suffix link
                            suffix_link_source_node.suffix_link = new_node
                        suffix_link_source_node = new_node
                        current_suffix_end = new_node
                    # Rule 3b
                    else:
                        suffix_link_source_node = None
                        starting_continuation = continuation
                        starting_node = current_suffix_end.parent
                        starting_path = (si, ss, ss+g+1)
                        break
            
            # Constant updating of all leafs, see [Gusfield {RUS}, p. 139]
            starting_node._e[string_ind] += 1
            
            return starting_node, starting_path, starting_continuation
                        
        for m in xrange(len(strings_collection)):
            # Check for phases 1..x that are already in tree
            starting_phase, starting_node, starting_path = _ukkonen_first_phases(m)
            starting_continuation = 0
            # Perform phases (x+1)..n explicitly
            for phase in xrange(starting_phase, len(strings_collection[m])):
                starting_node, starting_path, starting_continuation = \
                    _ukkonen_phase(m, phase, starting_node, starting_path, starting_continuation)
                    
        
        ############################################################
        ############################################################
        ############################################################
        
        # 3. Delete degenerate first-level children
        for k in root.children.keys():
            (ss, si, se) = root.children[k].arc()
            if (se - si == 1 and
                ord(strings_collection[ss][si]) >= consts.String.UNICODE_SPECIAL_SYMBOLS_START):
                del root.children[k]
        
        # 4. Make a depth-first bottom-up traversal and annotate
        #    each node by the sum of its children;
        #    each leaf is already annotated with '1'.
        def _annotate(node):
            weight = 0
            for k in node.children:
                if node.children[k].weight > 0:
                    weight += node.children[k].weight
                else:
                    weight += _annotate(node.children[k])
            node.weight = weight
            return weight
        _annotate(root)
        
        return root
    
    
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
            child_node = LinearAnnotatedSuffixTree.Node()
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
            