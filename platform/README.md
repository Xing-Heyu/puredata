# PureData - AI训练数据生成平台

## 项目简介

PureData 是一款专业的 AI 训练数据生成平台，支持多领域高质量数据生成。

### 核心功能

- **多领域数据生成**：人工智能、劳动合同、医疗、金融
- **质量门控系统**：高质量(≥0.85)、免费试用(0.80-0.85)、普通质量(0.75-0.80)、鲁棒性(<0.75)
- **智能去重**：MinHash 近似去重
- **数据血缘追溯**：完整的数据来源追踪
- **异常检测**：自动检测和修复数据异常
- **多样性增强**：基于学术界前沿方法

---

## 环境要求

| 项目 | 要求 |
|-----|------|
| Python | 3.8 - 3.11 |
| 内存 | ≥ 2GB |
| 磁盘 | ≥ 1GB |
| 系统 | Linux (Ubuntu 22.04) / Windows / macOS |

---

## 快速部署

### 1. 克隆项目

```bash
cd /root/project/
git clone <your-repo-url> puredata
cd puredata/platform
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r backend/requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填写必要配置
```

### 5. 创建必要目录

```bash
mkdir -p logs data/cache outputs backups
```

### 6. 启动服务

```bash
# Linux
bash start.sh start

# Windows
start.bat

# 或直接运行
cd backend
python start_server.py
```

### 7. 访问服务

- 前端页面：http://localhost:8000
- API文档：http://localhost:8000/docs
- 管理后台：http://localhost:8000/admin.html

---

## Docker 部署

```bash
# 构建镜像
docker build -t puredata:latest .

# 运行容器
docker run -d -p 8000:8000 --name puredata puredata:latest

# 或使用 docker-compose
docker-compose up -d
```

---

## 测试验证

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

### 2. 测试数据生成

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"domain": "人工智能", "count": 10}'
```

### 3. 运行测试脚本

```bash
cd backend
python test_all.py
```

---

## 目录结构

```
platform/
├── backend/                 # 后端代码
│   ├── config/             # 配置模块
│   ├── datagenpro/         # 核心生成模块
│   ├── filters/            # 过滤器模块
│   ├── generators/         # 生成器模块
│   ├── handlers/           # API处理器
│   ├── managers/           # 管理器模块
│   ├── keywords/           # 关键词数据
│   ├── requirements.txt    # 依赖清单
│   └── start_server.py     # 启动脚本
├── frontend/               # 前端页面
├── docs/                   # 文档
├── .env.example           # 环境变量示例
├── Dockerfile             # Docker配置
├── docker-compose.yml     # Docker Compose配置
└── start.sh               # 启动脚本
```

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 必填 |
|-------|------|------|
| HOST | 服务地址 | 否 |
| PORT | 服务端口 | 否 |
| QWEN_API_KEY | 千问API密钥 | 否 |
| SECRET_KEY | JWT密钥 | 是 |
| ADMIN_TOKEN | 管理员Token | 是 |

---

## 常见问题

### Q: 启动失败，提示端口被占用

```bash
# 查看端口占用
lsof -i:8000
# 或修改 .env 中的 PORT
```

### Q: 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 数据生成速度慢

- 检查是否使用了API生成（需要网络）
- 增大 MAX_CONCURRENT_TASKS 配置

---

## 技术支持

- 文档：`docs/` 目录
- API文档：http://localhost:8000/docs
- 问题反馈：提交 Issue

---

## 版本信息

- 版本：v2.9
- 更新日期：2026-02-21
- 许可证：商业许可
