import json
with open('test_output.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'总数据: {len(data)} 条')
for i, d in enumerate(data[:3]):
    print(f'\n[{i}] category: {d.get("category")}')
    print(f'    word: {d.get("word")}')
    print(f'    text: {d.get("text")[:60]}...')