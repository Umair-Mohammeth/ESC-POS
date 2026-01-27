@echo off
title POS System Launcher
cd /d "%~dp0"

echo Checking and installing dependencies...
if exist requirements.txt (
    py -m pip install -r requirements.txt --quiet
)

echo Starting POS System...
py main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Application crashed or could not start.
    pause
)
