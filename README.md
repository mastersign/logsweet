logsweet
========

>    A suite with a variety of tools for handling log messages.

The name `logsweet` is a word play by combining
`sweet logging` and a `suite of logging tools`.

## Installation

~~~
pip install logsweet
~~~

or

~~~
python ./setup.py install
~~~

## Usage

This is how you can use this tool.

~~~
Usage: logsweet [OPTIONS] COMMAND [ARGS]...

  A suite with a variety of tools for handling log messages

Options:
  --help  Show this message and exit.

Commands:
  broadcast  Follow logfiles and publish new lines via ZeroMQ PUB socket
  listen     Listen to text lines from ZeroMQ SUB sockets
  mock       Generate random log file entries
~~~

~~~
Usage: logsweet broadcast [OPTIONS] FILE_GLOB

  Follow logfiles and publish new lines via ZeroMQ PUB socket

Options:
  -b, --bind-address TEXT   IP and port to bind the ZeroMQ socket
  -a, --all-lines           Broadcast all existing content before following
  -t, --tail-lines INTEGER  Number of tail lines to broadcast before following
  -e, --encoding TEXT       Encoding for reading the text files.
  -s, --silent              Do not print new lines to the console.
  -n, --name TEXT           The source name for the watched logs.
  --help                    Show this message and exit.
~~~

~~~
Usage: logsweet listen [OPTIONS] [ADDRESSES]...

  Listen to text lines from ZeroMQ SUB sockets

Options:
  --help  Show this message and exit.
~~~

~~~
Usage: logsweet mock [OPTIONS] [LOGFILES]...

  Generate random log file entries

Options:
  -i, --interval FLOAT  The interval for entry generation in seconds.
  --help                Show this message and exit.
~~~