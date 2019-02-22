# -*- coding: utf-8 -*-

"""
This module contains the core functionality.
"""

from typing import Optional, Sequence
from time import sleep
from random import choice
from .signals import is_stopped
from .mock import random_log_message
from .watch import LogWatcher
from .net import Broadcaster, Listener


class LogWatcherHandler(object):

    def __init__(self, bc: Broadcaster, name: str, silent: bool):
        self._bc = bc
        self._name = name
        self._silent = silent

    def notify_watch(self, file_name):
        topic = 'log|watch|{}|{}'.format(self._name, file_name)
        self._bc.send(topic, '')
        if not self._silent:
            print('START WATCHING: ' + file_name)

    def notify_unwatch(self, file_name):
        topic = 'log|unwatch|{}|{}'.format(self._name, file_name)
        self._bc.send(topic, '')
        if not self._silent:
            print('STOP WATCHING: ' + file_name)

    def notify_lines(self, file_name, lines):
        topic = 'log|line|{}|{}'.format(self._name, file_name)
        for l in lines:
            self._bc.send(topic, l)
            if not self._silent:
                print('LINE: {} | {}'.format(file_name, l))


def write_logfiles(logfiles: Sequence[str], interval: float = 0.5):
    """
    Writes random entries into one or multiple logfiles.

    :param logfiles:
        An iterable with filenames to logfiles.
    :type logfiles: Sequence[str]

    :param interval:
        The interval for entry generation in seconds.
    :type interval: float
    """
    print("Writing random entries to the following log files:")
    for fn in logfiles:
        print("  - " + fn)

    try:
        while True:
            with open(choice(logfiles), 'a', encoding='UTF-8') as f:
                f.write(random_log_message() + '\n')
            if is_stopped():
                break
            sleep(interval)
    except KeyboardInterrupt:
        return


def broadcast_lines(bind_address: str,
                    file_glob: str,
                    all_lines: bool = False,
                    tail_lines: int = 0,
                    encoding: Optional[str] = None,
                    name: str = 'unknown',
                    silent: bool = False):
    """
    Start following text files, broadcasting newlines via an ZeroMQ PUB socket.

    :param file_glob:
        A path to the text file to tail.
    :type file_glob: str

    :param bind_address:
        The address to bind the socket to.
    :type bind_address: str

    :param all_lines:
        A flag to indicate if already existing content
        of the file should be broadcasted.
    :type all_lines: bool

    :param tail_lines:
        Indicates a number of trailing lines to broadcast before
        following new lines.
    :type tail_lines: int

    :param name:
        The name of this broadcaster.
    :type name: str

    :param silent:
        If `False`, new lines are printed to the console.
    :type silent: bool

    :param encoding:
        Specifies the encoding for reading the text files.
        If `None` defaults to preferred encoding of current user.
    :type encoding: Optional[str]
    """
    print("Listening to file(s): " + file_glob)
    print("Publishing on ZeroMQ PUB at: " + bind_address)
    if all_lines:
        print("Broadcasting existing content.")
    elif tail_lines > 0:
        print("Broadcasting {} trailing lines.".format(tail_lines))

    broadcaster = Broadcaster(bind_address)
    handler = LogWatcherHandler(broadcaster, name, silent)
    watcher = LogWatcher(file_glob, handler,
                         all_lines=all_lines, tail_lines=tail_lines,
                         encoding=encoding)
    try:
        watcher.watch()
    finally:
        broadcaster.close()


def listen_to_lines(addresses: Sequence[str], interval: float = 0.1):
    """
    Subscribes to a number of ZeroMQ PUB sockets
    and prints the received lines.

    :param addresses:
        An iterable with multiple addresses;
        each in the format of ``<ip>:<port>``.
    :type addresses: Sequence[str]

    :param interval:
        The timeout in seconds when waiting for new messages
        before handling possible interruption.
    :type interval: float
    """

    def handle_line(source, file_name, line):
        print("LINE {}: {} | {}".format(source, file_name, line))

    def handle_watch(source, file_name):
        print("BEGIN {}: {}".format(source, file_name))

    def handle_unwatch(source, file_name):
        print("END {}: {}".format(source, file_name))

    listener = Listener(addresses, handle_line,
                        watch_cb=handle_watch, unwatch_cb=handle_unwatch,
                        interval=interval)
    listener.listen()
