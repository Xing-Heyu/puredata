#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商业化风控系统 - 完整防护方案
包含: API限流、数据加密、审计日志、成本控制、自动熔断
"""

import time
import json
import os
import hashlib
import secrets
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from enum import Enum
import base64

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
RISK_CONTROL_FILE = os.path.join(BACKEND_DIR, 'risk_control.json')


class RateLimitType(Enum):
    IP = "ip"
    USER = "user"
    API = "api"
    GLOBAL = "global"


class RateLimiter:
    """API限流器 - 多维度限流"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked = defaultdict(float)
        self.lock = threading.Lock()
        
        self.limits = {
            RateLimitType.IP: {"requests": 100, "window": 60},
            RateLimitType.USER: {"requests": 50, "window": 60},
            RateLimitType.API: {
                "generate": {"requests": 10, "window": 60},
                "download": {"requests": 30, "window": 60},
                "register": {"requests": 3, "window": 3600},
                "login": {"requests": 10, "window": 300},
            },
            RateLimitType.GLOBAL: {"requests": 1000, "window": 60},
        }
        
        self.premium_multipliers = {
            "free": 1.0,
            "premium": 3.0,
            "enterprise": 10.0,
        }
    
    def _clean_old_requests(self, key: str, window: int):
        now = time.time()
        self.requests[key] = [t for t in self.requests[key] if now - t < window]
    
    def is_allowed(self, identifier: str, limit_type: RateLimitType, 
                   api_name: str = None, user_role: str = "free") -> Dict:
        with self.lock:
            now = time.time()
            
            if identifier in self.blocked:
                if now < self.blocked[identifier]:
                    return {
                        "allowed": False,
                        "reason": "暂时被封禁",
                        "retry_after": int(self.blocked[identifier] - now)
                    }
                else:
                    del self.blocked[identifier]
            
            if limit_type == RateLimitType.API and api_name:
                limit_config = self.limits[RateLimitType.API].get(api_name, {"requests": 60, "window": 60})
            else:
                limit_config = self.limits[limit_type]
            
            max_requests = limit_config["requests"]
            window = limit_config["window"]
            
            multiplier = self.premium_multipliers.get(user_role, 1.0)
            max_requests = int(max_requests * multiplier)
            
            key = f"{limit_type.value}:{identifier}"
            if api_name:
                key = f"{limit_type.value}:{api_name}:{identifier}"
            
            self._clean_old_requests(key, window)
            
            current_count = len(self.requests[key])
            
            if current_count >= max_requests:
                oldest = min(self.requests[key]) if self.requests[key] else now
                retry_after = int(window - (now - oldest))
                return {
                    "allowed": False,
                    "reason": f"请求过于频繁，请{retry_after}秒后再试",
                    "retry_after": max(retry_after, 1),
                    "current": current_count,
                    "limit": max_requests
                }
            
            self.requests[key].append(now)
            
            return {
                "allowed": True,
                "current": current_count + 1,
                "limit": max_requests,
                "remaining": max_requests - current_count - 1
            }
    
    def block(self, identifier: str, duration: int = 300, reason: str = "异常行为"):
        with self.lock:
            self.blocked[identifier] = time.time() + duration
        return {"blocked": True, "duration": duration, "reason": reason}
    
    def unblock(self, identifier: str):
        with self.lock:
            if identifier in self.blocked:
                del self.blocked[identifier]
        return {"unblocked": True}
    
    def get_stats(self, identifier: str = None) -> Dict:
        with self.lock:
            now = time.time()
            stats = {
                "active_keys": len(self.requests),
                "blocked_count": len(self.blocked),
                "blocked_entities": []
            }
            
            for blocked_id, expire_time in self.blocked.items():
                if identifier is None or identifier in blocked_id:
                    stats["blocked_entities"].append({
                        "identifier": blocked_id,
                        "expires_in": int(expire_time - now)
                    })
            
            return stats


class DataEncryptor:
    """数据加密器 - 敏感数据保护"""
    
    def __init__(self, secret_key: str = None):
        if secret_key is None:
            secret_key = os.environ.get("DATAGEN_SECRET_KEY")
            if not secret_key:
                import secrets
                secret_key = secrets.token_urlsafe(32)
                print("[WARNING] DATAGEN_SECRET_KEY not set, using random key. Set environment variable for production!")
        
        self.secret_key = secret_key
        self._fernet = None
        
        if CRYPTO_AVAILABLE:
            self._init_fernet()
    
    def _init_fernet(self):
        key = self.secret_key.encode()
        salt = b'DataGenProSalt2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key))
        self._fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        if CRYPTO_AVAILABLE and self._fernet:
            return self._fernet.encrypt(data.encode()).decode()
        else:
            return base64.b64encode(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        if CRYPTO_AVAILABLE and self._fernet:
            return self._fernet.decrypt(encrypted_data.encode()).decode()
        else:
            return base64.b64decode(encrypted_data.encode()).decode()
    
    def hash_password(self, password: str, salt: str = None) -> Dict:
        if salt is None:
            salt = secrets.token_hex(16)
        
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
        
        return {"hash": hashed, "salt": salt}
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        result = self.hash_password(password, salt)
        return secrets.compare_digest(result["hash"], hashed)
    
    def mask_email(self, email: str) -> str:
        if '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked = local[0] + '***'
        else:
            masked = local[0] + '***' + local[-1]
        
        return f"{masked}@{domain}"
    
    def mask_phone(self, phone: str) -> str:
        if len(phone) < 7:
            return phone
        return phone[:3] + '****' + phone[-4:]
    
    def mask_id_card(self, id_card: str) -> str:
        if len(id_card) < 8:
            return id_card
        return id_card[:4] + '**********' + id_card[-4:]
    
    def mask_bank_card(self, card: str) -> str:
        if len(card) < 8:
            return card
        return card[:4] + '****' + card[-4:]


class AuditLogger:
    """审计日志 - 操作追踪和合规"""
    
    def __init__(self):
        self.logs = []
        self.lock = threading.Lock()
        self.max_logs = 10000
        
        self.sensitive_fields = [
            'password', 'token', 'secret', 'key', 'credit_card',
            'id_card', 'phone', 'email', 'address'
        ]
    
    def _sanitize(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                k: '***MASKED***' if k.lower() in self.sensitive_fields else self._sanitize(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._sanitize(item) for item in data]
        else:
            return data
    
    def log(self, action: str, user_id: str = None, ip: str = None,
            details: Dict = None, result: str = "success", risk_level: str = "low"):
        with self.lock:
            entry = {
                "id": secrets.token_hex(8),
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "user_id": user_id,
                "ip": ip,
                "details": self._sanitize(details) if details else None,
                "result": result,
                "risk_level": risk_level
            }
            
            self.logs.append(entry)
            
            if len(self.logs) > self.max_logs:
                self.logs = self.logs[-self.max_logs:]
            
            self._persist(entry)
        
        return entry["id"]
    
    def _persist(self, entry: Dict):
        log_file = os.path.join(BACKEND_DIR, 'audit_logs.jsonl')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def get_logs(self, user_id: str = None, action: str = None,
                 start_time: datetime = None, end_time: datetime = None,
                 risk_level: str = None, limit: int = 100) -> List[Dict]:
        with self.lock:
            filtered = list(self.logs)
        
        if user_id:
            filtered = [l for l in filtered if l.get('user_id') == user_id]
        if action:
            filtered = [l for l in filtered if l.get('action') == action]
        if risk_level:
            filtered = [l for l in filtered if l.get('risk_level') == risk_level]
        if start_time:
            filtered = [l for l in filtered if datetime.fromisoformat(l['timestamp']) >= start_time]
        if end_time:
            filtered = [l for l in filtered if datetime.fromisoformat(l['timestamp']) <= end_time]
        
        return filtered[-limit:]
    
    def get_user_activity_summary(self, user_id: str) -> Dict:
        user_logs = [l for l in self.logs if l.get('user_id') == user_id]
        
        actions = defaultdict(int)
        for log in user_logs:
            actions[log.get('action', 'unknown')] += 1
        
        ips = set(l.get('ip') for l in user_logs if l.get('ip'))
        
        return {
            "user_id": user_id,
            "total_actions": len(user_logs),
            "action_breakdown": dict(actions),
            "unique_ips": len(ips),
            "last_activity": user_logs[-1]['timestamp'] if user_logs else None
        }


class CostController:
    """成本控制 - 资源消耗监控"""
    
    def __init__(self):
        self.usage = defaultdict(lambda: {
            "generate_count": 0,
            "total_records": 0,
            "storage_bytes": 0,
            "api_calls": 0,
            "compute_time": 0.0
        })
        self.lock = threading.Lock()
        
        self.costs = {
            "generate_per_1000": 0.01,
            "storage_per_gb": 0.10,
            "api_call_per_1000": 0.001,
            "compute_per_hour": 0.50
        }
        
        self.limits = {
            "free": {"daily_records": 1000, "storage_mb": 100},
            "premium": {"daily_records": 50000, "storage_mb": 5000},
            "enterprise": {"daily_records": 1000000, "storage_mb": 50000}
        }
    
    def record_usage(self, user_id: str, records: int = 0, 
                     storage_bytes: int = 0, api_calls: int = 0,
                     compute_time: float = 0):
        with self.lock:
            usage = self.usage[user_id]
            usage["generate_count"] += 1
            usage["total_records"] += records
            usage["storage_bytes"] += storage_bytes
            usage["api_calls"] += api_calls
            usage["compute_time"] += compute_time
    
    def check_limit(self, user_id: str, user_role: str, 
                    requested_records: int = 0) -> Dict:
        limits = self.limits.get(user_role, self.limits["free"])
        usage = self.usage.get(user_id, {})
        
        daily_records = usage.get("total_records", 0)
        storage_mb = usage.get("storage_bytes", 0) / (1024 * 1024)
        
        result = {"allowed": True, "limits": limits, "current": {}}
        
        if daily_records + requested_records > limits["daily_records"]:
            result["allowed"] = False
            result["reason"] = f"每日记录数限制 ({limits['daily_records']})"
        
        if storage_mb > limits["storage_mb"]:
            result["allowed"] = False
            result["reason"] = f"存储空间限制 ({limits['storage_mb']}MB)"
        
        result["current"] = {
            "daily_records": daily_records,
            "storage_mb": round(storage_mb, 2)
        }
        
        return result
    
    def calculate_cost(self, user_id: str) -> Dict:
        with self.lock:
            usage = self.usage.get(user_id, {})
        
        records_cost = (usage.get("total_records", 0) / 1000) * self.costs["generate_per_1000"]
        storage_cost = (usage.get("storage_bytes", 0) / (1024**3)) * self.costs["storage_per_gb"]
        api_cost = (usage.get("api_calls", 0) / 1000) * self.costs["api_call_per_1000"]
        compute_cost = (usage.get("compute_time", 0) / 3600) * self.costs["compute_per_hour"]
        
        total = records_cost + storage_cost + api_cost + compute_cost
        
        return {
            "user_id": user_id,
            "breakdown": {
                "records": round(records_cost, 4),
                "storage": round(storage_cost, 4),
                "api": round(api_cost, 4),
                "compute": round(compute_cost, 4)
            },
            "total": round(total, 4),
            "usage": usage
        }
    
    def get_usage_report(self, user_id: str = None) -> Dict:
        with self.lock:
            if user_id:
                return {user_id: dict(self.usage.get(user_id, {}))}
            return {k: dict(v) for k, v in self.usage.items()}


class CircuitBreaker:
    """熔断器 - 自动保护"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.states = {}
        self.lock = threading.Lock()
    
    def _get_state(self, service: str) -> Dict:
        if service not in self.states:
            self.states[service] = {
                "status": "closed",
                "failures": 0,
                "last_failure": None,
                "opened_at": None
            }
        return self.states[service]
    
    def is_available(self, service: str) -> bool:
        with self.lock:
            state = self._get_state(service)
            
            if state["status"] == "closed":
                return True
            
            if state["status"] == "open":
                if state["opened_at"]:
                    elapsed = time.time() - state["opened_at"]
                    if elapsed >= self.recovery_timeout:
                        state["status"] = "half_open"
                        return True
                return False
            
            if state["status"] == "half_open":
                return True
        
        return True
    
    def record_success(self, service: str):
        with self.lock:
            state = self._get_state(service)
            state["failures"] = 0
            state["status"] = "closed"
    
    def record_failure(self, service: str):
        with self.lock:
            state = self._get_state(service)
            state["failures"] += 1
            state["last_failure"] = datetime.now().isoformat()
            
            if state["failures"] >= self.failure_threshold:
                state["status"] = "open"
                state["opened_at"] = time.time()
    
    def get_status(self, service: str = None) -> Dict:
        with self.lock:
            if service:
                return {service: self._get_state(service)}
            return {k: dict(v) for k, v in self.states.items()}


class RiskControlSystem:
    """风控系统 - 统一入口"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.encryptor = DataEncryptor()
        self.audit_logger = AuditLogger()
        self.cost_controller = CostController()
        self.circuit_breaker = CircuitBreaker()
        
        self.suspicious_patterns = [
            {"pattern": "rapid_requests", "threshold": 50, "window": 10},
            {"pattern": "failed_logins", "threshold": 5, "window": 300},
            {"pattern": "large_requests", "threshold": 10000, "window": 60},
        ]
    
    def check_request(self, ip: str, user_id: str = None, 
                      api_name: str = None, user_role: str = "free") -> Dict:
        result = {"allowed": True, "checks": {}}
        
        ip_check = self.rate_limiter.is_allowed(ip, RateLimitType.IP, user_role=user_role)
        result["checks"]["ip_rate"] = ip_check
        if not ip_check["allowed"]:
            result["allowed"] = False
            result["reason"] = ip_check["reason"]
            return result
        
        if user_id:
            user_check = self.rate_limiter.is_allowed(user_id, RateLimitType.USER, user_role=user_role)
            result["checks"]["user_rate"] = user_check
            if not user_check["allowed"]:
                result["allowed"] = False
                result["reason"] = user_check["reason"]
                return result
        
        if api_name:
            api_check = self.rate_limiter.is_allowed(
                ip, RateLimitType.API, api_name=api_name, user_role=user_role
            )
            result["checks"]["api_rate"] = api_check
            if not api_check["allowed"]:
                result["allowed"] = False
                result["reason"] = api_check["reason"]
                return result
        
        return result
    
    def log_action(self, action: str, user_id: str = None, ip: str = None,
                   details: Dict = None, result: str = "success"):
        risk_level = "low"
        
        high_risk_actions = ["login_failed", "register", "payment", "api_key_create", "data_export"]
        if action in high_risk_actions:
            risk_level = "medium"
        
        if result == "failed":
            risk_level = "high"
        
        return self.audit_logger.log(action, user_id, ip, details, result, risk_level)
    
    def check_cost(self, user_id: str, user_role: str, 
                   requested_records: int = 0) -> Dict:
        return self.cost_controller.check_limit(user_id, user_role, requested_records)
    
    def calculate_cost(self, user_id: str) -> Dict:
        return self.cost_controller.calculate_cost(user_id)
    
    def record_usage(self, user_id: str, records: int = 0, 
                     storage_bytes: int = 0, api_calls: int = 0,
                     compute_time: float = 0):
        self.cost_controller.record_usage(user_id, records, storage_bytes, api_calls, compute_time)
    
    def encrypt_sensitive(self, data: str) -> str:
        return self.encryptor.encrypt(data)
    
    def decrypt_sensitive(self, encrypted_data: str) -> str:
        return self.encryptor.decrypt(encrypted_data)
    
    def mask_data(self, data_type: str, value: str) -> str:
        if data_type == "email":
            return self.encryptor.mask_email(value)
        elif data_type == "phone":
            return self.encryptor.mask_phone(value)
        elif data_type == "id_card":
            return self.encryptor.mask_id_card(value)
        elif data_type == "bank_card":
            return self.encryptor.mask_bank_card(value)
        return value
    
    def check_service(self, service: str) -> bool:
        return self.circuit_breaker.is_available(service)
    
    def record_service_result(self, service: str, success: bool):
        if success:
            self.circuit_breaker.record_success(service)
        else:
            self.circuit_breaker.record_failure(service)
    
    def get_dashboard(self) -> Dict:
        return {
            "rate_limiting": self.rate_limiter.get_stats(),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "cost_summary": self.cost_controller.get_usage_report(),
            "audit_summary": {
                "total_logs": len(self.audit_logger.logs),
                "recent_actions": [l["action"] for l in self.audit_logger.logs[-10:]]
            }
        }


risk_control = RiskControlSystem()


def rate_limit(api_name: str = None):
    """限流装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            ip = kwargs.get('ip', 'unknown')
            user_id = kwargs.get('user_id')
            user_role = kwargs.get('user_role', 'free')
            
            check = risk_control.check_request(ip, user_id, api_name, user_role)
            
            if not check["allowed"]:
                return {
                    "success": False,
                    "error": check["reason"],
                    "retry_after": check.get("retry_after", 60)
                }
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def audit_action(action: str):
    """审计装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            ip = kwargs.get('ip')
            
            try:
                result = func(*args, **kwargs)
                risk_control.log_action(action, user_id, ip, 
                                       {"args": str(args)[:200]}, "success")
                return result
            except Exception as e:
                risk_control.log_action(action, user_id, ip,
                                       {"error": str(e)}, "failed")
                raise
        return wrapper
    return decorator


if __name__ == "__main__":
    print("\n" + "="*60)
    print("商业化风控系统测试")
    print("="*60)
    
    print("\n[1] API限流测试...")
    for i in range(12):
        result = risk_control.check_request("192.168.1.100", "user_001", "generate", "free")
        if not result["allowed"]:
            print(f"  第{i+1}次请求: 被限流 - {result['reason']}")
            break
    else:
        print(f"  前12次请求全部通过")
    
    print("\n[2] 数据加密测试...")
    original = "敏感数据123456"
    encrypted = risk_control.encrypt_sensitive(original)
    decrypted = risk_control.decrypt_sensitive(encrypted)
    print(f"  原文: {original}")
    print(f"  加密: {encrypted[:30]}...")
    print(f"  解密: {decrypted}")
    
    print("\n[3] 数据脱敏测试...")
    print(f"  邮箱: {risk_control.mask_data('email', 'user@example.com')}")
    print(f"  手机: {risk_control.mask_data('phone', '13812345678')}")
    print(f"  身份证: {risk_control.mask_data('id_card', '110101199001011234')}")
    print(f"  银行卡: {risk_control.mask_data('bank_card', '6222021234567890123')}")
    
    print("\n[4] 审计日志测试...")
    log_id = risk_control.log_action("login", "user_001", "192.168.1.100", {"method": "password"}, "success")
    print(f"  日志ID: {log_id}")
    logs = risk_control.audit_logger.get_logs(user_id="user_001", limit=5)
    print(f"  用户日志数: {len(logs)}")
    
    print("\n[5] 成本控制测试...")
    risk_control.record_usage("user_001", records=100, storage_bytes=1024*1024, api_calls=5)
    cost = risk_control.calculate_cost("user_001")
    print(f"  使用量: {cost['usage']}")
    print(f"  费用: ${cost['total']}")
    
    limit_check = risk_control.check_cost("user_001", "free", 500)
    print(f"  限额检查: {'通过' if limit_check['allowed'] else '超限'}")
    
    print("\n[6] 熔断器测试...")
    for i in range(6):
        risk_control.record_service_result("generate_service", success=(i < 3))
        available = risk_control.check_service("generate_service")
        status = risk_control.circuit_breaker.get_status("generate_service")
        print(f"  第{i+1}次: available={available}, status={status['generate_service']['status']}")
    
    print("\n[7] 风控仪表盘...")
    dashboard = risk_control.get_dashboard()
    print(f"  限流统计: {dashboard['rate_limiting']}")
    print(f"  熔断状态: {dashboard['circuit_breaker']}")
    print(f"  审计日志数: {dashboard['audit_summary']['total_logs']}")
    
    print("\n" + "="*60)
    print("风控系统测试完成")
    print("="*60)
