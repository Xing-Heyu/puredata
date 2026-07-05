#!/usr/bin/env python3
"""快速API测试"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("="*60)
print("快速API测试")
print("="*60)

# 1. 测试首页
try:
    res = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"[OK] 首页: {res.status_code}")
except Exception as e:
    print(f"[FAIL] 首页: {e}")

# 2. 测试健康检查
try:
    res = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"[OK] 健康检查: {res.status_code} - {res.json()}")
except Exception as e:
    print(f"[FAIL] 健康检查: {e}")

# 3. 测试生成数据
try:
    res = requests.post(f"{BASE_URL}/generate", json={
        "domain": "劳动合同",
        "count": 10,
        "format": "json",
        "mode": "clean",
        "quality_mode": "standard"
    }, timeout=10)
    print(f"[OK] 生成数据: {res.status_code}")
    if res.status_code == 200:
        task_id = res.json().get('task_id')
        print(f"  Task ID: {task_id}")
except Exception as e:
    print(f"[FAIL] 生成数据: {e}")

# 4. 测试领域列表
try:
    res = requests.get(f"{BASE_URL}/domains", timeout=5)
    print(f"[OK] 领域列表: {res.status_code}")
    if res.status_code == 200:
        domains = res.json().get('domains', [])
        print(f"  领域数量: {len(domains)}")
except Exception as e:
    print(f"[FAIL] 领域列表: {e}")

# 5. 测试质量模式列表
try:
    res = requests.get(f"{BASE_URL}/quality_modes", timeout=5)
    print(f"[OK] 质量模式列表: {res.status_code}")
    if res.status_code == 200:
        modes = res.json().get('modes', [])
        print(f"  模式数量: {len(modes)}")
except Exception as e:
    print(f"[FAIL] 质量模式列表: {e}")

print("="*60)
print("测试完成")
print("="*60)
