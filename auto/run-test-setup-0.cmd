@ECHO OFF
SETLOCAL
DEL "%~dp0test-0.log"

START "Log Watch" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    watch -s -b 127.0.0.1:9500 "%~dp0test-0.log"

START "Log Mock" /D "%~dp0.." pipenv run python -m logsweet.cli ^
    mock -i 0.1 "%~dp0test-0.log"

PUSHD "%~dp0.."
CALL pipenv run python -m logsweet.cli ^
    listen -c 127.0.0.1:9500 -cfg "%~dp0demo.yml"
POPD
