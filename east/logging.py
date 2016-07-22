# -*- coding: utf-8 -*

import sys

from east import utils


def progress(message, step, total):
    if not utils.output_is_redirected():
        sys.stdout.write("\r%s: %i/%i" % (message, step, total))
        sys.stdout.flush()


def clear():
    if not utils.output_is_redirected():
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()
