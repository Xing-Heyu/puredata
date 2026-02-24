#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统完整流程测试
注册 → 登录 → 生成数据 → 下载
验证修复后的系统是否正常运行
"""

import urllib.request
import json
import time
import sys
from urllib.parse import quote

BASE_URL = "http://localhost:8000"

def make_request(url, data=None, headers=None, method='POST'):
    """发送HTTP请求"""
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    if data is not None:
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_register(username, password, email):
    """测试注册"""
    print("\n" + "="*60)
    print("【测试1】用户注册")
    print("="*60)
    
    data = {
        'username': username,
        'password': password,
        'email': email
    }
    
    result = make_request(f"{BASE_URL}/api/register", data)
    
    if result.get('success'):
        print(f"✅ 注册成功: {username}")
        return True
    elif '已存在' in result.get('error', '') or 'already exists' in result.get('error', '').lower():
        print(f"⚠️  用户已存在，继续测试: {username}")
        return True
    else:
        print(f"❌ 注册失败: {result.get('error', '未知错误')}")
        return False

def test_login(username, password):
    """测试登录"""
    print("\n" + "="*60)
    print("【测试2】用户登录")
    print("="*60)
    
    data = {
        'username': username,
        'password': password
    }
    
    result = make_request(f"{BASE_URL}/api/login", data)
    
    if result.get('success'):
        token = result.get('token', '')
        print(f"✅ 登录成功")
        print(f"   Token: {token[:30]}..." if len(token) > 30 else f"   Token: {token}")
        return token
    else:
        print(f"❌ 登录失败: {result.get('error', '未知错误')}")
        return None

def test_generate_data(domain, count, mode, quality_mode, token):
    """测试生成数据"""
    print("\n" + "="*60)
    print(f"【测试3】生成数据: {domain}, {count}条, mode={mode}, quality={quality_mode}")
    print("="*60)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    data = {
        'domain': domain,
        'count': count,
        'mode': mode,
        'quality_mode': quality_mode,
        'format': 'json'
    }
    
    result = make_request(f"{BASE_URL}/generate", data, headers)
    
    if result.get('task_id'):
        task_id = result['task_id']
        print(f"✅ 任务创建成功: {task_id}")
        return task_id
    else:
        print(f"❌ 任务创建失败: {result.get('error', '未知错误')}")
        return None

def test_wait_task(task_id, timeout=120):
    """等待任务完成"""
    print("\n" + "="*60)
    print(f"【测试4】等待任务完成: {task_id}")
    print("="*60)
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        result = make_request(f"{BASE_URL}/task/{task_id}", method='GET')
        
        status = result.get('status', 'unknown')
        progress = result.get('progress', 0)
        
        print(f"   状态: {status:12} | 进度: {progress:3}%", end='\r')
        
        if status == 'completed':
            print(f"\n✅ 任务完成! 生成 {result.get('count', 0)} 条数据")
            return result
        elif status == 'failed':
            print(f"\n❌ 任务失败: {result.get('error', '未知错误')}")
            return result
        
        time.sleep(2)
    
    print(f"\n⏰ 等待超时")
    return {'status': 'timeout', 'error': '等待超时'}

def test_download(download_url, token):
    """测试下载"""
    print("\n" + "="*60)
    print("【测试5】下载数据")
    print("="*60)
    
    try:
        filename = download_url.split('/')[-1]
        encoded_filename = quote(filename, safe='')
        url = f"{BASE_URL}/download/{encoded_filename}"
        
        print(f"   文件名: {filename}")
        
        headers = {'Authorization': f'Bearer {token}'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=60) as response:
            content = response.read().decode('utf-8')
            data = json.loads(content)
            
            print(f"✅ 下载成功: {len(data)} 条数据")
            
            # 验证数据质量
            if data:
                print("\n" + "-"*60)
                print("数据预览 (前3条):")
                print("-"*60)
                for i, item in enumerate(data[:3], 1):
                    text = item.get('text', '')
                    quality = item.get('quality_score', 'N/A')
                    print(f"\n[{i}] 质量: {quality}")
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"    内容: {preview}")
                
                # 统计
                scores = [item.get('quality_score', 0) for item in data if 'quality_score' in item]
                if scores:
                    avg_score = sum(scores) / len(scores)
                    high_quality = sum(1 for s in scores if s >= 0.75)
                    print(f"\n" + "-"*60)
                    print(f"质量统计:")
                    print(f"  - 平均质量: {avg_score:.2f}")
                    print(f"  - 高质量(>=0.75): {high_quality}/{len(scores)} ({high_quality/len(scores)*100:.1f}%)")
                
                return True, data
            else:
                print("⚠️  数据为空")
                return False, None
    
    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")
        return False, None

def main():
    """主测试流程"""
    print("\n" + "="*70)
    print(" PureData 系统完整流程测试 ")
    print(" 验证修复后的系统是否正常运行 ")
    print("="*70)
    
    # 测试配置
    username = f"test_user_{int(time.time())}"
    password = "Test123456"
    email = f"{username}@test.com"
    domain = "金融"
    count = 10
    mode = "clean"
    quality_mode = "high"
    
    print(f"\n测试配置:")
    print(f"  - 用户名: {username}")
    print(f"  - 领域: {domain}")
    print(f"  - 数量: {count}条")
    print(f"  - 模式: {mode}")
    print(f"  - 质量: {quality_mode}")
    
    # 1. 注册
    if not test_register(username, password, email):
        print("\n❌ 注册失败，测试终止")
        return False
    
    # 2. 登录
    token = test_login(username, password)
    if not token:
        print("\n❌ 登录失败，测试终止")
        return False
    
    # 3. 生成数据
    task_id = test_generate_data(domain, count, mode, quality_mode, token)
    if not task_id:
        print("\n❌ 任务创建失败，测试终止")
        return False
    
    # 4. 等待任务
    task_result = test_wait_task(task_id)
    if task_result.get('status') != 'completed':
        print("\n❌ 任务执行失败，测试终止")
        return False
    
    # 5. 下载数据
    download_url = task_result.get('download_url', '')
    if not download_url:
        print("\n❌ 无下载链接，测试终止")
        return False
    
    success, data = test_download(download_url, token)
    if not success:
        print("\n❌ 下载失败，测试终止")
        return False
    
    # 测试通过
    print("\n" + "="*70)
    print(" ✅ 所有测试通过！系统运行正常 ")
    print("="*70)
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
