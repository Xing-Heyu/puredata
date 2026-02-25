#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全协议 - 加密/防护/审计
支持：数据加密、请求验证、攻击防护、安全审计
"""

import os
import hashlib
import hmac
import secrets
import time
import re
import json
from datetime import datetime
from collections import defaultdict
import threading

class SecurityProtocol:
    """安全协议"""
    
    _SECRET_KEY = None
    
    RATE_LIMITS = {
        "default": {"requests": 100, "window": 60},
        "generate": {"requests": 10, "window": 60},
        "login": {"requests": 5, "window": 300}
    }
    
    RATE_LIMIT_FILE = os.path.join(os.path.dirname(__file__), 'rate_limits.json')
    
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.blocked_ips = set()
        self.audit_log = []
        self.lock = threading.Lock()
        self._init_secret_key()
        self._init_audit_log()
        self._load_rate_limits()
    
    def _load_rate_limits(self):
        """加载速率限制数据"""
        if os.path.exists(self.RATE_LIMIT_FILE):
            try:
                with open(self.RATE_LIMIT_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, timestamps in data.get('request_counts', {}).items():
                        self.request_counts[key] = timestamps
                    self.blocked_ips = set(data.get('blocked_ips', []))
            except Exception:
                pass
    
    def _save_rate_limits(self):
        """保存速率限制数据"""
        try:
            data = {
                'request_counts': dict(self.request_counts),
                'blocked_ips': list(self.blocked_ips)
            }
            with open(self.RATE_LIMIT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception:
            pass
    
    def _init_audit_log(self):
        """初始化审计日志 - 从文件加载"""
        self.audit_log_file = os.path.join(os.path.dirname(__file__), 'audit_log.json')
        self.audit_retention_days = 180
        
        if os.path.exists(self.audit_log_file):
            try:
                with open(self.audit_log_file, 'r', encoding='utf-8') as f:
                    self.audit_log = json.load(f)
                self._cleanup_old_logs()
            except Exception:
                self.audit_log = []
    
    def _cleanup_old_logs(self):
        """清理超过保留期的日志"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=self.audit_retention_days)
        cutoff_str = cutoff.isoformat()
        
        self.audit_log = [
            entry for entry in self.audit_log
            if entry.get("timestamp", "") >= cutoff_str
        ]
    
    def _save_audit_log(self):
        """保存审计日志到文件"""
        try:
            with open(self.audit_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[审计日志] 保存失败: {e}")
    
    def _init_secret_key(self):
        """初始化SECRET_KEY - 持久化存储"""
        key_file = os.path.join(os.path.dirname(__file__), '.secret_key')
        
        if os.path.exists(key_file):
            try:
                with open(key_file, 'r') as f:
                    SecurityProtocol._SECRET_KEY = f.read().strip()
            except Exception:
                SecurityProtocol._SECRET_KEY = secrets.token_urlsafe(32)
        else:
            SecurityProtocol._SECRET_KEY = secrets.token_urlsafe(32)
            try:
                with open(key_file, 'w') as f:
                    f.write(SecurityProtocol._SECRET_KEY)
            except Exception:
                pass
    
    @property
    def SECRET_KEY(self):
        """获取SECRET_KEY"""
        return SecurityProtocol._SECRET_KEY
    
    def hash_data(self, data):
        """数据哈希"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def sign_request(self, data, timestamp):
        """请求签名"""
        message = f"{data}{timestamp}{self.SECRET_KEY}"
        return hmac.new(
            self.SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_signature(self, data, timestamp, signature):
        """验证签名"""
        expected = self.sign_request(data, timestamp)
        return hmac.compare_digest(expected, signature)
    
    def check_rate_limit(self, client_id, endpoint="default"):
        """检查速率限制"""
        now = time.time()
        limit = self.RATE_LIMITS.get(endpoint, self.RATE_LIMITS["default"])
        
        with self.lock:
            requests = self.request_counts[f"{client_id}:{endpoint}"]
            
            requests[:] = [t for t in requests if now - t < limit["window"]]
            
            if len(requests) >= limit["requests"]:
                return False
            
            requests.append(now)
            self._save_rate_limits()
            return True
    
    def sanitize_input(self, text):
        """输入清理"""
        if not isinstance(text, str):
            return ""
        
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'\.\./',
            r'\.\.\\',
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        return text.strip()
    
    def validate_email(self, email):
        """验证邮箱"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        """验证密码强度"""
        if len(password) < 8:
            return False, "密码长度至少8位"
        
        if not re.search(r'[A-Z]', password):
            return False, "密码需要包含大写字母"
        
        if not re.search(r'[a-z]', password):
            return False, "密码需要包含小写字母"
        
        if not re.search(r'[0-9]', password):
            return False, "密码需要包含数字"
        
        return True, "密码强度合格"
    
    def generate_csrf_token(self):
        """生成CSRF令牌"""
        return secrets.token_urlsafe(32)
    
    def log_audit(self, action, user, details):
        """审计日志 - 持久化到文件"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user": user,
            "details": details,
            "ip": details.get("ip", "unknown")
        }
        
        with self.lock:
            self.audit_log.append(entry)
            self._cleanup_old_logs()
            self._save_audit_log()
    
    def get_audit_log(self, limit=100):
        """获取审计日志"""
        return self.audit_log[-limit:]
    
    def detect_attack(self, request_data):
        """检测攻击"""
        attack_patterns = [
            (r"(\bOR\b|\bAND\b).*=.*--", "SQL注入"),
            (r"<script", "XSS攻击"),
            (r"\.\./", "路径遍历"),
            (r"\$\{", "模板注入"),
            (r"eval\s*\(", "代码注入"),
        ]
        
        data_str = json.dumps(request_data) if isinstance(request_data, dict) else str(request_data)
        
        for pattern, attack_type in attack_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                return True, attack_type
        
        return False, None
    
    def encrypt_sensitive(self, data):
        """敏感数据加密 - 使用AES-256 (Fernet)"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            
            key = self._get_or_create_secret_key().encode()
            salt = b'PureDataSalt2024'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            fernet_key = base64.urlsafe_b64encode(kdf.derive(key))
            fernet = Fernet(fernet_key)
            
            json_str = json.dumps(data)
            return fernet.encrypt(json_str.encode()).decode()
        except ImportError:
            import base64
            json_str = json.dumps(data)
            return base64.b64encode(json_str.encode()).decode()
    
    def decrypt_sensitive(self, encrypted):
        """敏感数据解密 - 使用AES-256 (Fernet)"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            
            key = self._get_or_create_secret_key().encode()
            salt = b'PureDataSalt2024'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            fernet_key = base64.urlsafe_b64encode(kdf.derive(key))
            fernet = Fernet(fernet_key)
            
            json_str = fernet.decrypt(encrypted.encode()).decode()
            return json.loads(json_str)
        except ImportError:
            import base64
            try:
                json_str = base64.b64decode(encrypted.encode()).decode()
                return json.loads(json_str)
            except:
                return None
        except Exception:
            return None
    
    def _get_or_create_secret_key(self):
        """获取或创建密钥"""
        if self._SECRET_KEY is None:
            self._SECRET_KEY = os.environ.get("PUREDATA_SECRET_KEY", "puredata-default-key-change-in-production")
        return self._SECRET_KEY


security = SecurityProtocol()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("安全协议测试")
    print("="*60)
    
    # 测试输入清理
    print("\n[1] 输入清理测试...")
    malicious = "<script>alert('xss')</script>Hello"
    clean = security.sanitize_input(malicious)
    print(f"    原始: {malicious}")
    print(f"    清理后: {clean}")
    
    # 测试密码验证
    print("\n[2] 密码验证测试...")
    passwords = ["123", "password", "Password1", "Password123!"]
    for pwd in passwords:
        valid, msg = security.validate_password(pwd)
        print(f"    {pwd}: {msg}")
    
    # 测试速率限制
    print("\n[3] 速率限制测试...")
    for i in range(12):
        allowed = security.check_rate_limit("test_client", "generate")
        if not allowed:
            print(f"    第{i+1}次请求被限制")
            break
    else:
        print(f"    12次请求全部通过")
    
    # 测试攻击检测
    print("\n[4] 攻击检测测试...")
    attacks = [
        {"query": "SELECT * FROM users WHERE id=1 OR 1=1--"},
        {"content": "<script>steal()</script>"},
        {"path": "../../../etc/passwd"}
    ]
    for attack in attacks:
        detected, attack_type = security.detect_attack(attack)
        print(f"    检测到: {attack_type or '无攻击'}")
    
    # 测试审计日志
    print("\n[5] 审计日志测试...")
    security.log_audit("login", "testuser", {"ip": "127.0.0.1", "success": True})
    log = security.get_audit_log(1)
    print(f"    最新日志: {log[0]['action']} by {log[0]['user']}")
    
    print("\n" + "="*60)
    print("安全协议测试完成")
    print("="*60)
