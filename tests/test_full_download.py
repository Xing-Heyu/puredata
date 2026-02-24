import urllib.request
import json

print("=" * 50)
print("完整下载测试")
print("=" * 50)

# 1. 登录
print("\n1. 登录...")
data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/login',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    print(f"   登录: {'成功' if result.get('success') else '失败'}")

# 2. 生成数据
print("\n2. 生成50条数据...")
data = json.dumps({'domain': '人工智能', 'count': 50}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/generate',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    task_id = result['task_id']
    print(f"   任务ID: {task_id}")

# 3. 等待完成
print("\n3. 等待生成完成...")
import time
for i in range(20):
    time.sleep(0.5)
    req = urllib.request.Request(f'http://localhost:8000/task/{task_id}')
    with urllib.request.urlopen(req, timeout=10) as response:
        task = json.loads(response.read().decode('utf-8'))
        if task.get('status') == 'completed':
            download_url = task.get('download_url')
            print(f"   完成! 下载地址: {download_url}")
            break

# 4. 下载文件
print("\n4. 下载文件...")
from urllib.parse import quote
filename = download_url.split('/')[-1]
encoded_filename = quote(filename, safe='')
url = f'http://localhost:8000/download/{encoded_filename}'
print(f"   URL: {url}")

req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=10) as response:
    content = response.read()
    print(f"   文件大小: {len(content)} bytes")
    
    # 保存到桌面
    desktop = "d:/skill/skill3/downloaded_data.json"
    with open(desktop, 'wb') as f:
        f.write(content)
    print(f"   ✅ 已保存到: {desktop}")

# 5. 验证文件内容
print("\n5. 验证文件内容...")
with open(desktop, 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f"   数据条数: {len(data)}")
    print(f"   第一条: {data[0].get('text', '')[:50]}...")

print("\n" + "=" * 50)
print("✅ 下载功能完全正常!")
print("=" * 50)
