import urllib.request
import json
import time

print("=" * 60)
print("完整版 - 金融数据生成测试")
print("=" * 60)

# 登录
print("\n1. 登录...")
data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/login',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    print(f"   登录: {'成功' if result.get('success') else '失败'}")

# 生成金融数据
print("\n2. 生成20条金融数据...")
data = json.dumps({
    'domain': '金融',
    'count': 20,
    'mode': 'hybrid',
    'quality_mode': 'standard'
}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/generate',
                              data=data,
                              headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=10) as response:
    result = json.loads(response.read().decode('utf-8'))
    task_id = result['task_id']
    print(f"   任务ID: {task_id}")

# 等待完成
print("\n3. 等待生成完成...")
for i in range(30):
    time.sleep(0.5)
    req = urllib.request.Request(f'http://localhost:8000/task/{task_id}')
    with urllib.request.urlopen(req, timeout=10) as response:
        task = json.loads(response.read().decode('utf-8'))
        if task.get('status') == 'completed':
            print(f"   完成! 共{task.get('count')}条")
            
            # 显示数据
            print("\n4. 生成的数据:")
            print("-" * 60)
            for j, item in enumerate(task.get('preview', [])[:10]):
                print(f"\n[{j+1}]")
                print(f"   word: {item.get('word')}")
                print(f"   category: {item.get('category')}")
                print(f"   text: {item.get('text')[:80]}...")
            
            # 质量统计
            scores = [item.get('quality_score', 0) for item in task.get('preview', [])]
            if scores:
                print(f"\n质量分数: {min(scores):.2f} ~ {max(scores):.2f}")
            
            # 下载
            download_url = task.get('download_url')
            if download_url:
                from urllib.parse import quote
                filename = download_url.split('/')[-1]
                url = f'http://localhost:8000/download/{quote(filename)}'
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read()
                    with open('d:/skill/skill3/金融_完整版_20条.json', 'wb') as f:
                        f.write(content)
                    print(f"\n✅ 已保存到: 金融_完整版_20条.json")
            break
        elif task.get('status') == 'failed':
            print(f"   失败: {task.get('error')}")
            break

print("\n" + "=" * 60)
