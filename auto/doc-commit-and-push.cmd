@ECHO OFF
SETLOCAL

:: CMD script for commiting unstaged changes in Sphinx documentation HTML output
:: and pushing subtree to Git branch gh-pages

SET GITHUB_REMOTE=origin
SET DOCS_PATH=doc/build/html
PUSHD "%~dp0.."

CALL:ASSERT_COMMAND git
IF ERRORLEVEL 1 GOTO:ERROR

CALL git diff --exit-code --cached 2>&1 >NUL
IF %ERRORLEVEL% NEQ 0 (
	ECHO.There are files staged but not commited. Cancelling.
	GOTO:ERROR
)

CALL git add "%DOCS_PATH%"
IF %ERRORLEVEL% NEQ 0 (
	ECHO.Staging changed docs failed. Cancelling.
	GOTO:ERROR
)

CALL git commit -m "updated docs"
IF %ERRORLEVEL% NEQ 0 (
	ECHO.Committing changed docs failed. Cancelling.
	GOTO:ERROR
)

CALL git fetch %GITHUB_REMOTE% gh-pages
IF %ERRORLEVEL% NEQ 0 GOTO:INITIALIZE_SUBTREE

CALL git subtree split --prefix "%DOCS_PATH%" --onto %GITHUB_REMOTE%/gh-pages > gh-pages-ref.txt
IF %ERRORLEVEL% NEQ 0 (
	ECHO.Updating subtree reference failed. Cancelling.
	GOTO:ERROR
)
SET /P gh_pages_ref=<gh-pages-ref.txt
DEL gh-pages-ref.txt

CALL git push %GITHUB_REMOTE% %gh_pages_ref%:gh-pages
IF %ERRORLEVEL% NEQ 0 (
	ECHO.Pushing changed docs to branch gh-pages failed.
	GOTO:ERROR
)

GOTO:END

:: PROCEDURES ::

:END
POPD
GOTO:EOF

:ERROR
POPD
PAUSE
EXIT /B 1

:INITIALIZE_SUBTREE
CALL git subtree push --prefix "%DOCS_PATH%" %GITHUB_REMOTE% gh-pages
IF %ERRORLEVEL% NEQ 0 (
	ECHO.Creating subtree reference failed. Cancelling.
	GOTO:ERROR
)
GOTO:END

:ASSERT_COMMAND
SET NAME=%1
WHERE %NAME% >NUL 2>&1
IF ERRORLEVEL 1 (
	ECHO.
	ECHO.The command '%NAME%' was not found in PATH.
	EXIT /B 1
)
GOTO:EOF