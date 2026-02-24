#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块 - 领域配置
"""

import os
import json

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYWORDS_DIR = os.path.join(BACKEND_DIR, 'keywords')

_keywords_cache = {}

def get_keywords(domain):
    """懒加载关键词"""
    if domain in _keywords_cache:
        return _keywords_cache[domain]
    
    filepath = os.path.join(KEYWORDS_DIR, f'{domain}.json')
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')
            keywords = []
            for line in lines[1:]:
                keywords.extend([k.strip() for k in line.split(',') if k.strip()])
            _keywords_cache[domain] = keywords
            return keywords
    
    default_keywords = {
        "人工智能": ["机器学习", "深度学习", "神经网络", "自然语言处理", "计算机视觉", "大模型", "GPT", "Transformer"],
        "医疗": ["诊断", "治疗", "药物", "手术", "康复", "疫苗", "病历", "处方"],
        "金融": ["投资", "理财", "贷款", "保险", "股票", "基金", "风控", "支付"],
        "劳动合同": ["劳动合同", "薪资", "社保", "加班", "休假", "离职", "试用期", "竞业协议"],
    }
    return default_keywords.get(domain, ["数据", "分析", "处理", "生成"])

def get_available_domains():
    """获取可用领域列表"""
    if os.path.exists(KEYWORDS_DIR):
        files = os.listdir(KEYWORDS_DIR)
        return [f.replace('.json', '') for f in files if f.endswith('.json')]
    return ["人工智能", "劳动合同", "医疗", "金融"]

class LazyDomains:
    """懒加载领域字典"""
    def __getitem__(self, domain):
        return get_keywords(domain)
    
    def get(self, domain, default=None):
        if domain in self:
            return self[domain]
        return default
    
    def items(self):
        return [(d, get_keywords(d)) for d in get_available_domains()]
    
    def keys(self):
        return get_available_domains()
    
    def __contains__(self, domain):
        return domain in get_available_domains()

DOMAINS = LazyDomains()
