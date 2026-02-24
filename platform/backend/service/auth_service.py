#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务层 - 认证服务
整合自 管理员认证.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from 管理员认证 import AdminAuthManager
    AuthService = AdminAuthManager
    __all__ = ['AuthService', 'AdminAuthManager']
except ImportError:
    import hashlib
    import secrets
    from typing import Dict, Optional
    from datetime import datetime, timedelta
    
    class AuthService:
        """认证服务 - 占位实现"""
        
        def __init__(self, secret_key: str = "dev-secret"):
            self.secret_key = secret_key
            self.sessions: Dict[str, Dict] = {}
        
        def login(self, username: str, password: str) -> Optional[str]:
            # 简化实现
            token = secrets.token_urlsafe(32)
            self.sessions[token] = {
                "username": username,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            return token
        
        def verify_token(self, token: str) -> Optional[Dict]:
            return self.sessions.get(token)
        
        def logout(self, token: str) -> bool:
            if token in self.sessions:
                del self.sessions[token]
                return True
            return False
    
    AdminAuthManager = AuthService
    __all__ = ['AuthService', 'AdminAuthManager']
