#!/bin/bash
# start.sh
# Starts the Backend and Frontend for the Server Rack Monitor

# Absolute path to app directory (edit if moved)
APP_DIR=$(dirname "$0")/..
cd "$APP_DIR"

echo "Starting Backend..."
cd backend
# Start FastAPI (using uvicorn)
# In production, you might want to run this as a systemd service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend (Kiosk)..."
cd ../frontend
# For dev/preview, we use 'vite preview' or 'npm run dev'
# Ideally build first: npm run build
npm run dev -- --host &
FRONTEND_PID=$!

# Wait for services to start
sleep 5

# Launch Chromium in Kiosk Mode pointing to the local frontend
# Note: Adjust port if needed
chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 "http://localhost:5173" &

# Trap cleanup
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

wait
