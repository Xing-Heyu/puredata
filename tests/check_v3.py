import json
import os

path = '.trae/skills/data-cleaner/training_data.json'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'总数据: {len(data)} 条')
    sources = {}
    for d in data:
        s = d.get('source', 'unknown')
        sources[s] = sources.get(s, 0) + 1
    print(f'来源统计: {sources}')
    
    # 检查千问API数据
    qianwen = [d for d in data if d.get('source') == 'qianwen_api']
    if qianwen:
        print(f'\n千问API数据 ({len(qianwen)}条):')
        for d in qianwen[:2]:
            print(f'  {d.get("word")}: {d.get("text")[:60]}...')
else:
    print('文件不存在')