# PureData - AI训练数据合成引擎

本地运行的 AI 训练数据合成工具，支持多领域高质量数据生成。

## 核心功能

- **多领域数据生成**：人工智能、劳动合同、医疗、金融、交通驾驶
- **多输出类型**：纯文本、知识图谱、事件因果链、专业文献、多模态
- **多质量模式**：standard / high / ultra
- **多格式导出**：JSON、JSONL、CSV、TSV、XML、YAML、Parquet
- **实时进度**：SSE 实时推送

## 环境要求

| 项目 | 要求 |
|-----|------|
| Python | 3.8+ |
| 内存 | ≥ 2GB |
| 磁盘 | ≥ 1GB |
| 系统 | Windows / Linux / macOS |

## 快速部署

### 1. 安装依赖

```bash
pip install -r backend/requirements.txt
```

### 2. 启动服务

```bash
cd backend
python simple_main.py
```

### 3. 访问服务

- 服务页面：http://localhost:8000
- API文档：http://localhost:8000/docs

## 目录结构

```
platform/
├── backend/                 # 后端代码
│   ├── config/             # 配置模块
│   ├── converters/         # 格式转换器
│   ├── core/               # 核心模块
│   ├── domain_specialists/ # 领域专家
│   ├── filters/            # 过滤器（质量管控）
│   ├── generators/         # 生成器
│   ├── quality/            # 质量层
│   ├── routes/             # API路由
│   ├── service/            # 服务层
│   └── requirements.txt    # 依赖清单
├── frontend/               # 前端页面
└── docs/                   # 文档
```

## 配置

### 环境变量

| 变量名 | 说明 | 必填 |
|-------|------|------|
| HOST | 服务地址 | 否，默认 0.0.0.0 |
| PORT | 服务端口 | 否，默认 8000 |
| DATA_EXPIRE_DAYS | 数据保留天数 | 否，默认 90 天 |

### 千问 API（可选）

```bash
QIANWEN_API_KEY=sk-xxx
```

## API 概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/generate` | POST | 生成数据 |
| `/generate_sequence` | POST | 生成行为序列 |
| `/tasks` | GET | 查询所有任务 |
| `/task/{id}` | GET | 查询任务状态（支持SSE） |
| `/download/{id}.{format}` | GET | 下载数据 |
| `/domains` | GET | 获取支持领域 |
| `/quality_modes` | GET | 获取质量模式 |

完整 API 文档见 `backend/API.md`

## 常见问题

### Q: 启动失败，提示端口被占用

```bash
# 查看端口占用
lsof -i:8000
# 或修改启动参数
python simple_main.py --port 8080
```

### Q: 依赖安装失败

```bash
pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 许可证

MIT License
