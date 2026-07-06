@echo off
chcp 65001 >nul
title PureData - AI Data Generation Platform

cls
echo.
echo ================================================================
echo          PureData - AI Training Data Generation Platform
echo                             v1.0.0
echo ================================================================
echo.
echo   Frontend: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo ================================================================
echo.

cd /d "%~dp0platform\backend"

echo [%time%] Checking dependencies...
python -c "import numpy, pandas, scipy, sklearn" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Missing dependencies. Installing...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Dependency installation failed. Check pip and network.
        pause
        exit /b 1
    )
)

echo [%time%] Starting server...
echo.

python simple_main.py

if %errorlevel% neq 0 (
    echo.
    echo ================================================================
    echo [ERROR] Startup failed, please check the error message
    echo ================================================================
    echo.
    pause
)
