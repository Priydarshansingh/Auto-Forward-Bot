@echo off
title Telegram Auto Forward Bot

echo ========================================
echo  Starting Telegram Auto Forward Bot
echo ========================================
echo.

if not exist .env (
    echo ERROR: .env file not found!
    echo Please run install.bat first and configure your credentials
    pause
    exit /b 1
)

if not exist sessions mkdir sessions

echo Starting bot...
python main.py

echo.
echo Bot stopped. Press any key to exit...
pause >nul