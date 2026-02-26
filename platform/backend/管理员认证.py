#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理员认证系统 - 基于配置文件的管理员账户管理
支持：配置文件管理、登录验证、会话管理、IP白名单
"""

import json
import os
import hashlib
import secrets
import time
from datetime import datetime, timedelta
import threading

from password_validator import PasswordValidator

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ADMIN_CONFIG_FILE = os.path.join(BACKEND_DIR, '管理员配置.json')
ADMIN_SESSIONS_FILE = os.path.join(BACKEND_DIR, 'admin_sessions.json')

class AdminAuthManager:
    """管理员认证管理器"""
    
    SESSION_TIMEOUT_HOURS = 24
    
    def __init__(self):
        self.config = {}
        self.sessions = {}
        self.lock = threading.Lock()
        self._load_config()
        self._load_sessions()
    
    def _load_config(self):
        """加载管理员配置"""
        if os.path.exists(ADMIN_CONFIG_FILE):
            with open(ADMIN_CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "admins": [],
                "settings": {
                    "session_timeout_hours": 24,
                    "require_2fa": False,
                    "allowed_ip_whitelist": []
                }
            }
            self._save_config()
        
        self.SESSION_TIMEOUT_HOURS = self.config.get("settings", {}).get("session_timeout_hours", 24)
        
        self._init_admin_passwords()
    
    def _save_config(self):
        """保存管理员配置"""
        config_to_save = {k: v for k, v in self.config.items() if not k.startswith('_')}
        with open(ADMIN_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_to_save, f, ensure_ascii=False, indent=2)
    
    def _load_sessions(self):
        """加载会话"""
        if os.path.exists(ADMIN_SESSIONS_FILE):
            with open(ADMIN_SESSIONS_FILE, 'r', encoding='utf-8') as f:
                self.sessions = json.load(f)
    
    def _save_sessions(self):
        """保存会话"""
        with open(ADMIN_SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password):
        """密码哈希 - bcrypt优先，SHA256回退"""
        if BCRYPT_AVAILABLE:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password, password_hash):
        """验证密码 - 支持bcrypt和SHA256"""
        if BCRYPT_AVAILABLE and password_hash.startswith('$2b$'):
            try:
                return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            except Exception:
                return False
        return password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_password(self, length=16):
        """生成随机密码"""
        return secrets.token_urlsafe(length)
    
    def _init_admin_passwords(self):
        """初始化管理员密码"""
        admins = self.config.get("admins", [])
        has_changes = False
        
        if not admins:
            admins.append({
                "username": "admin",
                "password_hash": self._hash_password("PureData@2026"),
                "email": "admin@datagenpro.com",
                "created_at": datetime.now().isoformat(),
                "last_login": "",
                "note": "默认管理员账户",
                "failed_attempts": 0,
                "locked_until": None
            })
            has_changes = True
            
            print("\n" + "="*60)
            print("✅ 管理员账户已就绪")
            print("="*60)
            print(f"用户名: admin")
            print(f"密码: PureData@2026")
            print("="*60 + "\n")
        else:
            for admin in admins:
                if not admin.get("password_hash"):
                    admin["password_hash"] = self._hash_password("PureData@2026")
                    admin["created_at"] = admin.get("created_at") or datetime.now().isoformat()
                    has_changes = True
        
        self.config["admins"] = admins
        if has_changes:
            self._save_config()
    
    def check_ip_allowed(self, client_ip):
        """检查IP是否允许访问 - 默认拒绝，仅允许白名单IP"""
        whitelist = self.config.get("settings", {}).get("allowed_ip_whitelist", [])
        if not whitelist:
            return True
        if not client_ip:
            return False
        return client_ip in whitelist
    
    def login(self, username, password, client_ip=""):
        """管理员登录 - 带失败锁定机制"""
        if not self.check_ip_allowed(client_ip):
            return {"success": False, "error": "IP不在白名单中", "code": "IP_NOT_ALLOWED"}
        
        admins = self.config.get("admins", [])
        admin = None
        admin_index = -1
        for i, a in enumerate(admins):
            if a.get("username") == username:
                admin = a
                admin_index = i
                break
        
        if not admin:
            return {"success": False, "error": "用户名或密码错误", "code": "INVALID_CREDENTIALS"}
        
        if admin.get("locked_until"):
            locked_until = datetime.fromisoformat(admin["locked_until"])
            if datetime.now() < locked_until:
                remaining = (locked_until - datetime.now()).seconds // 60
                return {"success": False, "error": f"账户已锁定，请{remaining}分钟后再试", "code": "ACCOUNT_LOCKED"}
            else:
                admin["locked_until"] = None
                admin["failed_attempts"] = 0
        
        if not self._verify_password(password, admin.get("password_hash", "")):
            failed_attempts = admin.get("failed_attempts", 0) + 1
            admin["failed_attempts"] = failed_attempts
            
            if failed_attempts >= 5:
                lock_duration = min(30, 5 * (2 ** (failed_attempts - 5)))
                admin["locked_until"] = (datetime.now() + timedelta(minutes=lock_duration)).isoformat()
                self._save_config()
                return {"success": False, "error": f"登录失败次数过多，账户已锁定{lock_duration}分钟", "code": "ACCOUNT_LOCKED"}
            
            self._save_config()
            remaining = 5 - failed_attempts
            return {"success": False, "error": f"用户名或密码错误，剩余{remaining}次尝试", "code": "INVALID_CREDENTIALS"}
        
        admin["failed_attempts"] = 0
        admin["locked_until"] = None
        
        token = secrets.token_urlsafe(32)
        
        self.sessions[token] = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=self.SESSION_TIMEOUT_HOURS)).isoformat(),
            "client_ip": client_ip
        }
        
        admin["last_login"] = datetime.now().isoformat()
        self._save_config()
        self._save_sessions()
        
        return {
            "success": True,
            "token": token,
            "user": {
                "username": username,
                "email": admin.get("email", ""),
                "role": "admin"
            },
            "expires_in": self.SESSION_TIMEOUT_HOURS * 3600
        }
    
    def logout(self, token):
        """登出"""
        with self.lock:
            if token in self.sessions:
                del self.sessions[token]
                self._save_sessions()
                return {"success": True}
            return {"success": False, "error": "无效的令牌"}
    
    def validate_token(self, token):
        """验证令牌"""
        with self.lock:
            if token not in self.sessions:
                return None
            
            session = self.sessions[token]
            expires_at = datetime.fromisoformat(session["expires_at"])
            
            if datetime.now() > expires_at:
                del self.sessions[token]
                self._save_sessions()
                return None
            
            admins = self.config.get("admins", [])
            for admin in admins:
                if admin.get("username") == session["username"]:
                    return {
                        "username": admin.get("username"),
                        "email": admin.get("email", ""),
                        "role": "admin"
                    }
            
            return None
    
    def change_password(self, username, old_password, new_password):
        """修改密码"""
        with self.lock:
            admins = self.config.get("admins", [])
            
            for admin in admins:
                if admin.get("username") == username:
                    if not self._verify_password(old_password, admin.get("password_hash", "")):
                        return {"success": False, "error": "旧密码错误"}
                    
                    pwd_result = PasswordValidator.validate_success_dict(new_password)
                    if not pwd_result["success"]:
                        return pwd_result
                    
                    admin["password_hash"] = self._hash_password(new_password)
                    admin["password_changed_at"] = datetime.now().isoformat()
                    self._save_config()
                    
                    return {"success": True, "message": "密码修改成功"}
            
            return {"success": False, "error": "用户不存在"}
    
    def add_admin(self, username, password, email=""):
        """添加管理员"""
        with self.lock:
            admins = self.config.get("admins", [])
            
            for admin in admins:
                if admin.get("username") == username:
                    return {"success": False, "error": "用户名已存在"}
            
            pwd_result = PasswordValidator.validate_success_dict(password)
            if not pwd_result["success"]:
                return pwd_result
            
            admins.append({
                "username": username,
                "password_hash": self._hash_password(password),
                "email": email,
                "created_at": datetime.now().isoformat(),
                "last_login": ""
            })
            
            self.config["admins"] = admins
            self._save_config()
            
            return {"success": True, "message": f"管理员 '{username}' 添加成功"}
    
    def delete_admin(self, username):
        """删除管理员"""
        with self.lock:
            admins = self.config.get("admins", [])
            
            if len(admins) <= 1:
                return {"success": False, "error": "至少保留一个管理员账户"}
            
            new_admins = [a for a in admins if a.get("username") != username]
            
            if len(new_admins) == len(admins):
                return {"success": False, "error": "管理员不存在"}
            
            self.config["admins"] = new_admins
            self._save_config()
            
            for token, session in list(self.sessions.items()):
                if session.get("username") == username:
                    del self.sessions[token]
            self._save_sessions()
            
            return {"success": True, "message": f"管理员 '{username}' 已删除"}
    
    def list_admins(self):
        """列出所有管理员"""
        admins = self.config.get("admins", [])
        result = []
        for admin in admins:
            result.append({
                "username": admin.get("username"),
                "email": admin.get("email", ""),
                "created_at": admin.get("created_at", ""),
                "last_login": admin.get("last_login", "")
            })
        return result
    
    def get_settings(self):
        """获取安全设置"""
        return self.config.get("settings", {})
    
    def update_settings(self, settings):
        """更新安全设置"""
        with self.lock:
            current = self.config.get("settings", {})
            current.update(settings)
            self.config["settings"] = current
            self._save_config()
            return {"success": True, "message": "设置已更新"}


admin_auth = AdminAuthManager()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("管理员认证系统测试")
    print("="*60)
    
    print("\n[1] 管理员列表:")
    admins = admin_auth.list_admins()
    for a in admins:
        print(f"    - {a['username']} ({a['email']})")
    
    print("\n[2] 测试登录:")
    result = admin_auth.login("admin", "wrong_password")
    print(f"    错误密码: {result}")
    
    print("\n" + "="*60)
