import json
import os

# 检查多个可能的位置
paths = [
    '.trae/skills/data-cleaner/training_data.json',
    'training_data.json',
    '.trae\\skills\\data-cleaner\\training_data.json'
]

for path in paths:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f'找到文件: {path}')
        print(f'总数据: {len(data)} 条')
        sources = {}
        for d in data:
            s = d.get('source', 'unknown')
            sources[s] = sources.get(s, 0) + 1
        print(f'来源统计: {sources}')
        break
else:
    print('文件不存在')
    print('当前目录:', os.getcwd())
    print('目录内容:', os.listdir('.trae/skills/data-cleaner/')[:10])