# -*- coding: utf-8 -*-

from typing import Any, Optional, Union, Tuple, Sequence, Mapping
import re
from blessings import Terminal

term = Terminal()


class RuleFilter(object):

    def __init__(self, config: Mapping[str, Union[str, Sequence[str]]]):

        include = config['include'] if 'include' in config else []
        if include is str:
            include = [include]
        self._include_patterns = [re.compile(p) for p in include]

        exclude = config['exclude'] if 'exclude' in config else []
        if exclude is str:
            exclude = [exclude]
        self._exclude_patterns = [re.compile(p) for p in exclude]

    def match(self, line: str) -> Optional[Tuple[int, int]]:
        match = None
        for p in self._include_patterns:
            m = p.search(line)
            if m is None:
                return None
            if match is None:
                match = (m.start(), m.end())
        for p in self._exclude_patterns:
            if p.search(line):
                return None
        return match


class RuleFormat(object):

    def __init__(self, config: Mapping[str, str]):
        self._line_format = getattr(term, config['line'].replace(' ', '_')) \
            if 'line' in config else None
        self._match_format = getattr(term, config['match'].replace(' ', '_')) \
            if 'match' in config else None

    def format(self, line: str, match) -> str:
        s, e = match
        if self._match_format:
            line = line[:s] + self._match_format(line[s:e]) + line[e:]
        if self._line_format:
            line = self._line_format(line)
        return line


class Rule(object):

    def __init__(self, config: Mapping[str, Any]):
        self._filter = RuleFilter(config['filter']) if 'filter' in config else None
        self._format = RuleFormat(config['format']) if 'format' in config else None

    def process(self, line) -> Optional[str]:
        match = 0, len(line)
        if self._filter:
            match = self._filter.match(line)
        if match is None:
            return None
        if self._format:
            line = self._format.format(line, match)
        return line
