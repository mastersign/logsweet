@ECHO OFF
SETLOCAL
PUSHD "%~dp0.."

:: CMD script to install all required and development packages in the projects pipenv

CALL:ASSERT_COMMAND pipenv
IF ERRORLEVEL 1 (
	CALL:PACKAGE_INSTALL_INFO pipenv Pipenv https://pypi.org/project/pipenv/
	GOTO:ERROR
)

IF NOT EXIST "Pipfile.lock" GOTO:PIPENV_LOCK

:PIPENV_SYNC
CALL pipenv sync --dev
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

:PIPENV_LOCK
CALL pipenv install -r requirements.txt --pre
SET STATUS=%ERRORLEVEL%
IF %STATUS% NEQ 0 GOTO:ERROR
CALL pipenv install --dev -r dev-requirements.txt
SET STATUS=%ERRORLEVEL%
IF %STATUS% NEQ 0 GOTO:ERROR ELSE GOTO:PIPENV_SYNC

:ASSERT_COMMAND
SET NAME=%1
WHERE %NAME% >NUL 2>&1
IF ERRORLEVEL 1 (
	ECHO.
	ECHO.The command '%NAME%' was not found in PATH.
	EXIT /B 1
)
GOTO:EOF

:PACKAGE_INSTALL_INFO
SET PACKAGE=%1
SET TITLE=%2
SET URL=%3
ECHO.
ECHO.Install %TITLE% with:
ECHO.
ECHO.pip install %PACKAGE%
ECHO.or
ECHO.pip install --user %PACKAGE%
ECHO.
ECHO.Or grab it from %URL%
GOTO:EOF
