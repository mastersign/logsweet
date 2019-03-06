#!/usr/bin/env bash

# Bash script for running code quality checks, unit tests and doc tests

cd "$(dirname $0)/.."

function assert_python_cli() {
    command="$1"
    package="$2"
    title="$3"
    url="$4"
    if ! which $1 >/dev/null 2>&1; then
        echo "The command '$command' was not found in PATH."
        echo ""
        echo "Install $title with:"
        echo ""
        echo "pip3 install --user $package"
        echo ""
        echo "Or grab it from $url"
        exit 1
    fi
}

function run_flake8() {
    echo ""
    echo "Checking Code Style"
    echo "======================================================================"
    echo "$@"
    echo ""
    flake8 . $@
    if [ $? -ne 0 ]; then
        exit 1
    else
        echo "OK"
    fi
}

function run_unittests() {
    echo ""
    echo "Running Unit Tests"
    echo "======================================================================"
    echo ""
    python3 -m unittest $@
    if [ $? -ne 0 ]; then exit 1; fi
}

function run_doctests() {
    echo ""
    echo "Running Doc Tests"
    echo "======================================================================"
    echo ""
    pushd doc >/dev/null
    sphinx-build -M doctest source build $SPHINXOPTS
    if [ $? -ne 0 ]; then
        exit 1
    else
        echo ""
        echo "OK"
    fi
    popd >/dev/null
}

assert_python_cli flake8 flake8 Flake8 https://gitlab.com/pycqa/flake8
assert_python_cli sphinx-build sphinx Sphinx http://sphinx-doc.org/

run_flake8 --select=E901,E999,F821,F822,F823 --show-source --statistics
run_unittests discover
run_doctests
