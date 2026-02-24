#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '.trae', 'skills', 'data-cleaner', 'training_data.json')

if not os.path.exists(data_path):
    print(f'数据文件不存在: {data_path}')
    exit(1)

with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'总数据: {len(data)} 条')
sources = {}
for d in data:
    s = d.get('source', 'unknown')
    sources[s] = sources.get(s, 0) + 1
print(f'来源统计: {sources}')

qianwen_data = [d for d in data if d.get('source') == 'qianwen_api']
if qianwen_data:
    print(f'\n千问API数据示例:')
    for d in qianwen_data[:2]:
        print(f'  word: {d.get("word")}')
        print(f'  text: {d.get("text")[:80]}...')
else:
    print('\n没有千问API数据')
