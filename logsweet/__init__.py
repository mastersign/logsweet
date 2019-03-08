# -*- coding: utf-8 -*-

"""
Broadcast and receive log messages over network.
"""

import logging


try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())


# package metadata

__version__ = '0.1.0'
__url__ = 'https://github.com/mastersign/logsweet'
__author__ = 'Tobias Kiertscher'
__author_email__ = 'dev@mastersign.de'
__maintainer__ = 'Tobias Kiertscher'
__maintainer_email__ = 'dev@mastersign.de'
__keywords__ = ['lib', 'logsweet']
