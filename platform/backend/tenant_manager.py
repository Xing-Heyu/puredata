#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多租户隔离系统
功能：租户管理、数据隔离、权限校验、操作日志
"""

import json
import os
import threading
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from enum import Enum
from functools import wraps

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
TENANTS_FILE = os.path.join(BACKEND_DIR, 'tenants.json')
TENANT_LOGS_FILE = os.path.join(BACKEND_DIR, 'tenant_logs.json')


class TenantStatus(Enum):
    """租户状态"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TRIAL = "trial"


class TenantPlan(Enum):
    """租户套餐"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TENANT_LIMITS = {
    TenantPlan.FREE: {
        "max_users": 1,
        "max_tasks_per_day": 10,
        "max_data_per_month": 1000,
        "max_api_calls_per_day": 100,
        "storage_mb": 100,
    },
    TenantPlan.BASIC: {
        "max_users": 5,
        "max_tasks_per_day": 100,
        "max_data_per_month": 10000,
        "max_api_calls_per_day": 1000,
        "storage_mb": 1000,
    },
    TenantPlan.PRO: {
        "max_users": 20,
        "max_tasks_per_day": 500,
        "max_data_per_month": 100000,
        "max_api_calls_per_day": 10000,
        "storage_mb": 10000,
    },
    TenantPlan.ENTERPRISE: {
        "max_users": -1,
        "max_tasks_per_day": -1,
        "max_data_per_month": -1,
        "max_api_calls_per_day": -1,
        "storage_mb": -1,
    },
}


class TenantManager:
    """多租户管理器"""
    
    def __init__(self):
        self.tenants: Dict[str, Dict] = {}
        self.user_tenant_map: Dict[str, str] = {}
        self.lock = threading.Lock()
        self._load()
    
    def _load(self):
        """加载租户数据"""
        if os.path.exists(TENANTS_FILE):
            with open(TENANTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tenants = data.get("tenants", {})
                self.user_tenant_map = data.get("user_tenant_map", {})
    
    def _save(self):
        """保存租户数据"""
        with open(TENANTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "tenants": self.tenants,
                "user_tenant_map": self.user_tenant_map
            }, f, ensure_ascii=False, indent=2)
    
    def _generate_tenant_id(self) -> str:
        """生成租户ID"""
        return f"tenant_{secrets.token_hex(8)}"
    
    def create_tenant(self, name: str, plan: TenantPlan = TenantPlan.FREE, 
                      admin_user_id: str = None, contact_email: str = "",
                      contact_phone: str = "") -> Dict:
        """创建租户"""
        with self.lock:
            tenant_id = self._generate_tenant_id()
            
            now = datetime.now()
            expires_at = now + timedelta(days=30 if plan == TenantPlan.TRIAL else 365)
            
            self.tenants[tenant_id] = {
                "id": tenant_id,
                "name": name,
                "plan": plan.value,
                "status": TenantStatus.ACTIVE.value,
                "admin_user_id": admin_user_id,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "created_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "users": [admin_user_id] if admin_user_id else [],
                "usage": {
                    "tasks_today": 0,
                    "data_this_month": 0,
                    "api_calls_today": 0,
                    "storage_used_mb": 0,
                },
                "limits": TENANT_LIMITS.get(plan, TENANT_LIMITS[TenantPlan.FREE]),
                "settings": {
                    "allowed_domains": [],
                    "allowed_quality_modes": ["standard"],
                    "custom_branding": False,
                    "api_access": plan != TenantPlan.FREE,
                }
            }
            
            if admin_user_id:
                self.user_tenant_map[admin_user_id] = tenant_id
            
            self._save()
            
            return {"success": True, "tenant_id": tenant_id, "tenant": self.tenants[tenant_id]}
    
    def get_tenant(self, tenant_id: str) -> Optional[Dict]:
        """获取租户信息"""
        return self.tenants.get(tenant_id)
    
    def get_tenant_by_user(self, user_id: str) -> Optional[Dict]:
        """通过用户ID获取租户"""
        tenant_id = self.user_tenant_map.get(user_id)
        if tenant_id:
            return self.tenants.get(tenant_id)
        return None
    
    def add_user_to_tenant(self, user_id: str, tenant_id: str) -> Dict:
        """将用户添加到租户"""
        with self.lock:
            if tenant_id not in self.tenants:
                return {"success": False, "error": "租户不存在"}
            
            tenant = self.tenants[tenant_id]
            
            if user_id in self.user_tenant_map:
                return {"success": False, "error": "用户已属于其他租户"}
            
            limits = tenant.get("limits", {})
            max_users = limits.get("max_users", 1)
            if max_users > 0 and len(tenant.get("users", [])) >= max_users:
                return {"success": False, "error": "租户用户数已达上限"}
            
            tenant["users"].append(user_id)
            self.user_tenant_map[user_id] = tenant_id
            self._save()
            
            return {"success": True, "message": f"用户已添加到租户 {tenant['name']}"}
    
    def remove_user_from_tenant(self, user_id: str) -> Dict:
        """从租户移除用户"""
        with self.lock:
            tenant_id = self.user_tenant_map.get(user_id)
            if not tenant_id:
                return {"success": False, "error": "用户不属于任何租户"}
            
            tenant = self.tenants.get(tenant_id)
            if tenant:
                if user_id in tenant.get("users", []):
                    tenant["users"].remove(user_id)
                if tenant.get("admin_user_id") == user_id:
                    tenant["admin_user_id"] = None
            
            del self.user_tenant_map[user_id]
            self._save()
            
            return {"success": True, "message": "用户已从租户移除"}
    
    def check_permission(self, user_id: str, resource: str, action: str) -> Dict:
        """检查用户权限"""
        tenant = self.get_tenant_by_user(user_id)
        
        if not tenant:
            return {"allowed": False, "reason": "用户不属于任何租户"}
        
        if tenant.get("status") != TenantStatus.ACTIVE.value:
            return {"allowed": False, "reason": "租户已暂停或过期"}
        
        expires_at = datetime.fromisoformat(tenant.get("expires_at", "2099-12-31"))
        if datetime.now() > expires_at:
            return {"allowed": False, "reason": "租户已过期"}
        
        limits = tenant.get("limits", {})
        usage = tenant.get("usage", {})
        
        if resource == "task" and action == "create":
            max_tasks = limits.get("max_tasks_per_day", 10)
            if max_tasks > 0 and usage.get("tasks_today", 0) >= max_tasks:
                return {"allowed": False, "reason": "今日任务数已达上限"}
        
        elif resource == "data" and action == "generate":
            max_data = limits.get("max_data_per_month", 1000)
            if max_data > 0 and usage.get("data_this_month", 0) >= max_data:
                return {"allowed": False, "reason": "本月数据生成量已达上限"}
        
        elif resource == "api" and action == "call":
            max_calls = limits.get("max_api_calls_per_day", 100)
            if max_calls > 0 and usage.get("api_calls_today", 0) >= max_calls:
                return {"allowed": False, "reason": "今日API调用次数已达上限"}
        
        return {"allowed": True, "tenant_id": tenant["id"]}
    
    def record_usage(self, tenant_id: str, resource: str, amount: int = 1):
        """记录使用量"""
        with self.lock:
            if tenant_id not in self.tenants:
                return
            
            tenant = self.tenants[tenant_id]
            usage = tenant.get("usage", {})
            
            if resource == "task":
                usage["tasks_today"] = usage.get("tasks_today", 0) + amount
            elif resource == "data":
                usage["data_this_month"] = usage.get("data_this_month", 0) + amount
            elif resource == "api":
                usage["api_calls_today"] = usage.get("api_calls_today", 0) + amount
            
            tenant["usage"] = usage
            self._save()
    
    def log_tenant_action(self, tenant_id: str, user_id: str, action: str, 
                          details: Dict = None, ip: str = ""):
        """记录租户操作日志"""
        logs = self._load_logs()
        
        log_entry = {
            "id": secrets.token_hex(8),
            "tenant_id": tenant_id,
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "ip": ip,
            "timestamp": datetime.now().isoformat()
        }
        
        logs.append(log_entry)
        
        if len(logs) > 10000:
            logs = logs[-10000:]
        
        with open(TENANT_LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def _load_logs(self) -> List[Dict]:
        """加载租户日志"""
        if os.path.exists(TENANT_LOGS_FILE):
            with open(TENANT_LOGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def get_tenant_logs(self, tenant_id: str, limit: int = 100) -> List[Dict]:
        """获取租户日志"""
        logs = self._load_logs()
        tenant_logs = [l for l in logs if l.get("tenant_id") == tenant_id]
        return tenant_logs[-limit:]
    
    def filter_tenant_data(self, data: List[Dict], user_id: str, 
                           tenant_field: str = "tenant_id") -> List[Dict]:
        """过滤租户数据（核心隔离方法）"""
        tenant = self.get_tenant_by_user(user_id)
        if not tenant:
            return []
        
        tenant_id = tenant["id"]
        return [item for item in data if item.get(tenant_field) == tenant_id]
    
    def suspend_tenant(self, tenant_id: str, reason: str = "") -> Dict:
        """暂停租户"""
        with self.lock:
            if tenant_id not in self.tenants:
                return {"success": False, "error": "租户不存在"}
            
            self.tenants[tenant_id]["status"] = TenantStatus.SUSPENDED.value
            self.tenants[tenant_id]["suspend_reason"] = reason
            self.tenants[tenant_id]["suspended_at"] = datetime.now().isoformat()
            self._save()
            
            return {"success": True, "message": "租户已暂停"}
    
    def activate_tenant(self, tenant_id: str) -> Dict:
        """激活租户"""
        with self.lock:
            if tenant_id not in self.tenants:
                return {"success": False, "error": "租户不存在"}
            
            self.tenants[tenant_id]["status"] = TenantStatus.ACTIVE.value
            self.tenants[tenant_id].pop("suspend_reason", None)
            self.tenants[tenant_id].pop("suspended_at", None)
            self._save()
            
            return {"success": True, "message": "租户已激活"}
    
    def update_tenant_plan(self, tenant_id: str, new_plan: TenantPlan) -> Dict:
        """更新租户套餐"""
        with self.lock:
            if tenant_id not in self.tenants:
                return {"success": False, "error": "租户不存在"}
            
            self.tenants[tenant_id]["plan"] = new_plan.value
            self.tenants[tenant_id]["limits"] = TENANT_LIMITS.get(new_plan, TENANT_LIMITS[TenantPlan.FREE])
            self._save()
            
            return {"success": True, "message": f"套餐已更新为 {new_plan.value}"}
    
    def get_tenant_stats(self, tenant_id: str) -> Dict:
        """获取租户统计"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {"error": "租户不存在"}
        
        return {
            "tenant_id": tenant_id,
            "name": tenant.get("name"),
            "plan": tenant.get("plan"),
            "status": tenant.get("status"),
            "users_count": len(tenant.get("users", [])),
            "usage": tenant.get("usage", {}),
            "limits": tenant.get("limits", {}),
            "expires_at": tenant.get("expires_at"),
        }


def require_tenant(resource: str, action: str):
    """租户权限装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            if not user_id:
                return {"success": False, "error": "未登录"}
            
            check = tenant_manager.check_permission(user_id, resource, action)
            
            if not check["allowed"]:
                return {"success": False, "error": check["reason"]}
            
            kwargs['tenant_id'] = check.get("tenant_id")
            
            result = func(*args, **kwargs)
            
            tenant_manager.record_usage(check.get("tenant_id"), resource)
            
            return result
        return wrapper
    return decorator


tenant_manager = TenantManager()
