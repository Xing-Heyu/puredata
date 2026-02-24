"""
数据生成相关路由处理
完整版 - 包含所有生成相关的API处理逻辑
"""

import threading
import uuid
import json
from datetime import datetime

def handle_generate_routes(handler, path, method, body, context):
    """
    处理数据生成相关请求
    
    context包含:
    - user_manager: 用户管理器
    - tasks: 任务字典
    - task_lock: 任务锁
    - stats: 统计数据
    - client_ip: 客户端IP
    - QUALITY_MODES: 质量模式配置
    - RISK_CONTROL_AVAILABLE: 风控是否可用
    - get_risk_control: 获取风控实例
    - DOMAINS: 领域配置
    - TEMPLATES: 模板配置
    """
    
    user_manager = context.get('user_manager')
    tasks = context.get('tasks', {})
    task_lock = context.get('task_lock')
    stats = context.get('stats', {})
    client_ip = context.get('client_ip', '')
    QUALITY_MODES = context.get('QUALITY_MODES', {})
    RISK_CONTROL_AVAILABLE = context.get('RISK_CONTROL_AVAILABLE', False)
    get_risk_control = context.get('get_risk_control')
    
    if path == '/generate':
        if method != 'POST':
            handler._send_json(405, {"success": False, "error": "Method not allowed"})
            return True
        
        try:
            token = handler._get_token_from_request()
            user = handler._get_current_user(token) if hasattr(handler, '_get_current_user') else None
            
            user_role = user.get('role', 'free') if user else 'free'
            user_id = user.get('username', client_ip) if user else client_ip
            
            if RISK_CONTROL_AVAILABLE and get_risk_control:
                rc = get_risk_control()
                if rc:
                    rate_check = rc.check_request(client_ip, user_id, "generate", user_role)
                    if not rate_check["allowed"]:
                        handler._send_json(429, {
                            "success": False,
                            "error": rate_check["reason"],
                            "retry_after": rate_check.get("retry_after", 60)
                        })
                        return True
            
            domain = body.get('domain', '人工智能')
            count = int(body.get('count', 100))
            format_type = body.get('format', 'json')
            mode = body.get('mode', 'hybrid')
            noise_level = int(body.get('noise_level', 2))
            quality_mode = body.get('quality_mode', 'standard')
            
            if user and user.get('role') == 'free':
                quality_mode = 'free_trial'
            
            if quality_mode not in QUALITY_MODES:
                quality_mode = 'standard'
            
            if RISK_CONTROL_AVAILABLE and get_risk_control and user:
                rc = get_risk_control()
                if rc:
                    cost_check = rc.check_cost(user_id, user_role, count)
                    if not cost_check["allowed"]:
                        handler._send_json(403, {
                            "success": False,
                            "error": cost_check["reason"],
                            "current_usage": cost_check["current"],
                            "limits": cost_check["limits"]
                        })
                        return True
            
            if user and user_manager:
                if user.get('role') not in ['developer', 'admin']:
                    if not user_manager.check_quota(user['username'], count):
                        quota_status = user_manager.get_quota_status(user['username'])
                        handler._send_json(403, {
                            "success": False,
                            "error": "配额不足",
                            "message": f"本月剩余配额不足，剩余 {quota_status['monthly']['remaining']} 条，需要 {count} 条",
                            "quota": quota_status
                        })
                        return True
            
            task_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            username = user['username'] if user else None
            
            if task_lock:
                with task_lock:
                    tasks[task_id] = {
                        "id": task_id,
                        "status": "pending",
                        "domain": domain,
                        "count": count,
                        "progress": 0,
                        "total": count,
                        "mode": mode,
                        "noise_level": noise_level,
                        "quality_mode": quality_mode,
                        "created_at": datetime.now().isoformat(),
                        "username": username
                    }
            
            if hasattr(handler, '_run_task'):
                thread = threading.Thread(
                    target=handler._run_task,
                    args=(task_id, domain, count, format_type, mode, username, noise_level, quality_mode),
                    daemon=True
                )
                thread.start()
            
            if RISK_CONTROL_AVAILABLE and get_risk_control:
                rc = get_risk_control()
                if rc:
                    rc.log_action("generate", username, client_ip, {
                        "domain": domain,
                        "count": count,
                        "mode": mode
                    }, "success")
            
            handler._send_json(200, {"success": True, "task_id": task_id})
            
        except Exception as e:
            print(f"生成错误: {e}")
            if RISK_CONTROL_AVAILABLE and get_risk_control:
                rc = get_risk_control()
                if rc:
                    rc.log_action("generate", None, client_ip, {"error": str(e)}, "failed")
            handler._send_json(500, {"success": False, "error": str(e)})
        
        return True
    
    elif path == '/generate_sequence':
        if method != 'POST':
            handler._send_json(405, {"success": False, "error": "Method not allowed"})
            return True
        
        try:
            token = handler._get_token_from_request()
            user = handler._get_current_user(token) if hasattr(handler, '_get_current_user') else None
            
            if not user:
                handler._send_json(401, {"success": False, "error": "请先登录"})
                return True
            
            sequence_data = body.get('sequence', [])
            if not sequence_data:
                handler._send_json(400, {"success": False, "error": "请提供行为序列数据"})
                return True
            
            task_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            username = user['username']
            
            if task_lock:
                with task_lock:
                    tasks[task_id] = {
                        "id": task_id,
                        "status": "pending",
                        "type": "sequence",
                        "count": len(sequence_data),
                        "progress": 0,
                        "created_at": datetime.now().isoformat(),
                        "username": username
                    }
            
            handler._send_json(200, {"success": True, "task_id": task_id, "message": "序列生成任务已创建"})
            
        except Exception as e:
            handler._send_json(500, {"success": False, "error": str(e)})
        
        return True
    
    elif path == '/tasks':
        if method != 'GET':
            handler._send_json(405, {"success": False, "error": "Method not allowed"})
            return True
        
        task_list = list(tasks.values()) if tasks else []
        handler._send_json(200, {"success": True, "tasks": task_list})
        return True
    
    elif path.startswith('/task/'):
        if method != 'GET':
            handler._send_json(405, {"success": False, "error": "Method not allowed"})
            return True
        
        task_id = path.split('/task/')[-1]
        if task_id in tasks:
            handler._send_json(200, {"success": True, "task": tasks[task_id]})
        else:
            handler._send_json(404, {"success": False, "error": "任务不存在"})
        return True
    
    elif path == '/domains':
        if method != 'GET':
            handler._send_json(405, {"success": False, "error": "Method not allowed"})
            return True
        
        domains = context.get('DOMAINS', {})
        handler._send_json(200, {"success": True, "domains": [{"name": k, "keywords": len(v)} for k, v in domains.items()]})
        return True
    
    elif path == '/quality_modes':
        if method != 'GET':
            handler._send_json(405, {"success": False, "error": "Method not allowed"})
            return True
        
        modes = []
        for mode_id, mode_config in QUALITY_MODES.items():
            modes.append({
                "id": mode_id,
                "high_ratio": mode_config.get("high_ratio", 0),
                "medium_ratio": mode_config.get("medium_ratio", 0),
                "low_ratio": mode_config.get("low_ratio", 0),
                "description": mode_config.get("description", "")
            })
        handler._send_json(200, {"success": True, "quality_modes": modes})
        return True
    
    elif path.startswith('/task/'):
        # SSE实时任务进度推送
        if method != 'GET':
            handler._send_json(405, {"success": False, "error": "Method not allowed"})
            return True
        
        task_id = path.split('/task/')[-1]
        if task_id not in tasks:
            handler._send_json(404, {"success": False, "error": "任务不存在"})
            return True
        
        # 检查是否是SSE请求
        accept_header = handler.headers.get('Accept', '')
        if 'text/event-stream' in accept_header:
            # SSE实时推送
            handler.send_response(200)
            handler.send_header('Content-Type', 'text/event-stream')
            handler.send_header('Cache-Control', 'no-cache')
            handler.send_header('Connection', 'keep-alive')
            handler.send_header('Access-Control-Allow-Origin', '*')
            handler.end_headers()
            
            import time
            last_progress = -1
            last_status = None
            
            try:
                while True:
                    task = tasks.get(task_id, {})
                    current_progress = task.get('progress', 0)
                    current_status = task.get('status', 'unknown')
                    
                    # 只在进度或状态变化时推送
                    if current_progress != last_progress or current_status != last_status:
                        data = {
                            "id": task_id,
                            "progress": current_progress,
                            "status": current_status,
                            "total": task.get('total', 0),
                            "completed": task.get('completed', 0),
                            "timestamp": datetime.now().isoformat()
                        }
                        handler.wfile.write(f"data: {json.dumps(data)}\n\n".encode('utf-8'))
                        handler.wfile.flush()
                        
                        last_progress = current_progress
                        last_status = current_status
                    
                    # 任务完成或失败时结束推送
                    if current_status in ['completed', 'failed']:
                        break
                    
                    time.sleep(0.5)  # 每500ms检查一次
                    
            except (BrokenPipeError, ConnectionResetError):
                # 客户端断开连接
                pass
            except Exception as e:
                print(f"[SSE] 推送异常: {e}")
            
            return True
        else:
            # 普通JSON查询
            handler._send_json(200, {"success": True, "task": tasks[task_id]})
            return True
    
    return None
