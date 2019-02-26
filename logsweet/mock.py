# -*- coding: utf-8 -*-

"""
This module contains functionality for creating mocked log files.
"""

from random import choice
from datetime import datetime


_LEVELS = ['INFO', 'WARNING', 'ERROR']
_APPS = ['mock.worker', 'mock.broker', 'mock.manager']
_COMMANDS = ['PROGRESS', 'BEGIN', 'END']
_INFOS_1 = ['blue', 'red', 'green', 'black', 'yellow', 'pink', 'white']
_INFOS_2 = ['user', 'admin', 'operator']
_INFOS_3 = ['request', 'response', 'email', 'exception']


def random_log_message(n: int = 0) -> str:
    """
    Creates a random log message with the following parts:

    - Timestamp in the format ``yyyy-mm-dd HH:MM:SS``
    - Serial number
    - Message level (`INFO`, `WARNING`, or `ERROR`)
    - App name ``mock.<component>``
    - Command (`BEGIN`, `PROGRESS`, `END`)
    - Additional info text

    :parameter n:
        A serial number to identify the message
    :type n: int
    """
    return "{ts} {n} [{level}] {app}: {cmd} {info}".format(
        ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        n=n,
        level=choice(_LEVELS), app=choice(_APPS), cmd=choice(_COMMANDS),
        info=' '.join([choice(_INFOS_1), choice(_INFOS_2), choice(_INFOS_3)]))
