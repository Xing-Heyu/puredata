#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理器模块 - 数据生成处理器
"""

import json
import uuid
import threading
import concurrent.futures
from datetime import datetime
from urllib.parse import urlparse


class GenerationHandler:
    """数据生成处理器 - 处理数据生成相关请求"""
    
    def __init__(self, config, generators):
        self.config = config
        self.generators = generators
        self.tasks = {}
        self.stats = {"total": 0, "today": 0}
        self.task_lock = threading.Lock()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    
    def handle_generate(self, request_handler, generate_func, output_dir):
        """处理生成请求"""
        try:
            length = int(request_handler.headers.get('Content-Length', 0))
            body = json.loads(request_handler.rfile.read(length).decode('utf-8'))
            
            domain = body.get('domain', '人工智能')
            count = int(body.get('count', 100))
            quality_mode = body.get('quality_mode', 'standard')
            format_type = body.get('format', 'json')
            noise_level = body.get('noise_level')
            
            task_id = str(uuid.uuid4())[:8]
            
            with self.task_lock:
                self.tasks[task_id] = {
                    "id": task_id,
                    "domain": domain,
                    "count": count,
                    "status": "pending",
                    "progress": 0,
                    "created_at": datetime.now().isoformat()
                }
            
            def run_generation():
                try:
                    with self.task_lock:
                        self.tasks[task_id]["status"] = "processing"
                    
                    data = generate_func(domain, count, task_id, quality_mode)
                    
                    filename = f"{task_id}_{domain}_{count}.{format_type}"
                    filepath = f"{output_dir}/{filename}"
                    
                    self._save_data(data, filepath, format_type)
                    
                    with self.task_lock:
                        self.tasks[task_id]["status"] = "completed"
                        self.tasks[task_id]["progress"] = 100
                        self.tasks[task_id]["filename"] = filename
                        self.tasks[task_id]["count"] = len(data)
                        self.stats["total"] += len(data)
                        self.stats["today"] += len(data)
                    
                except Exception as e:
                    with self.task_lock:
                        self.tasks[task_id]["status"] = "failed"
                        self.tasks[task_id]["error"] = str(e)
            
            self.executor.submit(run_generation)
            
            return {
                "success": True,
                "task_id": task_id,
                "message": f"已开始生成{count}条{domain}数据"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_task_status(self, task_id):
        """获取任务状态"""
        return self.tasks.get(task_id, {"error": "任务不存在"})
    
    def handle_list_tasks(self):
        """列出所有任务"""
        return {"tasks": list(self.tasks.values())}
    
    def handle_stats(self, user_manager=None):
        """获取统计信息"""
        stats = {
            "total_data": self.stats.get("total", 0),
            "today_data": self.stats.get("today", 0),
            "total_tasks": len(self.tasks),
            "completed_tasks": len([t for t in self.tasks.values() if t.get("status") == "completed"]),
            "pending_tasks": len([t for t in self.tasks.values() if t.get("status") in ["pending", "processing"]]),
        }
        
        if user_manager:
            stats["users"] = len(user_manager.users)
        
        return stats
    
    def _save_data(self, data, filepath, format_type):
        """保存数据"""
        if format_type == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif format_type == 'jsonl':
            with open(filepath, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        elif format_type == 'csv':
            import csv
            if data:
                with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
