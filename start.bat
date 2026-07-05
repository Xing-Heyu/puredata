@echo off
chcp 65001 >nul
title PureData - AI Data Generation Platform

cls
echo.
echo ================================================================
echo          PureData - AI Data Generation Platform
echo                       v2.2.0
echo ================================================================
echo.
echo   Frontend: http://localhost:8000
echo   Backend:  http://localhost:8000/admin
echo   Account:  admin / PureData@2026
echo.
echo ================================================================
echo.

cd /d "%~dp0platform\backend"

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
