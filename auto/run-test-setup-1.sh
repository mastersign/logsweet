#!/usr/bin/env bash

this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pdir=`dirname "$this_dir"`
cd "$this_dir"

rm test-1-*.log

xterm -title "Log Listen" -geometry 160x20 -e bash -c "cd \"$pdir\" && pipenv run python3 -m logsweet.cli listen 127.0.0.1:9501 127.0.0.1:9502" &
xterm -title "Log Broadcast A" -geometry 120x20 -e bash -c "cd \"$pdir\" && pipenv run python3 -m logsweet.cli broadcast -s -b 127.0.0.1:9501 \"$this_dir/test-1-a-*.log\"" &
xterm -title "Log Broadcast B" -geometry 120x20 -e bash -c "cd \"$pdir\" && pipenv run python3 -m logsweet.cli broadcast -s -b 127.0.0.1:9502 \"$this_dir/test-1-b-*.log\"" &

log_files="\"$this_dir/test-1-a-1.log\" \"$this_dir/test-1-a-2.log\" \"$this_dir/test-1-b-1.log\" \"$this_dir/test-1-b-2.log\""
xterm -title "Log Mock" -geometry 120x20 -e bash -c "cd \"$pdir\" && pipenv run python3 -m logsweet.cli mock -i 0.001 $log_files" &
