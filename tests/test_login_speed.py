import urllib.request
import urllib.error
import json
import time

print("测试登录API响应时间...")
start = time.time()

try:
    data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/api/login',
                                  data=data,
                                  headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        elapsed = time.time() - start
        print(f"登录耗时: {elapsed:.3f}秒")
        print(f"结果: {result.get('success')}")
except Exception as e:
    print(f"错误: {e}")
