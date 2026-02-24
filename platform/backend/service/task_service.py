#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务层 - 任务服务
整合自 task_queue.py 和 datagenpro/managers/task_manager.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from task_queue import AsyncTaskQueue
    TaskService = AsyncTaskQueue
    __all__ = ['TaskService', 'AsyncTaskQueue']
except ImportError:
    from typing import Dict, List, Optional
    from datetime import datetime
    from enum import Enum
    
    class TaskStatus(Enum):
        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
    
    class TaskService:
        """任务服务 - 占位实现"""
        
        def __init__(self):
            self.tasks: Dict[str, Dict] = {}
        
        def create_task(self, task_type: str, params: Dict) -> str:
            task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.tasks)}"
            self.tasks[task_id] = {
                "id": task_id,
                "type": task_type,
                "params": params,
                "status": TaskStatus.PENDING.value,
                "created_at": datetime.now().isoformat()
            }
            return task_id
        
        def get_task(self, task_id: str) -> Optional[Dict]:
            return self.tasks.get(task_id)
        
        def update_task(self, task_id: str, **kwargs) -> bool:
            if task_id in self.tasks:
                self.tasks[task_id].update(kwargs)
                return True
            return False
        
        def list_tasks(self) -> List[Dict]:
            return list(self.tasks.values())
    
    AsyncTaskQueue = TaskService
    __all__ = ['TaskService', 'AsyncTaskQueue']
