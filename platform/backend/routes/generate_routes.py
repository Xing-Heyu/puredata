"""
数据生成相关路由处理
完整版 - 包含所有生成相关的API处理逻辑
"""

import threading
import uuid
import json
from datetime import datetime
from urllib.parse import unquote, quote

def handle_generate_routes(handler, path, method, body, context):
    """
    处理数据生成相关请求
    
    context包含:
    - tasks: 任务字典
    - task_lock: 任务锁
    - QUALITY_MODES: 质量模式配置
    - DOMAINS: 领域配置
    - TEMPLATES: 模板配置
    """
    
    tasks = context.get('tasks', {})
    task_lock = context.get('task_lock')
    print(f"[DEBUG] generate_routes: tasks id={id(tasks)}, len={len(tasks) if tasks else 0}")
    QUALITY_MODES = context.get('QUALITY_MODES', {})
    
    if path == '/generate':
        if method != 'POST':
            handler._send_json(405, {"success": False, "error": "Method not allowed"})
            return True
        
        try:
            domain = body.get('domain', '人工智能')
            try:
                count = int(body.get('count', 100))
                if count < 1 or count > 100000:
                    handler._send_json(400, {"success": False, "error": "生成数量必须在1-100000之间"})
                    return True
            except (ValueError, TypeError):
                handler._send_json(400, {"success": False, "error": "生成数量必须是整数"})
                return True
            
            format_type = body.get('format', 'json')
            mode = body.get('mode', 'hybrid')
            
            try:
                noise_level = int(body.get('noise_level', 2))
                if noise_level < 0 or noise_level > 5:
                    handler._send_json(400, {"success": False, "error": "噪声级别必须在0-5之间"})
                    return True
            except (ValueError, TypeError):
                handler._send_json(400, {"success": False, "error": "噪声级别必须是整数"})
                return True
            
            advanced_noise = body.get('advanced_noise')
            if advanced_noise:
                if advanced_noise.get('intensity', 0) < 0 or advanced_noise.get('intensity', 0) > 1:
                    handler._send_json(400, {"success": False, "error": "噪音强度必须在0-1之间"})
                    return True
            
            quality_mode = body.get('quality_mode', 'standard')
            
            output_type = body.get('output_type', 'text')
            image_style = body.get('image_style', '')
            image_requirement = body.get('image_requirement', '')
            voice_id = body.get('voice_id', 'Cherry')
            
            if quality_mode not in QUALITY_MODES:
                quality_mode = 'standard'
            
            task_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
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
                        "advanced_noise": advanced_noise,
                        "quality_mode": quality_mode,
                        "created_at": datetime.now().isoformat()
                    }
            
            if hasattr(handler, '_run_task'):
                thread = threading.Thread(
                    target=handler._run_task,
                    args=(task_id, domain, count, format_type, mode, None, noise_level, quality_mode, advanced_noise, output_type, image_style, image_requirement, voice_id),
                    daemon=True
                )
                thread.start()
            
            handler._send_json(200, {"success": True, "task_id": task_id})
            
        except Exception as e:
            print(f"生成错误: {e}")
            handler._send_json(500, {"success": False, "error": "数据生成失败，请稍后重试"})
        
        return True
    
    elif path == '/generate_sequence':
        if method != 'POST':
            handler._send_json(405, {"success": False, "error": "Method not allowed"})
            return True
        
        try:
            sequence_data = body.get('sequence', [])
            if not sequence_data:
                handler._send_json(400, {"success": False, "error": "请提供行为序列数据"})
                return True
            
            task_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            if task_lock:
                with task_lock:
                    tasks[task_id] = {
                        "id": task_id,
                        "status": "pending",
                        "type": "sequence",
                        "count": len(sequence_data),
                        "progress": 0,
                        "created_at": datetime.now().isoformat()
                    }
            
            handler._send_json(200, {"success": True, "task_id": task_id, "message": "序列生成任务已创建"})
            
        except Exception as e:
            handler._send_json(500, {"success": False, "error": "序列生成任务创建失败"})
        
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
        if task_id not in tasks:
            handler._send_json(404, {"success": False, "error": "任务不存在"})
            return True
        
        accept_header = handler.headers.get('Accept', '')
        if 'text/event-stream' in accept_header:
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
                    
                    if current_progress != last_progress or current_status != last_status:
                        data = {
                            "id": task_id,
                            "progress": current_progress,
                            "status": current_status,
                            "total": task.get('total', 0),
                            "completed": task.get('completed', 0),
                            "timestamp": datetime.now().isoformat(),
                            "download_url": task.get('download_url', ''),
                            "count": task.get('count', 0),
                            "preview": task.get('preview', [])[:5]
                        }
                        handler.wfile.write(f"data: {json.dumps(data)}\n\n".encode('utf-8'))
                        handler.wfile.flush()
                        
                        last_progress = current_progress
                        last_status = current_status
                    
                    if current_status in ['completed', 'failed']:
                        break
                    
                    time.sleep(0.5)
                    
            except (BrokenPipeError, ConnectionResetError):
                pass
            except Exception as e:
                print(f"[SSE] 推送异常: {e}")
            
            return True
        else:
            task_data = tasks[task_id]
            print(f"[DEBUG] /task/{task_id} 返回: status={task_data.get('status')}, download_url={task_data.get('download_url', '')[:50]}")
            handler._send_json(200, {
                "success": True, 
                "task": task_data,
                "download_url": task_data.get('download_url', ''),
                "count": task_data.get('count', 0),
                "preview": task_data.get('preview', [])[:5]
            })
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
    
    return None
