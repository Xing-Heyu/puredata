#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步任务队列模块
支持：任务排队、优先级处理、并发控制
"""

import json
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import uuid
from concurrent.futures import ThreadPoolExecutor

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
QUEUE_FILE = os.path.join(BACKEND_DIR, 'task_queue.json')

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    URGENT = 20

class TaskStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class QueuedTask:
    task_id: str
    task_type: str
    params: Dict
    priority: int
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    progress: int
    result: Optional[Dict]
    error: Optional[str]
    user_id: str
    retry_count: int
    max_retries: int

class AsyncTaskQueue:
    """异步任务队列"""
    
    MAX_WORKERS = 4
    MAX_QUEUE_SIZE = 100
    TASK_TIMEOUT = 3600
    
    def __init__(self):
        self.task_queue = queue.PriorityQueue(maxsize=self.MAX_QUEUE_SIZE)
        self.tasks: Dict[str, QueuedTask] = {}
        self.handlers: Dict[str, Callable] = {}
        self.lock = threading.Lock()
        self.running = False
        self.workers = []
        self.executor = ThreadPoolExecutor(max_workers=self.MAX_WORKERS)
        self._load()
    
    def _load(self):
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tasks_data = data.get("tasks", {}) if isinstance(data, dict) else {}
                for task_id, task_data in tasks_data.items():
                    if task_data["status"] in [TaskStatus.PENDING.value, TaskStatus.QUEUED.value]:
                        task = QueuedTask(**task_data)
                        self.tasks[task_id] = task
                        self.task_queue.put((-task.priority, task.created_at, task_id))
    
    def _save(self):
        with self.lock:
            data = {
                "tasks": {tid: asdict(t) for tid, t in self.tasks.items()},
                "updated_at": datetime.now().isoformat()
            }
            with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def register_handler(self, task_type: str, handler: Callable):
        self.handlers[task_type] = handler
    
    def submit_task(self, task_type: str, params: Dict, user_id: str, 
                    priority: TaskPriority = TaskPriority.NORMAL,
                    max_retries: int = 3) -> Dict:
        
        task_id = f"QT{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6].upper()}"
        
        task = QueuedTask(
            task_id=task_id,
            task_type=task_type,
            params=params,
            priority=priority.value,
            status=TaskStatus.QUEUED.value,
            created_at=datetime.now().isoformat(),
            started_at=None,
            completed_at=None,
            progress=0,
            result=None,
            error=None,
            user_id=user_id,
            retry_count=0,
            max_retries=max_retries
        )
        
        with self.lock:
            self.tasks[task_id] = task
            try:
                self.task_queue.put((-priority.value, task.created_at, task_id), block=False)
            except queue.Full:
                return {"success": False, "error": "任务队列已满，请稍后重试"}
        
        self._save()
        
        queue_position = self._get_queue_position(task_id)
        
        return {
            "success": True,
            "task_id": task_id,
            "queue_position": queue_position,
            "message": "任务已加入队列"
        }
    
    def _get_queue_position(self, task_id: str) -> int:
        """获取任务在队列中的位置 - 线程安全"""
        with self.lock:
            position = 0
            # 使用 list() 创建队列的快照，在锁保护下确保一致性
            queue_snapshot = list(self.task_queue.queue)
            for item in queue_snapshot:
                if item[2] == task_id:
                    return position + 1
                position += 1
            return 0
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        with self.lock:
            if task_id not in self.tasks:
                return None
            
            task = self.tasks[task_id]
            result = {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "error": task.error
            }
            
            if task.status == TaskStatus.QUEUED.value:
                result["queue_position"] = self._get_queue_position(task_id)
            
            if task.result:
                result["result"] = task.result
            
            return result
    
    def cancel_task(self, task_id: str, user_id: str = None) -> Dict:
        with self.lock:
            if task_id not in self.tasks:
                return {"success": False, "error": "任务不存在"}
            
            task = self.tasks[task_id]
            
            if user_id and task.user_id != user_id:
                return {"success": False, "error": "无权取消此任务"}
            
            if task.status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
                return {"success": False, "error": "任务已完成或已取消"}
            
            task.status = TaskStatus.CANCELLED.value
            task.completed_at = datetime.now().isoformat()
            self._save()
            
            return {"success": True, "message": "任务已取消"}
    
    def get_user_tasks(self, user_id: str, limit: int = 20) -> List[Dict]:
        with self.lock:
            user_tasks = [t for t in self.tasks.values() if t.user_id == user_id]
            user_tasks.sort(key=lambda x: x.created_at, reverse=True)
            return [asdict(t) for t in user_tasks[:limit]]
    
    def get_queue_stats(self) -> Dict:
        with self.lock:
            pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.QUEUED.value)
            running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING.value)
            completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED.value)
            failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED.value)
            
            return {
                "queue_size": self.task_queue.qsize(),
                "pending": pending,
                "running": running,
                "completed": completed,
                "failed": failed,
                "max_workers": self.MAX_WORKERS
            }
    
    def _process_task(self, task_id: str):
        with self.lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            if task.status != TaskStatus.QUEUED.value:
                return
            
            task.status = TaskStatus.RUNNING.value
            task.started_at = datetime.now().isoformat()
        
        self._save()
        
        try:
            if task.task_type in self.handlers:
                handler = self.handlers[task.task_type]
                result = handler(task.params, task_id)
                
                with self.lock:
                    task.status = TaskStatus.COMPLETED.value
                    task.completed_at = datetime.now().isoformat()
                    task.progress = 100
                    task.result = result
            else:
                raise Exception(f"未知的任务类型: {task.task_type}")
        
        except Exception as e:
            with self.lock:
                task.retry_count += 1
                if task.retry_count < task.max_retries:
                    task.status = TaskStatus.QUEUED.value
                    self.task_queue.put((-task.priority, task.created_at, task_id))
                else:
                    task.status = TaskStatus.FAILED.value
                    task.completed_at = datetime.now().isoformat()
                    task.error = str(e)
        
        self._save()
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        
        def worker():
            while self.running:
                try:
                    _, _, task_id = self.task_queue.get(timeout=1)
                    if task_id in self.tasks:
                        task = self.tasks[task_id]
                        if task.status == TaskStatus.QUEUED.value:
                            self._process_task(task_id)
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[Queue] Worker error: {e}")
        
        for i in range(self.MAX_WORKERS):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            self.workers.append(t)
        
        print(f"[Queue] 启动 {self.MAX_WORKERS} 个工作线程")
    
    def stop(self):
        self.running = False
        self.executor.shutdown(wait=False)
        print("[Queue] 队列已停止")

task_queue = AsyncTaskQueue()

if __name__ == "__main__":
    print("="*60)
    print("异步任务队列测试")
    print("="*60)
    
    def sample_handler(params, task_id):
        print(f"处理任务 {task_id}: {params}")
        time.sleep(2)
        return {"message": "完成", "params": params}
    
    task_queue.register_handler("test", sample_handler)
    
    result = task_queue.submit_task("test", {"data": "test"}, "user1", TaskPriority.HIGH)
    print(f"\n提交任务: {result}")
    
    stats = task_queue.get_queue_stats()
    print(f"\n队列状态: {stats}")
