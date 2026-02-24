# PureData - AI训练数据生成平台

## 项目简介

PureData 是一款专业的 AI 训练数据生成平台，支持多领域高质量数据生成，面向企业和开发者提供数据生成服务。

### 核心功能

- **多领域数据生成**：人工智能、劳动合同、医疗、金融、法律、电商、教育、科技
- **8种质量等级**：最高质量、高质量、标准质量、混合质量、免费试用、鲁棒性测试
- **智能质量管控**：MinHash去重、异常检测、多样性增强、数据血缘追溯
- **多格式导出**：JSON、JSONL、CSV、TSV、XML、YAML、Parquet、Excel
- **实时进度推送**：SSE实时任务进度
- **多租户管理**：企业级租户隔离、配额管理
- **安全防护**：风控系统、防滥用、数据加密、审计日志

---

## 功能清单

### 1. 数据生成功能

| 功能 | 说明 |
|------|------|
| **8大领域专家** | AI、医疗、金融、劳动合同、法律、电商、教育、科技 |
| **质量门控** | 4级质量等级（≥0.85/0.80/0.75/<0.75） |
| **智能去重** | MinHash LSH近似去重 |
| **异常检测** | 10+检测规则，自动修复 |
| **多样性增强** | GECE长尾检测、分布外增强 |
| **数据血缘** | 完整来源追溯、链式哈希 |
| **并行生成** | 多线程并行，4线程默认 |

### 2. 导出格式支持

| 格式 | 用途 |
|------|------|
| **JSON/JSONL** | 标准JSON格式 |
| **CSV/TSV** | 表格格式，Excel兼容 |
| **XML** | 传统NLP工具兼容 |
| **YAML** | 配置文件格式 |
| **Parquet** | 大数据列式存储 |
| **Excel** | 商务报表格式 |
| **AI训练格式** | 预训练、指令微调、对话、ShareGPT |

### 3. 用户系统

| 功能 | 说明 |
|------|------|
| **用户角色** | Admin/Developer/Premium/Standard/Free |
| **认证方式** | 用户名/密码 + Token |
| **配额管理** | 日/月配额，按角色分配 |
| **邀请系统** | 邀请码奖励机制 |
| **密码安全** | bcrypt哈希，强度检查 |

### 4. 多租户管理

| 功能 | 说明 |
|------|------|
| **租户套餐** | Free/Basic/Pro/Enterprise |
| **数据隔离** | 租户间完全隔离 |
| **用量限制** | 用户数、任务数、数据量、API调用 |
| **操作审计** | 完整操作日志 |

### 5. 安全功能

| 功能 | 说明 |
|------|------|
| **API限流** | IP/用户/API/全局多维度限流 |
| **数据加密** | Fernet/AES加密，PBKDF2哈希 |
| **数据脱敏** | 邮箱/手机/身份证/银行卡脱敏 |
| **防滥用** | 临时邮箱检测、IP追踪、同IP限制 |
| **熔断保护** | 自动熔断，失败阈值+恢复超时 |
| **审计日志** | 完整操作审计，敏感字段脱敏 |

### 6. 管理后台

| 功能 | 说明 |
|------|------|
| **仪表盘** | 用户统计、任务统计、数据量 |
| **用户管理** | 查看/添加/删除用户 |
| **任务管理** | 查看所有任务状态 |
| **系统设置** | 配额配置、系统参数 |
| **操作日志** | 审计日志查看 |

### 7. 监控功能

| 功能 | 说明 |
|------|------|
| **系统监控** | CPU/内存/磁盘监控 |
| **性能指标** | 请求速率、错误率、响应时间 |
| **告警系统** | 多级告警（info/warning/error/critical） |
| **自动备份** | 定期自动备份，支持恢复 |

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
python simple_main.py
```

### 7. 访问服务

- 前台页面：http://localhost:8000
- 管理后台：http://localhost:8000/admin
- API文档：http://localhost:8000/docs

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

## 目录结构

```
platform/
├── backend/                 # 后端代码
│   ├── config/             # 配置模块
│   ├── converters/         # 格式转换器
│   ├── core/               # 核心模块
│   ├── datagenpro/         # 数据生成核心
│   ├── domain_specialists/ # 领域专家
│   ├── filters/            # 过滤器（质量管控）
│   ├── generators/         # 生成器
│   ├── managers/           # 管理器
│   ├── quality/            # 质量层
│   ├── routes/             # API路由
│   ├── service/            # 服务层
│   ├── domain_configs/     # 领域配置
│   ├── domain_templates/   # 领域模板
│   └── requirements.txt    # 依赖清单
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
| HOST | 服务地址 | 否，默认0.0.0.0 |
| PORT | 服务端口 | 否，默认8000 |
| SECRET_KEY | JWT密钥 | 是 |
| ADMIN_USERNAME | 管理员用户名 | 是 |
| ADMIN_PASSWORD | 管理员密码 | 是 |
| DATA_EXPIRE_DAYS | 数据保留天数 | 否，默认90天 |

---

## API 概览

### 数据生成 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/generate` | POST | 生成数据 |
| `/generate_sequence` | POST | 生成行为序列 |
| `/tasks` | GET | 查询所有任务 |
| `/task/{id}` | GET | 查询任务状态（支持SSE） |
| `/download/{id}.{format}` | GET | 下载数据（json/jsonl/csv/xml/yaml） |
| `/domains` | GET | 获取支持领域 |
| `/quality_modes` | GET | 获取质量模式 |

### 用户 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/register` | POST | 用户注册 |
| `/api/login` | POST | 用户登录 |
| `/api/logout` | POST | 用户登出 |
| `/api/user/info` | GET | 用户信息 |
| `/api/user/quota` | GET | 用户配额 |

### 管理员 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/admin/login` | POST | 管理员登录 |
| `/api/admin/users` | GET | 用户列表 |
| `/api/admin/logs` | GET | 操作日志 |

完整 API 文档见 `docs/API.md`

---

## 数据留存策略

- **生成数据**：默认保留90天（3个月）
- **自动清理**：启动时自动清理过期文件
- **数据血缘**：每条数据都有完整来源追溯
- **备份机制**：支持自动/手动备份

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
- 调整并行线程数配置

---

## 技术支持

- 用户指南：`docs/USER_GUIDE.md`
- API文档：`docs/API.md`
- 部署文档：`DEPLOY.md`

---

## 许可证

见 `docs/COPYRIGHT.md`
