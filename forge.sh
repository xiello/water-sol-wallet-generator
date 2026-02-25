#!/bin/bash
cd ~/Documents/SolVanityCL
source .venv/bin/activate

if [ $# -eq 0 ]; then
    python3 start.py
else
    python3 dashboard.py "$@"
fi
