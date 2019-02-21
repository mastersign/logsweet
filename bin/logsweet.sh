#!/usr/bin/env bash
APP_ROOT="$(dirname "$(dirname "$(readlink -fm "$0")")")"
export PYTHONPATH="${APP_ROOT}:${PYTHONPATH}"
exec python3 -m logsweet.cli "$@"
