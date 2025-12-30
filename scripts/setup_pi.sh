#!/bin/bash
# setup_pi.sh
# Installs dependencies for Raspberry Pi 5

echo "Installing System Dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-venv nodejs npm git

# Try installing chromium (package name varies)
if ! sudo apt install -y chromium-browser; then
    echo "chromium-browser not found, trying 'chromium'..."
    sudo apt install -y chromium
fi

echo "Setting up Backend..."
cd ../backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Install RPi.GPIO and rpi_ws281x if on actual Pi
pip install rpi_ws281x adafruit-circuitpython-neopixel w1thermsensor

echo "Setting up Frontend..."
cd ../frontend
npm install
npm run build

echo "Configuring Boot Config (Prompts user)..."
echo "Remember to add 'dtoverlay=w1-gpio' to /boot/firmware/config.txt"
echo "Remember to configure your display settings in /boot/firmware/config.txt"

echo "Setup Complete!"
