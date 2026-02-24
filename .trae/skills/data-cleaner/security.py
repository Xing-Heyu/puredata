#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全防护模块
包含：反爬虫、限流、认证、加密、日志审计
"""

import hashlib
import hmac
import time
import json
import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
import secrets

# ============ 配置 ============

SECURITY_CONFIG = {
    # API限流
    "rate_limit": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "requests_per_day": 10000
    },
    
    # 反爬虫
    "anti_crawler": {
        "enabled": True,
        "block_duration": 3600,  # 封禁时长（秒）
        "suspicious_threshold": 100,  # 可疑请求阈值
        "ban_threshold": 200  # 封禁阈值
    },
    
    # Token配置
    "token": {
        "expire_hours": 24,
        "refresh_hours": 72
    },
    
    # 加密密钥（生产环境应从环境变量读取）
    "secret_key": os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
}

# ============ 数据库初始化 ============

def init_security_db():
    """初始化安全数据库"""
    conn = sqlite3.connect("security.db")
    c = conn.cursor()
    
    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        api_key TEXT UNIQUE,
        plan TEXT DEFAULT 'basic',
        created_at DATETIME,
        expire_at DATETIME
    )''')
    
    # 访问日志表
    c.execute('''CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        ip_address TEXT,
        endpoint TEXT,
        request_count INTEGER DEFAULT 1,
        first_access DATETIME,
        last_access DATETIME
    )''')
    
    # 封禁表
    c.execute('''CREATE TABLE IF NOT EXISTS bans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT,
        reason TEXT,
        banned_at DATETIME,
        expire_at DATETIME
    )''')
    
    # Token表
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        created_at DATETIME,
        expire_at DATETIME,
        is_active INTEGER DEFAULT 1
    )''')
    
    conn.commit()
    conn.close()

# ============ 密码加密 ============

def hash_password(password, salt=None):
    """密码哈希"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hashed.hex()}"

def verify_password(password, stored_hash):
    """验证密码"""
    salt, hashed = stored_hash.split(':')
    new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hmac.compare_digest(hashed.encode(), new_hash.hex().encode())

# ============ API Key管理 ============

def generate_api_key():
    """生成API Key"""
    return f"sk-{secrets.token_urlsafe(32)}"

def create_user(username, password, plan='basic'):
    """创建用户"""
    conn = sqlite3.connect("security.db")
    c = conn.cursor()
    
    password_hash = hash_password(password)
    api_key = generate_api_key()
    
    try:
        c.execute('''INSERT INTO users (username, password_hash, api_key, plan, created_at, expire_at)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (username, password_hash, api_key, plan, 
                   datetime.now().isoformat(),
                   (datetime.now() + timedelta(days=30)).isoformat()))
        conn.commit()
        return {"username": username, "api_key": api_key}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def validate_api_key(api_key):
    """验证API Key"""
    conn = sqlite3.connect("security.db")
    c = conn.cursor()
    
    c.execute('''SELECT id, plan, expire_at FROM users WHERE api_key=?''', (api_key,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return None
    
    user_id, plan, expire_at = row
    if datetime.fromisoformat(expire_at) < datetime.now():
        return None
    
    return {"user_id": user_id, "plan": plan}

# ============ 限流机制 ============

class RateLimiter:
    """限流器"""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(self, key, limit, window_seconds):
        """检查是否允许请求"""
        now = time.time()
        requests = self.requests[key]
        
        # 清理过期请求
        self.requests[key] = [t for t in requests if now - t < window_seconds]
        
        if len(self.requests[key]) >= limit:
            return False
        
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key, limit, window_seconds):
        """获取剩余请求次数"""
        now = time.time()
        requests = self.requests[key]
        self.requests[key] = [t for t in requests if now - t < window_seconds]
        return max(0, limit - len(self.requests[key]))

rate_limiter = RateLimiter()

# ============ 反爬虫机制 ============

class AntiCrawler:
    """反爬虫"""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.suspicious_ips = set()
        self.banned_ips = set()
    
    def check_request(self, ip_address, user_agent=""):
        """检查请求是否可疑"""
        # 检查是否已封禁
        if ip_address in self.banned_ips:
            return False, "IP已封禁"
        
        # 检查User-Agent
        suspicious_agents = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget']
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            self.suspicious_ips.add(ip_address)
            return False, "可疑User-Agent"
        
        # 检查请求频率
        self.request_counts[ip_address] += 1
        
        if self.request_counts[ip_address] > SECURITY_CONFIG["anti_crawler"]["ban_threshold"]:
            self.banned_ips.add(ip_address)
            self._log_ban(ip_address, "请求频率过高")
            return False, "请求频率过高，已封禁"
        
        if self.request_counts[ip_address] > SECURITY_CONFIG["anti_crawler"]["suspicious_threshold"]:
            self.suspicious_ips.add(ip_address)
            return True, "警告：请求频率较高"
        
        return True, "正常"
    
    def _log_ban(self, ip_address, reason):
        """记录封禁"""
        conn = sqlite3.connect("security.db")
        c = conn.cursor()
        c.execute('''INSERT INTO bans (ip_address, reason, banned_at, expire_at)
                     VALUES (?, ?, ?, ?)''',
                  (ip_address, reason, datetime.now().isoformat(),
                   (datetime.now() + timedelta(seconds=SECURITY_CONFIG["anti_crawler"]["block_duration"])).isoformat()))
        conn.commit()
        conn.close()
    
    def is_banned(self, ip_address):
        """检查IP是否被封禁"""
        conn = sqlite3.connect("security.db")
        c = conn.cursor()
        c.execute('''SELECT 1 FROM bans WHERE ip_address=? AND expire_at>?''',
                  (ip_address, datetime.now().isoformat()))
        banned = c.fetchone() is not None
        conn.close()
        return banned

anti_crawler = AntiCrawler()

# ============ 数据加密 ============

def encrypt_data(data, key=None):
    """简单加密（生产环境应使用专业加密库）"""
    key = key or SECURITY_CONFIG["secret_key"]
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)
    
    # 简单的XOR加密（演示用，生产环境请用cryptography库）
    encrypted = []
    for i, char in enumerate(data):
        key_char = key[i % len(key)]
        encrypted.append(chr(ord(char) ^ ord(key_char)))
    
    return ''.join(encrypted)

def decrypt_data(encrypted, key=None):
    """解密"""
    return encrypt_data(encrypted, key)  # XOR加密是对称的

# ============ 日志审计 ============

def log_access(user_id, ip_address, endpoint, success=True):
    """记录访问日志"""
    conn = sqlite3.connect("security.db")
    c = conn.cursor()
    
    # 查找现有记录
    c.execute('''SELECT id, request_count FROM access_logs 
                 WHERE user_id=? AND ip_address=? AND endpoint=? 
                 AND date(first_access) = date('now')''',
              (user_id, ip_address, endpoint))
    row = c.fetchone()
    
    if row:
        # 更新现有记录
        c.execute('''UPDATE access_logs 
                     SET request_count = request_count + 1, last_access = ?
                     WHERE id = ?''',
                  (datetime.now().isoformat(), row[0]))
    else:
        # 创建新记录
        c.execute('''INSERT INTO access_logs (user_id, ip_address, endpoint, first_access, last_access)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, ip_address, endpoint, datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# ============ 装饰器 ============

def require_auth(func):
    """认证装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = kwargs.get('api_key') or (args[0] if args else None)
        
        if not api_key:
            return {"error": "缺少API Key"}
        
        user = validate_api_key(api_key)
        if not user:
            return {"error": "无效的API Key"}
        
        kwargs['user'] = user
        return func(*args, **kwargs)
    
    return wrapper

def rate_limit(limit_type='minute'):
    """限流装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.get('user', {})
            user_id = user.get('user_id', 'anonymous')
            
            limits = {
                'minute': (SECURITY_CONFIG["rate_limit"]["requests_per_minute"], 60),
                'hour': (SECURITY_CONFIG["rate_limit"]["requests_per_hour"], 3600),
                'day': (SECURITY_CONFIG["rate_limit"]["requests_per_day"], 86400)
            }
            
            limit, window = limits.get(limit_type, (60, 60))
            key = f"{user_id}:{limit_type}"
            
            if not rate_limiter.is_allowed(key, limit, window):
                remaining = rate_limiter.get_remaining(key, limit, window)
                return {"error": f"请求过于频繁，请稍后再试", "remaining": remaining}
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# ============ 主程序 ============

if __name__ == '__main__':
    init_security_db()
    
    print("\n" + "="*50)
    print("安全模块测试")
    print("="*50)
    
    # 测试用户创建
    print("\n1. 创建测试用户...")
    user = create_user("test_user", "password123", "pro")
    if user:
        print(f"   用户名: {user['username']}")
        print(f"   API Key: {user['api_key']}")
    
    # 测试限流
    print("\n2. 测试限流...")
    for i in range(5):
        allowed = rate_limiter.is_allowed("test_key", 3, 60)
        print(f"   请求 {i+1}: {'允许' if allowed else '拒绝'}")
    
    # 测试反爬虫
    print("\n3. 测试反爬虫...")
    result, msg = anti_crawler.check_request("192.168.1.1", "Mozilla/5.0")
    print(f"   正常请求: {msg}")
    
    result, msg = anti_crawler.check_request("192.168.1.2", "Googlebot")
    print(f"   爬虫请求: {msg}")
    
    print("\n" + "="*50)
    print("安全模块已就绪")
    print("="*50)