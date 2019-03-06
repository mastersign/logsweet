#!/usr/bin/env bash

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pdir=`dirname "$this_dir"`
cd "$this_dir"
rm test-6.log

xterm -title "Log Mock" -geometry 120x10 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli mock -i 0.01 \"$this_dir/test-6.log\"" &

xterm -title "Log Watch" -geometry 120x10 -e bash -c \
    "cd \"$pdir\" && pipenv run python3 -m logsweet.cli watch -s -b 127.0.0.1:9500 \"$this_dir/test-6.log\"" &

cd "$pdir"
exec pipenv run python3 -m logsweet.cli listen -c 127.0.0.1:9500 -cfg "$this_dir/demo.yml" -x
