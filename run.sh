#!/bin/bash

echo "========================================"
echo " Starting Telegram Auto Forward Bot"
echo "========================================"
echo

if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please run install.sh first and configure your credentials"
    exit 1
fi

mkdir -p sessions

echo "Starting bot..."
python3 main.py