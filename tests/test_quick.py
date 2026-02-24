import urllib.request
import json
import time

print("测试数据质量...")

# 生成人工智能数据
data = json.dumps({'domain': '人工智能', 'count': 10}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/generate',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    task_id = result['task_id']

# 等待完成
for _ in range(20):
    time.sleep(0.5)
    req = urllib.request.Request(f'http://localhost:8000/task/{task_id}')
    with urllib.request.urlopen(req, timeout=10) as response:
        task = json.loads(response.read().decode('utf-8'))
        if task.get('status') == 'completed':
            print(f"\n任务完成!")
            print(f"数量: {task.get('count')}")
            print(f"\n前3条数据:")
            for i, item in enumerate(task.get('preview', [])[:3]):
                print(f"\n{i+1}. category: {item.get('category')}")
                print(f"   quality_score: {item.get('quality_score')}")
                print(f"   text: {item.get('text')[:60]}...")
            break
