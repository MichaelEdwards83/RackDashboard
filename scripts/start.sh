#!/bin/bash
# start.sh
# Starts the Backend and Frontend for the Server Rack Monitor

# Absolute path to app directory (edit if moved)
APP_DIR=$(dirname "$0")/..
cd "$APP_DIR"

# FORCE SCREEN ROTATION
if command -v wlr-randr &> /dev/null; then
    wlr-randr --output HDMI-A-2 --transform 90
fi

echo "Starting Backend..."
cd backend
# Activate venv!
source venv/bin/activate
# Start FastAPI (using uvicorn)
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend (Kiosk)..."
cd ../frontend
# For dev/preview, we use 'vite preview' or 'npm run dev'
# Ideally build first: npm run build
npm run dev -- --host &
FRONTEND_PID=$!

# Wait for Frontend to be ready (up to 30 seconds)
echo "Waiting for Frontend to launch..."
for i in {1..30}; do
    if curl -s http://localhost:5173 >/dev/null; then
        echo "Frontend is up!"
        break
    fi
    sleep 1
done

# Launch Chromium in Kiosk Mode pointing to the local frontend
# Note: Adjust port if needed
# try finding chromium executable (pi usually uses 'chromium-browser' or 'chromium')
if command -v chromium-browser &> /dev/null; then
    BROWSER="chromium-browser"
elif command -v chromium &> /dev/null; then
    BROWSER="chromium"
else
    echo "Chromium not found. Please install it."
    exit 1
fi

$BROWSER --password-store=basic --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 "http://localhost:5173" &

# Trap cleanup
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

wait
