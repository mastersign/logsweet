# -*- coding: utf-8 -*-

"""
This module contains the functionality to trigger actions
according to the match of regular expression.
"""

from typing import Any, Mapping, Tuple
import re
from string import Template
from requests_futures.sessions import FuturesSession


session = FuturesSession()


class HttpActionRule(object):
    """
    A rule for triggering a HTTP request when matching a text line,
    according to a regular expression.

    :param config:
        A dict like structure with the following keys:
        `pattern` with the regular expression,
        `url` with an URL to invoke,
        and `timeout` with a timeout in seconds,
        when to cancel the HTTP request.
    :type config: Mapping[str, Any]
    """

    def __init__(self, config: Mapping[str, Any]):
        try:
            self._pattern = re.compile(str(config.get('pattern')))
        except Exception as e:
            print('Error in regular expression: ', str(e))
            self._pattern = None
        self._url_template = Template(str(config.get('url')))
        try:
            self._timeout = float(config.get('timeout', 10.0))
        except Exception as e:
            print('Invalid timeout value: ', str(e))
            self._timeout = 10.0

    def _trigger(self, line, match):
        url = self._url_template.safe_substitute(**match.groupdict())
        session.get(url, timeout=self._timeout)

    def process(self, line: str) -> Tuple[bool, str]:
        """
        Process a line and trigger an HTTP request if this rule
        matches the given text line.

        :param line:
            The text line to process.
        :type line: str

        :return:
            A tuple with a boolean, stating if the pattern matched,
            and the text line.
        """
        match = self._pattern.search(line) if self._pattern else None
        if match:
            self._trigger(line, match)
            return True, line
        else:
            return False, line

    def __call__(self, line: str) -> Tuple[bool, str]:
        return self.process(line)
