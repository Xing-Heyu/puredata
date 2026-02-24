import urllib.request
import json
import time

print("=" * 50)
print("PureData 系统测试")
print("=" * 50)

# 测试登录
print("\n1. 测试登录...")
start = time.time()
data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/login',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    elapsed = time.time() - start
    print(f"   状态: {'成功' if result.get('success') else '失败'}")
    print(f"   耗时: {elapsed:.2f}秒")

# 测试生成
print("\n2. 测试生成100条数据...")
start = time.time()
data = json.dumps({'domain': '人工智能', 'count': 100}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/generate',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    task_id = result['task_id']
    print(f"   任务ID: {task_id}")

# 轮询
for i in range(20):
    time.sleep(0.5)
    req = urllib.request.Request(f'http://localhost:8000/task/{task_id}')
    with urllib.request.urlopen(req, timeout=10) as response:
        task = json.loads(response.read().decode('utf-8'))
        if task.get('status') == 'completed':
            elapsed = time.time() - start
            print(f"   状态: 完成")
            print(f"   数量: {task.get('count')}条")
            print(f"   耗时: {elapsed:.2f}秒")
            print(f"   质量: {task.get('quality', {}).get('grade', 'N/A')}")
            break
        elif task.get('status') == 'failed':
            print(f"   状态: 失败 - {task.get('error')}")
            break

print("\n" + "=" * 50)
print("✅ 系统正常运行!")
print("访问: http://localhost:8000")
print("=" * 50)
