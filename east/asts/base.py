# -*- coding: utf-8 -*

import abc
import inspect

from east import consts
from east import exceptions
from east import utils

class AST(object):
    __metaclass__ = abc.ABCMeta

    @staticmethod
    def get_ast(strings_collection, ast_algorithm="easa"):
        for ast_cls in utils.itersubclasses(AST):
            if not inspect.isabstract(ast_cls) and ast_algorithm == ast_cls.__algorithm__:
                return ast_cls(strings_collection)
        raise exceptions.NoSuchASTAlgorithm(name=ast_algorithm)

    def __init__(self, strings_collection):
        if not strings_collection:
            raise exceptions.EmptyStringsCollectionException()

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
