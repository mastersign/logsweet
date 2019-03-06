# -*- coding: utf-8 -*-

"""
This module contains the functionality to load
a `logsweet` configuration from a YAML file.
"""

from typing import Optional, Mapping, Union, Sequence
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
    """
    A filter with zero to many include rules and zero to many exclude rules.

    :param config:
        A dict like structure with the filter configuration.
        Can have the keys `include` and/or `exclude`,
        each with either a string or a sequence of strings.
        Each string represents a regular expression.
    :type config: Mapping[str, Union[str, Sequence[str]]]
    """

    def __init__(self, config: Mapping[str, Union[str, Sequence[str]]]):

        include = config['include'] if 'include' in config else []
        if type(include) is str:
            include = [include]
        self._include_patterns = [re.compile(p) for p in include]

        exclude = config['exclude'] if 'exclude' in config else []
        if type(exclude) is str:
            exclude = [exclude]
        self._exclude_patterns = [re.compile(p) for p in exclude]

    def is_match(self, line: str) -> bool:
        """
        Checks whether a given line passes the filter or not.

        :param line:
            A text line to check.
        :type line: str

        :returns: `True` if the line passes; otherwise `False`
        """
        return (len(self._include_patterns) == 0 or
                any(map(lambda p: p.search(line), self._include_patterns))) \
            and not any(map(lambda p: p.search(line), self._exclude_patterns))

    def __call__(self, line: str) -> bool:
        return self.is_match(line)


class Configuration(object):
    """
    The `logsweet` configuration.

    :param file:
        The name of a YAML configuration file.
    :type file: str
    """

    def __init__(self, file: str):
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
        """
        Processes a text line.

        :param line:
            A text line to process according to the configuration.
        :type line: str

        :returns:
            The potentially modified line or `None`
            if the line was dropped during processing.
        """
        if not self._filter(line):
            return None
        for r in self._colors:
            match, line = r.process(line)
            if match:
                break
        return line
