#!/bin/bash
# Stop existing service
echo "Stopping existing python process..."
pkill -f "main.py" || true
pkill -f "uvicorn" || true

# Enter directory
cd "$(dirname "$0")/backend"

# Run main.py using python direct (not module) to see stdout
echo "Starting backend in debug mode..."
export PYTHONPATH=$PYTHONPATH:.
python3 main.py
