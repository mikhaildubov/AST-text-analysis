# -*- coding: utf-8 -*

import abc

from east import consts
from east import exceptions
from east import utils

class AST(object):
    
    @staticmethod
    def get_ast(ast_algorithm, strings_collection):
        for ast_cls in utils.itersubclasses(AST):
            if ast_algorithm == ast_cls.__algorithm__:
                return ast_cls(strings_collection)
        raise exceptions.NoSuchASTAlgorithm(name=ast_algorithm)

    @abc.abstractmethod
    def score(self, query, normalized=True, synonimizer=None):
        """Computes the matching score for the given string against the AST."""

    def traverse(self, callback, order=consts.TraversalOrder.DEPTH_FIRST_PRE_ORDER):        
        if order == consts.TraversalOrder.DEPTH_FIRST_PRE_ORDER:
            self.traverse_depth_first_pre_order(callback)
        elif order == consts.TraversalOrder.DEPTH_FIRST_POST_ORDER:
            self.traverse_depth_first_post_order(callback)
        elif order == consts.TraversalOrder.BREADTH_FIRST:
            self.traverse_breadth_first(callback)

    @abc.abstractmethod
    def traverse_depth_first_pre_order(self, callback):
        """Traverses the annotated suffix tree in depth-first pre-order."""

    @abc.abstractmethod
    def traverse_depth_first_post_order(self, callback):
        """Traverses the annotated suffix tree in depth-first post-order."""

    @abc.abstractmethod
    def traverse_breadth_first(self, callback):
        """Traverses the annotated suffix tree in breadth-first order."""
