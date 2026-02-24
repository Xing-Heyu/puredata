#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析数据生成能力"""

from high_quality_generator import KnowledgeBase
import os
import json

print("=" * 70)
print("数据生成能力分析")
print("=" * 70)

KNOWLEDGE = KnowledgeBase.KNOWLEDGE

total_keywords = 0

for domain, keywords in KNOWLEDGE.items():
    print(f"\n【{domain}】")
    keyword_count = len(keywords)
    total_keywords += keyword_count
    print(f"  关键词数量: {keyword_count}")
    
    for keyword, definition in list(keywords.items())[:5]:
        print(f"  - {keyword}: {len(definition)}字")
    if len(keywords) > 5:
        print(f"  ... 还有 {len(keywords) - 5} 个关键词")

print("\n" + "=" * 70)
print(f"总计:")
print(f"  领域数量: {len(KNOWLEDGE)}个")
print(f"  关键词总数: {total_keywords}个")
print(f"  理论容量: {total_keywords}条基础数据")
print("=" * 70)

print("""
说明:
- 理论容量 = 关键词数
- 实际可用更多，因为可以:
  1. 添加更多关键词
  2. 使用变体生成（同义改写、噪声注入等）
  3. 调用API生成新内容
  4. 模板组合扩展
""")
