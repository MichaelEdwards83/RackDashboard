# Raspberry Pi Sensor Dashboard (1920x480)

A high-performance, ultra-wide dashboard designed for Raspberry Pi 5. It monitors temperature sensors (DS18B20) and controls status LEDs (WS2812B) while displaying live weather and time.

![Dashboard Preview](frontend/public/vite.svg) *Note: Replace with actual screenshot*

## Hardware Requirements

- **Compute**: Raspberry Pi 5 (Preferred) or Pi 4.
- **Display**: 8.8" Ultrawide IPS Display (1920x480 resolution).
- **Sensors**: 5x DS18B20 Waterproof Temperature Sensors.
- **LEDs**: WS2812B LED Strip (Addressable).
- **Power**: 5V Power Supply adequate for Pi and LEDs.

## Features

- **Pixel-Perfect Layout**: Optimized specifically for 1920x480 resolution.
- **Real-Time Monitoring**: Live updates via WebSocket/Polling from Python backend.
- **Status Indicators**: LED strip changes color based on temperature thresholds (Green/Orange/Red).
- **Weather Integration**: Local weather updates via Open-Meteo API.
- **Mock Mode**: Can run on Mac/PC for development without hardware sensors.

## Installation

### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_folder>
```

### 2. Auto-Setup (Raspberry Pi)
The included script handles system dependencies, Python environment, and Node.js installation.
```bash
cd scripts
chmod +x setup_pi.sh
./setup_pi.sh
```

### 3. Manual Setup (Mac/PC Dev)
**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## Configuration

The system is controlled by `backend/config.json`.

- **Mock Mode**: Set `"mock_mode": true` to simulate sensors on non-Pi hardware.
- **Thresholds**: Adjust `warning` and `critical` temperature limits.
- **Location**: Set `auto: true` to detect location via IP, or hardcode latitude/longitude.

Example `config.json`:
```json
{
    "mock_mode": false,
    "temp_unit": "F",
    "temp_thresholds": {
        "global": { "warning": 80.0, "critical": 90.0 }
    },
    "location": { "auto": true }
}
```

## Running the Application

### Production (Pi)
Use the start script to launch both backend and frontend, and open Chromium in Kiosk mode.
```bash
./scripts/start.sh
```

### Development
**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev -- --host
```
Access at `http://localhost:5173`.

## Hardware Setup Notes

- **One-Wire Sensors**: Ensure `dtoverlay=w1-gpio` is added to your `/boot/firmware/config.txt`.
- **Display**: Ensure your `config.txt` forces the HDMI mode to 1920x480 if it's not detected automatically.
