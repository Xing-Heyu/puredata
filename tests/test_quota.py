import urllib.request
import urllib.error
import json

print("测试quota API...")

# 先登录获取token
data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/login',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    token = result.get('token')
    print(f"登录成功，token: {token[:20]}...")

# 测试quota API
print("\n测试 /api/user/quota...")
req = urllib.request.Request('http://localhost:8000/api/user/quota',
                              headers={'Authorization': f'Bearer {token}'})
try:
    with urllib.request.urlopen(req, timeout=10) as response:
        result = response.read().decode('utf-8')
        print(f"状态码: {response.status}")
        print(f"响应: {result[:200]}")
except urllib.error.HTTPError as e:
    print(f"HTTP错误: {e.code}")
    print(f"响应: {e.read().decode()}")
except Exception as e:
    print(f"错误: {e}")
