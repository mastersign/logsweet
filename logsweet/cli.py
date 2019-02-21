# _*_ coding: utf-8 _*_
"""
This module provides the CLI for the tool.
"""

import click
import socket
from .core import write_logfiles, broadcast_lines, listen_to_lines


@click.group(help='A suite with a variety of tools for handling log messages')
def main():
    pass


@main.command(help='Generate random log file entries')
@click.option('-i', '--interval', type=float, default=0.5,
              help='The interval for entry generation in seconds.')
@click.argument('logfiles', nargs=-1)
def mock(logfiles, interval):
    write_logfiles(logfiles, interval)


@main.command(help='Follow logfiles '
                   'and publish new lines via ZeroMQ PUB socket')
@click.option('-b', '--bind-address', type=str, default='127.0.0.1:9000',
              help='IP and port to bind the ZeroMQ socket')
@click.option('-a', '--all-lines', is_flag=True,
              help='Broadcast all existing content before following')
@click.option('-t', '--tail-lines', type=int, default=0,
              help='Number of tail lines to broadcast before following')
@click.option('-e', '--encoding', type=str, default=None,
              help='Encoding for reading the text files.')
@click.option('-s', '--silent', is_flag=True,
              help='Do not print new lines to the console.')
@click.option('-n', '--name', type=str, default=None,
              help='The source name for the watched logs.')
@click.argument('file-glob')
def broadcast(file_glob, bind_address,
              all_lines, tail_lines, encoding,
              name, silent):
    broadcast_lines(bind_address, file_glob,
                    all_lines=all_lines,
                    tail_lines=tail_lines,
                    encoding=encoding,
                    name=name or socket.gethostname(),
                    silent=silent)


@main.command(help='Listen to text lines from ZeroMQ SUB sockets')
@click.argument('addresses', nargs=-1)
def listen(addresses):
    listen_to_lines(addresses)


if __name__ == '__main__':
    main()
