#!/bin/bash
set -e

echo "Detected dependency issues with apt."
echo "Installing Docker from static binaries (v27.3.1)..."

# 1. Download Static Binaries (ARM64 for Pi)
wget https://download.docker.com/linux/static/stable/aarch64/docker-27.3.1.tgz -O docker.tgz

# 2. Extract
echo "Extracting..."
tar xzvf docker.tgz

# 3. Move binaries to path
echo "Installing binaries to /usr/bin..."
sudo cp docker/* /usr/bin/

# 4. Create Group
echo "Configuring user permissions..."
sudo groupadd docker || true
sudo usermod -aG docker $USER

# 5. Create Systemd Service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/docker.service <<EOF
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network-online.target firewalld.service
Wants=network-online.target

[Service]
Type=notify
ExecStart=/usr/bin/dockerd
ExecReload=/bin/kill -s HUP \$MAINPID
LimitNOFILE=infinity
LimitNPROC=infinity
TimeoutStartSec=0
Delegate=yes
KillMode=process
Restart=on-failure
StartLimitBurst=3
StartLimitInterval=60s

[Install]
WantedBy=multi-user.target
EOF

# 6. Start Docker
echo "Starting Docker..."
sudo systemctl daemon-reload
sudo systemctl enable --now docker

# 7. Install Docker Compose Plugin (Static)
echo "Installing Docker Compose..."
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/download/v2.29.1/docker-compose-linux-aarch64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose

echo "------------------------------------------------"
echo "Done! Docker is installed."
echo "You MUST log out and log back in for group changes to take effect."
echo "After logging back in, try: docker ps"
