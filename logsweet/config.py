# -*- coding: utf-8 -*-

"""
This module contains the core functionality.
"""

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def _read_config(file):
    """
    Reads a YAML configuration file.
    """
    # wraps the simple yaml.load() call for automatically using
    # the C implementation of the yaml parser if available
    return yaml.load(file, Loader=Loader)


class FilterConfiguration(object):
    pass
