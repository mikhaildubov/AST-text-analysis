# -*- coding: utf-8 -*

from east import utils


class _TraversalOrder(utils.ImmutableMixin, utils.EnumMixin):
    DEPTH_FIRST_PRE_ORDER = "depth-first|pre-order"
    DEPTH_FIRST_POST_ORDER = "depth-first|post-order"
    BREADTH_FIRST = "breadth-first"


class _OperatingSystem(utils.ImmutableMixin, utils.EnumMixin):
    LINUX_32 = "linux_32"
    LINUX_64 = "linux_64"
    WINDOWS = "windows"
    MACOS = "macos"


class _URL(utils.ImmutableMixin, utils.EnumMixin):
    TOMITA = "http://api.yandex.ru/tomita/download.xml"


class _String(utils.ImmutableMixin, utils.EnumMixin):
    UNICODE_SPECIAL_SYMBOLS_START = 0x0A00


class _RelevanceMeasure(utils.ImmutableMixin, utils.EnumMixin):
    AST = "AST"
    COSINE = "cosine"


class _ASTAlgorithm(utils.ImmutableMixin, utils.EnumMixin):
    AST_LINEAR = "ast_linear"
    AST_NAIVE = "ast_naive"
    EASA = "easa"


class _TermWeighting(utils.ImmutableMixin, utils.EnumMixin):
    TF = "tf"
    TF_IDF = "tf-idf"


class _VectorSpace(utils.ImmutableMixin, utils.EnumMixin):
    WORDS = "words"
    STEMS = "stems"
    LEMMATA = "lemmata"


class _Language(utils.ImmutableMixin, utils.EnumMixin):
    DANISH = "danish"
    DUTCH = "dutch"
    ENGLISH = "english"
    FINNISH = "finnish"
    FRENCH = "french"
    GERMAN = "german"
    HUNGARIAN = "hungarian"
    ITALIAN = "italian"
    NORWEGIAN = "norwegian" 
    PORTUGUESE = "portuguese"
    ROMANIAN = "romanian"
    RUSSIAN = "russian"
    SPANISH = "spanish"
    SWEDISH = "swedish"


TraversalOrder = _TraversalOrder()
OperatingSystem = _OperatingSystem()
URL = _URL()
String = _String()
RelevanceMeasure = _RelevanceMeasure()
ASTAlgorithm = _ASTAlgorithm()
TermWeighting = _TermWeighting()
VectorSpace = _VectorSpace()
Language = _Language()
