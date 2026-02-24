#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import main as generator

# 生成少量数据测试
data = generator.generate_data("人工智能", 5, 'free_dict', ["machine learning", "deep learning"])

# 保存
with open('test_output.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'生成 {len(data)} 条数据 -> test_output.json')