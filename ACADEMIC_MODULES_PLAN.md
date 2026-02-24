# 学术模块启用方案 - 已实现

## 一、实现概述

已实现 **方案A + 方案B + 方案C** 的组合方案，支持三种方式启用学术模块：

1. **质量模式分级启用（方案A）** - 根据前台定义的质量模式自动配置
2. **按需模块启用（方案B）** - 用户自定义启用特定模块
3. **自动质量提升（方案C）** - 智能检测并自动启用增强模块

---

## 二、质量模式配置（与前台对应）

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           质量模式配置                                            │
└─────────────────────────────────────────────────────────────────────────────────┘

前台模式      │ 高质量比例 │ 最低分数 │ 启用模块
─────────────┼───────────┼─────────┼──────────────────────────────────────
standard     │    50%    │  0.70   │ 基础流水线（T²控制、验证、去重、门控）
high         │    80%    │  0.80   │ 基础 + 多样性增强 + 审计 + 失败回收
ultra        │    95%    │  0.85   │ 全部模块（包括所有学术模块）
mixed        │    70%    │  0.75   │ 自定义（用户可指定模块）
```

---

## 三、使用方法

### 方法1：质量模式分级启用

```python
from data_quality_pipeline import PipelineConfig, DataQualityPipeline

# 标准模式 - 50%高质量
config = PipelineConfig(quality_mode="standard")
pipeline = DataQualityPipeline(config)

# 高质量模式 - 80%高质量
config = PipelineConfig(quality_mode="high")
pipeline = DataQualityPipeline(config)

# 超高质量模式 - 95%高质量
config = PipelineConfig(quality_mode="ultra")
pipeline = DataQualityPipeline(config)
```

### 方法2：按需模块启用

```python
# 在标准模式基础上，额外启用特定模块
config = PipelineConfig(
    quality_mode="standard",
    enable_modules=["cads", "diversity", "audit"]
)

# 可用模块名称：
# - "cads"      → CADS对抗合成
# - "dasgen"    → DASGen分布对齐
# - "seed"      → 真实种子数据
# - "enhance"   → 增强数据生成器
# - "knowledge" → 本地知识图谱
# - "fac"       → FAC特征覆盖
# - "recovery"  → 失败数据回收
# - "diversity" → 多样性增强
# - "anomaly"   → 异常检测
# - "audit"     → 完整审计
```

### 方法3：自动质量提升

```python
# 自动检测质量，如果低于目标则启用额外增强
config = PipelineConfig(
    quality_mode="high",
    auto_enhance=True
)
```

---

## 四、各模式启用的模块详情

### standard（标准模式）
```
✅ T²质量控制
✅ 专业验证
✅ 异常检测与修复
✅ 去重处理
✅ 质量门控
❌ 多样性增强
❌ 完整审计
❌ CADS对抗合成
❌ DASGen分布对齐
❌ 真实种子数据
❌ 增强数据生成器
❌ 本地知识图谱
❌ FAC特征覆盖
❌ 失败数据回收
```

### high（高质量模式）
```
✅ T²质量控制
✅ 专业验证
✅ 异常检测与修复
✅ 去重处理
✅ 质量门控
✅ 多样性增强
✅ 完整审计
❌ CADS对抗合成
❌ DASGen分布对齐
❌ 真实种子数据
❌ 增强数据生成器
❌ 本地知识图谱
❌ FAC特征覆盖
✅ 失败数据回收
```

### ultra（超高质量模式）
```
✅ T²质量控制
✅ 专业验证
✅ 异常检测与修复
✅ 去重处理
✅ 质量门控
✅ 多样性增强
✅ 完整审计
✅ CADS对抗合成
✅ DASGen分布对齐
✅ 真实种子数据
✅ 增强数据生成器
✅ 本地知识图谱
✅ FAC特征覆盖
✅ 失败数据回收
```

---

## 五、与用户等级绑定

```
用户等级     │ 可用质量模式
────────────┼──────────────────────────────────────
FREE        │ standard
STANDARD    │ standard, high
PREMIUM     │ standard, high, ultra
ADMIN       │ standard, high, ultra, mixed + enable_modules
```

---

## 六、验证测试结果

```
=== 测试质量模式配置 ===

[standard] 50%高质量
  min_quality_score: 0.7
  enable_diversity_enhance: False
  enable_audit: False
  enable_cads: False
  enable_dasgen: False
  enable_failure_recovery: False

[high] 80%高质量
  min_quality_score: 0.8
  enable_diversity_enhance: True
  enable_audit: True
  enable_cads: False
  enable_dasgen: False
  enable_failure_recovery: True

[ultra] 95%高质量
  min_quality_score: 0.85
  enable_diversity_enhance: True
  enable_audit: True
  enable_cads: True
  enable_dasgen: True
  enable_failure_recovery: True

[mixed] 70%高质量
  min_quality_score: 0.75
  enable_diversity_enhance: True
  enable_audit: True
  enable_cads: False
  enable_dasgen: False
  enable_failure_recovery: True

=== 测试自定义模块启用 ===
自定义启用 cads, diversity, audit:
  enable_cads: True
  enable_diversity_enhance: True
  enable_audit: True

=== 所有测试通过! ===
```

---

## 七、修改的文件

1. **`data_quality_pipeline.py`**
   - 添加 `quality_mode` 参数
   - 添加 `QUALITY_MODE_CONFIGS` 配置字典
   - 添加 `MODULE_NAME_MAP` 模块名称映射
   - 添加 `enable_modules` 参数支持自定义模块启用
   - 添加 `auto_enhance` 参数支持自动质量提升
   - 在 `process` 方法中添加学术模块处理逻辑

2. **`high_quality_generator.py`**
   - 删除重复的 `QianwenAPI` 类
   - 改为调用 `千问API集成.py`

3. **`千问API集成.py`**
   - 恢复文件（包含完整功能）
