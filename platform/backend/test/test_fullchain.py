#!/usr/bin/env python3
"""
全链路测试脚本 - 完全模拟前台请求
测试前台点击"开始生成"按钮是否能触发完整的25个模块
"""
import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000"

def login():
    """登录获取token"""
    print("\n" + "="*60)
    print("步骤1: 登录获取Token")
    print("="*60)
    
    # 先尝试注册一个测试用户
    register_data = {
        "account": "test_fullchain@example.com",
        "code": "123456",
        "username": "test_fullchain",
        "password": "Test123456",
        "confirmPassword": "Test123456"
    }
    
    # 直接登录测试用户
    login_data = {
        "username": "test_fullchain",
        "password": "Test123456"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/login", json=login_data)
        if res.status_code == 200 and res.json().get('success'):
            token = res.json().get('token')
            print(f"[OK] 登录成功，Token: {token[:20]}...")
            return token
        else:
            # 尝试注册
            print("[INFO] 登录失败，尝试注册...")
            res = requests.post(f"{BASE_URL}/api/register", json=register_data)
            if res.status_code == 200:
                res = requests.post(f"{BASE_URL}/api/login", json=login_data)
                if res.status_code == 200 and res.json().get('success'):
                    token = res.json().get('token')
                    print(f"[OK] 注册并登录成功，Token: {token[:20]}...")
                    return token
    except Exception as e:
        print(f"[ERROR] 登录失败: {e}")
    
    print("[WARN] 使用无Token模式测试...")
    return None

def generate_data(token, domain, count, mode, quality_mode="standard"):
    """生成数据 - 完全模拟前台请求"""
    print(f"\n" + "="*60)
    print(f"步骤2: 生成数据 - {domain}, {count}条, {mode}模式, {quality_mode}质量")
    print("="*60)
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    payload = {
        "domain": domain,
        "count": count,
        "format": "json",
        "mode": mode,
        "noise_level": 30 if mode == "noisy" else 0,
        "quality_mode": quality_mode
    }
    
    print(f"[请求] POST /generate")
    print(f"[参数] {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        res = requests.post(f"{BASE_URL}/generate", json=payload, headers=headers)
        if res.status_code == 200:
            task_id = res.json().get('task_id')
            print(f"[OK] 任务创建成功，Task ID: {task_id}")
            return task_id
        else:
            print(f"[ERROR] 创建任务失败: {res.text}")
            return None
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
        return None

def poll_task(task_id, max_wait=300):
    """轮询任务状态 - 完全模拟前台轮询"""
    print(f"\n" + "="*60)
    print(f"步骤3: 轮询任务状态 - {task_id}")
    print("="*60)
    
    start_time = time.time()
    last_progress = 0
    
    while time.time() - start_time < max_wait:
        try:
            res = requests.get(f"{BASE_URL}/task/{task_id}")
            if res.status_code == 200:
                task = res.json()
                status = task.get('status', 'unknown')
                progress = task.get('progress', 0)
                
                if progress != last_progress:
                    print(f"[进度] {status} - {progress}%")
                    last_progress = progress
                
                if status == 'completed':
                    print(f"\n[OK] 任务完成!")
                    return task
                elif status == 'failed':
                    print(f"\n[ERROR] 任务失败: {task.get('error')}")
                    return task
        except Exception as e:
            print(f"[WARN] 轮询异常: {e}")
        
        time.sleep(0.5)
    
    print(f"[ERROR] 任务超时")
    return None

def analyze_result(task):
    """分析结果 - 检查全链路模块是否被调用"""
    print(f"\n" + "="*60)
    print(f"步骤4: 分析结果 - 检查全链路模块")
    print("="*60)
    
    if not task:
        print("[ERROR] 无任务结果")
        return
    
    print(f"\n[任务信息]")
    print(f"  - 状态: {task.get('status')}")
    print(f"  - 数量: {task.get('count')}")
    print(f"  - 下载链接: {task.get('download_url')}")
    
    # 检查质量报告
    quality = task.get('quality', {})
    if quality:
        print(f"\n[质量报告]")
        print(f"  - 总分: {quality.get('overall', 'N/A')}")
        print(f"  - 等级: {quality.get('grade', 'N/A')}")
        print(f"  - 多样性: {quality.get('diversity', 'N/A')}")
        print(f"  - 有效性: {quality.get('validity', 'N/A')}")
        print(f"  - 可读性: {quality.get('readability', 'N/A')}")
    
    # 检查预览数据
    preview = task.get('preview', [])
    if preview:
        print(f"\n[预览数据] (前3条)")
        for i, item in enumerate(preview[:3]):
            print(f"  {i+1}. {item.get('text', item)[:100]}...")
    
    # 检查统计信息
    stats = task.get('stats', {})
    if stats:
        print(f"\n[统计信息]")
        for key, value in stats.items():
            print(f"  - {key}: {value}")

def main():
    print("\n" + "#"*60)
    print("# 全链路测试 - 模拟前台点击'开始生成'按钮")
    print("#"*60)
    
    # 登录
    token = login()
    
    # 测试三种模式
    test_cases = [
        {"domain": "旅游", "count": 30, "mode": "clean", "quality_mode": "standard"},
        {"domain": "旅游", "count": 40, "mode": "hybrid", "quality_mode": "high"},
        {"domain": "旅游", "count": 30, "mode": "noisy", "quality_mode": "standard"},
    ]
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'#'*60}")
        print(f"# 测试用例 {i}/3: {case['mode']}模式, {case['count']}条")
        print(f"#"*60)
        
        task_id = generate_data(token, case['domain'], case['count'], case['mode'], case['quality_mode'])
        if task_id:
            task = poll_task(task_id)
            if task:
                analyze_result(task)
                results.append({
                    "case": case,
                    "task_id": task_id,
                    "status": task.get('status'),
                    "count": task.get('count')
                })
    
    # 汇总报告
    print(f"\n" + "#"*60)
    print("# 测试汇总报告")
    print("#"*60)
    
    print(f"\n| 序号 | 模式 | 数量 | 质量 | 状态 | 实际数量 |")
    print(f"|------|------|------|------|------|----------|")
    for i, r in enumerate(results, 1):
        c = r['case']
        print(f"| {i} | {c['mode']} | {c['count']} | {c['quality_mode']} | {r['status']} | {r['count']} |")
    
    print(f"\n[完成] 全链路测试结束")
    
    # 复制记录
    print(f"\n" + "="*60)
    print("复制记录 (可直接复制到前台测试)")
    print("="*60)
    print(f"""
测试参数:
- 领域: 旅游
- 格式: JSON
- 测试1: 30条 + clean模式 + standard质量
- 测试2: 40条 + hybrid模式 + high质量  
- 测试3: 30条 + noisy模式 + standard质量

API调用示例:
curl -X POST http://localhost:8000/generate \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{{"domain":"旅游","count":30,"format":"json","mode":"clean","quality_mode":"standard"}}'
""")

if __name__ == "__main__":
    main()
