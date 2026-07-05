#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:8000"

print("="*60)
print("全链路测试 - 生成旅游数据")
print("="*60)

print("\n[步骤1] 生成30条纯净数据")
payload = {"domain": "旅游", "count": 30, "format": "json", "mode": "clean", "noise_level": 0, "quality_mode": "standard"}
res = requests.post(f"{BASE_URL}/generate", json=payload)
if res.status_code == 200:
    task_id = res.json().get('task_id')
    print(f"[OK] 任务创建成功，Task ID: {task_id}")
else:
    print(f"[ERROR] 创建失败: {res.text}")
    task_id = None

if task_id:
    print("\n[步骤2] 轮询任务状态...")
    for i in range(60):
        res = requests.get(f"{BASE_URL}/task/{task_id}")
        task = res.json()
        status = task.get('status')
        progress = task.get('progress', 0)
        print(f"[进度] {status} - {progress}%")
        if status == 'completed':
            print(f"\n[OK] 任务完成!")
            print(f"[下载链接] {task.get('download_url')}")
            print(f"[实际数量] {task.get('count')}")
            quality = task.get('quality', {})
            if quality:
                print(f"\n[质量报告]")
                print(f"  总分: {quality.get('overall', 'N/A')}")
                print(f"  等级: {quality.get('grade', 'N/A')}")
            break
        elif status == 'failed':
            print(f"\n[ERROR] 任务失败: {task.get('error')}")
            break
        time.sleep(1)

print("\n" + "="*60)
print("测试完成！请检查服务器日志确认25个模块是否被调用")
print("="*60)
