# -*- coding: utf-8 -*-

"""
Real-time text file watcher supporting log rotation.

| Based on: Log Watcher Python Recipe
| From: Giampaolo Rodolà
| Licensed under: MIT
| Source: ActiveState Code Recipe 577968_

.. _577968: https://github.com/ActiveState/code/tree/master/recipes/Python/577968_Log_watcher_tail_F_log/
"""

from typing import Any, Optional, Callable, Union, Sequence
import os
import time
import errno
import stat
import glob
import codecs
import locale
from .signals import is_stopped


class LogWatcher(object):
    """
    Looks for changes in all files matching a glob pattern.
    This is useful for watching log file changes in real-time.
    It also supports files rotation.

    :param file_glob:
        A Unix shell style globbing pattern for the files to watch.
    :type file_glob: str

    :param handler:
        A function which is called every time one of the files being
        watched is updated;
        this is called with `filename` and `lines` arguments.

        Alternatively an object with a method ``notify_lines(filename, lines)``
        and optionally the methods ``notify_watch(filename)`` and
        ``notify_unwatch(filename)``.
    :type handler: Union[Callable[[str, Sequence[str]], None], Any]

    :param watch_cb:
        A function which is called every time a file has joined the
        set of watched files;
        this is called with a `filename` argument.
    :type watch_cb: Optional[Callable[[str], None]]

    :param unwatch_cb:
        A function which is called every time a file has left the
        set of watched files;
        this is called with a `filename` argument.
    :type unwatch_cb: Optional[Callable[[str], None]]

    :param all_lines:
        Read all existing lines before starting to watch new lines.
        Ignores `tail_lines`.
    :type all_lines: bool

    :param tail_lines:
        Read last N lines from files being watched before starting.
    :type tail_lines: int

    :param chunk_size:
        An approximation of the maximum number of bytes to read from
        a file on every ieration (as opposed to load the entire
        file in memory until EOF is reached).
        Is passed to ``file.readlines()``.
        Defaults to 1MB.
    :type chunk_size: int

    :param encoding:
        The name of a character encoding to decode the text files.
        If `None` defaults to ``locale.getpreferredencoding()``.
    :type encoding: Optional[str]

    Example:

    ::

        def callback(filename, lines):
            for line in lines:
                print(filename, line)

        lw = LogWatcher("/var/log/*.log", callback)
        lw.watch()
    """

    def __init__(self, file_glob: str,
                 handler: Union[Callable[[str, Sequence[str]], None], Any],
                 watch_cb: Optional[Callable[[str], None]] = None,
                 unwatch_cb: Optional[Callable[[str], None]] = None,
                 all_lines: bool = False,
                 tail_lines: int = 0,
                 chunk_size: int = 1048576,
                 encoding: Optional[str] = None):
        self._file_glob = file_glob
        self._files_map = {}
        if hasattr(handler, 'notify_lines') and callable(getattr(handler, 'notify_lines')):
            # treat handler as an object with notify_* methods
            self._lines_cb = handler.notify_lines
            self._watch_cb = getattr(handler, 'notify_watch', watch_cb)
            self._unwatch_cb = getattr(handler, 'notify_unwatch', unwatch_cb)
        else:
            # otherwise treat it as the handler function for lines
            self._lines_cb = handler
            self._watch_cb = watch_cb
            self._unwatch_cb = unwatch_cb
        self._all_lines = all_lines
        self._tail_lines = tail_lines
        self._size_hint = chunk_size
        self._encoding = encoding
        self.verbose = False
        self._update_files()
        for _, file in self._files_map.items():
            if self._all_lines:
                self._read_lines(file)
            else:
                if self._tail_lines:
                    try:
                        lines = self._tail(file.name, self._tail_lines)
                    except IOError as err:
                        if err.errno != errno.ENOENT:
                            raise
                    else:
                        if lines:
                            self._lines_cb(file.name, lines)
                file.seek(os.path.getsize(file.name))  # EOF

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()

    def watch(self, interval: float = 0.1, blocking: bool = True):
        """
        Starts watching for new lines in matching files
        and for new or removed matching files.

        Blocks until `Ctrl + C` is pressed,
        or ``SIGINT`` or ``SIGTERM`` is received by the process.

        :param interval:
            The polling interval in seconds.
        :type interval: float
        :param blocking:
            If `True` is given, performs only one loop and then returns.
        :type blocking: bool
        """

        # May be overridden in order to use pyinotify lib and block
        # until the directory being watched is updated.

        # Note that directly calling _read_lines() as we do is faster
        # than first checking file's last modification times.
        while True:
            self._update_files()
            for fid, file in list(self._files_map.items()):
                self._read_lines(file)
            if not blocking or is_stopped():
                return
            time.sleep(interval)

    def _open(self, file):
        """
        Opens a file in text mode.
        """
        encoding = self._encoding or locale.getpreferredencoding()
        return codecs.open(file, 'r', encoding=encoding, errors='ignore')

    def _tail(self, file_name, line_number):
        """
        Read last N lines from file file_name.
        """
        if line_number < 0:
            raise ValueError("line_number must be greater or equal then 0")
        if line_number == 0:
            return []

        with self._open(file_name) as f:
            buffer_size = 1024
            # True if open() was overridden and file was opened in text
            # mode. In that case readlines() will return unicode strings
            # instead of bytes.
            encoded = getattr(f, 'encoding', False)
            nl = '\n' if encoded else b'\n'
            data = '' if encoded else b''
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            block = -1
            finished = False
            while not finished:
                step = (block * buffer_size)
                if abs(step) >= file_size:
                    f.seek(0)
                    new_data = f.read(buffer_size - (abs(step) - file_size))
                    finished = True
                else:
                    f.seek(step, os.SEEK_END)
                    new_data = f.read(buffer_size)
                data = new_data + data
                if data.count(nl) >= line_number:
                    break
                else:
                    block -= 1
            return data.splitlines()[-line_number:]

    def _check_existing_files(self):
        for fid, file in list(self._files_map.items()):
            try:
                st = os.stat(file.name)
            except EnvironmentError as err:
                if err.errno == errno.ENOENT:
                    self._unwatch(file, fid)
                else:
                    raise
            else:
                if fid != self._get_file_id(st):
                    # same name but different file (rotation); reload it.
                    self._unwatch(file, fid)
                    self._watch(file.name)

    def _find_new_files(self):
        ls = []
        for name in glob.iglob(self._file_glob):
            absname = os.path.realpath(name)
            try:
                st = os.stat(absname)
            except EnvironmentError as err:
                if err.errno != errno.ENOENT:
                    raise
            else:
                if not stat.S_ISREG(st.st_mode):
                    continue
                fid = self._get_file_id(st)
                ls.append((fid, absname))

        for fid, file_name in ls:
            if fid not in self._files_map:
                self._watch(file_name)

    def _update_files(self):
        self._check_existing_files()
        self._find_new_files()

    def _read_lines(self, file):
        """
        Read file lines since last access until EOF is reached and
        invoke callback.
        """
        while True:
            lines = file.readlines(self._size_hint)
            if not lines:
                break
            lines = list(map(lambda l: l.rstrip('\r\n'), lines))
            self._lines_cb(file.name, lines)

    def _watch(self, file_name):
        try:
            file = self._open(file_name)
            fid = self._get_file_id(os.stat(file_name))
        except EnvironmentError as err:
            if err.errno != errno.ENOENT:
                raise
        else:
            self._files_map[fid] = file
            if callable(self._watch_cb):
                self._watch_cb(file_name)

    def _unwatch(self, file, fid):
        # File no longer exists. If it has been renamed try to read it
        # for the last time in case we're dealing with a rotating log
        # file.
        del self._files_map[fid]
        file_name = file.name
        with file:
            self._read_lines(file)
        if callable(self._unwatch_cb):
            self._unwatch_cb(file_name)

    @staticmethod
    def _get_file_id(st):
        if os.name == 'posix':
            return "%xg%x" % (st.st_dev, st.st_ino)
        else:
            return "%f" % st.st_ctime

    def close(self):
        for _, file in self._files_map.items():
            file.close()
        self._files_map.clear()
