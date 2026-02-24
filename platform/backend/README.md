# DataGen Pro - AI训练数据生成平台

## 快速开始

### 启动服务

```bash
# 启动HTTP服务
python simple_main.py

# 访问地址
前台: http://localhost:8000
后台: http://localhost:8000/admin
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

---

## 新架构目录结构

```
backend/
├── core/                    # 核心层 - 配置、日志、缓存、存储
│   ├── __init__.py          # 懒加载入口
│   ├── config_impl.py       # 配置管理
│   ├── logger_impl.py       # 日志系统
│   ├── cache_impl.py        # 缓存系统
│   ├── storage_impl.py      # 存储层
│   ├── exceptions.py        # 异常定义
│   └── constants.py         # 常量定义
│
├── generation/              # 生成层 - 数据生成核心
│   ├── __init__.py          # 懒加载入口
│   ├── topology_generator.py
│   ├── data_generator.py
│   ├── variation_engine.py
│   └── ...
│
├── quality/                 # 质量层 - 质量控制
│   ├── __init__.py          # 懒加载入口
│   ├── gate.py              # 质量门控（常驻）
│   ├── diversity_enhancer.py # 多样性增强（常驻）
│   ├── data_recovery.py     # 失败数据回收（常驻）
│   └── ...
│
├── academic/               # 学术层 - 高级生成算法
│   ├── __init__.py          # 懒加载入口
│   ├── cads.py              # CADS对抗合成
│   ├── dasgen.py            # 分布对齐生成
│   ├── fac.py               # FAC特征覆盖
│   └── ...
│
├── domain/                 # 领域层 - 垂直领域专精
│   ├── __init__.py          # 懒加载入口
│   ├── medical.py           # 医疗
│   ├── finance.py           # 金融
│   └── ...
│
├── api/
│   └── llm/                # API层 - 千问API集成
│       ├── __init__.py      # 懒加载入口
│       ├── qwen.py          # 千问API
│       └── smart_caller.py  # 智能调用器
│
├── service/                # 服务层 - 业务服务
│   ├── user_service.py      # 用户服务
│   ├── auth_service.py      # 认证服务
│   ├── task_service.py      # 任务服务
│   └── ...
│
├── converters/             # 转换层 - 格式转换
│   ├── ai_format.py         # AI格式转换
│   └── ...
│
├── test/                   # 测试目录
│   ├── test_pipeline.py
│   ├── test_minimal.py
│   └── ...
│
├── main.py                 # 主入口（精简版）
└── simple_main.py          # 原主入口（保留）
```

---

## 导入方式

### 新架构导入（推荐）

```python
# 核心层
from core import config, logger, cache, storage
from core import DOMAINS, QUALITY_LEVELS

# 质量层
from quality import QualityGateController, DiversityEnhancer, DataRecoveryEngine

# 生成层
from generation import TopologyGenerator, HighQualityGenerator

# 学术层（懒加载）
from academic import CADSPipeline, FACSynthesisPipeline

# 领域层
from domain import MedicalSpecialist, get_specialist

# API层
from api.llm import QwenAPI

# 服务层
from service import UserService, TaskService

# 转换层
from converters import AIFormatConverter
```

### 原有导入（兼容性保持）

```python
# 原有导入方式仍然可用
from filters.quality_gate import QualityGateController
from high_quality_generator import HighQualityGenerator
from 千问API集成 import QwenAPI
from 缓存管理 import CacheManager
```

---

## 25个核心模块

| 序号 | 模块 | 功能 | 位置 |
|------|------|------|------|
| 1 | QualityGate | 质量门控 | quality/gate.py |
| 2 | DeduplicationSystem | 去重系统 | quality/deduplication.py |
| 3 | AnomalyDetector | 异常检测 | quality/anomaly_detector.py |
| 4 | DiversityEnhancer | 多样性增强 | quality/diversity_enhancer.py |
| 5 | ProfessionalValidator | 专业验证 | quality/professional_validator.py |
| 6 | T2QualityControl | T²质量控制 | quality/t2_control.py |
| 7 | CADS对抗合成 | CADS对抗合成 | academic/cads.py |
| 8 | DASGen分布对齐生成 | 分布对齐生成 | academic/dasgen.py |
| 9 | 真实种子数据 | 种子数据管理 | academic/seed_data.py |
| 10 | 增强数据生成器 | 增强数据生成 | academic/enhanced_generator.py |
| 11 | 本地知识图谱生成 | 知识图谱 | academic/knowledge_graph.py |
| 12 | FAC特征覆盖合成 | FAC特征覆盖 | academic/fac.py |
| 13 | 失败数据回收 | 失败数据回收 | quality/data_recovery.py |
| 14 | SmartDiversityEnhancer | 智能多样性 | quality/smart_diversity_enhancer.py |
| 15 | CalibratedEnhancer | 校准增强 | quality/calibrated_enhancer.py |
| 16 | DataLineage | 数据血缘 | quality/data_lineage.py |
| 17 | 千问API集成 | 千问API | api/llm/qwen.py |
| 18 | 高质量生成器 | 高质量生成 | generation/high_quality.py |
| 19 | 数据质量评估 | 质量评估 | quality/auditor.py |
| 20 | 缓存管理 | 缓存管理 | core/cache_impl.py |
| 21 | 配置管理 | 配置管理 | core/config_impl.py |
| 22 | 用户系统 | 用户系统 | service/user_service.py |
| 23 | 领域专家 | 领域专家 | domain/ |
| 24 | 数据质量Pipeline | 数据质量流水线 | quality/pipeline.py |
| 25 | 生成器 | 生成器 | generation/ |

---

## 环境变量

```bash
# API配置
QIANWEN_API_KEY=your_api_key
QIANWEN_MODEL=qwen-turbo

# 数据库配置
DATABASE_URL=sqlite:///./data/datagenpro.db
REDIS_URL=redis://localhost:6379

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
SECRET_KEY=your_secret_key
```

---

## 版本

- **版本**: 2.0.0
- **更新日期**: 2025-02-22
- **主要更新**: 
  - 新架构懒加载设计
  - 质量模式优化（ultra 90%高质量）
  - 25个模块完整保留
  - 导入路径更新
