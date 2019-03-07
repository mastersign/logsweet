#!/usr/bin/env bash

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pdir=`dirname "$this_dir"`
cd "$this_dir"
rm test-5-*.log

xterm -title "Log Proxy" -geometry 120x10 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli proxy -bc 127.0.0.1:9508 -bc 127.0.0.1:9509 -fc 127.0.0.1:9510 -fc 127.0.0.1:9511" &

xterm -title "Log Listen A" -geometry 200x20 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli listen -b 127.0.0.1:9510" &

xterm -title "Log Listen B" -geometry 200x20 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli listen -b 127.0.0.1:9511" &

xterm -title "Log Watch A" -geometry 120x10 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli watch -b 127.0.0.1:9508 \"$this_dir/test-5-a-*.log\"" &

xterm -title "Log Watch B" -geometry 120x10 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli watch -b 127.0.0.1:9509 \"$this_dir/test-5-b-*.log\"" &

log_files="\"$this_dir/test-5-a-1.log\" \"$this_dir/test-5-a-2.log\" \"$this_dir/test-5-b-1.log\" \"$this_dir/test-5-b-2.log\""
xterm -title "Log Mock" -geometry 120x10 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli mock -i 0.001 $log_files" &
