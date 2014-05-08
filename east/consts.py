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


TraversalOrder = _TraversalOrder()
OperatingSystem = _OperatingSystem()
URL = _URL()
String = _String()
