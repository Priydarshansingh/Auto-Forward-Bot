#!/bin/bash

echo "========================================"
echo " Telegram Auto Forward Bot - Installer"
echo "========================================"
echo

echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from your package manager"
    exit 1
fi

echo "[2/4] Installing required packages..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi

echo "[3/4] Creating configuration file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Configuration file created: .env"
    echo "Please edit .env file with your credentials before running the bot"
else
    echo "Configuration file already exists: .env"
fi

echo "[4/4] Creating sessions directory..."
mkdir -p sessions

echo
echo "========================================"
echo " Installation Complete!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: python3 main.py"
echo
echo "For detailed setup guide, see: setup_guide.md"
echo