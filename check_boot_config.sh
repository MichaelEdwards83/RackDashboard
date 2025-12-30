#!/bin/bash
# check_boot_config.sh
echo "--- scripts/start.sh permissions ---"
ls -l ~/Documents/pidash/scripts/start.sh

echo "--- ~/.config/wayfire.ini [autostart] section ---"
if [ -f ~/.config/wayfire.ini ]; then
    grep -A 5 "\[autostart\]" ~/.config/wayfire.ini
else
    echo "wayfire.ini not found"
fi

echo "--- ~/.config/autostart contents ---"
ls -la ~/.config/autostart/ 2>/dev/null
