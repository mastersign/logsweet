logsweet
========

>    A suite with a variety of tools for handling log messages.

The name _logsweet_ is a word play by combining
_sweet logging_ and a _suite of logging tools_.

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
  listen  Listen to text lines with ZeroMQ SUB and/or PULL socket
  mock    Generate random log file entries
  watch   Follow logfiles and send new lines via ZeroMQ PUB and/or PUSH...
~~~

~~~
Usage: logsweet listen [OPTIONS]

  Listen to text lines with ZeroMQ SUB and/or PULL socket

Options:
  -b, --bind-address TEXT     IP and port to bind the ZeroMQ PULL socket.
  -c, --connect-address TEXT  Hostname(s) or IP(s) with port to connect the
                              ZeroMQ SUB socket.
  --help                      Show this message and exit.
~~~

~~~
Usage: logsweet mock [OPTIONS] [LOGFILES]...

  Generate random log file entries

Options:
  -i, --interval FLOAT     The interval for entry generation in seconds.
  -n, --max-lines INTEGER  The number of log messages to generate.
  --help                   Show this message and exit.
~~~

~~~
Usage: logsweet watch [OPTIONS] FILE_GLOB

  Follow logfiles and send new lines via ZeroMQ PUB and/or PUSH socket

Options:
  -b, --bind-address TEXT     IP and port to bind the ZeroMQ PUB socket.
  -c, --connect-address TEXT  Hostname(s) or IP(s) with port to connect the
                              ZeroMQ PUSH socket.
  -a, --all-lines             Broadcast all existing content before following.
  -t, --tail-lines INTEGER    Number of tail lines to broadcast before
                              following.
  -e, --encoding TEXT         Encoding for reading the text files.
  -s, --silent                Do not print new lines to the console.
  -n, --name TEXT             The source name for the watched logs.
  --help                      Show this message and exit.
~~~
