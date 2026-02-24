import urllib.request
import json
import time
from collections import Counter

print("=" * 60)
print("数据质量测试")
print("=" * 60)

# 生成数据
print("\n1. 生成各领域数据...")
domains = ["人工智能", "医疗", "金融", "劳动合同"]
all_data = {}

for domain in domains:
    data = json.dumps({'domain': domain, 'count': 20}).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/generate',
                                  data=data,
                                  headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        task_id = result['task_id']
    
    # 等待完成
    for _ in range(20):
        time.sleep(0.3)
        req = urllib.request.Request(f'http://localhost:8000/task/{task_id}')
        with urllib.request.urlopen(req, timeout=10) as response:
            task = json.loads(response.read().decode('utf-8'))
            if task.get('status') == 'completed':
                all_data[domain] = task.get('preview', [])
                break

# 分析数据质量
print("\n2. 数据质量分析:")
print("-" * 60)

for domain, items in all_data.items():
    print(f"\n【{domain}】")
    
    # 检查分类
    categories = [item.get('category') for item in items]
    category_correct = sum(1 for c in categories if c == domain)
    print(f"   分类正确率: {category_correct}/{len(categories)} ({category_correct/len(categories)*100:.0f}%)")
    
    # 质量分数分布
    scores = [item.get('quality_score', 0) for item in items]
    print(f"   质量分数: 最低={min(scores):.2f}, 最高={max(scores):.2f}, 平均={sum(scores)/len(scores):.2f}")
    
    # 文本长度
    lengths = [len(item.get('text', '')) for item in items]
    print(f"   文本长度: 最短={min(lengths)}, 最长={max(lengths)}, 平均={sum(lengths)/len(lengths):.0f}")
    
    # 模板多样性
    texts = [item.get('text', '') for item in items]
    unique_texts = len(set(texts))
    print(f"   文本多样性: {unique_texts}/{len(texts)} 条不重复")
    
    # 示例
    print(f"   示例: {items[0].get('text', '')[:60]}...")

print("\n" + "=" * 60)
print("质量评估完成")
print("=" * 60)
