@ECHO OFF
SETLOCAL
PUSHD "%~dp0.."

:: CMD script for running code quality checks, unit tests and doc tests

CALL:ASSERT_COMMAND flake8
IF ERRORLEVEL 1 (
	CALL:PACKAGE_INSTALL_INFO flake8 Flake8 https://gitlab.com/pycqa/flake8
	GOTO:ERROR
)

CALL:ASSERT_COMMAND sphinx-build
IF ERRORLEVEL 1 (
	CALL:PACKAGE_INSTALL_INFO sphinx Sphinx http://sphinx-doc.org/
	GOTO:ERROR
)

CALL:FLAKE8 --select=E901,E999,F821,F822,F823 --show-source --statistics
IF %STATUS% GEQ 1 GOTO:ERROR

CALL:FLAKE8 --max-complexity=10 --statistics
IF %STATUS% GEQ 1 GOTO:ERROR

CALL:UNITTEST discover
IF %STATUS% GEQ 1 GOTO:ERROR

CALL:DOCTEST
IF %STATUS% GEQ 1 GOTO:ERROR

GOTO:END

:: PROCEDURES ::

:END
POPD
GOTO:EOF

:ERROR
POPD
EXIT /B 1

:FLAKE8
ECHO.
ECHO.Checking Code Style
ECHO.======================================================================
ECHO.%*
ECHO.
CALL flake8 . %*
SET STATUS=%ERRORLEVEL%
IF %STATUS% == 0 ECHO.OK
IF %STATUS% GEQ 1 EXIT /B %STATUS%
GOTO:EOF

:UNITTEST
ECHO.
ECHO.Running Unit Tests
ECHO.======================================================================
ECHO.
CALL python -m unittest %*
SET STATUS=%ERRORLEVEL%
IF %STATUS% GEQ 1 EXIT /B %STATUS%
GOTO:EOF

:DOCTEST
ECHO.
ECHO.Running Doc Tests
ECHO.======================================================================
ECHO.
PUSHD doc
CALL sphinx-build -M doctest source build %SPHINXOPTS%
SET STATUS=%ERRORLEVEL%
POPD
IF %STATUS% == 0 ECHO.OK
IF %STATUS% GEQ 1 EXIT /B %STATUS%
GOTO:EOF

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
