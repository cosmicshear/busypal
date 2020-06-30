#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import re
import threading
import colored as cl
from functools import wraps
from . import session

"""
-----------------------------------------------------------------------------
. Built on the basic idea from https://stackoverflow.com/a/39504463/11560784
. Some styles are from
  `pyspin`        : https://pypi.org/project/pyspin
  `alive-progress`: https://github.com/rsalmei/alive-progress/
  `go-spin`.      : https://github.com/tj/go-spin/
. Color and formatting are from
  `colored`       : https://pypi.org/project/colored/

Erfan Nourbakhsh, June 2020
-----------------------------------------------------------------------------

Usage:

*** With the decorator BusyPal provides:

>>> from busypal import busy
>>> @busy
... def a_long_running_operation(delay):
...     time.sleep(delay)
...
>>> a_long_running_operation(10)
/

>>> @busy(message='Please wait', style1=20, style2=29, fmt='{spinner1} {message} {spinner2} {outcome}', cleanup=['spinner2'])
... def a_long_running_operation(delay):
...     time.sleep(delay)
...     # raise Exception('something went wrong!') # this will be raised and terminate the whole process
>>> a_long_running_operation(6)
▆▅▄ Please wait ...

*** Or with the context manager, if preferred:

>>> from busypal import BusyPal
>>> with BusyPal('Hold on, it is taking longer than expected', style1={'id':25, 'color':{'fore':'BLACK','back':'DARK_ORANGE'}, 'typeface':'BOLD'}):
...     time.sleep(8) # some long-running operations
>>>     a_long_running_operation(5) # call a function
|   ● | Hold on, it is taking longer than expected

*** Do not use the context manager and the decorator together! You'll see a mess.
"""

default_style_id = 0
default_delay = 0.13

anim     = [None]*37
anim[0]  = '|/-\\✘✔'
anim[1]  = '⠁⠈⠐⠠⢀⡀⠄⠂✘✔'
anim[2]  = '∙○⦿●✘✔'
anim[3]  = '▏▎▍▌▋▊▉█▉▊▋▌▍▎▏✘✔'
anim[4]  = '▏▎▍▌▋▊▉█✘✔'
anim[5]  = '▁▂▃▄▅▆▇█▇▆▅▄▃▂✘✔'
anim[6]  = '⣾⣷⣯⣟⡿⢿⣻⣽✘✔'
anim[7]  = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏✘✔'
anim[8]  = '⠋⠙⠚⠞⠖⠦⠴⠲⠳⠓✘✔'
anim[9]  = '⠄⠆⠇⠋⠙⠸⠰⠠⠰⠸⠙⠋⠇⠆✘✔'
anim[10] = '⠋⠙⠚⠒⠂⠂⠒⠲⠴⠦⠖⠒⠐⠐⠒⠓⠋✘✔'
anim[11] = '⠁⠉⠙⠚⠒⠂⠂⠒⠲⠴⠤⠄⠄⠤⠴⠲⠒⠂⠂⠒⠚⠙⠉⠁✘✔'
anim[12] = '⠈⠉⠋⠓⠒⠐⠐⠒⠖⠦⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒⠓⠋⠉⠈✘✔'
anim[13] = '⠁⠁⠉⠙⠚⠒⠂⠂⠒⠲⠴⠤⠄⠄⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒⠓⠋⠉⠈⠈✘✔'
anim[14] = '←↖↑↗→↘↓↙✘✔'
anim[15] = '◴◷◶◵✘✔'
anim[16] = '◰◳◲◱✘✔'
anim[17] = '◐◓◑◒✘✔'
anim[18] = '▌▄▐▀✘✔'
anim[19] = '■□▪▫✘✔'
anim[20] = ['▁▂▃','▄▅▆','▇█▇','▆▅▄','▃▂▁','✘','✔']
anim[21] = ['○○○','⦿○○', '●○○', '●⦿○', '●●○', '●●⦿', '●●●','✘','✔']
anim[22] = ['○○○','⦿○○', '●○○', '○⦿○', '○●○', '○○⦿', '○○●','✘','✔']
anim[23] = ['∙∙∙','●∙∙', '∙●∙', '∙∙●','✘','✔']
anim[24] = ['  ','∙  ', '∙∙ ', '∙∙∙',' ∙∙','  ∙', ,'   ', '  ∙', ' ∙∙', '∙∙∙', '∙∙ ', '∙  ', '✘','✔']
anim[25] = ['|-----|', '|#----|', '|-#---|', '|--#--|', '|---#-|', '|----#|','✘','✔']
anim[26] = ['|-----|', '|#----|', '|-#---|', '|--#--|', '|---#-|', '|----#|','✘','✔']
anim[27] = ['|#----|', '|-#---|', '|--#--|', '|---#-|', '|----#|', '|---#-|', '|--#--|', '|-#---|','✘','✔']
anim[28] = ['------','>-----', '->----', '-->---', '--->--', '---->-','----->','✘','✔']
anim[29] = ['------','>-----', '>>----', '->>---', '-->>--', '--->>-','---->>','----->','✘','✔']
anim[30] = ['|●    |', '| ●   |', '|  ●  |', '|   ● |', '|    ●|', '|   ● |', '|  ●  |', '| ●   |','✘','✔']
anim[31] = ['|●∙   |', '|∙●   |', '| ∙●  |', '|  ∙● |', '|   ∙●|', '|   ●∙|', '|  ●∙ |', '| ●∙  |','✘','✔']
anim[32] = ['|█    |', '| █   |', '|  █  |', '|   █ |', '|    █|', '|   █ |', '|  █  |', '| █   |','✘','✔']
anim[33] = ['|▍    |','|▊    |','|█    |', '| █   |', '|  █  |', '|   █ |', '|    █|', '|    █|', '|   █ |', '|  █  |', '| █   |','✘','✔'] ## needs some work
anim[34] = ['   ','.  ','.. ','...','✘','✔']
anim[35] = ['▷▷▷','▶▷▷','▷▶▷','▷▷▶','✘','✔']
anim[36] = [r'•–––––––––––––',
            r'–•––––––––––––',
            r'––•–––––––––––',
            r'–––•––––––––––',
            r'––––•–––––––––',
            r'–––––√––––––––',
            r'–––––√\–––––––',
            r'–––––√\/––––––',
            r'–––––√\/•–––––',
            r'–––––√\/–•––––',
            r'––––––\/––•–––',
            r'–––––––/–––•––',
            r'––––––––––––•–',
            r'–––––––––––––•',
             '✘', '✔']

stylized_done = lambda x: cl.fore.GREEN+cl.style.BOLD+x+cl.style.RESET
stylized_fail = lambda x: cl.fore.RED+cl.style.BOLD+x+cl.style.RESET # cl.style.REVERSE inverts the colors

class BusyPal:

    @staticmethod
    def generate_spin(frames,color,typeface):
        if color is None:
            colors = ''
        else:
            if isinstance(color,str):
                color = {'fore': color}
            colors = ''
            for key, value in color.items():
                fbg = getattr(cl, key) # 'fore', 'back'
                colors += getattr(fbg, value.upper())
        stylized_frames = lambda x: getattr(cl.style,typeface)+colors+x+cl.style.RESET
        while True: 
            for frame in frames[:-2]:
                yield stylized_frames(frame)
    
    @staticmethod
    def remove_block(key, line):
        key='{'+key+'}'
        for pattern, sub in [(f' {key} ', ' '),(f' {key}', ''),(f'{key} ',''),(f'{key}','')]:
            line = line.replace(pattern, sub)
        return line
    
    def __init__(self, message='', style=None, style1=None, style2=None, frames=None, frames1=None, frames2=None, delay=None,
                 fmt='{spinner} {message} {outcome}', donetext='Done!', failtext='Failed!', cleanup=False, skip=0):
        
        # TODO style_message, style_outcome
        # TODO simultaneously print a message without overlap with the sppinners [similar to tqdm.write() method] - also look at https://pypi.org/project/enlighten/
        # TODO different enter/busy/exit styles for the message
        
        if not isinstance(skip, (bool, int)):
            raise ValueError('`skip` should be of type boolean or integer.')

        self.skip = skip

        if skip==0 and not session.viewedonscreen():
            self.skip = 1 # it does not show the animation part at least

        self.message = message
        
        if not self.skip:
            self.fmt = fmt
            self.donetext = donetext
            self.failtext = failtext
            self.cleanup = cleanup

            if not isinstance(self.cleanup, bool):
                if isinstance(self.cleanup, str):
                    self.cleanup = re.sub(r'\bspinner\b', 'spinner1', self.cleanup) 
                    self.cleanup = [self.cleanup]
                else:
                    self.cleanup = [re.sub(r'\bspinner\b', 'spinner1', item) for item in self.cleanup] 

            if delay and float(delay):
                if delay==0:
                    raise ValueError("`delay` can't be zero, try 0.1 (in seconds) or do not set it so that we can use the default value.")
                self.delay = delay
            else:
                self.delay = default_delay

            if style is not None:
                style1 = style

            if frames is not None:
                frames1 = frames

            if '{spinner}' in self.fmt:
                self.fmt = self.fmt.replace('{spinner}', '{spinner1}')

            if '{spinner1}' in self.fmt:
                if isinstance(style1, dict):
                    style_id1 = style1['id'] if 'id' in style1 else default_style_id
                    frames1 = style1['frames'] if 'frames' in style1 else None
                    color1 = style1['color'] if 'color' in style1 else None # DARK_ORANGE
                    typeface1 = style1['typeface'] if 'typeface' in style1 else 'RESET'
                else:
                    if style1 is not None and not isinstance(style1, (int,str,list,tuple)):
                        raise ValueError('styles only accept dictionaries, strings, list, tuples and integers')
                    style1 = style1 if style1 is not None else default_style_id
                    color1 = None
                    typeface1 = 'RESET'
                    if isinstance(style1, (str,list,tuple)):
                        frames1 = style1
                    else:
                        style_id1 = style1
                self.spinner1 = frames1 if frames1 is not None else anim[style_id1]
                self.spinner1_generator = self.generate_spin(self.spinner1,color1,typeface1)

            if '{spinner2}' in self.fmt:
                if isinstance(style2, dict):
                    style_id2 = style2['id'] if 'id' in style2 else default_style_id
                    frames2 = style2['frames'] if 'frames' in style2 else None
                    color2 = style2['color'] if 'color' in style2 else None # DARK_ORANGE
                    typeface2 = style2['typeface'] if 'typeface' in style2 else 'RESET'
                else:
                    if style2 is not None and not isinstance(style2, (int,str,list,tuple)):
                        raise ValueError('styles only accept dictionaries, strings, list, tuples and integers')
                    style2 = style2 if style2 is not None else default_style_id
                    color2 = None
                    typeface2 = 'RESET'
                    if isinstance(style2, (str,list,tuple)):
                        frames2 = style2
                    else:
                        style_id2 = style2
                self.spinner2 = frames2 if frames2 is not None else anim[style_id2]
                self.spinner2_generator = self.generate_spin(self.spinner2,color2,typeface2)

    def animate(self):
        while self.busy:
            line = self.fmt
            if '{spinner1}' in self.fmt:
                spinner1 = next(self.spinner1_generator)
            if '{spinner2}' in self.fmt:
                spinner2 = next(self.spinner2_generator)
            if 'message' in self.fmt:
                message = self.message
            if 'outcome' in self.fmt:
            	# - add an additional space here because sometimes the last character blinks unwantedly
                line = self.remove_block('outcome', line)+' '
            self.line = f"\r{line.format(**locals())}"
            sys.stdout.write(self.line)
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush() ## this extra flush makes it not smooth?

    def __enter__(self):
        self.busy = True
        if not self.skip:
            # - thread.daemon=True causes the thread to terminate when the main process ends
            threading.Thread(target=self.animate, daemon=True).start()
        else:
            # *** don't output anything - neigther the message (even if provided) nor the animation - if:
            #       * `skip` is explicitely set to something more than 1 (which can be 2)
            # *** otherwise just skip the animation part and write the message if:
            #       * `skip` is explicitely set to 1
            #                  - or -
            #       * the output is not being viewed on the screen (i.e. redirected to a file or something)
            if self.skip == 1:
                if self.message!='':
                    sys.stdout.write(f'{self.message}\n')

    def __exit__(self, exception, value, traceback):
        if self.skip:
            if exception is not None:
                return False
        else:
            self.busy = False
            time.sleep(self.delay)
            if self.cleanup is True:
                blank = ' ' * len(self.line) # overwrite with blank
                sys.stdout.write(f"\r{blank}\r")
                sys.stdout.flush()
                if exception is not None:
                    return False
            else:
                if self.cleanup is False:
                    self.cleanup = ['']
                if exception is not None:
                    if 'spinner1' in self.fmt:
                        if 'spinner1' in self.cleanup:
                            self.fmt = self.remove_block('spinner1', self.fmt)
                        else:
                            spinner1 = cl.stylize(self.spinner1[-2], cl.fg('red'), cl.attr('bold'))
                    if 'spinner2' in self.fmt:
                        if 'spinner2' in self.cleanup:
                            self.fmt = self.remove_block('spinner2', self.fmt)
                        else:
                            spinner2 = cl.stylize(self.spinner2[-2], cl.fg('red'), cl.attr('bold'))
                    if 'message' in self.fmt:
                        if 'message' in self.cleanup:
                            self.fmt = self.remove_block('message', self.fmt)
                        else:
                            message = self.message
                    if 'outcome' in self.fmt:
                        if 'outcome' in self.cleanup:
                            self.fmt = self.remove_block('outcome', self.fmt)
                        else:
                            outcome = stylized_fail(self.failtext)
                    fail = self.fmt.format(**locals()).lstrip()
                    blank = ' ' * (len(self.line)-len(fail)) # overwrite excess existing characters with blank
                    sys.stdout.write(f'\r{fail+blank}')
                    time.sleep(self.delay) # avoiding race condition (just in case)
                    return False
                else:
                    if 'spinner1' in self.fmt:
                        if 'spinner1' in self.cleanup:
                            self.fmt = self.remove_block('spinner1', self.fmt)
                        else:
                            spinner1 = cl.stylize(self.spinner1[-1], cl.fg('green'), cl.attr('bold'))
                    if 'spinner2' in self.fmt:
                        if 'spinner2' in self.cleanup:
                            self.fmt = self.remove_block('spinner2', self.fmt)
                        else:
                            spinner2 = cl.stylize(self.spinner2[-1], cl.fg('green'), cl.attr('bold'))
                    if 'message' in self.fmt:
                        if 'message' in self.cleanup:
                            self.fmt = self.remove_block('message', self.fmt)
                        else:
                            message = self.message
                    if 'outcome' in self.fmt:
                        if 'outcome' in self.cleanup:
                            self.fmt = self.remove_block('outcome', self.fmt)
                        else:
                            outcome = stylized_done(self.donetext)
                    done = self.fmt.format(**locals()).lstrip()
                    blank = ' ' * (len(self.line)-len(done)) # overwrite excess existing characters with blank
                    sys.stdout.write(f'\r{done+blank}\n')
                    time.sleep(self.delay) # avoiding race condition (just in case)

# function from: https://stackoverflow.com/a/62314128/11560784
def omittable_parentheses_decorator(decorator):
    """A decorator for decorators that allows them to be used without parentheses

    >>> @omittable_parentheses_decorator
    ... def multiplier(multiply_by=2):
    ...     def decorator(func):
    ...         def multiplying_wrapper(*args, **kwargs):
    ...             return multiply_by * func(*args, **kwargs)
    ...         return multiplying_wrapper
    ...     return decorator
    ...
    >>> @multiplier
    ... def no_parentheses():
    ...     return 2
    ...
    >>> @multiplier()
    ... def parentheses():
    ...     return 2
    ...
    >>> @multiplier(3)
    ... def parameter():
    ...     return 2
    ...
    >>> no_parentheses(), parentheses(), parameter()
    (4, 4, 6)
    """
    @wraps(decorator)
    def wrapper(*args, **kwargs):
        if not kwargs and len(args) == 1 and callable(args[0]):
            return decorator()(args[0])
        else:
            return decorator(*args, **kwargs)
    return wrapper

@omittable_parentheses_decorator
def busy(message='', style=None, style1=None, style2=None, frames=None,
         frames1=None, frames2=None, delay=None,fmt='{spinner} {message} {outcome}',
         donetext='Done!', failtext='Failed!', cleanup=False, skip=0, *args, **kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with BusyPal(message=message, style=style, style1=style1, style2=style2, frames=frames,
                         frames1=frames1, frames2=frames2, delay=delay,fmt=fmt,
                         donetext=donetext, failtext=failtext, cleanup=cleanup, skip=skip):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

