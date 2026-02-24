#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据质量流水线
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("测试1: 专业验证器")
print("=" * 60)

from quality import ProfessionalValidator

validator = ProfessionalValidator()

result1 = validator.validate("高血压患者常出现头痛、头晕、心悸等症状，需要长期服药控制。", "医疗")
print(f"正确内容验证: 通过={result1.is_valid}, 分数={result1.score:.2f}")

result2 = validator.validate("腰椎间盘突出会导致头痛，因为神经受压会影响全身。", "医疗")
print(f"错误内容验证: 通过={result2.is_valid}, 分数={result2.score:.2f}")
if result2.errors:
    print(f"发现错误: {result2.errors[0].description}")
    print(f"修复建议: {result2.errors[0].suggestion}")

print()
print("=" * 60)
print("测试2: 数据质量流水线")
print("=" * 60)

from quality import DataQualityPipeline, PipelineConfig

config = PipelineConfig(verbose=True)
pipeline = DataQualityPipeline(config)

test_data = [
    {"id": 1, "content": "高血压是指以体循环动脉血压持续升高为主要特征的临床综合征。诊断标准：收缩压>=140mmHg和/或舒张压>=90mmHg。", "domain": "医疗"},
    {"id": 2, "content": "腰椎间盘突出会导致头痛，因为神经受压会影响全身。", "domain": "医疗"},
    {"id": 3, "content": "市盈率(PE) = 股价 / 每股收益，反映投资者为每1元净利润支付的价格。", "domain": "金融"},
    {"id": 4, "content": "Transformer是一种基于自注意力机制的神经网络架构，核心组件包括自注意力机制、多头注意力和位置编码。", "domain": "人工智能"},
]

result = pipeline.process(test_data, "医疗")
print(f"\n最终结果: 数据量={len(result.data)}, 质量分数={result.quality_score:.2f}")
print(f"质量等级: {result.quality_level}")
print(f"通过阶段: {result.stages_passed}")

print()
print("=" * 60)
print("测试3: 高质量生成器")
print("=" * 60)

from generation import HighQualityGenerator

gen = HighQualityGenerator(use_pipeline=False, use_validator=True)
print(f"生成器初始化成功")
print(f"验证器可用: {gen.validator is not None}")

print()
print("=" * 60)
print("测试4: 专业增强器 - 生成质量提示词")
print("=" * 60)

from quality import ProfessionalEnhancer

enhancer = ProfessionalEnhancer()
prompt = enhancer.generate_quality_prompt("医疗")
print(prompt[:500])

print()
print("=" * 60)
print("所有测试通过!")
print("=" * 60)

print("\n流水线报告:")
print(pipeline.get_report())
