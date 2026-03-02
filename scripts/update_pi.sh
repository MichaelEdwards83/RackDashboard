#!/bin/bash

# RackDashboard Update Script for Raspberry Pi
# Run this from the project root!

echo "🚀 Starting RackDashboard Update..."

# 1. Pull latest changes
echo "📥 Pulling latest changes from Git..."
git pull origin main

# 2. Update Backend
echo "🐍 Updating Backend dependencies..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "⚠️  Virtual environment not found. Please run scripts/setup_pi.sh first."
    exit 1
fi
cd ..

# 3. Update Frontend
echo "⚛️  Updating Frontend dependencies and building..."
cd frontend
if [ -d "node_modules" ]; then
    npm install
    npm run build
else
    echo "⚠️  Node modules not found. Please run scripts/setup_pi.sh first."
    exit 1
fi
cd ..

# 4. Restart Services
echo "🔄 Restarting RackDashboard services..."
sudo systemctl restart rack-dashboard.service

echo "✅ Update Complete! Your dashboard should be running the latest version."
echo "💡 Note: If time is still incorrect, ensure you have an active internet connection for auto-location."
