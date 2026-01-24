@echo off
title POS System Launcher
cd /d "%~dp0"
echo Starting POS System...
py main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Application crashed or could not start.
    pause
)
