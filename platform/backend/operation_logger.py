#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
操作日志模块
支持：用户操作记录、审计追踪
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import uuid

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_FILE = os.path.join(BACKEND_DIR, 'operation_logs.json')

class ActionType(Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    GENERATE = "generate"
    DOWNLOAD = "download"
    API_KEY_CREATE = "api_key_create"
    API_KEY_DELETE = "api_key_delete"
    PROFILE_UPDATE = "profile_update"
    PASSWORD_CHANGE = "password_change"
    SUBSCRIPTION = "subscription"
    ADMIN_ACTION = "admin_action"

@dataclass
class OperationLog:
    log_id: str
    user_id: str
    username: str
    action: str
    details: Dict
    ip_address: str
    user_agent: str
    timestamp: str
    status: str
    extra: Optional[Dict]

class OperationLogger:
    """操作日志记录器"""
    
    MAX_LOGS = 10000
    
    def __init__(self):
        self.logs: List[Dict] = []
        self.lock = threading.Lock()
        self._load()
    
    def _load(self):
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                self.logs = json.load(f)
    
    def _save(self):
        with open(LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.logs[-self.MAX_LOGS:], f, ensure_ascii=False, indent=2)
    
    def log(self, user_id: str, username: str, action: ActionType, 
            details: Dict = None, ip_address: str = "unknown", 
            user_agent: str = "unknown", status: str = "success", 
            extra: Dict = None) -> str:
        
        with self.lock:
            log_id = str(uuid.uuid4())[:12]
            
            log_entry = {
                "log_id": log_id,
                "user_id": user_id,
                "username": username,
                "action": action.value,
                "details": details or {},
                "ip_address": ip_address,
                "user_agent": user_agent[:200] if user_agent else "unknown",
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "extra": extra
            }
            
            self.logs.append(log_entry)
            self._save()
            
            return log_id
    
    def log_login(self, username: str, user_id: str, ip: str, success: bool, reason: str = None):
        return self.log(
            user_id=user_id,
            username=username,
            action=ActionType.LOGIN,
            details={"success": success, "reason": reason},
            ip_address=ip,
            status="success" if success else "failed"
        )
    
    def log_logout(self, username: str, user_id: str, ip: str):
        return self.log(
            user_id=user_id,
            username=username,
            action=ActionType.LOGOUT,
            ip_address=ip
        )
    
    def log_generate(self, username: str, user_id: str, domain: str, count: int, ip: str):
        return self.log(
            user_id=user_id,
            username=username,
            action=ActionType.GENERATE,
            details={"domain": domain, "count": count},
            ip_address=ip
        )
    
    def log_download(self, username: str, user_id: str, task_id: str, count: int, ip: str):
        return self.log(
            user_id=user_id,
            username=username,
            action=ActionType.DOWNLOAD,
            details={"task_id": task_id, "count": count},
            ip_address=ip
        )
    
    def log_api_key(self, username: str, user_id: str, action_type: str, key_name: str, ip: str):
        return self.log(
            user_id=user_id,
            username=username,
            action=ActionType.API_KEY_CREATE if action_type == "create" else ActionType.API_KEY_DELETE,
            details={"key_name": key_name},
            ip_address=ip
        )
    
    def log_admin_action(self, admin_id: str, admin_name: str, action: str, target: str, ip: str):
        return self.log(
            user_id=admin_id,
            username=admin_name,
            action=ActionType.ADMIN_ACTION,
            details={"admin_action": action, "target": target},
            ip_address=ip
        )
    
    def get_user_logs(self, user_id: str, limit: int = 100) -> List[Dict]:
        user_logs = [log for log in self.logs if log["user_id"] == user_id]
        return user_logs[-limit:]
    
    def get_logs_by_action(self, action: ActionType, limit: int = 100) -> List[Dict]:
        action_logs = [log for log in self.logs if log["action"] == action.value]
        return action_logs[-limit:]
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        return self.logs[-limit:]
    
    def get_logs_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        result = []
        for log in self.logs:
            if start_date <= log["timestamp"] <= end_date:
                result.append(log)
        return result
    
    def get_stats(self, days: int = 7) -> Dict:
        from datetime import timedelta
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        recent_logs = [log for log in self.logs if log["timestamp"] >= cutoff]
        
        stats = {
            "total": len(recent_logs),
            "by_action": {},
            "by_user": {},
            "by_status": {"success": 0, "failed": 0}
        }
        
        for log in recent_logs:
            action = log["action"]
            stats["by_action"][action] = stats["by_action"].get(action, 0) + 1
            
            user = log["username"]
            stats["by_user"][user] = stats["by_user"].get(user, 0) + 1
            
            status = log["status"]
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        return stats

operation_logger = OperationLogger()

if __name__ == "__main__":
    print("="*60)
    print("操作日志测试")
    print("="*60)
    
    operation_logger.log_login("testuser", "user_001", "127.0.0.1", True)
    operation_logger.log_generate("testuser", "user_001", "人工智能", 100, "127.0.0.1")
    
    stats = operation_logger.get_stats()
    print(f"\n统计: {stats}")
    
    logs = operation_logger.get_recent_logs(5)
    print(f"\n最近日志: {logs}")
