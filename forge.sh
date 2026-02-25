#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Missing .venv. Run: python3 -m venv .venv && source .venv/bin/activate && python3 -m pip install -r requirements.txt"
    exit 1
fi

source .venv/bin/activate

if [ $# -eq 0 ]; then
    python3 start.py
else
    python3 dashboard.py "$@"
fi
