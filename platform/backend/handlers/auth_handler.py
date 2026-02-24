#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理器模块 - 认证处理器
"""

import json
from urllib.parse import urlparse


class AuthHandler:
    """认证处理器 - 处理登录、注册、登出等"""
    
    def __init__(self, user_manager, admin_auth):
        self.user_manager = user_manager
        self.admin_auth = admin_auth
    
    def handle_login(self, request_handler):
        """处理登录请求"""
        try:
            length = int(request_handler.headers.get('Content-Length', 0))
            body = json.loads(request_handler.rfile.read(length).decode('utf-8'))
            
            username = body.get('username', '')
            password = body.get('password', '')
            
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
