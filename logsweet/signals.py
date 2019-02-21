# _*_ coding: utf-8 _*_

"""
This module provides a way to gracefully shut down a loop
when SIGTERM or SIGINT are sent to the process.
"""

from signal import signal, SIGINT, SIGTERM

_stopped = False


def _notify_stop(signum, frame):
    global _stopped
    _stopped = True


signal(SIGINT, _notify_stop)
signal(SIGTERM, _notify_stop)


def is_stopped():
    """
    Checks if SIGINT or SIGTERM was received by the process
    since this module was initialized.

    :return: bool
    """
    return _stopped
