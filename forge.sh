#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required."
    echo "Install Python 3 from https://www.python.org/downloads/mac-osx/ and run this again."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating local Python environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

if ! python3 -c "import base58, click, nacl, pyopencl, rich" >/dev/null 2>&1; then
    echo "Installing required Python packages..."
    python3 -m pip install --upgrade pip setuptools wheel
    python3 -m pip install -r requirements.txt
fi

if [ $# -eq 0 ]; then
    python3 start.py
else
    python3 dashboard.py "$@"
fi
