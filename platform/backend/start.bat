@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo PureData 服务器启动
echo ========================================
echo.
echo 正在启动服务器...
echo.

:: 启动服务器（在新窗口中）
start "PureData Server" python simple_main.py

:: 等待服务器启动
echo 等待服务器启动...
timeout /t 3 /nobreak >nul

:: 自动打开浏览器
echo 正在打开浏览器...
start http://localhost:8000/

echo.
echo ========================================
echo 服务器已启动！
echo 前台: http://localhost:8000/
echo 后台: http://localhost:8000/admin
echo ========================================
echo.
echo 按任意键关闭此窗口（服务器将继续运行）
pause >nul
