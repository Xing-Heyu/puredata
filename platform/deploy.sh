#!/bin/bash
# PureData 一键部署脚本

set -e

echo "=============================================="
echo "  PureData - AI训练数据生成平台 部署脚本"
echo "=============================================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装"
    exit 1
fi

echo "✅ Docker环境检查通过"

# 创建必要目录
mkdir -p backend/data backend/outputs backend/logs backend/cache
mkdir -p ssl

# 检查.env文件
if [ ! -f .env ]; then
    echo "📝 创建.env配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置API密钥"
fi

# 构建镜像
echo "🔨 构建Docker镜像..."
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 健康检查
if curl -f http://localhost:8000/health &> /dev/null; then
    echo ""
    echo "=============================================="
    echo "✅ 部署成功！"
    echo "=============================================="
    echo ""
    echo "前台地址: http://localhost:8000"
    echo "后台地址: http://localhost:8000/admin"
    echo "API文档:  http://localhost:8000/docs"
    echo ""
    echo "管理员账号启动时打印在控制台"
    echo ""
    echo "查看日志: docker-compose logs -f"
    echo "停止服务: docker-compose down"
    echo "=============================================="
else
    echo "❌ 服务启动失败，请检查日志"
    docker-compose logs
    exit 1
fi
