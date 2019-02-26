@ECHO OFF
SETLOCAL
DEL "%~dp0test-2-*.log"

START "Log Listen" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	listen -b 127.0.0.1:9503

START "Log Watch A" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	watch -s -c 127.0.0.1:9503 "%~dp0test-2-a-*.log"
START "Log Watch B" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	watch -s -c 127.0.0.1:9503 "%~dp0test-2-b-*.log"

START "Log Mock" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	mock -i 0.001 ^
    "%~dp0test-2-a-1.log" "%~dp0test-2-a-2.log" "%~dp0test-2-b-1.log" "%~dp0test-2-b-2.log"
