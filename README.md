# PureData - AI训练数据合成引擎

一键生成高质量AI训练数据，支持多领域、多格式、多质量模式。本地运行，零隐私风险。

## 快速开始

```bash
# 1. 安装依赖
pip install -r platform/backend/requirements.txt

# 2. 启动服务
cd platform/backend
python simple_main.py
```

浏览器访问 **http://localhost:8000**，即可使用 Web 界面生成数据。

> 纯本地运行，不上传任何数据。生成数据附带 CC0 协议声明，可自由商用。

## 功能特性

### 支持领域
人工智能 / 医疗 / 金融 / 劳动合同 / 交通驾驶

### 输出类型
| 类型 | 说明 |
|------|------|
| 纯文本 | 结构化文本数据，含实体标注 |
| 知识图谱 | 实体-关系-实体三元组 |
| 事件因果链 | 事件→传导→结果链条 |

### 质量模式
| 模式 | 说明 |
|------|------|
| standard | 标准质量，适用于大规模数据预训练 |
| high | 高质量，含专业术语校验与去重 |
| ultra | 最高质量，含多样性增强与多维度审计 |

### 输出格式
JSON / JSONL / CSV / TXT / Parquet

## 系统架构

```
platform/
├── backend/
│   ├── simple_main.py         # 主服务入口
│   ├── core/                  # 核心模块
│   ├── routes/                # API 路由
│   ├── service/               # 服务层
│   ├── domain_specialists/    # 领域专家（各领域生成逻辑）
│   ├── quality/               # 质量管控
│   └── filters/               # 数据过滤器（去重、校验等）
└── frontend/
    └── index.html             # Web 界面（单文件）
```

## 质量管道

```
数据生成 → 基本验证 → 专业校验 → 去重 → 多样性增强 → 质量门控 → 输出
```

| 阶段 | 说明 |
|------|------|
| 专业验证 | 领域术语检查、专业约束验证 |
| 去重 | MinHash LSH 近似去重 + MD5 精确去重 |
| 多样性增强 | 长尾检测、分布外增强 |
| 质量门控 | 四级质量分类 + 自动重试 |

## API 概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/generate` | POST | 生成数据 |
| `/tasks` | GET | 查询所有任务 |
| `/task/{id}` | GET | 查询任务状态 |
| `/download/{filename}` | GET | 下载数据文件 |
| `/domains` | GET | 获取支持领域 |
| `/stats` | GET | 系统统计 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | API 文档 |

## 技术栈

- **后端**: Python 3.10+, 标准库 HTTPServer
- **前端**: Vue 3 (CDN), 单 HTML 文件
- **存储**: SQLite + 文件系统

## 许可证

MIT License

生成的训练数据携带 CC0-1.0 (Public Domain) 声明，可自由使用、修改、商用。
