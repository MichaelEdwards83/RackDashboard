#!/bin/bash
# install_autostart.sh
# Sets up the dashboard to run automatically on boot (Desktop login)

# Ensure autostart directory exists
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

# Get absolute path to start.sh
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
START_SCRIPT="$SCRIPT_DIR/start.sh"

# Create the .desktop entry
echo "Creating autostart entry at $AUTOSTART_DIR/pidash.desktop..."

cat <<EOF > "$AUTOSTART_DIR/pidash.desktop"
[Desktop Entry]
Type=Application
Name=PiDash
Comment=Rack Temperature Dashboard
Exec=$START_SCRIPT
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

# Ensure start script is executable
chmod +x "$START_SCRIPT"

echo "✅ Autostart configured!"
echo "The dashboard should now launch automatically when the Desktop loads."
echo "Try it out: sudo reboot"
