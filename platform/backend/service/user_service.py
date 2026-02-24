#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务层 - 用户服务
整合自 user_system.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from user_system import UserManager, UserRole, Permission
    UserService = UserManager
    __all__ = ['UserService', 'UserManager', 'UserRole', 'Permission']
except ImportError:
    from enum import Enum
    from typing import Dict, List, Optional
    from datetime import datetime
    
    class UserRole(Enum):
        ADMIN = "admin"
        VIP = "vip"
        USER = "user"
        GUEST = "guest"
    
    class Permission:
        def __init__(self, name: str, description: str = ""):
            self.name = name
            self.description = description
    
    class UserService:
        """用户服务 - 占位实现"""
        
        def __init__(self):
            self.users: Dict[str, Dict] = {}
        
        def create_user(self, username: str, email: str, password: str, role: UserRole = UserRole.USER) -> Dict:
            user_id = f"user_{len(self.users) + 1}"
            self.users[user_id] = {
                "id": user_id,
                "username": username,
                "email": email,
                "role": role,
                "created_at": datetime.now().isoformat()
            }
            return self.users[user_id]
        
        def get_user(self, user_id: str) -> Optional[Dict]:
            return self.users.get(user_id)
        
        def list_users(self) -> List[Dict]:
            return list(self.users.values())
    
    UserManager = UserService
    __all__ = ['UserService', 'UserManager', 'UserRole', 'Permission']
