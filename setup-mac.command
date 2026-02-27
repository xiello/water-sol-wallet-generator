#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required."
    echo "Install Python 3 from https://www.python.org/downloads/mac-osx/"
    exit 1
fi

echo "Setting up the project..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt

echo
echo "Setup complete."
echo "Next step:"
echo "  - Double-click start.command"
echo "  - Or run: npm start"
