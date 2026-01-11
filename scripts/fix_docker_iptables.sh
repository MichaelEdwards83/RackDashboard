#!/bin/bash
set -e

echo "Configuring Docker to run WITHOUT iptables (workaround for missing iptables binary)..."

# 1. Create daemon.json
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<EOF
{
  "iptables": false
}
EOF

# 2. Restart Docker
echo "Restarting Docker service..."
sudo systemctl restart docker

# 3. Check status
echo "Checking Docker status..."
sudo systemctl status docker --no-pager

echo "------------------------------------------------"
echo "Docker Restarted. If 'Active: active (running)', you are good to go!"
