@echo off
setlocal
title HacxGPT Installer

echo ======================================
echo     HacxGPT Installer for Windows
echo ======================================

:: Check for Git
echo [~] Checking for Git...
git --version >nul 2>nul
if errorlevel 1 (
    echo [!] Git is not installed or not in PATH.
    echo [!] Please install Git from https://git-scm.com/download/win and try again.
    pause
    exit /b 1
)
echo [+] Git found.

:: Check for Python
echo [~] Checking for Python...
python --version >nul 2>nul
if errorlevel 1 (
    echo [!] Python is not installed or not in PATH.
    echo [!] Please install Python from https://www.python.org/downloads/ and make sure to check "Add Python to PATH".
    pause
    exit /b 1
)
echo [+] Python found.

:: Clone the repository
if exist "Hacx-GPT" (
    echo [!] Hacx-GPT directory already exists. Skipping clone.
) else (
    echo [+] Cloning Hacx-GPT repository...
    git clone https://github.com/BlackTechX011/Hacx-GPT.git
    if errorlevel 1 (
        echo [!] Failed to clone the repository.
        exit /b 1
    )
)

cd /d Hacx-GPT
if errorlevel 1 (
    echo [!] Failed to enter the Hacx-GPT directory.
    exit /b 1
)

:: Install Python requirements
echo [+] Installing required python packages...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [!] Failed to install Python requirements.
    exit /b 1
)

echo.
echo ======================================
echo       Installation Complete!
echo ======================================
echo To run HacxGPT, run this command in this terminal:
echo.
echo python HacxGPT.py
echo.
echo Don't forget to get your API key from OpenRouter or DeepSeek!
echo ======================================
pause
exit /b 0
