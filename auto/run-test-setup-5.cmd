@ECHO OFF
SETLOCAL
DEL "%~dp0test-5-*.log"

START "Log Proxy" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    proxy -bc 127.0.0.1:9508 -bc 127.0.0.1:9509 ^
          -fc 127.0.0.1:9510 -fc 127.0.0.1:9511

START "Log Listen A" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    listen -b 127.0.0.1:9510
START "Log Listen B" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    listen -b 127.0.0.1:9511

START "Log Watch A" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    watch -b 127.0.0.1:9508 "%~dp0test-5-a-*.log"
START "Log Watch B" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    watch -b 127.0.0.1:9509 "%~dp0test-5-b-*.log"

START "Log Mock" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    mock -i 0.001 ^
    "%~dp0test-5-a-1.log" "%~dp0test-5-a-2.log" "%~dp0test-5-b-1.log" "%~dp0test-5-b-2.log"
