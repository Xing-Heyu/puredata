"""
风控相关路由处理
"""

def handle_risk_routes(handler, path, method, body, context):
    """
    处理风控相关请求
    
    context包含:
    - user_manager: 用户管理器
    - admin_auth: 管理员认证
    - client_ip: 客户端IP
    - RISK_CONTROL_AVAILABLE: 风控是否可用
    - get_risk_control: 获取风控实例
    - ANTI_ABUSE_AVAILABLE: 反滥用是否可用
    - get_anti_abuse: 获取反滥用实例
    """
    
    user_manager = context.get('user_manager')
    admin_auth = context.get('admin_auth')
    client_ip = context.get('client_ip', '')
    RISK_CONTROL_AVAILABLE = context.get('RISK_CONTROL_AVAILABLE', False)
    get_risk_control = context.get('get_risk_control')
    ANTI_ABUSE_AVAILABLE = context.get('ANTI_ABUSE_AVAILABLE', False)
    get_anti_abuse = context.get('get_anti_abuse')
    
    def _is_admin(token):
        if not admin_auth:
            return False
        return admin_auth.validate_token(token) is not None
    
    if path == '/api/admin/anti_abuse/ip_info':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        target_ip = body.get('ip', client_ip)
        
        if ANTI_ABUSE_AVAILABLE and get_anti_abuse:
            anti_abuse_module = get_anti_abuse()
            if anti_abuse_module:
                info = anti_abuse_module.anti_abuse.get_ip_info(target_ip)
                handler._send_json(200, {"success": True, "info": info})
            else:
                handler._send_json(200, {"success": True, "info": {}})
        else:
            handler._send_json(200, {"success": True, "info": {}, "message": "反滥用模块未启用"})
        return True
    
    elif path == '/api/admin/anti_abuse/mark_suspicious':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        target = body.get('target', '')
        reason = body.get('reason', '管理员标记')
        
        if ANTI_ABUSE_AVAILABLE and get_anti_abuse:
            anti_abuse_module = get_anti_abuse()
            if anti_abuse_module:
                anti_abuse_module.anti_abuse.mark_suspicious(target, reason)
                handler._send_json(200, {"success": True, "message": f"已标记 {target} 为可疑"})
            else:
                handler._send_json(500, {"success": False, "error": "反滥用模块不可用"})
        else:
            handler._send_json(200, {"success": True, "message": "演示模式：已标记"})
        return True
    
    elif path == '/api/admin/anti_abuse/whitelist':
        if method == 'GET':
            token = handler._get_token_from_request()
            if not _is_admin(token):
                handler._send_json(403, {"error": "权限不足"})
                return True
            
            if ANTI_ABUSE_AVAILABLE and get_anti_abuse:
                anti_abuse_module = get_anti_abuse()
                if anti_abuse_module:
                    whitelist = anti_abuse_module.anti_abuse.get_whitelist()
                    handler._send_json(200, {"success": True, "whitelist": whitelist})
                else:
                    handler._send_json(200, {"success": True, "whitelist": []})
            else:
                handler._send_json(200, {"success": True, "whitelist": []})
            return True
        
        elif method == 'POST':
            token = handler._get_token_from_request()
            if not _is_admin(token):
                handler._send_json(403, {"error": "权限不足"})
                return True
            
            target = body.get('target', '')
            action = body.get('action', 'add')
            
            if ANTI_ABUSE_AVAILABLE and get_anti_abuse:
                anti_abuse_module = get_anti_abuse()
                if anti_abuse_module:
                    if action == 'add':
                        anti_abuse_module.anti_abuse.add_to_whitelist(target)
                        handler._send_json(200, {"success": True, "message": f"已添加 {target} 到白名单"})
                    else:
                        anti_abuse_module.anti_abuse.remove_from_whitelist(target)
                        handler._send_json(200, {"success": True, "message": f"已从白名单移除 {target}"})
                else:
                    handler._send_json(500, {"success": False, "error": "反滥用模块不可用"})
            else:
                handler._send_json(200, {"success": True, "message": "演示模式：操作成功"})
            return True
    
    elif path == '/api/admin/risk_control/dashboard':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        if RISK_CONTROL_AVAILABLE and get_risk_control:
            rc = get_risk_control()
            if rc:
                dashboard = rc.get_dashboard()
                handler._send_json(200, {"success": True, "dashboard": dashboard})
            else:
                handler._send_json(200, {"success": True, "dashboard": {}})
        else:
            handler._send_json(200, {"success": True, "dashboard": {}, "message": "风控模块未启用"})
        return True
    
    elif path == '/api/admin/risk_control/block':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        target = body.get('target', '')
        duration = body.get('duration', 3600)
        
        if RISK_CONTROL_AVAILABLE and get_risk_control:
            rc = get_risk_control()
            if rc:
                rc.block(target, duration)
                handler._send_json(200, {"success": True, "message": f"已封锁 {target} {duration}秒"})
            else:
                handler._send_json(500, {"success": False, "error": "风控模块不可用"})
        else:
            handler._send_json(200, {"success": True, "message": "演示模式：已封锁"})
        return True
    
    elif path == '/api/admin/risk_control/unblock':
        if method != 'POST':
            handler._send_json(405, {"error": "Method not allowed"})
            return True
        
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        target = body.get('target', '')
        
        if RISK_CONTROL_AVAILABLE and get_risk_control:
            rc = get_risk_control()
            if rc:
                rc.unblock(target)
                handler._send_json(200, {"success": True, "message": f"已解封 {target}"})
            else:
                handler._send_json(500, {"success": False, "error": "风控模块不可用"})
        else:
            handler._send_json(200, {"success": True, "message": "演示模式：已解封"})
        return True
    
    elif path == '/api/admin/risk_control/audit_logs':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        limit = body.get('limit', 100)
        
        if RISK_CONTROL_AVAILABLE and get_risk_control:
            rc = get_risk_control()
            if rc:
                logs = rc.get_audit_logs(limit)
                handler._send_json(200, {"success": True, "logs": logs})
            else:
                handler._send_json(200, {"success": True, "logs": []})
        else:
            handler._send_json(200, {"success": True, "logs": [], "message": "风控模块未启用"})
        return True
    
    elif path == '/api/admin/risk_control/cost_report':
        token = handler._get_token_from_request()
        if not _is_admin(token):
            handler._send_json(403, {"error": "权限不足"})
            return True
        
        if RISK_CONTROL_AVAILABLE and get_risk_control:
            rc = get_risk_control()
            if rc:
                report = rc.get_cost_report()
                handler._send_json(200, {"success": True, "report": report})
            else:
                handler._send_json(200, {"success": True, "report": {}})
        else:
            handler._send_json(200, {"success": True, "report": {}, "message": "风控模块未启用"})
        return True
    
    return None
