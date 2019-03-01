# -*- coding: utf-8 -*-

from typing import Optional, Mapping
import re
import os

if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    try:
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        import colorama
        colorama.init()
    else:
        import colorama
        colorama.init = lambda: None

import colorful

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

    def __init__(self, config: Mapping[str, str]):
        try:
            self._pattern = re.compile(config.get('pattern'))
        except Exception as e:
            print('Error in regular expression: ', str(e))
            self._pattern = None
        else:
            self._format = _build_format_handler(config, self._pattern)

    def process(self, line: str):
        match = self._pattern.search(line) if self._pattern else None
        if match:
            return True, self._format(line, match)
        else:
            return False, line
