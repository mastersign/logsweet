# -*- coding: utf-8 -*-

"""
This module contains functionality for transporting
log messages over the network.
"""

from typing import Any, Union, Optional, Callable, Sequence
from time import sleep
from zmq import Context, ZMQError, PUB, SUB, SUBSCRIBE, NOBLOCK
from .signals import is_stopped

_TOPIC_ENCODING = 'UTF-8'
_LINE_ENCODING = 'UTF-8'


class Broadcaster(object):
    """
    A text line broadcaster.

    :parameter bind_address:
        An IP and port to bind the ZeroMQ socket to.
        E.g. ``127.0.0.1:9001``
    :type bind_address: str

    :parameter ctx:
        An existing ZeroMQ context to use for the IO work.
        If `None` uses the default singleton instance.
    :type ctx: Optional[zmq.Context]
    """

    def __init__(self, bind_address: str,
                 ctx: Optional[Context] = None):
        self._ctx = ctx or Context.instance()
        self._socket = self._ctx.socket(PUB)
        self._socket.bind('tcp://' + bind_address)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    @staticmethod
    def _multipart_message(topic: str, line: str):
        return [
            topic.encode(encoding=_TOPIC_ENCODING, errors='ignore'),
            line.encode(encoding=_LINE_ENCODING, errors='ignore')
        ]

    def send(self, topic: str, line: str):
        """
        Broadcasts the given text line.

        :parameter topic:
            The topic association of the text line.
        :type topic: str

        :parameter line:
            The text line.
        :type line: str
        """
        data = self._multipart_message(topic, line.rstrip('\n\r'))
        self._socket.send_multipart(data)

    def close(self):
        self._socket.close()
        self._socket = None
        self._ctx = None


class Listener(object):
    """
    Subscribes to one or more ZeroMQ PUB sockets and listens to
    broadcasted log messages;
    passing log messages to a callback.

    :param addresses:
        A sequence of addresses to connect to.
        E.g. ``["127.0.0.1:9001", "192.168.10.20:9001"]``
    :type addresses: Sequence[str]

    :param handler:
        A function which is called every time a log message is received;
        this is called with `source`, `filename`, and `line` arguments.

        Alternatively an object with a method ``notify_line(source, filename, line)``
        and optionally the methods ``notify_watch(source, filename)`` and
        ``notify_unwatch(source, filename)``.
    :type handler: Union[Callable[[str, str, str], None], Any]

    :param watch_cb:
        A function which is called every time a file has joined the
        set of watched files;
        this is called with a `filename` argument.
    :type watch_cb: Optional[Callable[[str, str], None]]

    :param unwatch_cb:
        A function which is called every time a file has left the
        set of watched files;
        this is called with a `filename` argument.
    :type unwatch_cb: Optional[Callable[[str, str], None]]

    :param interval:
        The timeout in seconds when waiting for new messages
        before handling possible interruption.
    :type interval: float

    :parameter ctx:
        An existing ZeroMQ context to use for the IO work.
        If `None` uses the default singleton instance.
    :type ctx: Optional[zmq.Context]
    """

    def __init__(self, addresses: Sequence[str],
                 handler: Union[Callable[[str, str, str], None], Any],
                 watch_cb: Optional[Callable[[str, str], None]] = None,
                 unwatch_cb: Optional[Callable[[str, str], None]] = None,
                 interval: float = 0.1,
                 ctx: Optional[Context] = None):
        self._addresses = addresses
        if hasattr(handler, 'notify_line') and callable(getattr(handler, 'notify_line')):
            # treat handler as an object with notify_* methods
            self._line_cb = handler.notify_line
            self._watch = getattr(handler, 'notify_watch', watch_cb)
            self._unwatch = getattr(handler, 'notify_unwatch', unwatch_cb)
        else:
            # otherwise treat it as the handler function for lines
            self._line_cb = handler
            self._watch_cb = watch_cb
            self._unwatch_cb = unwatch_cb
        self._interval = interval
        self._ctx = ctx or Context.instance()
        self._socket = None

    def _handle_message(self, data):
        topic = data[0].decode(encoding=_TOPIC_ENCODING).split('|')
        msg_type = topic[1]
        if msg_type == 'line':
            source_name = topic[2]
            file_name = topic[3]
            text = data[1].decode(encoding=_LINE_ENCODING)
            self._line_cb(source_name, file_name, text)
        elif msg_type == 'watch':
            source_name = topic[2]
            file_name = topic[3]
            if callable(self._watch_cb):
                self._watch_cb(source_name, file_name)
        elif msg_type == 'unwatch':
            source_name = topic[2]
            file_name = topic[3]
            if callable(self._unwatch_cb):
                self._unwatch_cb(source_name, file_name)

    def listen(self):
        self._socket = self._ctx.socket(SUB)
        self._socket.setsockopt(SUBSCRIBE, 'log|'.encode(encoding=_TOPIC_ENCODING))
        for address in self._addresses:
            self._socket.connect('tcp://' + address)
        try:
            while not is_stopped():
                try:
                    data = self._socket.recv_multipart(flags=NOBLOCK)
                except ZMQError:
                    sleep(self._interval)
                else:
                    self._handle_message(data)
        finally:
            self._socket.close()
