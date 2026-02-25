"""
监控相关路由处理
"""

def handle_monitor_request(handler, path, method, body, context):
    """
    处理监控相关请求
    
    context包含:
    - user_manager: 用户管理器
    - user_system_available: 用户系统是否可用
    - get_monitor_service: 获取监控服务
    - get_operation_logger: 获取操作日志器
    """
    import json
    
    user_manager = context.get('user_manager')
    user_system_available = context.get('user_system_available', False)
    get_monitor_service = context.get('get_monitor_service')
    get_operation_logger = context.get('get_operation_logger')
    
    if path == '/api/monitor/status':
        monitor = get_monitor_service() if get_monitor_service else None
        if monitor:
            try:
                status = monitor.get_status()
                handler._send_json(200, {"success": True, "data": status})
            except Exception as e:
                handler._send_json(500, {"success": False, "error": str(e)})
        else:
            handler._send_json(200, {"success": True, "data": {"running": False}})
        return True
    
    elif path == '/api/monitor/metrics':
        monitor = get_monitor_service() if get_monitor_service else None
        if monitor:
            try:
                metrics = monitor.get_metrics()
                handler._send_json(200, {"success": True, "metrics": metrics})
            except Exception as e:
                handler._send_json(500, {"success": False, "error": str(e)})
        else:
            handler._send_json(200, {"success": True, "metrics": {}})
        return True
    
    elif path == '/api/logs/user':
        token = handler._get_token_from_request()
        user = user_manager.validate_token(token) if user_system_available and user_manager else None
        if not user:
            handler._send_json(401, {"success": False, "error": "未登录"})
            return True
        op_logger = get_operation_logger() if get_operation_logger else None
        logs = op_logger.get_user_logs(user['username'], 50) if op_logger else []
        handler._send_json(200, {"success": True, "logs": logs})
        return True
    
    return None
