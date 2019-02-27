# -*- coding: utf-8 -*-

from typing import Any, Optional, Union, Tuple, Sequence, Mapping
import re
import colorama

colorama.init()

_colors = [
    'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'
]
_foreground_colors = {
    key: getattr(colorama.Fore, key.upper())
    for key in _colors
}
for c in _colors:
    _foreground_colors['light' + c] =\
        getattr(colorama.Fore, 'LIGHT' + c.upper() + '_EX')
_background_colors = {
    key: getattr(colorama.Back, key.upper())
    for key in _colors
}
for c in _colors:
    _background_colors['light' + c] =\
        getattr(colorama.Fore, 'LIGHT' + c.upper() + '_EX')


def _parse_format(fmt: Optional[str]):
    if fmt is None:
        return '', ''
    parts = [p.strip() for p in fmt.split(' ')]
    if len(parts) == 1:
        return _foreground_colors[parts[0]], colorama.Fore.RESET
    if len(parts) == 2 and parts[0] == 'on':
        return _background_colors[parts[1]], colorama.Back.RESET
    if len(parts) == 3 and parts[1] == 'on':
        return _foreground_colors[parts[0]] + _background_colors[parts[2]], \
               colorama.Style.RESET_ALL
    return '', ''


def _build_format_handler(line_fmt: Optional[str], match_fmt: Optional[str]):
    outer_start, outer_end = _parse_format(line_fmt)
    inner_start, inner_end = _parse_format(match_fmt)
    if outer_start:
        inner_start = outer_end + inner_start
    if inner_start:
        inner_end = inner_end + outer_start

    def __format(line: str, match: Tuple[int, int]):
        s, e = match
        return outer_start + line[:s] + \
            inner_start + line[s:e] + inner_end + \
            line[e:] + outer_end

    return __format


class RuleFilter(object):

    def __init__(self, config: Mapping[str, Union[str, Sequence[str]]]):

        include = config['include'] if 'include' in config else []
        if type(include) is str:
            include = [include]
        self._include_patterns = [re.compile(p) for p in include]

        exclude = config['exclude'] if 'exclude' in config else []
        if type(exclude) is str:
            exclude = [exclude]
        self._exclude_patterns = [re.compile(p) for p in exclude]

    def match(self, line: str) -> Optional[Tuple[int, int]]:
        match = None
        for p in self._include_patterns:
            m = p.search(line)
            if m and match is None:
                match = m.span()
                break
        if match is None:
            return
        for p in self._exclude_patterns:
            if p.search(line):
                return None
        return match


class RuleFormat(object):

    def __init__(self, config: Mapping[str, str]):
        self.format = _build_format_handler(config.get('line'), config.get('match'))


class Rule(object):

    def __init__(self, config: Mapping[str, Any]):
        self._filter = RuleFilter(config['filter']) if 'filter' in config else None
        self._format = RuleFormat(config['format']) if 'format' in config else None

    def process(self, line) -> Tuple[bool, str]:
        match = 0, len(line)
        if self._filter:
            match = self._filter.match(line)
        if match is None:
            return False, line
        if self._format:
            line = self._format.format(line, match)
        return True, line
