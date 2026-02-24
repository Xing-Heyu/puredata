import json
with open('test_small.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'总数据: {len(data)} 条')
print(f'第一条: {data[0]}')
print(f'category: {data[0].get("category", "N/A")}')