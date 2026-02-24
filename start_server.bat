@echo off
chcp 65001 >nul
title PureData Server

echo ================================================
echo PureData 服务器
echo ================================================
echo.

cd /d "%~dp0platform\backend"

:restart
echo [%time%] 启动服务器...
python simple_main.py
if %errorlevel% neq 0 (
    echo [%time%] 服务器异常退出，5秒后重启...
    timeout /t 5 /nobreak >nul
    goto restart
)

echo [%time%] 服务器已停止
pause
