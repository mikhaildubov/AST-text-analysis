# -*- coding: utf-8 -*

import platform

from east import consts


def determine_operating_system():
    system = platform.system()
    bits = platform.architecture()[0]
    if system == "Windows":
        return consts.OperatingSystem.WINDOWS
    elif system == "Linux":
        if bits.startswith("64"):
            return consts.OperatingSystem.LINUX_64
        else:
            return consts.OperatingSystem.LINUX_32
    else:
        return consts.OperatingSystem.MACOS
