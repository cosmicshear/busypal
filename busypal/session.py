#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Acquires the following information about the running session:
(1) Type (terminal, notebook, spyder, etc.)
(2) Stdout/Stderr redirection
(3) Javascript compatibility
'''

import os
import sys
from contextlib import redirect_stderr
import re
import psutil
from multiprocessing import current_process
from io import StringIO         # python 3
# from StringIO import StringIO # python 2 (who cares?)

def isterminal():
    '''
    Are we running this in a Python command shell directly executed from a standard terminal
    command line (e.g. bash, tcsh, zsh) with the stdout/stderr shown in the terminal?
    '''
    return sys.stdin.isatty() # checks if stdin is a terminal [or os.fstat(0) == os.fstat(1) but it wasn't working in Windows]

def isipythonterminal():
    '''
    Are we running this in an IPython command shell directly executed from a standard terminal?
    Otherwise, it is either an IPython kernel (used for notebooks and
    advanced python GUI editors and IDEs) or just a standard terminal.
    '''
    try:
        if getattr(get_ipython(), 'kernel', None) is None:
            return True    # IPython running in terminal ('TerminalInteractiveShell' object has no attribute 'kernel')
        else:
            return False   # [Jupyter Lab/Notebook, Google Colab], [Qt Console, Spyder], etc.
    except NameError:
        return False       # Probably a standard Python interpreter running e.g. in your bash shell

def isipythongui(): # with advanced functionalities (e.g. inline plots) but not extensible as notebooks
    if any(s in session_type() for s in ['qt-console', 'spyder']): ## more to add?
        return True
    else:
        return False

# tested on Spyder, Qt Console, JupyterLab, Jupyter Notebook, IPython terminal, Google Colab, OSX default terminal, iTerm2
# courtesy of https://github.com/tqdm/tqdm/issues/443#issuecomment-369453219
def isnotebook():
    ' Are we running this in a notebook (jupyter lab/notebook or google colab) environment? '
    # - you can add more than just jupyter lab/notebook if you know more that exist. This currently
    #   covers the jupyter lab, the jupyter notebook and the google colab environments
    return cmdline_has('jupyter-(lab|notebook)')

def cmdline_has(whole_word):
    # - psutil is cross-platform
    if any(
            re.search(r'\b{}\b'.format(whole_word), s)
            for s in psutil.Process().parent().cmdline()
    ):
        return True
    else:
        return False

def session_type():
    ' A more general function which gives you the session type as a string '
    try:
        ipython = get_ipython()
        kernel  = ipython.kernel.__module__
    except NameError:                       # standard python interpreter in terminal
        ipython = False
        kernel  = 'None'
    except AttributeError:                  # 'TerminalInteractiveShell' object has no attribute 'kernel'   
        ipython = True                      # IPython running from terminal
        kernel  = 'None'
    if cmdline_has('jupyter-(lab|notebook)') and 'google' in kernel:
        return 'google-colab'
    elif cmdline_has('jupyter-lab'):
        return 'jupyter-lab'                # IPython running from the web-based JupyterLab Notebook with a kernel
    elif cmdline_has('jupyter-notebook'):
        return 'jupyter-notebook'           # IPython running from the web-based Jupyter Notebook with a kernel
    elif cmdline_has('qtconsole'):
        return 'qt-console'                 # IPython running from the PyQt GUI editor
    elif cmdline_has('spyder'):
        return 'spyder'                     # IPython running from the Spyder IDE
                                            # ... Can we add more GUIs, IDEs, etc. here? ...
    else:
        shell = psutil.Process().parent().cmdline()[0]
        # - now pull the exact name out
        if os.name == 'nt':                 # Windows (e.g. shell = 'Explorer.EXE' for python executable,
                                            # 'pythonw.exe' for IDLE python executable,
                                            # 'cmd.exe' for the standard Windows cmd
                                            # 'ipython' for ipython typed in the standard Windows cmd (we will change it to 'cmd.exe')
            shell = shell.split('\\').pop()
            if shell == 'ipython':
                shell = 'cmd.exe'
        else:                               # Linux, OSX (e.g. shell = 'zsh', 'bash', 'fish', 'tcsh', 'ash', 'dash')
            shell = shell.rstrip('/').split('/').pop().replace('-','')
        if ipython:                         # IPython running from shell, e.g. 'ipython-bash', 'ipython-fish', etc.
            return 'ipython-{}'.format(shell)
        else:
            return shell

## modified from https://stackoverflow.com/a/39662359/11560784 [not working as expected, I used a different approach]
# def isnotebook():
#     ' Are we running this in a notebook environment? '
#     try:
#         shell = get_ipython().__class__.__name__ # get_ipython().__class__.__module__ == 'Shell' for google colab
#         if shell == 'ZMQInteractiveShell':
#             return True   # Jupyter notebook or qtconsole
#         elif shell == 'TerminalInteractiveShell':
#             return False  # Terminal running IPython
#         elif shell == 'Shell':
#             return True  # Google Colab (last time I checked)
#         else:
#             return False  # Other type (?)
#     except NameError:
#         return False      # Probably standard Python interpreter

def viewedonscreen():
    ' Checks whether the stdout/stderr directly gets dumped to the screen or is being redirected to a file '
    if isterminal() or isipythonterminal() or isipythongui() or isnotebook():
        return True
    else:
        return False

def isparent():
    ' Main/parent or forked etc.? '
    return current_process().name=='MainProcess'

def javascript_friendly():
    ' Checks whether we are able to run codes that require javascript through ipywidgets '
    # `javascript_friendly()==True` also means `viewedonscreen()==True`
    try:
        from ipywidgets import IntSlider
        IntSlider()
        f = StringIO()
        with redirect_stderr(f):
            IntSlider()
        stderr = f.getvalue()
        if stderr.lower().find("widget javascript not detected") > -1:
            return False
    except ImportError:
        return False
    return True if isnotebook() else False
