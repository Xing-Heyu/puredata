#!/bin/bash

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           DataGen Pro - AI训练数据生成平台                  ║"
echo "║                    一键启动脚本                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

show_menu() {
    echo "请选择启动模式:"
    echo "  [1] 本地开发模式 (推荐首次使用)"
    echo "  [2] Docker容器模式 (生产环境)"
    echo "  [3] 安装依赖"
    echo "  [4] 停止服务"
    echo "  [5] 查看日志"
    echo "  [0] 退出"
    echo ""
    read -p "请输入选项 (0-5): " choice
    
    case $choice in
        1) local_mode ;;
        2) docker_mode ;;
        3) install_mode ;;
        4) stop_mode ;;
        5) log_mode ;;
        0) exit 0 ;;
        *) show_menu ;;
    esac
}

local_mode() {
    echo ""
    echo "[*] 正在启动本地开发服务器..."
    echo "[*] 访问地址: http://localhost:8000"
    echo "[*] 按 Ctrl+C 停止服务"
    echo ""
    cd backend
    python simple_main.py
}

docker_mode() {
    echo ""
    echo "[*] 正在启动Docker容器..."
    docker-compose up -d --build
    if [ $? -ne 0 ]; then
        echo "[!] Docker启动失败，请确保已安装Docker和Docker Compose"
        exit 1
    fi
    echo ""
    echo "[*] 服务已启动!"
    echo "[*] 前端地址: http://localhost"
    echo "[*] 后端地址: http://localhost:8000"
    echo "[*] API文档: http://localhost:8000/docs"
}

install_mode() {
    echo ""
    echo "[*] 正在安装Python依赖..."
    cd backend
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[!] 依赖安装失败"
        exit 1
    fi
    echo "[*] 依赖安装完成!"
}

stop_mode() {
    echo ""
    echo "[*] 正在停止服务..."
    docker-compose down 2>/dev/null
    pkill -f "python.*simple_main.py" 2>/dev/null
    echo "[*] 服务已停止"
}

log_mode() {
    echo ""
    echo "[*] 显示最近日志 (按Ctrl+C退出)..."
    docker-compose logs -f --tail=100
}

case "$1" in
    docker) docker_mode ;;
    install) install_mode ;;
    stop) stop_mode ;;
    *) show_menu ;;
esac
