# PureData - AI训练数据合成引擎

一键生成高质量AI训练数据，支持多领域、多格式、多质量模式。本地运行，零隐私风险。

## 快速开始

```bash
cd platform/backend
python simple_main.py
```

访问 http://localhost:8000

## 功能特性

### 核心功能
- **多领域数据生成**：人工智能、劳动合同、医疗、金融、交通驾驶
- **多输出类型**：
  - 纯文本（结构化文本数据）
  - 知识图谱（实体-关系-实体三元组）
  - 事件因果链（事件→传导→结果链条）
  - 专业文献（学术论文格式）
  - 多模态（文本+图片+音频）
- **多质量模式**：standard / high / ultra
- **多输出格式**：JSON/JSONL/CSV/TXT/Parquet
- **批量生成**：支持万级以上

### 统一质量管道

所有输出类型都经过统一质量管道：

```
数据生成 → 基本质量验证 → 逻辑验证 → 自动修复 → 输出
```

### 质量处理流程

| 阶段 | 说明 |
|------|------|
| T²质量控制 | 多生成器协作 + 质量修剪 |
| 专业验证 | 领域术语验证、约束检查 |
| 异常检测修复 | 基于标准的异常检测与自动修复 |
| 去重 | MinHash LSH 近似去重 + MD5精确去重 |
| 多样性增强 | GECE长尾检测、分布外增强 |
| 质量门控 | 四级质量分类 + 自动重试 |
| LLM审计 | 9维度评估 |

## 系统架构

```
platform/
├── backend/
│   ├── simple_main.py      # 主服务入口
│   ├── core/               # 核心模块（配置、日志、缓存、存储）
│   ├── routes/             # API路由
│   ├── service/            # 服务层
│   ├── domain_specialists/ # 领域专家
│   ├── quality/            # 质量管控
│   ├── filters/            # 数据过滤器
│   └── config/             # 配置管理
└── frontend/
    └── index.html          # Web界面
```

## API 概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/generate` | POST | 生成数据 |
| `/generate_sequence` | POST | 生成行为序列 |
| `/tasks` | GET | 查询所有任务 |
| `/task/{id}` | GET | 查询任务状态 |
| `/progress` | GET | 查询进度（SSE） |
| `/download/{filename}` | GET | 下载数据文件 |
| `/domains` | GET | 获取支持领域 |
| `/quality_modes` | GET | 获取质量模式 |
| `/stats` | GET | 系统统计 |
| `/health` | GET | 健康检查 |

## 配置

```bash
# 千问API（可选，用于API生成模式）
QIANWEN_API_KEY=sk-xxx
```

## 命令行使用

```bash
# 生成100条人工智能领域数据
python simple_main.py --domain 人工智能 --count 100 --quality standard

# 生成500条医疗领域数据
python simple_main.py --domain 医疗 --count 500 --quality high
```

## 技术栈

- **后端**: Python 3.10+, HTTPServer
- **前端**: Vue 3, Axios
- **存储**: SQLite, 文件系统
- **缓存**: Redis (可选)

## 许可证

MIT License
