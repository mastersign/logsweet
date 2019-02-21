@ECHO OFF
SETLOCAL
SET PYTHONPATH=%~dp0..;%PYTHONPATH%
python -m logsweet.cli %*
