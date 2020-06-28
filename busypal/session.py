#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Acquires the following information about the running session:
(1) Type (terminal, notebook, etc.)
(2) Stdout/Stderr redirection
(3) Javascript compatibility
'''

import os
import sys
from contextlib import redirect_stderr
from io import StringIO         # python 3
# from StringIO import StringIO # python 2

def isterminal():
    ' Are we running this in a terminal? '
    return os.fstat(0) == os.fstat(1) # or sys.stdin.isatty()

def isipython():
    ' Are we running this in an IPython terminal? '
    try:
        if getattr(get_ipython(), 'kernel', None) is None:
            return True   # 'TerminalInteractiveShell' object has no attribute 'kernel'
        else:
            return False  # Jupyter notebook
    except NameError:
        return False      # Probably standard Python interpreter

# https://stackoverflow.com/a/39662359/11560784
def isnotebook():
    ' Are we running this in a notebook environment? '
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter

def shownonscreen():
    ' Checks whether the stdout/stderr shows up on the screen or is being redirected to a file '
    if isterminal() or isipython() or isnotebook():
        return True
    else:
        return False

def javascript_friendly():
    ' Checks whether we are able to run codes that require javascript through ipywidgets '
    try:
        from ipywidgets import IntSlider
        f = StringIO()
        with redirect_stderr(f):
            IntSlider()
        stderr = f.getvalue()
        if stderr.lower().find("widget javascript not detected") > -1:
            return False
    except ImportError:
        return False
    return True
