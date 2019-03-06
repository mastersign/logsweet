# -*- coding: utf-8 -*-

"""
This module contains the functionality to colorize text lines
according to the match of regular expression.
"""

from typing import Optional, Mapping, Tuple
import re
import os

# check if os is windows
if os.name == 'nt':
    # try to enable ANSI escape sequence support in console
    import ctypes
    kernel32 = ctypes.windll.kernel32
    try:
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:  # noqa: E722
        # otherwise initialize colorama
        import colorama
        colorama.init()
    else:
        import colorama
        # monkey-patch colorama init, because it is always called by colorful
        colorama.init = lambda: None

# import colorful after potentially monky-patching colorama.init()
# if os is windows and console does support ANSI sequences
import colorful  # noqa: E402

colorful.use_256_ansi_colors()


def _parse_format(fmt: Optional[str]):
    if fmt is None:
        return '', ''
    c = str(getattr(colorful, fmt.replace(' ', '_'), None))
    if c:
        return c, str(colorful.reset)
    else:
        print("Invalid colorful style: ", fmt.replace(' ', '_'))
    return '', ''


def _build_format_handler(colors: Mapping[str, str], pattern):
    lcs, lce = _parse_format(colors.get('line'))
    mcs, mce = _parse_format(colors.get('match'))
    groups = [(group_name, _parse_format(colors.get(group_name)))
              for group_name in pattern.groupindex.keys()]

    def __format(line: str, match):
        ms, me = match.span()
        ccs, cce = mcs or lcs, mce or lce
        p = ms
        result = lcs + line[:ms] + lce
        for n, (cs, ce) in sorted(groups, key=lambda g: match.start(g[0])):
            s, e = match.span(n)
            result += ccs + line[p:s] + cce
            p = s
            ccs, cce = cs or lcs, ce or lce
        if groups:
            result += ccs + line[p:e] + cce
            p = e
            ccs, cce = mcs or lcs, mce or lce
        result += ccs + line[p:me] + cce
        result += lcs + line[me:] + lce
        return result

    return __format


class ColorRule(object):
    """
    A coloring rule for applying ANSI colors to a text line
    according to a regular expression.

    :param config:
        A dict like structure with the following keys:
        `pattern` with the regular expression,
        `line` with a color for the whole line,
        `match` with a color for the matched string,
        and more entries with colors for every named group in the regex.
    :type config: Mapping[str, str]
    """

    def __init__(self, config: Mapping[str, str]):
        try:
            self._pattern = re.compile(config.get('pattern'))
        except Exception as e:
            print('Error in regular expression: ', str(e))
            self._pattern = None
        else:
            self._format = _build_format_handler(config, self._pattern)
        self.__call__ = self.process

    def process(self, line: str) -> Tuple[bool, str]:
        """
        Process a line and insert ANSI escape sequences for colors
        if the pattern is a match.

        :param line:
            The text line to process.
        :type line: str

        :return:
            A tuple with a boolean, stating if the pattern matched,
            and the potentially modified text line.
        """
        match = self._pattern.search(line) if self._pattern else None
        if match:
            return True, self._format(line, match)
        else:
            return False, line
