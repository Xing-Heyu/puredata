#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API密钥管理模块
支持：创建、删除、查询API Key
"""

import json
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
API_KEYS_FILE = os.path.join(BACKEND_DIR, 'api_keys.json')

class KeyStatus(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    EXPIRED = "expired"

@dataclass
class APIKey:
    key_id: str
    key_hash: str
    key_prefix: str
    user_id: str
    name: str
    created_at: str
    expires_at: Optional[str]
    last_used_at: Optional[str]
    usage_count: int
    status: str
    permissions: List[str]
    rate_limit: int

class APIKeyManager:
    """API密钥管理器"""
    
    DEFAULT_RATE_LIMIT = 1000
    DEFAULT_EXPIRE_DAYS = 365
    
    def __init__(self):
        self.keys: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self._load()
    
    def _load(self):
        if os.path.exists(API_KEYS_FILE):
            with open(API_KEYS_FILE, 'r', encoding='utf-8') as f:
                self.keys = json.load(f)
    
    def _save(self):
        with open(API_KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.keys, f, ensure_ascii=False, indent=2)
    
    def _generate_key(self) -> tuple:
        raw_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:8]
        return raw_key, key_hash, key_prefix
    
    def create_key(self, user_id: str, name: str, permissions: List[str] = None, 
                   expires_days: int = None, rate_limit: int = None) -> Dict:
        with self.lock:
            raw_key, key_hash, key_prefix = self._generate_key()
            
            key_id = secrets.token_urlsafe(8)
            expires_at = None
            if expires_days:
                expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
            
            key_data = {
                "key_id": key_id,
                "key_hash": key_hash,
                "key_prefix": key_prefix,
                "user_id": user_id,
                "name": name,
                "created_at": datetime.now().isoformat(),
                "expires_at": expires_at,
                "last_used_at": None,
                "usage_count": 0,
                "status": KeyStatus.ACTIVE.value,
                "permissions": permissions or ["generate", "download"],
                "rate_limit": rate_limit or self.DEFAULT_RATE_LIMIT
            }
            
            self.keys[key_id] = key_data
            self._save()
            
            return {
                "success": True,
                "key_id": key_id,
                "api_key": f"dg_{raw_key}",
                "key_prefix": key_prefix,
                "name": name,
                "expires_at": expires_at,
                "message": "API密钥创建成功，请妥善保管"
            }
    
    def validate_key(self, api_key: str) -> Optional[Dict]:
        if not api_key.startswith("dg_"):
            return None
        
        raw_key = api_key[3:]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        for key_id, key_data in self.keys.items():
            if key_data["key_hash"] == key_hash:
                if key_data["status"] != KeyStatus.ACTIVE.value:
                    return None
                
                if key_data.get("expires_at"):
                    if datetime.now() > datetime.fromisoformat(key_data["expires_at"]):
                        key_data["status"] = KeyStatus.EXPIRED.value
                        self._save()
                        return None
                
                key_data["last_used_at"] = datetime.now().isoformat()
                key_data["usage_count"] += 1
                self._save()
                
                return {
                    "key_id": key_id,
                    "user_id": key_data["user_id"],
                    "permissions": key_data["permissions"],
                    "rate_limit": key_data["rate_limit"]
                }
        
        return None
    
    def list_keys(self, user_id: str = None) -> List[Dict]:
        result = []
        for key_id, key_data in self.keys.items():
            if user_id and key_data["user_id"] != user_id:
                continue
            
            result.append({
                "key_id": key_id,
                "key_prefix": key_data["key_prefix"],
                "name": key_data["name"],
                "created_at": key_data["created_at"],
                "expires_at": key_data.get("expires_at"),
                "last_used_at": key_data.get("last_used_at"),
                "usage_count": key_data["usage_count"],
                "status": key_data["status"]
            })
        
        return result
    
    def delete_key(self, key_id: str, user_id: str = None) -> Dict:
        with self.lock:
            if key_id not in self.keys:
                return {"success": False, "error": "密钥不存在"}
            
            if user_id and self.keys[key_id]["user_id"] != user_id:
                return {"success": False, "error": "无权删除此密钥"}
            
            del self.keys[key_id]
            self._save()
            
            return {"success": True, "message": "密钥已删除"}
    
    def disable_key(self, key_id: str, user_id: str = None) -> Dict:
        with self.lock:
            if key_id not in self.keys:
                return {"success": False, "error": "密钥不存在"}
            
            if user_id and self.keys[key_id]["user_id"] != user_id:
                return {"success": False, "error": "无权操作此密钥"}
            
            self.keys[key_id]["status"] = KeyStatus.DISABLED.value
            self._save()
            
            return {"success": True, "message": "密钥已禁用"}
    
    def enable_key(self, key_id: str, user_id: str = None) -> Dict:
        with self.lock:
            if key_id not in self.keys:
                return {"success": False, "error": "密钥不存在"}
            
            if user_id and self.keys[key_id]["user_id"] != user_id:
                return {"success": False, "error": "无权操作此密钥"}
            
            self.keys[key_id]["status"] = KeyStatus.ACTIVE.value
            self._save()
            
            return {"success": True, "message": "密钥已启用"}

api_key_manager = APIKeyManager()

if __name__ == "__main__":
    print("="*60)
    print("API密钥管理测试")
    print("="*60)
    
    result = api_key_manager.create_key("test_user", "测试密钥")
    print(f"\n创建密钥: {result}")
    
    if result["success"]:
        api_key = result["api_key"]
        validated = api_key_manager.validate_key(api_key)
        print(f"验证密钥: {validated}")
        
        keys = api_key_manager.list_keys("test_user")
        print(f"密钥列表: {keys}")
