#!/bin/bash
# fix_boot.sh

echo "1. Making start.sh executable..."
chmod +x scripts/start.sh
ls -l scripts/start.sh

echo "2. Configuring Autostart in wayfire.ini..."
CONFIG_FILE="$HOME/.config/wayfire.ini"

# Check if [autostart] exists
if grep -q "\[autostart\]" "$CONFIG_FILE"; then
    echo "[autostart] section exists."
else
    echo "Adding [autostart] section..."
    echo "" >> "$CONFIG_FILE"
    echo "[autostart]" >> "$CONFIG_FILE"
fi

# Check if our app entry exists
if grep -q "pidash =" "$CONFIG_FILE"; then
    echo "Entry for pidash already exists."
else
    echo "Adding pidash entry..."
    # Ensure it points to the absolute path of start.sh
    # Assuming user is always 'pidash' or we use $HOME
    echo "pidash = $HOME/Documents/pidash/scripts/start.sh" >> "$CONFIG_FILE"
fi

echo "--- Boot Repair Complete ---"
echo "Please verify content below:"
grep -A 2 "\[autostart\]" "$CONFIG_FILE"
