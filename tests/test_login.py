import urllib.request
import urllib.error
import json

print("测试生成数据API...")
try:
    data = json.dumps({
        'domain': '人工智能',
        'count': 10,
        'format': 'json',
        'mode': 'hybrid'
    }).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/generate',
                                  data=data,
                                  headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"状态码: {response.status}")
        print(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
except urllib.error.HTTPError as e:
    result = json.loads(e.read().decode('utf-8'))
    print(f"状态码: {e.code}")
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"错误: {e}")
