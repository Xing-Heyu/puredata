@echo off
chcp 65001 >nul
title PureData

cls
echo ================================================
echo PureData 数据生成平台
echo ================================================
echo.
echo 访问: http://localhost:8000
echo 账号: admin / admin123
echo.
echo ================================================
echo.

cd /d "%~dp0platform\backend"
python simple_main.py

if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请检查错误信息
    pause
)
