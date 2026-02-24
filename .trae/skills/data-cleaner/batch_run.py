#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量训练数据生成脚本
输出单个合并文件
"""

import json
import os
import sys
import hashlib
from datetime import datetime

# 强制UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
import main as generator

# 全局去重
_hashes = set()

def is_dup(text):
    h = hashlib.md5(text.encode('utf-8')).hexdigest()
    if h in _hashes:
        return True
    _hashes.add(h)
    return False

# 配置
CONFIG = {
    "output_file": "training_data.json",
    "tasks": [
        {"topic": "人工智能", "keywords": ["machine learning", "deep learning", "neural network", "natural language processing", "computer vision"], "count": 20},
        {"topic": "医疗", "keywords": ["disease", "symptom", "treatment", "medicine", "diagnosis"], "count": 20},
        {"topic": "金融", "keywords": ["stock", "bond", "investment", "banking", "finance"], "count": 20},
        {"topic": "科技", "keywords": ["technology", "computer", "software", "hardware", "internet"], "count": 20},
        {"topic": "教育", "keywords": ["education", "learning", "teaching", "student", "school"], "count": 20},
    ]
}

def main():
    print(f'\n{"="*50}')
    print(f'批量训练数据生成')
    print(f'时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'{"="*50}\n')
    
    all_data = []
    
    for i, task in enumerate(CONFIG["tasks"], 1):
        topic = task["topic"]
        keywords = task["keywords"]
        count = task["count"]
        
        print(f'[{i}/{len(CONFIG["tasks"])}] {topic} ({count}条)')
        
        try:
            data = generator.generate_data(topic, count, 'free_dict', keywords)
            
            added = 0
            for item in data:
                text = item.get('text', '')
                if not is_dup(text):
                    item['category'] = topic
                    all_data.append(item)
                    added += 1
            
            print(f'  ✓ 新增 {added} 条')
        except Exception as e:
            print(f'  ✗ 失败: {e}')
    
    # 重新编号
    for idx, item in enumerate(all_data):
        item['id'] = idx
    
    # 保存到脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, CONFIG["output_file"])
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f'\n{"="*50}')
    print(f'完成! 总计 {len(all_data)} 条数据')
    print(f'输出: {output_path}')
    print(f'{"="*50}\n')

if __name__ == '__main__':
    main()