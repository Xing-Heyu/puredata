# PureData - 云端部署指南

## 一、快速部署（Docker）

### 1. 准备服务器

| 配置 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核 |
| 内存 | 4GB | 8GB |
| 存储 | 50GB | 100GB SSD |
| 系统 | Ubuntu 20.04+ | Ubuntu 22.04 |

### 2. 安装Docker

```bash
# 安装Docker
curl -fsSL https://get.docker.com | bash

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 3. 部署应用

```bash
# 克隆项目
git clone <your-repo-url>
cd platform

# 配置环境变量
cp .env.example .env
nano .env  # 填写API密钥

# 一键部署
chmod +x deploy.sh
./deploy.sh
```

### 4. 访问服务

- 前台: http://your-server-ip:8000
- 后台: http://your-server-ip:8000/admin
- API: http://your-server-ip:8000/docs

---

## 二、生产环境部署

### 1. 启用Nginx反向代理

```bash
# 创建SSL目录
mkdir -p ssl

# 上传SSL证书
# ssl/cert.pem - 证书文件
# ssl/key.pem - 私钥文件

# 启动生产环境
docker-compose --profile production up -d
```

### 2. 配置域名

修改 `nginx.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 强制HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... 其他配置
}
```

### 3. 启用Redis缓存

```bash
docker-compose --profile cache up -d
```

---

## 三、云服务商部署

### 阿里云ECS

```bash
# 1. 购买ECS实例（推荐：2核4G，按量付费）
# 2. 安全组开放端口：8000、80、443
# 3. SSH连接后执行快速部署步骤
```

### 腾讯云CVM

```bash
# 同阿里云ECS步骤
```

### 华为云ECS

```bash
# 同阿里云ECS步骤
```

---

## 四、常用命令

```bash
# 查看日志
docker-compose logs -f datagen

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新部署
git pull
docker-compose build
docker-compose up -d

# 进入容器
docker exec -it puredata bash

# 备份数据
tar -czf backup_$(date +%Y%m%d).tar.gz backend/data backend/outputs
```

---

## 五、监控与维护

### 健康检查

```bash
curl http://localhost:8000/health
```

### 资源监控

```bash
docker stats puredata
```

### 日志轮转

在 `.env` 中配置：

```
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10
```

---

## 六、故障排查

### 服务无法启动

```bash
# 检查端口占用
netstat -tlnp | grep 8000

# 检查日志
docker-compose logs datagen

# 检查资源
df -h
free -m
```

### API调用失败

```bash
# 检查API密钥
docker exec -it puredata env | grep QWEN

# 测试API连接
docker exec -it puredata curl https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
```

---

## 七、安全建议

1. **修改默认密码**：首次登录后立即修改
2. **启用HTTPS**：生产环境必须
3. **配置防火墙**：只开放必要端口
4. **定期备份**：每天自动备份
5. **更新依赖**：定期更新安全补丁

### 生产环境必配环境变量

创建 `.env` 文件：

```bash
# 必须配置 - 安全相关
SECRET_KEY=your-random-secret-key-at-least-32-characters
PUREDATA_SECRET_KEY=another-random-key-for-encryption
DATAGEN_SECRET_KEY=third-key-for-data-encryption

# 必须配置 - API密钥
QWEN_API_KEY=sk-your-qwen-api-key

# 可选配置 - 会话超时
SESSION_TIMEOUT=3600

# 可选配置 - 日志级别
LOG_LEVEL=INFO
```

### 生成安全密钥

```bash
# 生成32位随机密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 防火墙配置

```bash
# Ubuntu UFW配置
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 性能优化

```bash
# 增加文件描述符限制
echo "* soft nofile 65535" >> /etc/security/limits.conf
echo "* hard nofile 65535" >> /etc/security/limits.conf

# 优化内核参数
cat >> /etc/sysctl.conf << EOF
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 1024
EOF
sysctl -p
```

---

## 八、成本估算

| 配置 | 云服务商 | 月成本 |
|------|----------|--------|
| 2核4G | 阿里云 | ¥100-150 |
| 2核4G | 腾讯云 | ¥80-120 |
| 4核8G | 阿里云 | ¥200-300 |
| 4核8G | 腾讯云 | ¥180-250 |

**API成本**：约 ¥0.0013/条数据
