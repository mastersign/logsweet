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
from .net import Broadcaster, Transmitter, Listener


class LogWatcherHandler(object):

    def __init__(self, name: str, silent: bool,
                 bc: Optional[Broadcaster] = None,
                 tm: Optional[Transmitter] = None):
        self._bc = bc
        self._tm = tm
        self._name = name
        self._silent = silent

    def notify_watch(self, file_name):
        topic = 'log|watch|{}|{}'.format(self._name, file_name)
        if self._bc:
            self._bc.send(topic, '')
        if self._tm:
            self._tm.send(topic, '')
        if not self._silent:
            print('START WATCHING: ' + file_name)

    def notify_unwatch(self, file_name):
        topic = 'log|unwatch|{}|{}'.format(self._name, file_name)
        if self._bc:
            self._bc.send(topic, '')
        if self._tm:
            self._tm.send(topic, '')
        if not self._silent:
            print('STOP WATCHING: ' + file_name)

    def notify_lines(self, file_name, lines):
        topic = 'log|line|{}|{}'.format(self._name, file_name)
        for l in lines:
            if self._bc:
                self._bc.send(topic, l)
            if self._tm:
                self._tm.send(topic, l)
            if not self._silent:
                print('LINE: {} | {}'.format(file_name, l))


def write_logfiles(logfiles: Sequence[str],
                   interval: float = 0.5,
                   max_n: Optional[int] = None):
    """
    Writes random entries into one or multiple log files.

    :param logfiles:
        An iterable with file names to log files.
    :type logfiles: Sequence[str]

    :param interval:
        The interval for entry generation in seconds.
    :type interval: float

    :param max_n:
        The maximal number of entries to write.
    :type max_n: Optional[int]
    """
    print("Writing random entries to the following log files:")
    for fn in logfiles:
        print("  - " + fn)

    n = 0
    try:
        while True:
            with open(choice(logfiles), 'a', encoding='UTF-8') as f:
                f.write(random_log_message(n) + '\n')
            n += 1
            if is_stopped() or (max_n is not None and n >= max_n):
                break
            sleep(interval)
    except KeyboardInterrupt:
        return


def watch_and_send(file_glob: str,
                   bind_address: Optional[str] = None,
                   connect_addresses: Optional[Sequence[str]] = None,
                   all_lines: bool = False,
                   tail_lines: int = 0,
                   encoding: Optional[str] = None,
                   name: str = 'unknown',
                   silent: bool = False):
    """
    Start following text files, sending new lines
    via a ZeroMQ PUB and/or PUSH socket.

    :param file_glob:
        A path to the text file to tail.
    :type file_glob: str

    :param bind_address:
        The address to bind the PUB socket to;
        Listening for incoming connections from listeners and proxies.
    :type bind_address: Optional[str]

    :param connect_addresses:
        The addresses to connect a PUSH socket to;
        Actively connecting to one listener or multiple proxies.
    :type connect_addresses: Optional[Sequence[str]]

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
    if bind_address:
        print("Broadcasting with ZeroMQ PUB at: " + bind_address)
    if connect_addresses:
        print("Transmitting with ZeroMQ PUSH to:")
        for address in connect_addresses:
            print("  - " + address)
    if all_lines:
        print("Broadcasting all existing content.")
    elif tail_lines > 0:
        print("Broadcasting {} trailing lines.".format(tail_lines))

    broadcaster = Broadcaster(bind_address) if bind_address else None
    transmitter = Transmitter(connect_addresses) if connect_addresses else None

    handler = LogWatcherHandler(name, silent, bc=broadcaster, tm=transmitter)
    watcher = LogWatcher(file_glob, handler,
                         all_lines=all_lines, tail_lines=tail_lines,
                         encoding=encoding)
    try:
        watcher.watch()
    finally:
        if broadcaster:
            broadcaster.close()
        if transmitter:
            transmitter.close()


def listen_and_print(bind_address: Optional[str] = None,
                     connect_addresses: Optional[Sequence[str]] = None,
                     interval: float = 0.1):
    """
    Connects to watchers and proxies with a ZeroMQ SUB socket
    and/or binds a ZeroMQ PULL socket for watchers and proxies
    to connect to;
    and prints the received lines.

    :param bind_address:
        The address to bind the PULL socket to.
        (Listening for incoming connections from watchers or proxies.)
    :type bind_address: Optional[str]

    :param connect_addresses:
        The addresses to connect a SUB socket to.
        (Actively connecting to watchers or proxies.)
    :type connect_addresses: Optional[Sequence[str]]

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

    listener = Listener(handler=handle_line,
                        watch_cb=handle_watch, unwatch_cb=handle_unwatch,
                        bind_address=bind_address,
                        connect_addresses=connect_addresses,
                        interval=interval)
    listener.listen()


def proxy(backend_bind_address: Optional[str] = None,
          backend_connect_addresses: Optional[Sequence[str]] = None,
          frontend_bind_address: Optional[str] = None,
          frontend_connect_addresses: Optional[Sequence[str]] = None,
          interval: float = 0.1):
    """
    :param backend_bind_address:
        The address to bind the PULL socket to.
        (Listening for incoming connections from watchers and other proxies.)
    :type backend_bind_address: Optional[str]

    :param backend_connect_addresses:
        The addresses to connect a SUB socket to.
        (Actively connecting to watchers and other proxies.)
    :type backend_connect_addresses: Optional[Sequence[str]]

    :param frontend_bind_address:
        The address to bind a PUB socket to;
        Listening for incoming connections from listeners or other proxies.
    :type frontend_bind_address: Optional[str]

    :param frontend_connect_addresses:
        The addresses to connect a PUSH socket to;
        Actively connecting to one listener or multiple other proxies.
    :type frontend_connect_addresses: Optional[Sequence[str]]

    :param interval:
        The timeout in seconds when waiting for new messages
        before handling possible interruption.
    :type interval: float
    """

    if backend_bind_address:
        print("Receiving with ZeroMQ PULL at: " + backend_bind_address)
    if backend_connect_addresses:
        print("Collecting with ZeroMQ SUB from:")
        for address in backend_connect_addresses:
            print("  - " + address)

    if frontend_bind_address:
        print("Broadcasting with ZeroMQ PUB at: " + frontend_bind_address)
    if frontend_connect_addresses:
        print("Transmitting with ZeroMQ PUSH to:")
        for address in frontend_connect_addresses:
            print("  - " + address)

    broadcaster = Broadcaster(frontend_bind_address) if frontend_bind_address else None
    transmitter = Transmitter(frontend_connect_addresses) if frontend_connect_addresses else None

    def handle_message(data: Sequence[bytes]):
        if broadcaster:
            broadcaster.send_raw(data)
        if transmitter:
            transmitter.send_raw(data)

    listener = Listener(raw_cb=handle_message,
                        bind_address=backend_bind_address,
                        connect_addresses=backend_connect_addresses,
                        interval=interval)

    try:
        listener.listen()
    finally:
        if broadcaster:
            broadcaster.close()
        if transmitter:
            transmitter.close()
