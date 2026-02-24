#!/usr/bin/env python3
"""完整API测试 - 使用urllib"""
import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://localhost:8000"

def get(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, json.loads(response.read().decode())
    except Exception as e:
        return None, str(e)

def post(url, data):
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.loads(response.read().decode())
    except Exception as e:
        return None, str(e)

print("="*60)
print("完整API测试")
print("="*60)

# 1. 健康检查
print("\n[1] 健康检查")
status, data = get(f"{BASE_URL}/health")
print(f"    状态: {status}")
print(f"    响应: {data}")

# 2. 领域列表
print("\n[2] 领域列表")
status, data = get(f"{BASE_URL}/domains")
print(f"    状态: {status}")
if status == 200:
    domains = data.get('domains', [])
    print(f"    领域数量: {len(domains)}")
    print(f"    领域列表: {[d.get('name') if isinstance(d, dict) else d for d in domains]}")

# 3. 生成数据
print("\n[3] 生成数据")
status, data = post(f"{BASE_URL}/generate", {
    "domain": "劳动合同",
    "count": 10,
    "format": "json",
    "mode": "clean",
    "quality_mode": "standard"
})
print(f"    状态: {status}")
if status == 200:
    task_id = data.get('task_id')
    print(f"    Task ID: {task_id}")
    
    # 轮询任务状态
    print("\n[4] 轮询任务状态")
    for i in range(10):
        time.sleep(0.5)
        status, task = get(f"{BASE_URL}/task/{task_id}")
        if status == 200:
            st = task.get('status')
            progress = task.get('progress')
            print(f"    进度: {st} - {progress}%")
            if st == 'completed':
                print(f"    完成! 数据量: {task.get('count')}")
                print(f"    质量评分: {task.get('quality', {}).get('overall')}")
                break

# 5. 关键词
print("\n[5] 关键词列表")
status, data = get(f"{BASE_URL}/domains")
print(f"    状态: {status}")
if status == 200:
    domains = data.get('domains', [])
    if domains and len(domains) > 0:
        first_domain = domains[0].get('name') if isinstance(domains[0], dict) else domains[0]
        print(f"    第一个领域: {first_domain}")
        print(f"    关键词数量: {domains[0].get('keywords') if isinstance(domains[0], dict) else 'N/A'}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
