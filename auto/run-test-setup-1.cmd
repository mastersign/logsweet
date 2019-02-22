@ECHO OFF
SETLOCAL
DEL "%~dp0*.log"

START "Log Listen" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	listen 127.0.0.1:9501 127.0.0.1:9502

START "Log Broadcast A" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	broadcast -s -b 127.0.0.1:9501 "%~dp0test-1-a-*.log"
START "Log Broadcast B" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	broadcast -s -b 127.0.0.1:9502 "%~dp0test-1-b-*.log"

START "Log Mock" /D "%~dp0.." pipenv run python -m logsweet.cli ^
	mock -i 0.001 ^
    "%~dp0test-1-a-1.log" "%~dp0test-1-a-2.log" "%~dp0test-1-b-1.log" "%~dp0test-1-b-2.log"
