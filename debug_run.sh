#!/bin/bash
# Stop existing service
echo "Stopping existing python process..."
pkill -f "main.py" || true
pkill -f "uvicorn" || true

# Enter directory
cd "$(dirname "$0")/backend"

# Run main.py using python direct (not module) to see stdout
echo "Starting backend in debug mode..."

# Try to find and activate venv
if [ -f "../backend/venv/bin/activate" ]; then
    source ../backend/venv/bin/activate
    echo "Activated venv (backend/venv)"
elif [ -f "../.venv/bin/activate" ]; then
    source ../.venv/bin/activate
    echo "Activated .venv"
else
    echo "WARNING: No venv found. Running in system python."
fi

# Ensure dependencies are installed
pip install -r requirements.txt

export PYTHONPATH=$PYTHONPATH:.
python3 main.py
