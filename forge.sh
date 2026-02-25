#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate

if [ $# -eq 0 ]; then
    python3 start.py
else
    python3 dashboard.py "$@"
fi
