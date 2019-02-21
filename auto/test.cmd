@ECHO OFF
SETLOCAL
PUSHD "%~dp0.."

:: CMD script for running test in the pipenv

CALL pipenv run "auto\command-test.cmd"
SET STATUS=%ERRORLEVEL%
IF %STATUS% NEQ 0 GOTO:ERROR

GOTO:END

:: PROCEDURES ::

:END
POPD
GOTO:EOF

:ERROR
POPD
PAUSE
EXIT /B %STATUS%
