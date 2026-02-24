import json
with open('人工智能_100.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'总数据: {len(data)} 条')
sources = {}
for d in data:
    s = d.get('source', 'unknown')
    sources[s] = sources.get(s, 0) + 1
print(f'来源统计: {sources}')
print(f'\n示例数据:')
for d in data[:3]:
    print(f'  [{d["id"]}] {d["word"]}: {d["text"][:50]}...')