#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟前台完整流程测试
注册 → 登录 → 生成数据 → 下载
生成100条金融数据（核心领域）
"""

import urllib.request
import json
import time
from urllib.parse import quote

BASE_URL = "http://localhost:8000"

def make_request(url, data=None, headers=None):
    """发送HTTP请求"""
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    if data is not None:
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)
    else:
        req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {'success': False, 'error': str(e)}

def register_user(username, password, email):
    """注册用户"""
    print(f"\n{'='*60}")
    print("步骤1: 用户注册")
    print(f"{'='*60}")
    
    data = {
        'username': username,
        'password': password,
        'account': email
    }
    
    result = make_request(f"{BASE_URL}/api/register", data)
    
    if result.get('success'):
        print(f"✅ 注册成功!")
        print(f"   用户名: {username}")
        print(f"   账号: {email}")
    else:
        print(f"⚠️  注册: {result.get('error', '可能已注册')}")
    
    return result

def login_user(username, password):
    """用户登录"""
    print(f"\n{'='*60}")
    print("步骤2: 用户登录")
    print(f"{'='*60}")
    
    data = {
        'username': username,
        'password': password
    }
    
    result = make_request(f"{BASE_URL}/api/login", data)
    
    if result.get('success'):
        token = result.get('token', '')
        print(f"✅ 登录成功!")
        print(f"   用户名: {username}")
        print(f"   Token: {token[:20]}..." if len(token) > 20 else f"   Token: {token}")
    else:
        print(f"❌ 登录失败: {result.get('error', '未知错误')}")
    
    return result

def generate_data(domain, count, mode='clean', quality_mode='high', token=''):
    """生成数据"""
    print(f"\n{'='*60}")
    print(f"生成数据: {domain}, {count}条, quality={quality_mode}")
    print(f"{'='*60}")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    data = {
        'domain': domain,
        'count': count,
        'mode': mode,
        'quality_mode': quality_mode
    }
    
    result = make_request(f"{BASE_URL}/generate", data, headers)
    
    if result.get('task_id'):
        task_id = result['task_id']
        print(f"✅ 任务已创建: {task_id}")
        return task_id
    else:
        print(f"❌ 生成失败: {result.get('error', '未知错误')}")
        return None

def wait_for_completion(task_id, timeout=180):
    """等待任务完成"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        result = make_request(f"{BASE_URL}/task/{task_id}")
        
        status = result.get('status', 'unknown')
        progress = result.get('progress', 0)
        
        print(f"   状态: {status} | 进度: {progress}%", end='\r')
        
        if status == 'completed':
            print(f"\n✅ 完成! 共{result.get('count', 0)}条")
            return result
        elif status == 'failed':
            print(f"\n❌ 失败: {result.get('error', '未知错误')}")
            return result
        
        time.sleep(2)
    
    print(f"\n⏰ 等待超时")
    return {'status': 'failed', 'error': '等待超时'}

def download_file(download_url, save_path, token):
    """下载文件"""
    print(f"\n下载文件...")
    
    try:
        filename = download_url.split('/')[-1]
        encoded_filename = quote(filename, safe='')
        url = f"{BASE_URL}/download/{encoded_filename}"
        
        print(f"   文件名: {filename}")
        
        headers = {'Authorization': f'Bearer {token}'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=60) as response:
            content = response.read()
            
            with open(save_path, 'wb') as f:
                f.write(content)
            
            print(f"✅ 已保存: {save_path} ({len(content)} bytes)")
            
            return {'success': True, 'filepath': save_path}
    
    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")
        return {'success': False, 'error': str(e)}

def main():
    """主流程"""
    print(f"\n{'='*60}")
    print("PureData 模拟前台完整流程测试")
    print(f"{'='*60}")
    print("流程: 注册 → 登录 → 生成数据 → 下载")
    print("领域: 金融（核心领域）")
    print(f"{'='*60}")
    
    username = "test_finance_user"
    password = "test123456"
    email = "test_finance@test.com"
    
    # 1. 注册
    register_result = register_user(username, password, email)
    
    # 2. 登录
    login_result = login_user(username, password)
    
    if not login_result.get('success'):
        print("\n❌ 登录失败，测试终止")
        return None
    
    token = login_result.get('token', '')
    
    # 3. 生成数据（使用high模式）
    task_id = generate_data('金融', 20, 'clean', 'high', token)
    
    if task_id:
        result = wait_for_completion(task_id)
        
        if result.get('status') == 'completed':
            download_url = result.get('download_url', '')
            if download_url:
                save_path = "D:/skill/skill3/training_data/finance_test_20条.json"
                download_result = download_file(download_url, save_path, token)
                
                if download_result.get('success'):
                    try:
                        with open(save_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        print(f"\n{'='*60}")
                        print("数据预览 (前5条)")
                        print(f"{'='*60}")
                        for i, item in enumerate(data[:5], 1):
                            print(f"\n[{i}] {item.get('word', 'N/A')}")
                            print(f"    质量: {item.get('quality_score', 'N/A')}")
                            text = item.get('text', '')
                            print(f"    内容: {text[:80]}..." if len(text) > 80 else f"    内容: {text}")
                        
                        scores = [item.get('quality_score', 0) for item in data if 'quality_score' in item]
                        if scores:
                            print(f"\n质量统计: 最高{max(scores):.2f}, 最低{min(scores):.2f}, 平均{sum(scores)/len(scores):.2f}")
                            high_count = sum(1 for s in scores if s >= 0.75)
                            print(f"高质量(>=0.75): {high_count}/{len(scores)} ({high_count/len(scores)*100:.1f}%)")
                        
                        return data
                    except Exception as e:
                        print(f"   读取失败: {e}")
    
    return None

if __name__ == '__main__':
    result = main()
    
    print(f"\n{'='*60}")
    if result:
        print(f"✅ 测试完成，共{len(result)}条数据")
    else:
        print(f"❌ 测试失败")
    print(f"{'='*60}")
