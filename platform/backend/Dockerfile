# DataGen Pro - Dockerfile
# 多阶段构建，优化镜像大小

# 阶段1：基础镜像
FROM python:3.10-slim as base

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 阶段2：运行镜像
FROM python:3.10-slim

WORKDIR /app

# 从基础镜像复制依赖
COPY --from=base /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/output

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "simple_main.py"]
