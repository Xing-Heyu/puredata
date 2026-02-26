#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理器模块 - 认证处理器
"""

import json
import re
import sys
import os
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from password_validator import PasswordValidator


class AuthHandler:
    """认证处理器 - 处理登录、注册、登出等"""
    
    MIN_USERNAME_LEN = 2
    MAX_USERNAME_LEN = 50
    
    def __init__(self, user_manager, admin_auth):
        self.user_manager = user_manager
        self.admin_auth = admin_auth
    
    def _validate_username(self, username):
        """验证用户名"""
        if not username:
            return False, "用户名不能为空"
        if len(username) < self.MIN_USERNAME_LEN:
            return False, f"用户名长度至少{self.MIN_USERNAME_LEN}个字符"
        if len(username) > self.MAX_USERNAME_LEN:
            return False, f"用户名长度不能超过{self.MAX_USERNAME_LEN}个字符"
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            return False, "用户名只能包含字母、数字、下划线和中文"
        return True, None
    
    def _validate_password(self, password, check_complexity=False):
        """验证密码"""
        return PasswordValidator.validate(password, check_complexity=check_complexity)
    
    def _validate_email(self, email):
        """验证邮箱"""
        if not email:
            return True, None
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "邮箱格式不正确"
        return True, None
    
    def handle_login(self, request_handler):
        """处理登录请求"""
        try:
            length = int(request_handler.headers.get('Content-Length', 0))
            body = json.loads(request_handler.rfile.read(length).decode('utf-8'))
            
            username = body.get('username', '')
            password = body.get('password', '')
            
            valid, error = self._validate_username(username)
            if not valid:
                return {"success": False, "error": error}
            
            valid, error = self._validate_password(password)
            if not valid:
                return {"success": False, "error": error}
            
            result = self.user_manager.login(username, password)
            
            if result.get('success'):
                return {"success": True, "token": result.get('token'), "user": result.get('user')}
            else:
                return {"success": False, "error": result.get('error', '登录失败')}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_register(self, request_handler):
        """处理注册请求"""
        try:
            length = int(request_handler.headers.get('Content-Length', 0))
            body = json.loads(request_handler.rfile.read(length).decode('utf-8'))
            
            username = body.get('username', '')
            password = body.get('password', '')
            email = body.get('email', '')
            
            valid, error = self._validate_username(username)
            if not valid:
                return {"success": False, "error": error}
            
            valid, error = self._validate_password(password, check_complexity=True)
            if not valid:
                return {"success": False, "error": error}
            
            valid, error = self._validate_email(email)
            if not valid:
                return {"success": False, "error": error}
            
            result = self.user_manager.register(username, password, email)
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_logout(self, request_handler):
        """处理登出请求"""
        try:
            token = self._get_token_from_request(request_handler)
            if token:
                self.user_manager.logout(token)
            return {"success": True, "message": "已登出"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_admin_login(self, request_handler):
        """处理管理员登录"""
        try:
            length = int(request_handler.headers.get('Content-Length', 0))
            body = json.loads(request_handler.rfile.read(length).decode('utf-8'))
            
            username = body.get('username', '')
            password = body.get('password', '')
            
            if not username or not password:
                return {"success": False, "error": "用户名和密码不能为空"}
            
            result = self.admin_auth.login(username, password)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_token_from_request(self, request_handler):
        """从请求中获取token"""
        auth_header = request_handler.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        cookie = request_handler.headers.get('Cookie', '')
        for part in cookie.split(';'):
            if 'token=' in part:
                return part.split('=')[1].strip()
        
        return None
    
    def validate_token(self, request_handler):
        """验证token"""
        token = self._get_token_from_request(request_handler)
        if token:
            return self.user_manager.validate_token(token)
        return None
