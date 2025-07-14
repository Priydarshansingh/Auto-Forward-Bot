@echo off
echo ========================================
echo  Telegram Auto Forward Bot - Installer
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [2/4] Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo [3/4] Creating configuration file...
if not exist .env (
    copy .env.example .env
    echo Configuration file created: .env
    echo Please edit .env file with your credentials before running the bot
) else (
    echo Configuration file already exists: .env
)

echo [4/4] Creating sessions directory...
if not exist sessions mkdir sessions

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your credentials
echo 2. Run: python main.py
echo.
echo For detailed setup guide, see: setup_guide.md
echo.
pause