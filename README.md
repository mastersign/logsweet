logsweet
========

>    A suite with a variety of tools for handling log messages.

The name _logsweet_ is a word play by combining
_sweet logging_ and a _suite of logging tools_.

## Requirements

* Python &ge;3.4

## Installation

### Python Package `logsweet`

~~~
pip install logsweet
~~~

or

~~~
python ./setup.py install
~~~

### Docker Image `mastersign/logsweet`

There is a public Docker image for *logsweet* available.

```sh
docker run --rm -it mastersign/logsweet [command] [OPTIONS] [ARGUMENTS]
```

Remember to mount log files as volumes into the container,
when using the `watch` or `mock` command.

## Usage

Logsweet supports the following commands:

* `watch` watches for new lines in text files (e.g. log files)
  and broadcasts them via a &empty;MQ PUB socket
  and/or sends them via a &empty;MQ PUSH socket.
* `listen` listens to new lines broadcasted via &empty;MQ PUB socket
  and/or collects new lines from &empty;MQ PUSH sockets
  and prints them on the console.
* `proxy` can connect to watchers at the backend
  and to listeners at the frontend.
  It supports both transmission modes (PUB/SUB and PUSH/PULL)
  at both backend and frontend.
  It can be used as a single point of knowledge
  or to build groups of log streams.
* `mock` to write random log messages to text files
  for testing purposes.

### One or more known services

At the service hosts `service-1` and `service-2` run:

```sh
logsweet watch -b *:9000 "/var/log/myservice/*.log"
```

To watch the two services:

```sh
logsweet listen -c service-1:9000 -c service-2:9000
```

### Use a proxy for dynamic services

First start the proxy on host `log-proxy`
to wait for backend connections from services on port 9001
and frontend connections from listeners on port 9002:

```sh
logsweet proxy -bb *:9001 -fb *:9002
```

Run one or more listeners to print the messages:

```sh
logsweet listen -c log-proxy:9002
```

Start one or more watchers to send log messages to the proxy:

```sh
logsweet watch -c log-proxy:9001 "/var/log/myservice/*.log"
```

### Use two proxies for high availability

First start two proxies on host `log-proxy-1` and `log-proxy-2`:

```sh
logsweet proxy -bb *:9001 -fb *:9002
```

Then start one or more listeners to print the messages:

```sh
logsweet listen -c log-proxy-1:9002 -c log-proxy-2:9002
```

Start one or more watchers to send log messages to the proxies:

```sh
logsweet watch -c log-proxy-1:9002 -c log-proxy-2:9002 "/var/log/myservice/*.log"
```

If multiple proxies are alive, the load is balanced evenly over all proxies.
If a proxy becomes unavailable, its load is automatically taken
by the remaining proxies.

### Write random log messages for testing

You can write random log messages to one or more log files
in order to test _logsweet_ and its usage scenarios:

```sh
logsweet mock -i 0.2 /var/log/test/1.log /var/log/test/2.log
```

Use the `-i` or `--interval` option to control the
interval for new log messages in seconds.

## Configuration

The commands `watch` and `listen` can process a YAML configuration file.
The configuration controls *filtering*, *coloring* output and
triggering *actions*.

For the command `watch` to print the text lines, the switch `--echo`
must be used.

A configuration file is specified with the `-cfg <yaml file>` option.
Here is an example:

```yaml
version: '0.1'

# The include statement is an array of regular expressions or a single one.
# A log messages is dropped if it does not match any of the expressions.
include:
  - 'error|Error|ERROR'
  - 'warning|Warning|WARNING'

# The exclude statement is an array of regular expressions or a single one.
# A log message is dropped if it matches any of the expressions.
exclude: 'ignore\s+this'

# The colors statement is an array of colorization rules.
# The rules are tried in the given order until one matches.
colors:
  # A colorization rule must have a pattern, which is a regular expression,
  # optionally with named groups.
  - pattern: '\[ERROR\]'
    # There are multiple color statements with the syntax of.
    # <foreground color> [on <background color>]
    # Every color is a color name from the X11 rgb.txt.
    # Spcifically the names supported by the Python package colorful
    # are supported.
    # The color names are Camel Case with a lower first letter.
    line: red  # line specifies a color for the whole line
    match: black on lightGrey # match specifies a color for the whole match

  - pattern: '^.*?(?P<level>\[[A-Z]+\]).*(?P<user>admin|user)'
    line: lightGrey
    match: white
    level: yellow
    user: cyan

# The actions statement is an array of action rules.
# The rules are all tried, regardless of matches.
# To execute actions from a watch or listen command,
# the switch -x or --exec-action must be used.
actions:
  # An action rule must have a pattern, which is a regular expression,
  # optionally with named groups.
  - pattern: '\[ERROR\] (?P<err>.*)$'
    # If the rule has an url property, it is considered an HTTP GET action.
    # The URL is treaded as a Python string template,
    # that means it can contain variables from the named regex groups.
    url: 'http://127.0.0.1:23456/notify-error/${err}'
    # A timeout in seconds can be specified,
    # to limit the amount of time used to execute the HTTP request.
    timeout: 2.5
```
