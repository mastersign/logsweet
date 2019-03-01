# -*- coding: utf-8 -*-

"""
This module contains the core functionality.
"""

from typing import Optional, Tuple, Mapping, Union, Sequence
import re
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from .colors import ColorRule


def _read_config(file):
    """
    Reads a YAML configuration file.
    """
    # wraps the simple yaml.load() call for automatically using
    # the C implementation of the yaml parser if available
    return yaml.load(file, Loader=Loader)


SUPPORTED_VERSIONS = {'0.1'}


class Filter(object):

    def __init__(self, config: Mapping[str, Union[str, Sequence[str]]]):

        include = config['include'] if 'include' in config else []
        if type(include) is str:
            include = [include]
        self._include_patterns = [re.compile(p) for p in include]

        exclude = config['exclude'] if 'exclude' in config else []
        if type(exclude) is str:
            exclude = [exclude]
        self._exclude_patterns = [re.compile(p) for p in exclude]

    def __call__(self, line: str) -> Optional[Tuple[int, int]]:
        return (len(self._include_patterns) == 0 or
                any(map(lambda p: p.search(line), self._include_patterns))) \
            and not any(map(lambda p: p.search(line), self._exclude_patterns))


class Configuration(object):

    def __init__(self, file):
        with open(file, 'r', encoding='UTF-8') as f:
            data = _read_config(f)
        if type(data) is not dict:
            raise Exception('Configuration file does not contain a YAML map.')
        if data.get('version', 'unknown') not in SUPPORTED_VERSIONS:
            raise Exception('Unsupported configuration file format.')

        self._filter = Filter(data)

        self._colors = [ColorRule(r) for r in data['colors']] \
            if 'colors' in data else []

    def process(self, line: str) -> Optional[str]:
        if not self._filter(line):
            return None
        for r in self._colors:
            match, line = r.process(line)
            if match:
                break
        return line
