@ECHO OFF
SETLOCAL
DEL "%~dp0test-4-*.log"

START "Log Proxy" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    proxy -bb 127.0.0.1:9506 -fb 127.0.0.1:9507

START "Log Listen A" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    listen -c 127.0.0.1:9507
START "Log Listen B" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    listen -c 127.0.0.1:9507

START "Log Watch A" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    watch -c 127.0.0.1:9506 "%~dp0test-4-a-*.log"
START "Log Watch B" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    watch -c 127.0.0.1:9506 "%~dp0test-4-b-*.log"

START "Log Mock" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    mock -i 0.001 ^
    "%~dp0test-4-a-1.log" "%~dp0test-4-a-2.log" "%~dp0test-4-b-1.log" "%~dp0test-4-b-2.log"
