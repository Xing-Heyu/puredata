import urllib.request
import json
import time

print("测试简化版登录...")
start = time.time()

data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/login',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    elapsed = time.time() - start
    print(f"耗时: {elapsed:.3f}秒")
    print(f"结果: {result}")
