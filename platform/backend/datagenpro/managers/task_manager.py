#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理器
"""

import json
import os
import threading
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskManager:
    """任务管理器"""
    
    def __init__(self, state_file=None):
        self.state_file = state_file or "task_states.json"
        self.tasks = {}
        self.lock = threading.Lock()
        self._load()
    
    def _load(self):
        """加载任务数据 - 带异常处理"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] 加载任务数据失败: {e}")
                self.tasks = {}
    
    def _save(self):
        """保存任务数据 - 带异常处理"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] 保存任务数据失败: {e}")
    
    def create(self, task_id, task_type, params):
        task = {
            "id": task_id,
            "type": task_type,
            "params": params,
            "status": TaskStatus.PENDING.value,
            "progress": 0,
            "total": params.get("count", 100),
            "created_at": datetime.now().isoformat()
        }
        
        with self.lock:
            self.tasks[task_id] = task
            self._save()
        
        return task
    
    def update(self, task_id, **kwargs):
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].update(kwargs)
                self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
                self._save()
    
    def get(self, task_id):
        return self.tasks.get(task_id)
    
    def list(self):
        return list(self.tasks.values())
