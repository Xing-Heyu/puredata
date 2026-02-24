import urllib.request
import json

print("测试关键词数量...")

req = urllib.request.Request('http://localhost:8000/domains')
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    print("\n领域关键词数量:")
    total = 0
    for d in result['domains']:
        print(f"  {d['name']}: {d['keywords']}个关键词")
        total += d['keywords']
    print(f"\n总计: {total}个关键词")
