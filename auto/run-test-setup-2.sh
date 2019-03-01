#!/usr/bin/env bash

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pdir=`dirname "$this_dir"`
cd "$this_dir"
rm test-2-*.log

xterm -title "Log Listen" -geometry 200x20 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli listen -b 127.0.0.1:9503" &

xterm -title "Log Watch A" -geometry 120x10 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli watch -c 127.0.0.1:9503 -cfg \"$this_dir/demo.yml\" \"$this_dir/test-2-a-*.log\"" &

xterm -title "Log Watch B" -geometry 120x10 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli watch -s -c 127.0.0.1:9503 \"$this_dir/test-2-b-*.log\"" &

log_files="\"$this_dir/test-2-a-1.log\" \"$this_dir/test-2-a-2.log\" \"$this_dir/test-2-b-1.log\" \"$this_dir/test-2-b-2.log\""
xterm -title "Log Mock" -geometry 120x10 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli mock -i 0.001 $log_files" &
