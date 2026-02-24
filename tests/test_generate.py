import urllib.request
import json
import time

print("测试生成数据...")

# 登录
data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/login',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    token = result['token']
    print(f"登录成功")

# 生成数据
print("\n生成100条数据...")
start = time.time()
data = json.dumps({'domain': '人工智能', 'count': 100}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/generate',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    task_id = result['task_id']
    print(f"任务ID: {task_id}")

# 轮询任务状态
for i in range(20):
    time.sleep(0.5)
    req = urllib.request.Request(f'http://localhost:8000/task/{task_id}')
    with urllib.request.urlopen(req, timeout=10) as response:
        task = json.loads(response.read().decode('utf-8'))
        if task.get('status') == 'completed':
            elapsed = time.time() - start
            print(f"✅ 完成: {task.get('count')}条, 耗时{elapsed:.2f}秒")
            print(f"下载: {task.get('download_url')}")
            break
        elif task.get('status') == 'failed':
            print(f"❌ 失败: {task.get('error')}")
            break
