# -*- coding: utf-8 -*-

"""
This module contains the core functionality.
"""

from typing import Optional
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from .rules import Rule


def _read_config(file):
    """
    Reads a YAML configuration file.
    """
    # wraps the simple yaml.load() call for automatically using
    # the C implementation of the yaml parser if available
    return yaml.load(file, Loader=Loader)


SUPPORTED_VERSIONS = {'0.1'}


class Configuration(object):

    def __init__(self, file):
        with open(file, 'r', encoding='UTF-8') as f:
            data = _read_config(f)
        if type(data) is not dict:
            raise Exception('Configuration file does not contain a YAML map.')
        if data.get('version', 'unknown') not in SUPPORTED_VERSIONS:
            raise Exception('Unsupported configuration file format.')

        self._rules = [Rule(r) for r in data['rules']] if 'rules' in data else []

    def process(self, line: str) -> Optional[str]:
        for r in self._rules:
            match, line = r.process(line)
            if match:
                return line
        return line
