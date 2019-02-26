# _*_ coding: utf-8 _*_
"""
This module provides the CLI for the tool.
"""

import click
import socket
from .core import write_logfiles, watch_and_send, listen_and_print


@click.group(help='A suite with a variety of tools for handling log messages')
def main():
    pass


@main.command(help='Generate random log file entries')
@click.option('-i', '--interval', type=float, default=0.5,
              help='The interval for entry generation in seconds.')
@click.option('-n', '--max-lines', type=int, default=None,
              help='The number of log messages to generate.')
@click.argument('logfiles', nargs=-1)
def mock(logfiles, interval, max_lines):
    write_logfiles(logfiles, interval=interval, max_n=max_lines)


@main.command(help='Follow logfiles '
                   'and send new lines via ZeroMQ PUB and/or PUSH socket')
@click.option('-b', '--bind-address', type=str, default=None,
              help='IP and port to bind the ZeroMQ PUB socket.')
@click.option('-c', '--connect-address', type=str, multiple=True,
              help='Hostname(s) or IP(s) with port to connect the ZeroMQ PUSH socket.')
@click.option('-a', '--all-lines', is_flag=True,
              help='Broadcast all existing content before following.')
@click.option('-t', '--tail-lines', type=int, default=0,
              help='Number of tail lines to broadcast before following.')
@click.option('-e', '--encoding', type=str, default=None,
              help='Encoding for reading the text files.')
@click.option('-s', '--silent', is_flag=True,
              help='Do not print new lines to the console.')
@click.option('-n', '--name', type=str, default=None,
              help='The source name for the watched logs.')
@click.argument('file-glob')
def watch(file_glob, bind_address, connect_address,
          all_lines, tail_lines, encoding,
          name, silent):
    if bind_address is None and not connect_address:
        bind_address = '127.0.0.1:9000'
    watch_and_send(file_glob,
                   bind_address=bind_address,
                   connect_addresses=connect_address,
                   all_lines=all_lines,
                   tail_lines=tail_lines,
                   encoding=encoding,
                   name=name or socket.gethostname(),
                   silent=silent)


@main.command(help='Listen to text lines with ZeroMQ SUB and/or PULL socket')
@click.option('-b', '--bind-address', type=str, default=None,
              help='IP and port to bind the ZeroMQ PULL socket.')
@click.option('-c', '--connect-address', type=str, multiple=True,
              help='Hostname(s) or IP(s) with port to connect the ZeroMQ SUB socket.')
def listen(bind_address, connect_address):
    listen_and_print(bind_address=bind_address,
                     connect_addresses=connect_address)


# @main.command(help='Run a log proxy '
#                    'for watchers and listeners to connect to. '
#                    'Allowing listeners and watchers to come and go. '
#                    'Supporting a high availability architecture '
#                    'with multiple proxies.')
# @click.option('-b', '--backend-address', type=str, default='127.0.0.1:9001',
#               help='The IP and port to bind the PULL socket for the '
#                    'reception of log messages from watchers.')
# @click.option('-f', '--frontend-address', type=str, default='127.0.0.1:9002',
#               help='The IP and port to bind the XPUB socket for the '
#                    'broadcasting of log messages to listeners.')
# def proxy(backend_address, frontend_address):
#     pass


if __name__ == '__main__':
    main()
