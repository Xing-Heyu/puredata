#!/bin/bash

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           PureData - AI训练数据生成平台                     ║"
echo "║                云端部署启动脚本                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend"
LOG_DIR="${SCRIPT_DIR}/logs"
PID_FILE="${SCRIPT_DIR}/server.pid"

mkdir -p "$LOG_DIR"

get_public_ip() {
    local ip=""
    ip=$(curl -s --connect-timeout 5 ifconfig.me 2>/dev/null)
    if [ -z "$ip" ]; then
        ip=$(curl -s --connect-timeout 5 ipinfo.io/ip 2>/dev/null)
    fi
    if [ -z "$ip" ]; then
        ip=$(curl -s --connect-timeout 5 icanhazip.com 2>/dev/null)
    fi
    echo "$ip"
}

check_port() {
    if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
        return 0
    fi
    if ss -tlnp 2>/dev/null | grep -q ":8000 "; then
        return 0
    fi
    return 1
}

check_dependencies() {
    echo "[*] 检查依赖..."
    
    if ! command -v python3 &> /dev/null; then
        echo "[!] 未安装Python3，正在安装..."
        apt-get update && apt-get install -y python3 python3-pip
    fi
    
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        echo "[*] 安装Python依赖..."
        pip3 install -r "$BACKEND_DIR/requirements.txt" -q
    fi
    
    echo "[✓] 依赖检查完成"
}

start_server() {
    echo ""
    echo "[*] 正在启动服务器..."
    
    if check_port; then
        echo "[!] 端口8000已被占用"
        echo "[*] 尝试停止旧服务..."
        stop_server
        sleep 2
    fi
    
    cd "$BACKEND_DIR"
    
    PUBLIC_IP=$(get_public_ip)
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  服务已启动!"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  本地访问:  http://localhost:8000"
    if [ -n "$PUBLIC_IP" ]; then
        echo "  外网访问:  http://$PUBLIC_IP:8000"
        echo "  管理后台:  http://$PUBLIC_IP:8000/admin.html"
        echo "  API文档:   http://$PUBLIC_IP:8000/docs"
    fi
    echo ""
    echo "  日志文件:  $LOG_DIR/server.log"
    echo "  停止服务:  bash $0 stop"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    nohup python3 simple_main.py > "$LOG_DIR/server.log" 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 2
    
    if check_port; then
        echo "[✓] 服务启动成功!"
    else
        echo "[!] 服务启动失败，请检查日志: $LOG_DIR/server.log"
    fi
}

stop_server() {
    echo ""
    echo "[*] 正在停止服务..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "[✓] 服务已停止 (PID: $PID)"
        fi
        rm -f "$PID_FILE"
    fi
    
    pkill -f "python.*simple_main.py" 2>/dev/null
    
    echo "[✓] 停止完成"
}

restart_server() {
    stop_server
    sleep 2
    start_server
}

view_logs() {
    echo ""
    echo "[*] 显示日志 (按Ctrl+C退出)..."
    echo ""
    tail -f "$LOG_DIR/server.log"
}

check_status() {
    echo ""
    echo "[*] 服务状态:"
    echo ""
    
    if check_port; then
        echo "  状态: 运行中 ✓"
        if [ -f "$PID_FILE" ]; then
            echo "  PID:  $(cat $PID_FILE)"
        fi
    else
        echo "  状态: 未运行 ✗"
    fi
    
    echo ""
    echo "  端口监听:"
    netstat -tlnp 2>/dev/null | grep ":8000" || ss -tlnp 2>/dev/null | grep ":8000" || echo "  无"
    echo ""
}

show_help() {
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    查看状态"
    echo "  logs      查看日志"
    echo "  install   安装依赖"
    echo "  help      显示帮助"
    echo ""
}

case "$1" in
    start)
        check_dependencies
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    install)
        check_dependencies
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac
