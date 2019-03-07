# -*- coding: utf-8 -*-

"""
This module contains the core functionality.
"""

from typing import Optional, Sequence, TextIO
from time import sleep
from random import choice

from logsweet.config import Configuration
from .signals import is_stopped
from .mock import random_log_message
from .watch import LogWatcher
from .net import Broadcaster, Transmitter, Listener


class LogWatcherHandler(object):

    def __init__(self, name: str,
                 config: Optional[Configuration],
                 echo: bool,
                 bc: Optional[Broadcaster] = None,
                 tm: Optional[Transmitter] = None):
        self._name = name
        self._cfg = config
        self._echo = echo
        self._bc = bc
        self._tm = tm

    def notify_watch(self, file_name):
        topic = 'log|watch|{}|{}'.format(self._name, file_name)
        if self._bc:
            self._bc.send(topic, '')
        if self._tm:
            self._tm.send(topic, '')
        if self._echo:
            print('START WATCHING: ' + file_name)

    def notify_unwatch(self, file_name):
        topic = 'log|unwatch|{}|{}'.format(self._name, file_name)
        if self._bc:
            self._bc.send(topic, '')
        if self._tm:
            self._tm.send(topic, '')
        if self._echo:
            print('STOP WATCHING: ' + file_name)

    def notify_lines(self, file_name, lines):
        topic = 'log|line|{}|{}'.format(self._name, file_name)
        for line in lines:
            line2 = self._cfg.process(line) if self._cfg else line
            if line2 is None:
                continue
            if self._bc:
                self._bc.send(topic, line)
            if self._tm:
                self._tm.send(topic, line)
            if self._echo:
                print('LINE: {} | {}'.format(file_name, line2))


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


def _watch_and_send_greeting(**kwargs):
    print("Listening to file(s): " + kwargs.get('file_glob'))
    if kwargs.get('bind_address'):
        print("Broadcasting with ZeroMQ PUB at: " + kwargs.get('bind_address'))
    if kwargs.get('connect_addresses'):
        print("Transmitting with ZeroMQ PUSH to:")
        for address in kwargs.get('connect_addresses'):
            print("  - " + address)
    if kwargs.get('all_lines'):
        print("Reading already existing content.")
    elif kwargs.get('tail_lines') > 0:
        print("Reading {} trailing lines.".format(kwargs.get('tail_lines')))
    if kwargs.get('config_file'):
        print("Using YAML configuration.")
        if kwargs.get('exec_actions'):
            print("Executing actions from configuration.")


def watch_and_send(file_glob: str,
                   bind_address: Optional[str] = None,
                   connect_addresses: Optional[Sequence[str]] = None,
                   config_file: Optional[TextIO] = None,
                   exec_actions: bool = False,
                   all_lines: bool = False,
                   tail_lines: int = 0,
                   encoding: Optional[str] = None,
                   name: str = 'unknown',
                   echo: bool = False):
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

    :param config_file:
        The name of a YAML configuration file.
    :type config_file: Optional[TextIO]

    :param exec_actions:
        A switch to activate the execution of actions.
    :type exec_actions: bool

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

    :param echo:
        If `True`, new lines are printed to the console.
    :type echo: bool

    :param encoding:
        Specifies the encoding for reading the text files.
        If `None` defaults to preferred encoding of current user.
    :type encoding: Optional[str]
    """
    _watch_and_send_greeting(**locals())

    config = Configuration(config_file, exec_actions) if config_file else None

    broadcaster = Broadcaster(bind_address) \
        if bind_address else None
    transmitter = Transmitter(connect_addresses) \
        if connect_addresses else None

    handler = LogWatcherHandler(name, config, echo,
                                bc=broadcaster, tm=transmitter)
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
                     config_file: Optional[TextIO] = None,
                     interval: float = 0.1,
                     exec_actions: bool = False):
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

    :param config_file:
        The name of a YAML configuration file.
    :type config_file: Optional[TextIO]

    :param interval:
        The timeout in seconds when waiting for new messages
        before handling possible interruption.
    :type interval: float

    :param exec_actions:
        A switch to activate the execution of actions.
    :type exec_actions: bool
    """

    config = Configuration(config_file, exec_actions) if config_file else None

    def handle_line(source, file_name, line):
        if config:
            line = config.process(line)
        if line is not None:
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


def _proxy_greeting(**kwargs):
    if kwargs.get('backend_bind_address'):
        print("Receiving with ZeroMQ PULL at: " +
              kwargs.get('backend_bind_address'))
    if kwargs.get('backend_connect_addresses'):
        print("Collecting with ZeroMQ SUB from:")
        for address in kwargs.get('backend_connect_addresses'):
            print("  - " + address)

    if kwargs.get('frontend_bind_address'):
        print("Broadcasting with ZeroMQ PUB at: " +
              kwargs.get('frontend_bind_address'))
    if kwargs.get('frontend_connect_addresses'):
        print("Transmitting with ZeroMQ PUSH to:")
        for address in kwargs.get('frontend_connect_addresses'):
            print("  - " + address)


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
    _proxy_greeting(**locals())

    broadcaster = Broadcaster(frontend_bind_address) \
        if frontend_bind_address else None
    transmitter = Transmitter(frontend_connect_addresses) \
        if frontend_connect_addresses else None

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
