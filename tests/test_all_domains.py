import urllib.request
import json
import time

print("=" * 60)
print("多领域数据质量测试")
print("=" * 60)

domains = ["人工智能", "医疗", "金融", "劳动合同"]

for domain in domains:
    print(f"\n【{domain}】")
    
    data = json.dumps({'domain': domain, 'count': 5}).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/generate',
                                  data=data,
                                  headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        task_id = result['task_id']
    
    for _ in range(20):
        time.sleep(0.3)
        req = urllib.request.Request(f'http://localhost:8000/task/{task_id}')
        with urllib.request.urlopen(req, timeout=10) as response:
            task = json.loads(response.read().decode('utf-8'))
            if task.get('status') == 'completed':
                items = task.get('preview', [])
                
                # 检查分类
                categories = [item.get('category') for item in items]
                correct = sum(1 for c in categories if c == domain)
                
                # 质量分数
                scores = [item.get('quality_score', 0) for item in items]
                
                print(f"   分类正确: {correct}/{len(categories)}")
                print(f"   质量分数: {min(scores):.2f} ~ {max(scores):.2f}")
                print(f"   示例: {items[0].get('text')[:50]}...")
                break

print("\n" + "=" * 60)
print("✅ 测试完成")
print("=" * 60)
