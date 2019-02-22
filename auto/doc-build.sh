#!/usr/bin/env bash

# Bash script for running command-doc-build in the pipenv

cd "$(dirname $0)/.."

function assert_command() {
    if ! which $1 >/dev/null 2>&1; then
        echo "The command '$1' was not found in PATH."
        exit 1
    fi
}

assert_command pipenv

exec pipenv run auto/command-doc-build.sh "$@"
