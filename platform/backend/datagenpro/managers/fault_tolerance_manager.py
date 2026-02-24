#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataGen Pro - 容错管理器
断点续传、自动重试、任务队列、混沌工程、数据质量分级

合并自：
- fault_tolerance.py（完整功能）
- datagenpro/managers/fault_tolerance_manager.py（自定义目录支持）
"""

import json
import os
import time
import threading
import hashlib
import random
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class DataQuality(Enum):
    """数据质量等级"""
    PERFECT = "perfect"
    CLEAN = "clean"
    NORMAL = "normal"
    NOISY = "noisy"
    CHAOTIC = "chaotic"

class FaultToleranceManager:
    """容错管理器 - 完整版"""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    CHECKPOINT_INTERVAL = 10
    
    def __init__(self, checkpoint_dir=None, state_file=None, queue_file=None):
        self.checkpoint_dir = checkpoint_dir or "checkpoints"
        self.state_file = state_file or "task_states.json"
        self.queue_file = queue_file or "task_queue.json"
        
        self.task_states = {}
        self.task_queue = []
        self.checkpoints = {}
        self.retry_counts = defaultdict(int)
        self.lock = threading.Lock()
        
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        self._load_states()
        self._load_queue()
    
    def _load_states(self):
        """加载任务状态 - 带异常处理"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.task_states = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] 加载任务状态失败: {e}")
                self.task_states = {}
    
    def _save_states(self):
        """保存任务状态 - 带异常处理"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.task_states, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] 保存任务状态失败: {e}")
    
    def _load_queue(self):
        """加载任务队列 - 带异常处理"""
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    self.task_queue = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ERROR] 加载任务队列失败: {e}")
                self.task_queue = []
    
    def _save_queue(self):
        """保存任务队列 - 带异常处理"""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(self.task_queue, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] 保存任务队列失败: {e}")
    
    def create_task(self, task_id, task_type, params, quality=DataQuality.NORMAL):
        task = {
            "id": task_id,
            "type": task_type,
            "params": params,
            "quality": quality.value if isinstance(quality, DataQuality) else quality,
            "status": TaskStatus.PENDING.value,
            "progress": 0,
            "total": params.get("count", 100),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "checkpoints": [],
            "errors": [],
            "retry_count": 0,
            "result": None
        }
        
        with self.lock:
            self.task_states[task_id] = task
            self.task_queue.append(task_id)
            self._save_states()
            self._save_queue()
        
        return task
    
    def save_checkpoint(self, task_id, progress, data=None):
        checkpoint = {
            "task_id": task_id,
            "progress": progress,
            "timestamp": datetime.now().isoformat(),
            "data_hash": hashlib.md5(str(data).encode()).hexdigest()[:8] if data else None
        }
        
        checkpoint_file = os.path.join(self.checkpoint_dir, f"{task_id}_checkpoint.json")
        checkpoint_data = {"checkpoint": checkpoint, "data": data}
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False)
        
        with self.lock:
            if task_id in self.task_states:
                self.task_states[task_id]["progress"] = progress
                self.task_states[task_id]["updated_at"] = datetime.now().isoformat()
                self.task_states[task_id]["checkpoints"].append(checkpoint)
                self._save_states()
    
    def load_checkpoint(self, task_id):
        checkpoint_file = os.path.join(self.checkpoint_dir, f"{task_id}_checkpoint.json")
        
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def update_status(self, task_id, status, error=None):
        with self.lock:
            if task_id in self.task_states:
                self.task_states[task_id]["status"] = status.value if isinstance(status, TaskStatus) else status
                self.task_states[task_id]["updated_at"] = datetime.now().isoformat()
                
                if error:
                    self.task_states[task_id]["errors"].append({
                        "time": datetime.now().isoformat(),
                        "error": str(error)
                    })
                
                self._save_states()
    
    def handle_failure(self, task_id, error):
        with self.lock:
            if task_id not in self.task_states:
                return False
            
            task = self.task_states[task_id]
            retry_count = task.get("retry_count", 0)
            
            if retry_count < self.MAX_RETRIES:
                task["retry_count"] = retry_count + 1
                task["status"] = TaskStatus.RETRYING.value
                task["errors"].append({
                    "time": datetime.now().isoformat(),
                    "error": str(error),
                    "retry": retry_count + 1
                })
                self._save_states()
                return True
            else:
                task["status"] = TaskStatus.FAILED.value
                self._save_states()
                return False
    
    def get_pending_tasks(self):
        pending = []
        for task_id in self.task_queue:
            if task_id in self.task_states:
                task = self.task_states[task_id]
                if task["status"] in [TaskStatus.PENDING.value, TaskStatus.RETRYING.value]:
                    pending.append(task)
        return pending
    
    def recover_interrupted_tasks(self):
        recovered = []
        for task_id, task in self.task_states.items():
            if task["status"] == TaskStatus.RUNNING.value:
                checkpoint = self.load_checkpoint(task_id)
                if checkpoint:
                    task["status"] = TaskStatus.PENDING.value
                    task["recovered"] = True
                    task["recovery_point"] = checkpoint["checkpoint"]["progress"]
                    recovered.append(task_id)
        
        if recovered:
            self._save_states()
        
        return recovered
    
    def pause_task(self, task_id):
        self.update_status(task_id, TaskStatus.PAUSED)
    
    def abandon_task(self, task_id, reason="用户放弃"):
        with self.lock:
            if task_id in self.task_states:
                self.task_states[task_id]["status"] = TaskStatus.CANCELLED.value
                self.task_states[task_id]["abandoned"] = True
                self.task_states[task_id]["abandon_reason"] = reason
                self.task_states[task_id]["abandoned_at"] = datetime.now().isoformat()
                
                if task_id in self.task_queue:
                    self.task_queue.remove(task_id)
                
                self._save_states()
                self._save_queue()
    
    def detect_abandoned_tasks(self, idle_minutes=30):
        abandoned = []
        cutoff = datetime.now() - timedelta(minutes=idle_minutes)
        
        for task_id, task in self.task_states.items():
            if task["status"] == TaskStatus.RUNNING.value:
                updated = datetime.fromisoformat(task.get("updated_at", "2000-01-01"))
                if updated < cutoff:
                    self.abandon_task(task_id, f"超过{idle_minutes}分钟无响应")
                    abandoned.append(task_id)
        
        return abandoned
    
    def get_partial_result(self, task_id):
        checkpoint = self.load_checkpoint(task_id)
        if checkpoint and "data" in checkpoint:
            return {
                "partial": True,
                "progress": checkpoint["checkpoint"]["progress"],
                "data": checkpoint["data"],
                "message": "这是部分生成结果"
            }
        return None
    
    def resume_task(self, task_id):
        checkpoint = self.load_checkpoint(task_id)
        if checkpoint:
            self.update_status(task_id, TaskStatus.PENDING)
            return checkpoint
        return None
    
    def cancel_task(self, task_id):
        self.update_status(task_id, TaskStatus.CANCELLED)
        with self.lock:
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)
                self._save_queue()
    
    def get_task_info(self, task_id):
        return self.task_states.get(task_id)
    
    def list_all_tasks(self):
        return list(self.task_states.values())
    
    def cleanup_old_tasks(self, days=7):
        cutoff = datetime.now() - timedelta(days=days)
        to_remove = []
        
        for task_id, task in self.task_states.items():
            updated = datetime.fromisoformat(task.get("updated_at", "2000-01-01"))
            if updated < cutoff and task["status"] in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.task_states[task_id]
            checkpoint_file = os.path.join(self.checkpoint_dir, f"{task_id}_checkpoint.json")
            if os.path.exists(checkpoint_file):
                os.remove(checkpoint_file)
        
        if to_remove:
            self._save_states()
        
        return to_remove

class DataQualityController:
    """数据质量控制器"""
    
    QUALITY_CONFIGS = {
        DataQuality.PERFECT: {
            "noise_level": 0,
            "error_rate": 0,
            "completeness": 1.0,
            "consistency": 1.0,
            "description": "完美数据 - 测试基准",
            "use_cases": ["模型评估基准", "自动化测试", "质量对比参照"]
        },
        DataQuality.CLEAN: {
            "noise_level": 0.05,
            "error_rate": 0.01,
            "completeness": 0.99,
            "consistency": 0.98,
            "description": "干净数据 - 预训练",
            "use_cases": ["模型预训练", "知识蒸馏", "高质量微调"]
        },
        DataQuality.NORMAL: {
            "noise_level": 0.15,
            "error_rate": 0.05,
            "completeness": 0.95,
            "consistency": 0.90,
            "description": "正常数据 - 通用",
            "use_cases": ["通用训练", "日常测试", "功能验证"]
        },
        DataQuality.NOISY: {
            "noise_level": 0.30,
            "error_rate": 0.15,
            "completeness": 0.85,
            "consistency": 0.75,
            "description": "噪声数据 - 压力测试",
            "use_cases": ["鲁棒性测试", "噪声容忍训练", "异常检测训练"]
        },
        DataQuality.CHAOTIC: {
            "noise_level": 0.50,
            "error_rate": 0.30,
            "completeness": 0.60,
            "consistency": 0.50,
            "description": "混沌数据 - 极端测试",
            "use_cases": ["极端场景测试", "系统边界测试", "故障恢复训练"]
        }
    }
    
    @staticmethod
    def recommend_quality(use_case):
        recommendations = {
            "测试基准": DataQuality.PERFECT,
            "预训练": DataQuality.CLEAN,
            "通用训练": DataQuality.NORMAL,
            "压力测试": DataQuality.NOISY,
            "极端测试": DataQuality.CHAOTIC,
            "模型评估": DataQuality.PERFECT,
            "鲁棒性测试": DataQuality.NOISY,
            "故障测试": DataQuality.CHAOTIC,
        }
        return recommendations.get(use_case, DataQuality.NORMAL)
    
    @staticmethod
    def generate_perfect_sample(domain, count):
        """生成完美样本 - 100%正确"""
        return [{
            "id": i + 1,
            "text": f"[{domain}] 完美样本 #{i+1}",
            "quality": "perfect",
            "verified": True,
            "confidence": 1.0
        } for i in range(count)]
    
    @staticmethod
    def generate_chaotic_sample(domain, count):
        """生成混沌样本 - 极端混乱"""
        import string
        
        def random_noise():
            return ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*()', k=random.randint(5, 20)))
        
        samples = []
        for i in range(count):
            chaos_type = random.choice([
                "empty", "garbage", "truncated", "corrupted", "mixed"
            ])
            
            if chaos_type == "empty":
                text = ""
            elif chaos_type == "garbage":
                text = random_noise()
            elif chaos_type == "truncated":
                text = f"[{domain}] 样本..."[:random.randint(5, 15)]
            elif chaos_type == "corrupted":
                text = f"[{domain}] 样本" + random_noise()
            else:
                text = random_noise() + f"[{domain}]" + random_noise()
            
            samples.append({
                "id": i + 1,
                "text": text,
                "quality": "chaotic",
                "chaos_type": chaos_type,
                "verified": False,
                "confidence": random.uniform(0, 0.3)
            })
        
        return samples
    
    @staticmethod
    def get_config(quality):
        return DataQualityController.QUALITY_CONFIGS.get(
            quality, 
            DataQualityController.QUALITY_CONFIGS[DataQuality.NORMAL]
        )
    
    @staticmethod
    def apply_quality(data, quality):
        config = DataQualityController.get_config(quality)
        result = []
        
        for item in data:
            if random.random() > config["completeness"]:
                continue
            
            processed = item.copy()
            
            if random.random() < config["noise_level"]:
                processed = DataQualityController._add_noise(processed)
            
            if random.random() < config["error_rate"]:
                processed = DataQualityController._add_error(processed)
            
            result.append(processed)
        
        return result
    
    @staticmethod
    def _add_noise(item):
        if "text" in item and len(item["text"]) > 10:
            text = item["text"]
            pos = random.randint(0, len(text) - 1)
            text = text[:pos] + random.choice([" ", "  ", "\n", "x"]) + text[pos+1:]
            item["text"] = text
        return item
    
    @staticmethod
    def _add_error(item):
        errors = [
            lambda x: {**x, "text": ""},
            lambda x: {**x, "word": ""},
            lambda x: {**x, "category": "unknown"},
        ]
        return random.choice(errors)(item)

fault_manager = FaultToleranceManager()
