#!/bin/bash
set -e

echo "Installing Docker Compose plugin system-wide..."

# 1. Create system directory
sudo mkdir -p /usr/local/lib/docker/cli-plugins

# 2. Copy the plugin we already downloaded
if [ -f "$HOME/.docker/cli-plugins/docker-compose" ]; then
    echo "Found plugin in user directory, copying..."
    sudo cp "$HOME/.docker/cli-plugins/docker-compose" /usr/local/lib/docker/cli-plugins/
else
    echo "Redownloading plugin..."
    sudo curl -SL https://github.com/docker/compose/releases/download/v2.29.1/docker-compose-linux-aarch64 -o /usr/local/lib/docker/cli-plugins/docker-compose
fi

# 3. Make executable
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

echo "------------------------------------------------"
echo "Docker Compose installed."
echo "You can now run: sudo docker compose up -d"
