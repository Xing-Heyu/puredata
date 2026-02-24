import urllib.request
import urllib.error
import json
import time

print("=" * 50)
print("手动测试登录API")
print("=" * 50)

# 测试1: 简单的GET请求
print("\n1. 测试GET /test...")
try:
    req = urllib.request.Request('http://localhost:8000/test')
    with urllib.request.urlopen(req, timeout=5) as response:
        print(f"   状态码: {response.status}")
        print(f"   响应: {response.read().decode()}")
except Exception as e:
    print(f"   错误: {e}")

# 测试2: 登录API
print("\n2. 测试POST /api/login...")
start = time.time()
try:
    data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/api/login',
                                  data=data,
                                  headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        result = response.read().decode()
        elapsed = time.time() - start
        print(f"   状态码: {response.status}")
        print(f"   耗时: {elapsed:.2f}秒")
        print(f"   响应: {result[:200]}")
except urllib.error.HTTPError as e:
    elapsed = time.time() - start
    print(f"   HTTP错误: {e.code}")
    print(f"   耗时: {elapsed:.2f}秒")
    print(f"   响应: {e.read().decode()[:200]}")
except Exception as e:
    elapsed = time.time() - start
    print(f"   错误: {e}")
    print(f"   耗时: {elapsed:.2f}秒")

print("\n" + "=" * 50)
