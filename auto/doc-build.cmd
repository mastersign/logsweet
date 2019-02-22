@ECHO OFF
SETLOCAL
PUSHD "%~dp0.."

:: CMD script for running command-doc-build in the pipenv

CALL pipenv run "auto\command-doc-build.cmd" html
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
