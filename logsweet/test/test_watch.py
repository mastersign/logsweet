# -*- coding: utf-8 -*-
from unittest import TestCase
import atexit
import os
import locale
from ..watch import LogWatcher

TESTFN = '$testfile.log'
TESTFN2 = '$testfile2.log'


class TestLogWatcher(TestCase):

    def setUp(self):
        def callback(filename, lines):
            self.filename.append(filename)
            for line in lines:
                self.lines.append(line)

        self.filename = []
        self.lines = []
        self.file = open(TESTFN, 'w', encoding=locale.getpreferredencoding())
        self.watcher = LogWatcher('./*', callback)

    def tearDown(self):
        self.watcher.close()
        self.file.close()
        self.remove_test_files()

    def write_file(self, data):
        self.file.write(data)
        self.file.flush()

    @staticmethod
    @atexit.register
    def remove_test_files():
        for x in [TESTFN, TESTFN2]:
            try:
                os.remove(x)
            except EnvironmentError:
                pass

    def test_no_lines(self):
        self.watcher.watch(blocking=False)

    def test_one_line(self):
        self.write_file('foo')
        self.watcher.watch(blocking=False)
        self.assertEqual(self.lines, ["foo"])
        self.assertEqual(self.filename, [os.path.abspath(TESTFN)])

    def test_two_lines(self):
        self.write_file('foo\n')
        self.write_file('bar\n')
        self.watcher.watch(blocking=False)
        self.assertEqual(self.lines, ["foo", "bar"])
        self.assertEqual(self.filename, [os.path.abspath(TESTFN)])

    def test_new_file(self):
        with open(TESTFN2, "w") as f:
            f.write("foo")
        self.watcher.watch(blocking=False)
        self.assertEqual(self.lines, ["foo"])
        self.assertEqual(self.filename, [os.path.abspath(TESTFN2)])

    def test_file_removed(self):
        self.write_file("foo")
        try:
            os.remove(TESTFN)
        except EnvironmentError:  # necessary on Windows
            pass
        self.watcher.watch(blocking=False)
        self.assertEqual(self.lines, ["foo"])

    def test_tail(self):
        MAX = 10000
        content = '\n'.join([str(x) for x in range(0, MAX)])
        self.write_file(content)
        # no lines
        lines = self.watcher._tail(self.file.name, 0)
        self.assertEqual(len(lines), 0)
        # input < BUFSIZ (1 iteration)
        lines = self.watcher._tail(self.file.name, 100)
        self.assertEqual(len(lines), 100)
        self.assertEqual(lines, [str(x) for x in range(MAX - 100, MAX)])
        # input > BUFSIZ (multiple iterations)
        lines = self.watcher._tail(self.file.name, 5000)
        self.assertEqual(len(lines), 5000)
        self.assertEqual(lines, [str(x) for x in range(MAX - 5000, MAX)])
        # input > file's total lines
        lines = self.watcher._tail(self.file.name, MAX + 9999)
        self.assertEqual(len(lines), MAX)
        self.assertEqual(lines, [str(x) for x in range(0, MAX)])
        #
        self.assertRaises(ValueError, self.watcher._tail, self.file.name, -1)
        self.watcher._tail(self.file.name, 10)

    def test_ctx_manager(self):
        with self.watcher:
            pass
