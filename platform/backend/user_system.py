#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户系统 - 注册/登录/UAC
支持：用户管理、权限控制、会话管理
"""

import json
import os
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from enum import Enum
import threading

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

# 配置
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DB_FILE = os.path.join(BACKEND_DIR, 'users.json')
SESSION_FILE = os.path.join(BACKEND_DIR, 'sessions.json')

class UserRole(Enum):
    """用户角色"""
    ADMIN = "admin"
    DEVELOPER = "developer"
    PREMIUM = "premium"
    STANDARD = "standard"
    FREE = "free"

class Permission(Enum):
    """权限枚举"""
    GENERATE_DATA = "generate_data"
    GENERATE_SEQUENCE = "generate_sequence"
    GENERATE_AI_FORMAT = "generate_ai_format"
    CREATE_TEMPLATE = "create_template"
    VIEW_STATS = "view_stats"
    MANAGE_USERS = "manage_users"
    EXPORT_DATA = "export_data"
    API_ACCESS = "api_access"
    QUALITY_CONTROL = "quality_control"
    HIGH_QUALITY = "high_quality"
    FREE_QUALITY = "free_quality"
    MEDIUM_QUALITY = "medium_quality"
    ROBUSTNESS_QUALITY = "robustness_quality"

ROLE_PERMISSIONS = {
    UserRole.ADMIN: [p for p in Permission],
    UserRole.PREMIUM: [
        Permission.GENERATE_DATA,
        Permission.GENERATE_SEQUENCE,
        Permission.GENERATE_AI_FORMAT,
        Permission.CREATE_TEMPLATE,
        Permission.VIEW_STATS,
        Permission.EXPORT_DATA,
        Permission.API_ACCESS,
        Permission.QUALITY_CONTROL,
        Permission.HIGH_QUALITY,
        Permission.FREE_QUALITY,
        Permission.MEDIUM_QUALITY,
        Permission.ROBUSTNESS_QUALITY
    ],
    UserRole.STANDARD: [
        Permission.GENERATE_DATA,
        Permission.GENERATE_SEQUENCE,
        Permission.VIEW_STATS,
        Permission.EXPORT_DATA,
        Permission.API_ACCESS,
        Permission.FREE_QUALITY,
        Permission.MEDIUM_QUALITY
    ],
    UserRole.FREE: [
        Permission.GENERATE_DATA,
        Permission.VIEW_STATS,
        Permission.FREE_QUALITY
    ]
}

QUALITY_LEVEL_PERMISSIONS = {
    "high_quality": Permission.HIGH_QUALITY,
    "free_quality": Permission.FREE_QUALITY,
    "medium_quality": Permission.MEDIUM_QUALITY,
    "robustness_quality": Permission.ROBUSTNESS_QUALITY
}

from pricing_config import ROLE_QUOTA_LIMITS, ROLE_OVERAGE_PRICES

QUOTA_LIMITS = {
    UserRole.ADMIN: ROLE_QUOTA_LIMITS["admin"],
    UserRole.PREMIUM: ROLE_QUOTA_LIMITS["premium"],
    UserRole.STANDARD: ROLE_QUOTA_LIMITS["standard"],
    UserRole.FREE: ROLE_QUOTA_LIMITS["free"]
}

OVERAGE_PRICES = {
    UserRole.PREMIUM: ROLE_OVERAGE_PRICES["premium"],
    UserRole.STANDARD: ROLE_OVERAGE_PRICES["standard"],
    UserRole.FREE: ROLE_OVERAGE_PRICES["free"]
}

INVITE_REWARD = 500
INVITE_MAX_COUNT = 10
FREE_QUOTA = 1000

TASK_REWARDS = {
    "generate_1000": {"type": "quota", "amount": 500, "name": "生成满1000条"},
    "try_3_domains": {"type": "priority", "amount": 1, "name": "体验3个不同领域"},
    "use_api": {"type": "template", "amount": 1, "name": "试用API"}
}

class UserManager:
    """用户管理器"""
    
    SESSION_TIMEOUT = int(os.environ.get("SESSION_TIMEOUT", "3600"))  # 可配置，默认1小时
    
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.lock = threading.Lock()
        self._load()
    
    def _load(self):
        """加载用户数据 - 带异常处理"""
        # 加载用户数据库
        if os.path.exists(USER_DB_FILE):
            try:
                with open(USER_DB_FILE, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] 加载用户数据库失败: {e}")
                self.users = {}
        
        # 加载会话数据
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] 加载会话数据失败: {e}")
                self.sessions = {}
        
        # 如果没有用户，创建默认管理员
        if not self.users:
            self._create_default_admin()
    
    def _save(self):
        """保存用户数据 - 带异常处理"""
        try:
            with open(USER_DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] 保存用户数据库失败: {e}")
        
        try:
            with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] 保存会话数据失败: {e}")
    
    def _create_default_admin(self):
        """创建默认管理员"""
        self.users["admin"] = {
            "username": "admin",
            "password_hash": self._hash_password("PureData@2026"),
            "role": UserRole.ADMIN.value,
            "email": "admin@datagenpro.com",
            "created_at": datetime.now().isoformat(),
            "quota_used": {"daily": 0, "monthly": 0, "total": 0},
            "quota_reset": datetime.now().isoformat(),
            "free_quota": 999999999,
            "invite_code": "ADMIN001",
            "invited_by": None,
            "invite_count": 0,
            "invite_quota_earned": 0,
            "tasks_completed": [],
            "domains_tried": [],
            "is_developer": True
        }
        
        self._save()
        
        print("="*60)
        print("✅ 管理员账户已就绪")
        print("="*60)
        print("用户名: admin")
        print("密码: PureData@2026")
        print("额度: 无限")
        print("="*60)
    
    def _hash_password(self, password):
        """密码哈希 - 强制使用bcrypt"""
        if not BCRYPT_AVAILABLE:
            raise RuntimeError("bcrypt库未安装，请运行: pip install bcrypt")
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def _verify_password(self, password, password_hash):
        """验证密码 - 强制使用bcrypt"""
        if not BCRYPT_AVAILABLE:
            raise RuntimeError("bcrypt库未安装，请运行: pip install bcrypt")
        if not password_hash.startswith('$2b$'):
            raise ValueError("无效的密码哈希格式，请重置密码")
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    
    def _generate_token(self):
        """生成会话令牌"""
        return secrets.token_urlsafe(32)
    
    def register(self, username, password, email='', phone='', role=UserRole.FREE, invite_code=None, email_verified=False):
        with self.lock:
            if username in self.users:
                return {"success": False, "error": "用户名已存在"}
            
            if not email:
                return {"success": False, "error": "请填写邮箱地址"}
            
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return {"success": False, "error": "邮箱格式不正确"}
            
            for u in self.users.values():
                if u.get('email') == email:
                    return {"success": False, "error": "邮箱已被注册"}
            
            if phone:
                for u in self.users.values():
                    if u.get('phone') == phone:
                        return {"success": False, "error": "手机号已被注册"}
            
            if len(password) < 8:
                return {"success": False, "error": "密码长度至少8位"}
            
            if not re.search(r'[A-Z]', password):
                return {"success": False, "error": "密码需包含大写字母"}
            
            if not re.search(r'[a-z]', password):
                return {"success": False, "error": "密码需包含小写字母"}
            
            if not re.search(r'\d', password):
                return {"success": False, "error": "密码需包含数字"}
            
            invite_code_user = self._generate_invite_code(username)
            
            user = {
                "username": username,
                "password_hash": self._hash_password(password),
                "role": role.value,
                "email": email,
                "email_verified": email_verified,
                "phone": phone,
                "created_at": datetime.now().isoformat(),
                "quota_used": {"daily": 0, "monthly": 0, "total": 0},
                "quota_reset": datetime.now().isoformat(),
                "free_quota": FREE_QUOTA,
                "invite_code": invite_code_user,
                "invited_by": None,
                "invite_count": 0,
                "invite_quota_earned": 0,
                "tasks_completed": [],
                "domains_tried": [],
                "login_attempts": 0,
                "locked_until": None
            }
            
            bonus_message = ""
            if invite_code:
                inviter = self._find_user_by_invite_code(invite_code)
                if inviter and inviter["invite_count"] < INVITE_MAX_COUNT:
                    user["invited_by"] = inviter["username"]
                    user["free_quota"] += INVITE_REWARD
                    inviter["invite_count"] += 1
                    inviter["invite_quota_earned"] += INVITE_REWARD
                    inviter["free_quota"] = inviter.get("free_quota", FREE_QUOTA) + INVITE_REWARD
                    bonus_message = f"，邀请奖励+{INVITE_REWARD}条"
            
            self.users[username] = user
            
            token = self._generate_token()
            self.sessions[token] = {
                "username": username,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(seconds=self.SESSION_TIMEOUT)).isoformat()
            }
            
            self._save()
            
            return {
                "success": True, 
                "message": f"注册成功，赠送{FREE_QUOTA}条免费额度{bonus_message}",
                "token": token,
                "user": {
                    "username": username,
                    "email": email,
                    "role": role.value
                },
                "free_quota": user["free_quota"],
                "invite_code": invite_code_user
            }
    
    def _generate_invite_code(self, username):
        import hashlib
        hash_input = f"{username}{datetime.now().timestamp()}{secrets.token_hex(4)}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8].upper()
    
    def _find_user_by_invite_code(self, invite_code):
        for user in self.users.values():
            if user.get("invite_code") == invite_code:
                return user
        return None
    
    def login(self, username, password):
        """用户登录"""
        with self.lock:
            if username not in self.users:
                return {"success": False, "error": "用户名或密码错误"}
            
            user = self.users[username]
            
            locked_until_str = user.get("locked_until")
            if locked_until_str:
                try:
                    locked_until = datetime.fromisoformat(locked_until_str)
                    if datetime.now() < locked_until:
                        remaining = int((locked_until - datetime.now()).total_seconds() / 60)
                        return {"success": False, "error": f"账户已锁定，请{remaining}分钟后再试"}
                    else:
                        user["locked_until"] = None
                        user["login_attempts"] = 0
                except (ValueError, TypeError):
                    # 如果日期解析失败，清除锁定状态
                    user["locked_until"] = None
                    user["login_attempts"] = 0
            
            if not self._verify_password(password, user["password_hash"]):
                user["login_attempts"] = user.get("login_attempts", 0) + 1
                
                if user["login_attempts"] >= 5:
                    user["locked_until"] = (datetime.now() + timedelta(minutes=30)).isoformat()
                    self._save()
                    return {"success": False, "error": "密码错误次数过多，账户已锁定30分钟"}
                
                self._save()
                remaining = 5 - user["login_attempts"]
                return {"success": False, "error": f"用户名或密码错误，还剩{remaining}次机会"}
            
            user["login_attempts"] = 0
            user["locked_until"] = None
            
            token = self._generate_token()
            
            self.sessions[token] = {
                "username": username,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(seconds=self.SESSION_TIMEOUT)).isoformat()
            }
            
            self._save()
            
            return {
                "success": True,
                "token": token,
                "user": {
                    "username": username,
                    "role": user["role"],
                    "email": user["email"],
                    "email_verified": user.get("email_verified", False)
                }
            }
    
    def logout(self, token):
        """用户登出"""
        with self.lock:
            if token in self.sessions:
                del self.sessions[token]
                self._save()
                return {"success": True}
            return {"success": False, "error": "无效的令牌"}
    
    def request_password_reset(self, email):
        """请求重置密码 - 发送验证码到邮箱"""
        with self.lock:
            user = None
            for u in self.users.values():
                if u.get("email") == email:
                    user = u
                    break
            
            if not user:
                return {"success": False, "error": "该邮箱未注册"}
            
            from otp_manager import OTPManager, OTPType, OTPChannel
            otp_manager = OTPManager()
            
            result = otp_manager.send_code(
                target=email,
                otp_type=OTPType.RESET_PASSWORD.value,
                channel=OTPChannel.EMAIL.value
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"验证码已发送到 {self._mask_email(email)}",
                    "username": user["username"]
                }
            else:
                return {"success": False, "error": result.get("error", "发送验证码失败")}
    
    def reset_password(self, email, code, new_password):
        """重置密码 - 验证验证码并设置新密码"""
        with self.lock:
            user = None
            for u in self.users.values():
                if u.get("email") == email:
                    user = u
                    break
            
            if not user:
                return {"success": False, "error": "该邮箱未注册"}
            
            from otp_manager import OTPManager, OTPType
            otp_manager = OTPManager()
            
            result = otp_manager.verify_code(
                target=email,
                code=code,
                otp_type=OTPType.RESET_PASSWORD.value
            )
            
            if not result["success"]:
                return {"success": False, "error": result.get("error", "验证码错误")}
            
            import re
            if len(new_password) < 8:
                return {"success": False, "error": "密码长度至少8位"}
            
            if not re.search(r'[A-Z]', new_password):
                return {"success": False, "error": "密码需包含大写字母"}
            
            if not re.search(r'[a-z]', new_password):
                return {"success": False, "error": "密码需包含小写字母"}
            
            if not re.search(r'\d', new_password):
                return {"success": False, "error": "密码需包含数字"}
            
            user["password_hash"] = self._hash_password(new_password)
            user["login_attempts"] = 0
            user["locked_until"] = None
            
            username = user["username"]
            tokens_to_remove = [t for t, s in self.sessions.items() if s.get("username") == username]
            for t in tokens_to_remove:
                del self.sessions[t]
            
            self._save()
            
            return {"success": True, "message": "密码重置成功，请重新登录"}
    
    def verify_email(self, email, code):
        """验证邮箱"""
        with self.lock:
            user = None
            for u in self.users.values():
                if u.get("email") == email:
                    user = u
                    break
            
            if not user:
                return {"success": False, "error": "该邮箱未注册"}
            
            from otp_manager import OTPManager, OTPType
            otp_manager = OTPManager()
            
            result = otp_manager.verify_code(
                target=email,
                code=code,
                otp_type=OTPType.REGISTER.value
            )
            
            if not result["success"]:
                return {"success": False, "error": result.get("error", "验证码错误")}
            
            user["email_verified"] = True
            self._save()
            
            return {"success": True, "message": "邮箱验证成功"}
    
    def _mask_email(self, email):
        if "@" in email:
            parts = email.split("@")
            if len(parts[0]) > 2:
                return parts[0][:2] + "***@" + parts[1]
            return "***@" + parts[1]
        return email
    
    def validate_token(self, token):
        """验证令牌"""
        if token not in self.sessions:
            return None
        
        session = self.sessions[token]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            del self.sessions[token]
            self._save()
            return None
        
        return self.users.get(session["username"])
    
    def check_permission(self, username, permission):
        """检查权限"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        role = UserRole(user["role"])
        
        return permission in ROLE_PERMISSIONS.get(role, [])
    
    def check_quality_permission(self, username, quality_level: str) -> tuple:
        """
        检查质量等级权限
        
        Args:
            username: 用户名
            quality_level: 质量等级 (high_quality, medium_quality, low_quality)
            
        Returns:
            (是否有权限, 错误信息)
        """
        if username not in self.users:
            return False, "用户不存在"
        
        user = self.users[username]
        role = UserRole(user["role"])
        
        permission = QUALITY_LEVEL_PERMISSIONS.get(quality_level)
        if not permission:
            return False, f"未知的质量等级: {quality_level}"
        
        if permission in ROLE_PERMISSIONS.get(role, []):
            return True, None
        
        role_names = {
            UserRole.ADMIN: "管理员",
            UserRole.PREMIUM: "高级用户",
            UserRole.STANDARD: "标准用户",
            UserRole.FREE: "免费用户"
        }
        
        quality_names = {
            "high_quality": "高质量(≥0.85分)",
            "free_quality": "免费试用质量(0.80-0.85分)",
            "medium_quality": "普通质量(0.75-0.80分)",
            "robustness_quality": "鲁棒性测试质量(<0.75分)"
        }
        
        required_roles = {
            "high_quality": ["管理员", "高级用户"],
            "free_quality": ["管理员", "高级用户", "标准用户", "免费用户"],
            "medium_quality": ["管理员", "高级用户", "标准用户"],
            "robustness_quality": ["管理员", "高级用户"]
        }
        
        error_msg = f"您的等级({role_names[role]})无法使用{quality_names[quality_level]}。"
        error_msg += f"需要: {', '.join(required_roles[quality_level])}"
        
        return False, error_msg
    
    def get_available_quality_levels(self, username) -> list:
        """获取用户可用的质量等级"""
        if username not in self.users:
            return ["low_quality"]
        
        user = self.users[username]
        role = UserRole(user["role"])
        permissions = ROLE_PERMISSIONS.get(role, [])
        
        available = []
        for level, perm in QUALITY_LEVEL_PERMISSIONS.items():
            if perm in permissions:
                available.append(level)
        
        return available
    
    def check_quota(self, username, amount=1):
        if username not in self.users:
            return False
        
        user = self.users[username]
        role = UserRole(user["role"])
        
        if role == UserRole.FREE:
            free_quota = user.get("free_quota", FREE_QUOTA)
            total_used = user["quota_used"].get("total", 0)
            return total_used + amount <= free_quota
        
        limits = QUOTA_LIMITS.get(role, QUOTA_LIMITS[UserRole.FREE])
        self._reset_quota_if_needed(user)
        
        if user["quota_used"]["daily"] + amount > limits["daily"]:
            return False
        
        if user["quota_used"]["monthly"] + amount > limits["monthly"]:
            return False
        
        return True
    
    def use_quota(self, username, amount=1, domain=None):
        with self.lock:
            if username not in self.users:
                return False
            
            user = self.users[username]
            role = UserRole(user["role"])
            
            if role == UserRole.FREE:
                user["quota_used"]["total"] = user["quota_used"].get("total", 0) + amount
                user["quota_used"]["daily"] = user["quota_used"].get("daily", 0) + amount
                user["quota_used"]["monthly"] = user["quota_used"].get("monthly", 0) + amount
                
                if domain and domain not in user.get("domains_tried", []):
                    user["domains_tried"] = user.get("domains_tried", []) + [domain]
                
                self._check_tasks(user)
                self._save()
                return True
            
            self._reset_quota_if_needed(user)
            
            user["quota_used"]["daily"] += amount
            user["quota_used"]["monthly"] += amount
            user["quota_used"]["total"] = user["quota_used"].get("total", 0) + amount
            
            self._save()
            return True
    
    def add_paid_quota(self, username: str, quota: int) -> Dict:
        """添加付费配额"""
        with self.lock:
            if username not in self.users:
                return {"success": False, "error": "用户不存在"}
            
            user = self.users[username]
            user["paid_quota"] = user.get("paid_quota", 0) + quota
            user["total_paid"] = user.get("total_paid", 0) + quota
            
            self._save()
            return {"success": True, "paid_quota": user["paid_quota"], "added": quota}
    
    def _check_tasks(self, user):
        total_used = user["quota_used"].get("total", 0)
        domains_tried = user.get("domains_tried", [])
        tasks_completed = user.get("tasks_completed", [])
        
        if total_used >= 1000 and "generate_1000" not in tasks_completed:
            user["free_quota"] = user.get("free_quota", FREE_QUOTA) + 500
            user["tasks_completed"] = tasks_completed + ["generate_1000"]
        
        if len(domains_tried) >= 3 and "try_3_domains" not in tasks_completed:
            user["tasks_completed"] = tasks_completed + ["try_3_domains"]
    
    def _reset_quota_if_needed(self, user):
        """重置配额"""
        reset_time_str = user.get("quota_reset")
        if not reset_time_str:
            # 如果没有重置时间，设置为当前时间
            user["quota_reset"] = datetime.now().isoformat()
            return
        
        try:
            reset_time = datetime.fromisoformat(reset_time_str)
        except (ValueError, TypeError):
            # 如果日期解析失败，重置为当前时间
            user["quota_reset"] = datetime.now().isoformat()
            return
        
        now = datetime.now()
        
        if now.date() > reset_time.date():
            user["quota_used"]["daily"] = 0
        
        if now.month != reset_time.month:
            user["quota_used"]["monthly"] = 0
        
        user["quota_reset"] = now.isoformat()
    
    def get_user_info(self, username):
        if username not in self.users:
            return None
        
        user = self.users[username]
        role = UserRole(user["role"])
        limits = QUOTA_LIMITS.get(role, QUOTA_LIMITS[UserRole.FREE])
        
        self._reset_quota_if_needed(user)
        
        return {
            "username": username,
            "email": user["email"],
            "role": user["role"],
            "permissions": [p.value for p in ROLE_PERMISSIONS.get(role, [])],
            "quota": {
                "used": user["quota_used"],
                "limit": limits,
                "free_quota": user.get("free_quota", 0)
            },
            "created_at": user["created_at"],
            "is_developer": user.get("is_developer", False)
        }
    
    def get_quota_status(self, username):
        if username not in self.users:
            return None
        
        user = self.users[username]
        role = UserRole(user["role"])
        
        if role == UserRole.FREE:
            free_quota = user.get("free_quota", FREE_QUOTA)
            total_used = user["quota_used"].get("total", 0)
            remaining = max(0, free_quota - total_used)
            percent = round((total_used / free_quota) * 100, 1) if free_quota > 0 else 0
            
            warning_level = "normal"
            if remaining <= 0:
                warning_level = "exhausted"
            elif remaining <= 50:
                warning_level = "critical"
            elif remaining <= 200:
                warning_level = "warning"
            
            return {
                "username": username,
                "role": role.value,
                "plan_name": "体验版",
                "is_free": True,
                "free_quota": free_quota,
                "used": total_used,
                "remaining": remaining,
                "percent": percent,
                "warning_level": warning_level,
                "overage_price": 0.08,
                "invite_code": user.get("invite_code", ""),
                "invite_count": user.get("invite_count", 0),
                "invite_quota_earned": user.get("invite_quota_earned", 0),
                "tasks_completed": user.get("tasks_completed", []),
                "domains_tried": user.get("domains_tried", [])
            }
        
        limits = QUOTA_LIMITS.get(role, QUOTA_LIMITS[UserRole.FREE])
        self._reset_quota_if_needed(user)
        
        daily_used = user["quota_used"]["daily"]
        monthly_used = user["quota_used"]["monthly"]
        daily_limit = limits["daily"]
        monthly_limit = limits["monthly"]
        
        daily_percent = round((daily_used / daily_limit) * 100, 1) if daily_limit > 0 else 0
        monthly_percent = round((monthly_used / monthly_limit) * 100, 1) if monthly_limit > 0 else 0
        
        warning_level = "normal"
        if monthly_percent >= 90:
            warning_level = "critical"
        elif monthly_percent >= 75:
            warning_level = "warning"
        
        overage_price = OVERAGE_PRICES.get(role, 0.08)
        
        return {
            "username": username,
            "role": role.value,
            "daily": {
                "used": daily_used,
                "limit": daily_limit,
                "remaining": max(0, daily_limit - daily_used),
                "percent": daily_percent
            },
            "monthly": {
                "used": monthly_used,
                "limit": monthly_limit,
                "remaining": max(0, monthly_limit - monthly_used),
                "percent": monthly_percent
            },
            "warning_level": warning_level,
            "overage_price": overage_price,
            "plan_name": self._get_plan_name(role),
            "is_free": False
        }
    
    def _get_plan_name(self, role):
        plan_names = {
            UserRole.ADMIN: "企业版",
            UserRole.PREMIUM: "企业版",
            UserRole.STANDARD: "专业版",
            UserRole.FREE: "基础版"
        }
        return plan_names.get(role, "免费版")
    
    def change_password(self, username, old_password, new_password):
        """修改密码"""
        with self.lock:
            if username not in self.users:
                return {"success": False, "error": "用户不存在"}
            
            user = self.users[username]
            
            if not self._verify_password(old_password, user["password_hash"]):
                return {"success": False, "error": "旧密码错误"}
            
            if len(new_password) < 8:
                return {"success": False, "error": "新密码长度至少8位"}
            
            user["password_hash"] = self._hash_password(new_password)
            self._save()
            
            return {"success": True, "message": "密码修改成功"}
    
    def upgrade_role(self, username, new_role):
        """升级角色"""
        with self.lock:
            if username not in self.users:
                return {"success": False, "error": "用户不存在"}
            
            self.users[username]["role"] = new_role.value
            self._save()
            
            return {"success": True, "message": f"已升级为 {new_role.value}"}


# 全局用户管理器
user_manager = UserManager()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("用户系统测试")
    print("="*60)
    
    # 测试注册
    print("\n[1] 测试注册...")
    result = user_manager.register("testuser", "password123", "test@example.com")
    print(f"    注册结果: {result}")
    
    # 测试登录
    print("\n[2] 测试登录...")
    result = user_manager.login("testuser", "password123")
    print(f"    登录结果: {result.get('success')}")
    
    if result.get("success"):
        token = result["token"]
        
        # 测试权限
        print("\n[3] 测试权限...")
        has_perm = user_manager.check_permission("testuser", Permission.GENERATE_DATA)
        print(f"    生成数据权限: {has_perm}")
        
        # 测试配额
        print("\n[4] 测试配额...")
        has_quota = user_manager.check_quota("testuser", 10)
        print(f"    配额检查: {has_quota}")
        
        # 获取用户信息
        print("\n[5] 用户信息...")
        info = user_manager.get_user_info("testuser")
        print(f"    角色: {info['role']}")
        print(f"    权限: {len(info['permissions'])}个")
        print(f"    日配额: {info['quota']['limit']['daily']}")
    
    print("\n" + "="*60)
    print("用户系统测试完成")
    print("="*60)
