import json
with open('.trae/skills/data-cleaner/training_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'总数据: {len(data)} 条')
print(f'\n前3条:')
for i, d in enumerate(data[:3]):
    print(f'\n[{i}] category: {d.get("category")}')
    print(f'    word: {d.get("word")}')
    print(f'    source: {d.get("source")}')
    print(f'    text: {d.get("text")[:60]}...')

print(f'\n来源统计:')
sources = {}
for d in data:
    s = d.get('source', 'unknown')
    sources[s] = sources.get(s, 0) + 1
for k, v in sources.items():
    print(f'  {k}: {v}')
    