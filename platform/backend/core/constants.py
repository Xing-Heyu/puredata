#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层 - 常量定义
系统级常量配置
"""

DOMAINS = {
    "人工智能": ["机器学习", "深度学习", "神经网络", "自然语言处理", "计算机视觉", "强化学习", "知识图谱", "大模型", "AI应用", "智能系统"],
    "医疗": ["诊断", "治疗", "药物", "检查", "症状", "疾病", "手术", "康复", "预防", "医学影像"],
    "金融": ["投资", "融资", "风险", "收益", "股票", "债券", "基金", "期货", "外汇", "银行", "舆情", "ESG", "监管"],
    "劳动合同": ["劳动合同", "工资", "社保", "工伤", "休假", "解雇", "竞业限制", "试用期", "加班", "福利"],
    "交通驾驶": ["高速公路", "城市道路", "山区道路", "隧道", "桥梁", "路口", "匝道", "追尾", "侧翻", "碰撞", "失控", "爆胎", "疲劳驾驶", "酒驾", "鬼探头", "前车急刹", "行人横穿"],
}

QUALITY_LEVELS = {
    "high": {"min_length": 50, "max_length": 500, "completeness": 0.9},
    "medium": {"min_length": 30, "max_length": 300, "completeness": 0.7},
    "low": {"min_length": 10, "max_length": 200, "completeness": 0.5},
}

SUPPORTED_FORMATS = [
    "pretrain",
    "instruction",
    "conversation",
    "sharegpt",
    "behavior_sequence",
    "jsonl",
    "csv",
    "parquet",
]

DEFAULT_QUALITY_MODES = {
    "high_quality": {
        "high_ratio": 0.80,
        "medium_ratio": 0.15,
        "low_ratio": 0.05,
        "description": "高质量模式 - 适合模型训练、知识库构建"
    },
    "standard": {
        "high_ratio": 0.50,
        "medium_ratio": 0.30,
        "low_ratio": 0.20,
        "description": "标准质量模式 - 适合数据增强、一般训练"
    },
    "mixed": {
        "high_ratio": 0.25,
        "medium_ratio": 0.50,
        "low_ratio": 0.25,
        "description": "混合质量模式 - 适合鲁棒性测试、压力测试"
    }
}

API_PREFIX = "/api/v1"

MAX_BATCH_SIZE = 10000
MAX_WORKERS = 8
DEFAULT_PORT = 8000

__all__ = [
    'DOMAINS',
    'QUALITY_LEVELS',
    'SUPPORTED_FORMATS',
    'DEFAULT_QUALITY_MODES',
    'API_PREFIX',
    'MAX_BATCH_SIZE',
    'MAX_WORKERS',
    'DEFAULT_PORT',
]
