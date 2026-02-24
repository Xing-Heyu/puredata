#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量层 - 失败数据回收（常驻模块）
整合自 失败数据回收.py
论文来源：TheoremForge (arXiv:2601.17332)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from 失败数据回收 import DataRecoveryEngine, SubTaskDecomposer, TaskTrajectory
    __all__ = ['DataRecoveryEngine', 'SubTaskDecomposer', 'TaskTrajectory']
except ImportError:
    import json
    import random
    import hashlib
    from typing import Dict, List, Optional, Any
    from dataclasses import dataclass, field
    from datetime import datetime
    from collections import defaultdict
    
    @dataclass
    class SubTask:
        """子任务"""
        task_id: str
        task_type: str
        input_data: Dict
        expected_output: Optional[Dict]
        actual_output: Optional[Dict]
        status: str
        error_reason: Optional[str]
        reusable_parts: List[Dict]
    
    @dataclass
    class TaskTrajectory:
        """任务轨迹"""
        trajectory_id: str
        main_task: str
        subtasks: List[SubTask]
        final_status: str
        success_rate: float
        reusable_data: List[Dict]
        failure_analysis: Dict
    
    class SubTaskDecomposer:
        """子任务拆解器"""
        
        TASK_TEMPLATES = {
            "generate_user_sequence": {
                "description": "生成用户行为序列",
                "subtasks": [
                    {"id": "user_profile", "name": "生成用户画像", "difficulty": 1},
                    {"id": "session_context", "name": "生成会话上下文", "difficulty": 2},
                    {"id": "action_sequence", "name": "生成行为序列", "difficulty": 3},
                ]
            }
        }
        
        def decompose(self, task_type: str, input_data: Dict) -> List[SubTask]:
            """拆解任务"""
            template = self.TASK_TEMPLATES.get(task_type, {})
            subtasks = []
            for st in template.get("subtasks", []):
                subtasks.append(SubTask(
                    task_id=f"{task_type}_{st['id']}",
                    task_type=st["name"],
                    input_data=input_data,
                    expected_output=None,
                    actual_output=None,
                    status="pending",
                    error_reason=None,
                    reusable_parts=[]
                ))
            return subtasks
    
    class DataRecoveryEngine:
        """失败数据回收引擎"""
        
        def __init__(self):
            self.decomposer = SubTaskDecomposer()
            self.trajectories = []
        
        def process_task(self, task_type: str, input_data: Dict, execute_func) -> TaskTrajectory:
            """处理任务并记录轨迹"""
            subtasks = self.decomposer.decompose(task_type, input_data)
            
            success_count = 0
            reusable_data = []
            
            for subtask in subtasks:
                try:
                    result = execute_func(subtask.input_data)
                    subtask.actual_output = result
                    subtask.status = "success"
                    success_count += 1
                    reusable_data.append(result)
                except Exception as e:
                    subtask.status = "failed"
                    subtask.error_reason = str(e)
            
            trajectory = TaskTrajectory(
                trajectory_id=hashlib.md5(f"{task_type}{datetime.now()}".encode()).hexdigest()[:8],
                main_task=task_type,
                subtasks=subtasks,
                final_status="success" if success_count == len(subtasks) else "partial",
                success_rate=success_count / len(subtasks) if subtasks else 0,
                reusable_data=reusable_data,
                failure_analysis={}
            )
            
            self.trajectories.append(trajectory)
            return trajectory
        
        def get_reusable_data(self) -> List[Dict]:
            """获取可复用数据"""
            all_reusable = []
            for trajectory in self.trajectories:
                all_reusable.extend(trajectory.reusable_data)
            return all_reusable
        
        def get_failure_stats(self) -> Dict:
            """获取失败统计"""
            total = len(self.trajectories)
            success = sum(1 for t in self.trajectories if t.final_status == "success")
            partial = sum(1 for t in self.trajectories if t.final_status == "partial")
            
            return {
                "total_tasks": total,
                "success": success,
                "partial": partial,
                "failed": total - success - partial,
                "success_rate": success / total if total > 0 else 0
            }
    
    __all__ = ['DataRecoveryEngine', 'SubTaskDecomposer', 'TaskTrajectory']
