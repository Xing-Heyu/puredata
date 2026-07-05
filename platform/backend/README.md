# PureData Backend

## 快速开始

### 启动服务

```bash
python simple_main.py

# 访问地址
服务: http://localhost:8000
API文档: http://localhost:8000/docs
```

### 命令行生成

```bash
# 生成100条人工智能领域数据（标准质量）
python simple_main.py --domain 人工智能 --count 100 --quality standard

# 生成500条医疗领域数据（高质量）
python simple_main.py --domain 医疗 --count 500 --quality high

# 生成1000条金融领域数据（超高质量）
python simple_main.py --domain 金融 --count 1000 --quality ultra
```

---

## 质量模式

| 模式 | 高质量比例 | 模块开启 | 适用场景 |
|------|-----------|---------|---------|
| **ultra** | 90% | 全部25个模块 | 高端训练场景 |
| **high** | 80% | 核心模块 | LLM预训练、模型微调 |
| **standard** | 50% | 基础模块 | 数据增强、一般训练 |
| **mixed** | 25% | 基础模块 | 鲁棒性测试、压力测试 |

---

## 支持领域

- 人工智能
- 劳动合同
- 医疗
- 金融
- 交通驾驶

---

## 支持的输出类型

| 输出类型 | 说明 |
|---------|------|
| text | 纯文本数据 |
| knowledge_graph | 知识图谱三元组 |
| event_chain | 事件因果链 |
| literature | 专业文献 |
| image | 文本+图片 |
| audio | 文本+音频 |
| multimodal | 文本+图片+音频 |

---

## 质量验证

新增输出类型（知识图谱、事件链、文献）均经过统一质量管道验证：

- **EventChainValidator**: 评级变化一致性、传导方向一致性
- **KnowledgeGraphValidator**: 实体非空、关系有效
- **LiteratureValidator**: 标题非空、内容长度

---

## 目录结构

```
backend/
├── core/                    # 核心层 - 配置、日志、缓存、存储
│   ├── __init__.py          # 懒加载入口
│   ├── config_impl.py       # 配置管理
│   ├── logger_impl.py       # 日志系统
│   ├── cache_impl.py        # 缓存系统
│   ├── storage_impl.py      # 存储层
│   ├── exceptions.py        # 异常定义
│   ├── constants.py         # 常量定义
│   ├── module_registry.py   # 模块注册表
│   └── request_handler.py   # 请求处理辅助
│
├── routes/                  # 路由层 - HTTP路由处理
│   ├── __init__.py          # 路由入口
│   ├── static_routes.py     # 静态文件路由
│   ├── generate_routes.py   # 生成路由
│   ├── cache_routes.py      # 缓存路由
│   ├── analytics_routes.py  # 分析路由
│   ├── download_routes.py   # 下载路由
│   ├── batch_routes.py      # 批量任务路由
│   └── academic_routes.py   # 学术验证路由
│
├── quality/                 # 质量层 - 质量控制
│   ├── gate.py              # 质量门控
│   ├── diversity_enhancer.py # 多样性增强
│   ├── data_recovery.py     # 失败数据回收
│   └── ...
│
├── academic/               # 学术层 - 高级生成算法
│   ├── cads.py              # CADS对抗合成
│   ├── dasgen.py            # 分布对齐生成
│   ├── fac.py               # FAC特征覆盖
│   └── ...
│
├── domain/                 # 领域层 - 垂直领域专精
│   ├── medical.py           # 医疗
│   ├── finance.py           # 金融
│   └── ...
│
├── api/
│   └── llm/                # API层 - 千问API集成
│       ├── qwen.py          # 千问API
│       └── smart_caller.py  # 智能调用器
│
├── service/                # 服务层 - 业务服务
│   └── task_service.py      # 任务服务
│
├── converters/             # 转换层 - 格式转换
│   └── ai_format.py         # AI格式转换
│
├── simple_main.py          # 主入口
└── ...
```

---

## 环境变量

```bash
# API配置
QIANWEN_API_KEY=your_api_key
QIANWEN_MODEL=qwen-turbo

# 数据库配置
DATABASE_URL=sqlite:///./data/puredata.db
REDIS_URL=redis://localhost:6379

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

---

## 版本

- **版本**: 1.0.0
- **更新日期**: 2026-07-05
