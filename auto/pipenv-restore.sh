#!/usr/bin/env bash

# Bash script to install all required and development packages in the projects pipenv

cd "$(dirname $0)/.."

function assert_command() {
    if ! which $1 >/dev/null 2>&1; then
        echo "The command '$1' was not found in PATH."
        exit 1
    fi
}

assert_command pipenv

if [[ -f Pipfile.lock ]]; then
    pipenv sync --dev
else
    pipenv install -r requirements.txt --pre
    if [[ $? -ne 0 ]]; then exit 1; fi
    pipenv install --dev -r dev-requirements.txt
fi
