@ECHO OFF
SETLOCAL
DEL "%~dp0test-3-*.log"

START "Log Listen" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	listen -b 127.0.0.1:9504 -c 127.0.0.1:9505

START "Log Watch A" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	watch -s -c 127.0.0.1:9504 "%~dp0test-3-a-*.log"
START "Log Watch B" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	watch -s -b 127.0.0.1:9505 "%~dp0test-3-b-*.log"

START "Log Mock" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	mock -i 0.001 ^
    "%~dp0test-3-a-1.log" "%~dp0test-3-a-2.log" "%~dp0test-3-b-1.log" "%~dp0test-3-b-2.log"
