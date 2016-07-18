# -*- coding: utf-8 -*

import sys

from east import utils


def progress(message, *args):
    if not utils.output_is_redirected():
        sys.stdout.write("\r%s" % (message % args))
        sys.stdout.flush()


def clear():
    if not utils.output_is_redirected():
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()
