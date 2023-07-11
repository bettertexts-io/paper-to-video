#!/bin/bash

# Check if pylint and python3 are installed
command -v black >/dev/null 2>&1 || { echo "black is required but it's not installed.  Aborting." >&2; exit 1; }
command -v pylint >/dev/null 2>&1 || { echo "pylint is required but it's not installed.  Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 is required but it's not installed.  Aborting." >&2; exit 1; }

if [ -z "$1" ]; then
    python3 app.py
else
    python3 $1
fi