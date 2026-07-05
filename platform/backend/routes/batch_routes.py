"""
批量任务路由处理
处理批量生成和流式下载
"""

import json
import threading
import uuid
from datetime import datetime


def handle_batch_routes(handler, path, context):
    """
    处理批量任务请求
    
    context包含:
    - tasks: 任务字典
    - task_lock: 任务锁
    - stats: 统计数据
    - client_ip: 客户端IP
    - QUALITY_MODES: 质量模式列表
    - TASK_QUEUE_AVAILABLE: 任务队列是否可用
    - get_module: 获取模块函数
    """
    
    tasks = context.get('tasks', {})
    task_lock = context.get('task_lock')
    stats = context.get('stats', {})
    client_ip = context.get('client_ip', '')
    QUALITY_MODES = context.get('QUALITY_MODES', ['standard'])
    TASK_QUEUE_AVAILABLE = context.get('TASK_QUEUE_AVAILABLE', False)
    get_module = context.get('get_module')
    
    if path == '/api/generate/download':
        try:
            token = handler._get_token_from_request()
            user = handler._get_current_user(token)
            
            if not user:
                handler._send_json(401, {"success": False, "error": "请先登录"})
                return True
            
            user_role = user.get('role', 'free')
            user_id = user.get('username', client_ip)
            
            length = int(handler.headers.get('Content-Length', 0))
            body = json.loads(handler.rfile.read(length).decode('utf-8'))
            
            domain = body.get('domain', '人工智能')
            count = int(body.get('count', 10000))
            format_type = body.get('format', 'jsonl')
            quality_mode = body.get('quality_mode', 'standard')
            
            if user.get('role') == 'free':
                quality_mode = 'free_trial'
            
            if quality_mode not in QUALITY_MODES:
                quality_mode = 'standard'
            
            task_id = str(uuid.uuid4())[:8]
            
            with task_lock:
                tasks[task_id] = {
                    "id": task_id,
                    "status": "pending",
                    "domain": domain,
                    "count": count,
                    "progress": 0,
                    "total": count,
                    "quality_mode": quality_mode,
                    "created_at": datetime.now().isoformat(),
                    "username": user['username'],
                    "type": "streaming_download"
                }
            
            thread = threading.Thread(
                target=handler._run_streaming_download_task,
                args=(task_id, domain, count, format_type, user['username'], quality_mode),
                daemon=True
            )
            thread.start()
            
            handler._send_json(200, {
                "success": True,
                "task_id": task_id,
                "message": f"已开始生成 {count} 条数据，完成后可直接下载"
            })
        except Exception as e:
            print(f"流式下载生成错误: {e}")
            handler._send_json(500, {"success": False, "error": str(e)})
        return True
    
    elif path == '/api/batch/generate':
        token = handler._get_token_from_request()
        user = handler._get_current_user(token)
        if not user:
            handler._send_json(401, {"success": False, "error": "未登录"})
            return True
        length = int(handler.headers.get('Content-Length', 0))
        body = json.loads(handler.rfile.read(length).decode('utf-8'))
        task_list = body.get('tasks', [])
        results = []
        for task_params in task_list:
            if TASK_QUEUE_AVAILABLE:
                try:
                    mod = get_module('task_queue')
                    TaskPriority = mod.TaskPriority if mod and hasattr(mod, 'TaskPriority') else None
                    priority = TaskPriority.NORMAL if TaskPriority else 5
                    if mod and hasattr(mod, 'task_queue'):
                        result = mod.task_queue.submit_task(
                            "generate",
                            task_params,
                            user['username'],
                            priority
                        )
                    else:
                        result = {"success": False, "error": "任务队列未初始化"}
                except Exception as e:
                    result = {"success": False, "error": str(e)}
            else:
                result = {"success": False, "error": "队列服务不可用"}
            results.append(result)
        handler._send_json(200, {"success": True, "results": results, "total": len(results)})
        return True
    
    return False
