import http.client
import json
import time

conn = http.client.HTTPConnection('localhost', 8000)
payload = json.dumps({
    'domain': '人工智能',
    'count': 30,
    'format': 'json',
    'mode': 'hybrid',
    'quality_mode': 'ultra'
})

print("发送请求: 生成30条人工智能领域顶级数据...")
conn.request('POST', '/generate', payload, {'Content-Type': 'application/json'})
response = conn.getresponse()
print(f'状态码: {response.status}')
data = json.loads(response.read().decode('utf-8'))
print(f'响应: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}')

if data.get('task_id'):
    task_id = data['task_id']
    print(f"\n任务ID: {task_id}")
    print("等待生成完成...")
    
    for i in range(30):
        time.sleep(1)
        conn = http.client.HTTPConnection('localhost', 8000)
        conn.request('GET', f'/task/{task_id}')
        resp = conn.getresponse()
        status = json.loads(resp.read().decode('utf-8'))
        print(f"进度: {status.get('progress', 0)}%, 状态: {status.get('status')}")
        if status.get('status') == 'completed':
            print(f"\n生成完成! 共 {status.get('total', 0)} 条数据")
            if status.get('download_url'):
                print(f"下载链接: {status['download_url']}")
            break
        elif status.get('status') == 'failed':
            print(f"生成失败: {status.get('error')}")
            break
