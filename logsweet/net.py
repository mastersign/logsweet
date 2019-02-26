# -*- coding: utf-8 -*-

"""
This module contains functionality for transporting
log messages over the network.
"""

from typing import Any, Union, Optional, Callable, Sequence, Iterable
from zmq import Context, Poller, PUB, SUB, PUSH, PULL, SUBSCRIBE, NOBLOCK, POLLIN
from .signals import is_stopped

_TOPIC_ENCODING = 'UTF-8'
_LINE_ENCODING = 'UTF-8'


def _multipart_message(topic: str, line: str):
    return [
        topic.encode(encoding=_TOPIC_ENCODING, errors='ignore'),
        line.encode(encoding=_LINE_ENCODING, errors='ignore')
    ]


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
        data = _multipart_message(topic, line.rstrip('\n\r'))
        self._socket.send_multipart(data)

    def send_raw(self, data: Sequence[bytes]):
        """
        Broadcasts a raw multipart message.
        :param data:
            A raw multipart message.
        :type data: Sequence[bytes]
        """
        self._socket.send_multipart(data)

    def close(self):
        """
        Closes the ZeroMQ socket and releases allocated resources.
        """
        self._socket.close()
        self._socket = None
        self._ctx = None


class Transmitter(object):
    """
    A text line transmitter.

    :parameter connect_addresses:
        An iterable with addresses to connect the ZeroMQ PUSH socket to.
        E.g. ``["log-proxy-1.my-company.com:9001", "192.168.10.30:9001"]``
    :type connect_addresses: Iterable[str]

    :parameter ctx:
        An existing ZeroMQ context to use for the IO work.
        If `None` uses the default singleton instance.
    :type ctx: Optional[zmq.Context]
    """

    def __init__(self,
                 connect_addresses: Iterable[str],
                 ctx: Optional[Context] = None):
        self._ctx = ctx or Context.instance()
        self._socket = self._ctx.socket(PUSH)
        for address in connect_addresses:
            self._socket.connect('tcp://' + address)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def send(self, topic: str, line: str):
        """
        Transmits the given text line.

        :parameter topic:
            The topic association of the text line.
        :type topic: str

        :parameter line:
            The text line.
        :type line: str
        """
        data = _multipart_message(topic, line.rstrip('\n\r'))
        self._socket.send_multipart(data)

    def send_raw(self, data: Sequence[bytes]):
        """
        Transmits a raw multipart message.
        :param data:
            A raw multipart message.
        :type data: Sequence[bytes]
        """
        self._socket.send_multipart(data)

    def close(self):
        """
        Closes the ZeroMQ socket and releases allocated resources.
        """
        self._socket.close()
        self._socket = None
        self._ctx = None


class Listener(object):
    """
    Subscribes to one or more ZeroMQ PUB sockets,
    and/or waits for connections from ZeroMQ PUSH sockets;
    passing received log messages to a callback.

    :param handler:
        A function which is called every time a log message is received;
        this is called with `source`, `filename`, and `line` arguments.

        Alternatively an object with a method ``notify_line(source, filename, line)``
        and optionally the methods ``notify_watch(source, filename)`` and
        ``notify_unwatch(source, filename)``.
    :type handler: Optional[Union[Callable[[str, str, str], None], Any]]

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

    :param raw_cb:
        A function which is called on every received message.
        This is called with a sequence of `bytes`; the raw multi-message.
    type: raw_cb: Optional[Callable[[Sequence[bytes]], None]]

    :param bind_address:
        An IP and port to bind the ZeroMQ PULL socket to.
        E.g. ``127.0.0.1:9000``.
    :type bind_address: Optional[str]

    :param connect_addresses:
        An iterable of addresses to connect the ZeroMQ SUB socket to.
        E.g. ``["log-proxy-1.my-company.com:9001", "192.168.10.20:9001"]``
    :type connect_addresses: Optional[Iterable[str]]

    :param interval:
        The timeout in seconds when waiting for new messages
        before handling possible interruption.
    :type interval: float

    :parameter ctx:
        An existing ZeroMQ context to use for the IO work.
        If `None` uses the default singleton instance.
    :type ctx: Optional[zmq.Context]
    """

    def __init__(self,
                 handler: Optional[Union[Callable[[str, str, str], None], Any]] = None,
                 watch_cb: Optional[Callable[[str, str], None]] = None,
                 unwatch_cb: Optional[Callable[[str, str], None]] = None,
                 raw_cb: Optional[Callable[[Sequence[bytes]], None]] = None,
                 bind_address: Optional[str] = None,
                 connect_addresses: Optional[Iterable[str]] = None,
                 interval: float = 0.1,
                 ctx: Optional[Context] = None):
        self._bind_address = bind_address
        self._connect_addresses = list(connect_addresses)
        if handler \
                and hasattr(handler, 'notify_line') \
                and callable(getattr(handler, 'notify_line')):
            # treat handler as an object with notify_* methods
            self._line_cb = handler.notify_line
            self._watch = getattr(handler, 'notify_watch', watch_cb)
            self._unwatch = getattr(handler, 'notify_unwatch', unwatch_cb)
        else:
            # otherwise treat it as the handler function for lines
            self._line_cb = handler
            self._watch_cb = watch_cb
            self._unwatch_cb = unwatch_cb
        self._raw_cb = raw_cb
        self._interval = interval
        self._ctx = ctx or Context.instance()
        self._sub_socket = None
        self._pull_socket = None

    def _handle_message(self, data):
        if self._raw_cb:
            self._raw_cb(data)
        if self._line_cb is None \
                and self._watch_cb is None \
                and self._unwatch_cb is None:
            return
        topic = data[0].decode(encoding=_TOPIC_ENCODING).split('|')
        msg_type = topic[1]
        if msg_type == 'line':
            source_name = topic[2]
            file_name = topic[3]
            text = data[1].decode(encoding=_LINE_ENCODING)
            if callable(self._line_cb):
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

    def listen(self, topics: Iterable[str] = ("log|",)):
        """
        Listens to incoming log messages on the ZeroMQ socket(s).
        Blocks until `Ctrl + C` is pressed,
        or ``SIGINT`` or ``SIGTERM`` is received by the process.

        Returns immediately if either a bind address nor at least
        one connect address is set.

        :param topics:
            The topic to subscribe with.
            Can be used for selecting log messages from specific source.
            Defaults to ``["log|"]``.
        :type topics: Iterable[str]
        """
        if not self._bind_address and not self._connect_addresses:
            return
        poller = Poller()
        if self._bind_address:
            self._pull_socket = self._ctx.socket(PULL)
            self._pull_socket.bind('tcp://' + self._bind_address)
            poller.register(self._pull_socket, POLLIN)
        if self._connect_addresses:
            self._sub_socket = self._ctx.socket(SUB)
            for topic in topics:
                self._sub_socket.setsockopt(SUBSCRIBE, topic.encode(encoding=_TOPIC_ENCODING))
            for address in self._connect_addresses:
                self._sub_socket.connect('tcp://' + address)
            poller.register(self._sub_socket, POLLIN)
        try:
            while not is_stopped():
                events = dict(poller.poll(self._interval * 1000))
                if self._pull_socket in events and events[self._pull_socket] == POLLIN:
                    data = self._pull_socket.recv_multipart(flags=NOBLOCK)
                    self._handle_message(data)
                if self._sub_socket in events and events[self._sub_socket] == POLLIN:
                    data = self._sub_socket.recv_multipart(flags=NOBLOCK)
                    self._handle_message(data)
        finally:
            if self._pull_socket:
                self._pull_socket.close()
                self._pull_socket = None
            if self._sub_socket:
                self._sub_socket.close()
                self._sub_socket = None
