"""
管理员相关路由处理
完整版 - 包含所有管理员相关的API处理逻辑
"""

import json
from datetime import datetime

def handle_admin_routes(handler, path, method, body, context):
    """
    处理管理员相关请求
    
    context包含:
    - user_manager: 用户管理器
    - admin_auth: 管理员认证
    - client_ip: 客户端IP
    - tasks: 任务字典
    - stats: 统计数据
    """
    
    user_manager = context.get('user_manager')
    admin_auth = context.get('admin_auth')
    client_ip = context.get('client_ip', '')
    tasks = context.get('tasks', {})
    stats = context.get('stats', {})
    
    def _is_admin(token):
        if not admin_auth:
            return False
        return admin_auth.validate_token(token) is not None
    
    if path == '/api/admin/login':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        username = body.get('username', '')
        password = body.get('password', '')
        
        if not admin_auth:
            handler._send_json(500, {"error": "管理员系统不可用"})
            return True
        
        result = admin_auth.login(username, password, client_ip)
        if result.get("success"):
            handler._send_json(200, result)
        else:
            handler._send_json(401, result)
        return True
    
    elif path == '/api/admin/logout':
        token = handler._get_token_from_request()
        if admin_auth:
            admin_auth.logout(token)
        handler._send_json(200, {"success": True})
        return True
    
    elif path == '/api/admin/info':
        token = handler._get_token_from_request()
        if not admin_auth:
            handler._send_json(500, {"error": "管理员系统不可用"})
            return True
        
        admin = admin_auth.validate_token(token)
        if admin:
            handler._send_json(200, {"success": True, "admin": admin})
        else:
            handler._send_json(401, {"error": "未登录"})
        return True
    
    elif path == '/api/admin/change_password':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        token = handler._get_token_from_request()
        if not admin_auth:
            handler._send_json(500, {"error": "管理员系统不可用"})
            return True
        
        admin = admin_auth.validate_token(token)
        if not admin:
            handler._send_json(401, {"error": "未登录"})
            return True
        
        old_password = body.get('old_password', '')
        new_password = body.get('new_password', '')
        
        result = admin_auth.change_password(admin['username'], old_password, new_password)
        handler._send_json(200, result)
        return True
    
    elif path == '/api/admin/list':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        if not admin_auth:
            handler._send_json(500, {"error": "管理员系统不可用"})
            return True
        
        admins = admin_auth.list_admins()
        handler._send_json(200, {"success": True, "admins": admins})
        return True
    
    elif path == '/api/admin/add':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        if not admin_auth:
            handler._send_json(500, {"error": "管理员系统不可用"})
            return True
        
        result = admin_auth.add_admin(body)
        handler._send_json(200, result)
        return True
    
    elif path == '/api/admin/delete':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        if not admin_auth:
            handler._send_json(500, {"error": "管理员系统不可用"})
            return True
        
        username = body.get('username', '')
        result = admin_auth.delete_admin(username)
        handler._send_json(200, result)
        return True
    
    elif path == '/api/admin/users':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        if not user_manager:
            handler._send_json(500, {"error": "用户系统不可用"})
            return True
        
        users = user_manager.list_users()
        handler._send_json(200, {"success": True, "users": users})
        return True
    
    elif path == '/api/admin/users/update':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        if not user_manager:
            handler._send_json(500, {"error": "用户系统不可用"})
            return True
        
        username = body.get('username', '')
        updates = body.get('updates', {})
        
        result = user_manager.admin_update_user(username, updates)
        handler._send_json(200, result)
        return True
    
    elif path == '/api/admin/users/delete':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        if not user_manager:
            handler._send_json(500, {"error": "用户系统不可用"})
            return True
        
        username = body.get('username', '')
        result = user_manager.delete_user(username)
        handler._send_json(200, result)
        return True
    
    elif path == '/api/admin/logs':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        get_operation_logger = context.get('get_operation_logger')
        if get_operation_logger:
            op_logger = get_operation_logger()
            logs = op_logger.get_recent_logs(100) if op_logger else []
            log_stats = op_logger.get_stats() if op_logger else {}
        else:
            logs = []
            log_stats = {}
        
        handler._send_json(200, {"success": True, "logs": logs, "stats": log_stats})
        return True
    
    elif path == '/api/admin/docs':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        docs = {
            "api_version": "1.0",
            "endpoints": [
                {"path": "/api/admin/login", "method": "POST", "desc": "管理员登录"},
                {"path": "/api/admin/users", "method": "GET", "desc": "获取用户列表"},
                {"path": "/api/admin/logs", "method": "GET", "desc": "获取操作日志"},
            ]
        }
        handler._send_json(200, docs)
        return True
    
    return None
