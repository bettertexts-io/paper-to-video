#!/bin/bash

# Check if pylint and python3 are installed
command -v black >/dev/null 2>&1 || { echo "black is required but it's not installed.  Aborting." >&2; exit 1; }
command -v pylint >/dev/null 2>&1 || { echo "pylint is required but it's not installed.  Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 is required but it's not installed.  Aborting." >&2; exit 1; }

isort src/*
black src/**.py
find . -type f -name "src/*.py" | xargs pylint
