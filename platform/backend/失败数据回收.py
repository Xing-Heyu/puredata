#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
失败数据回收机制 - 基于TheoremForge论文

核心思想：
1. 子任务拆解 - 复杂任务分解为简单子任务
2. 失败轨迹分析 - 分析失败原因
3. 数据回收 - 从失败中提取有效部分
4. 迭代优化 - 用回收数据改进生成

论文来源：TheoremForge (arXiv:2601.17332)
核心洞察：失败轨迹中也包含有价值的中间步骤
"""

import json
import random
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import statistics


@dataclass
class SubTask:
    """子任务"""
    task_id: str
    task_type: str
    input_data: Dict
    expected_output: Optional[Dict]
    actual_output: Optional[Dict]
    status: str  # pending, success, failed, partial
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
    """
    子任务拆解器 - 将复杂任务分解为简单子任务
    
    基于TheoremForge的核心理念：
    - 复杂任务 → 多个简单子任务
    - 每个子任务独立评估
    - 失败不影响其他子任务
    """
    
    TASK_TEMPLATES = {
        "generate_user_sequence": {
            "description": "生成用户行为序列",
            "subtasks": [
                {"id": "user_profile", "name": "生成用户画像", "difficulty": 1},
                {"id": "session_context", "name": "生成会话上下文", "difficulty": 2},
                {"id": "action_sequence", "name": "生成行为序列", "difficulty": 3},
                {"id": "emotion_injection", "name": "注入情绪变化", "difficulty": 2},
                {"id": "unexpected_events", "name": "添加意外事件", "difficulty": 2},
            ]
        },
        "generate_dialogue": {
            "description": "生成多轮对话",
            "subtasks": [
                {"id": "context_setup", "name": "设置对话背景", "difficulty": 1},
                {"id": "intent_definition", "name": "定义用户意图", "difficulty": 2},
                {"id": "turn_generation", "name": "生成对话轮次", "difficulty": 3},
                {"id": "emotion_variation", "name": "添加情绪变化", "difficulty": 2},
                {"id": "topic_transition", "name": "话题转换", "difficulty": 3},
            ]
        },
        "generate_multimodal": {
            "description": "生成多模态数据",
            "subtasks": [
                {"id": "text_content", "name": "生成文本内容", "difficulty": 2},
                {"id": "image_metadata", "name": "生成图片元数据", "difficulty": 2},
                {"id": "audio_metadata", "name": "生成音频元数据", "difficulty": 2},
                {"id": "cross_modal_ref", "name": "建立跨模态引用", "difficulty": 3},
            ]
        },
        "quality_check": {
            "description": "数据质量检查",
            "subtasks": [
                {"id": "completeness_check", "name": "完整性检查", "difficulty": 1},
                {"id": "consistency_check", "name": "一致性检查", "difficulty": 2},
                {"id": "authenticity_check", "name": "真实性检查", "difficulty": 3},
                {"id": "privacy_check", "name": "隐私安全检查", "difficulty": 2},
            ]
        }
    }
    
    def decompose(self, task_type: str, input_data: Dict) -> List[SubTask]:
        """拆解任务为子任务"""
        template = self.TASK_TEMPLATES.get(task_type)
        if not template:
            return [SubTask(
                task_id=f"{task_type}_single",
                task_type=task_type,
                input_data=input_data,
                expected_output=None,
                actual_output=None,
                status="pending",
                error_reason=None,
                reusable_parts=[]
            )]
        
        subtasks = []
        for i, sub_def in enumerate(template["subtasks"]):
            subtask = SubTask(
                task_id=f"{task_type}_{sub_def['id']}_{i}",
                task_type=sub_def["name"],
                input_data=self._extract_sub_input(input_data, sub_def),
                expected_output=None,
                actual_output=None,
                status="pending",
                error_reason=None,
                reusable_parts=[]
            )
            subtasks.append(subtask)
        
        return subtasks
    
    def _extract_sub_input(self, main_input: Dict, sub_def: Dict) -> Dict:
        """提取子任务输入"""
        return {
            "main_context": main_input,
            "subtask_type": sub_def["id"],
            "difficulty": sub_def["difficulty"]
        }


class FailureAnalyzer:
    """
    失败分析器 - 分析失败原因并提取可复用部分
    
    核心功能：
    1. 识别失败原因
    2. 提取成功的中间步骤
    3. 评估可复用价值
    """
    
    FAILURE_PATTERNS = {
        "data_incomplete": {
            "pattern": "缺少必要字段",
            "recovery": "补充缺失字段后可复用"
        },
        "format_error": {
            "pattern": "格式不符合要求",
            "recovery": "修正格式后可复用"
        },
        "logic_error": {
            "pattern": "逻辑不一致",
            "recovery": "部分数据可复用"
        },
        "quality_low": {
            "pattern": "质量分数过低",
            "recovery": "低质量部分可丢弃，其余可复用"
        },
        "timeout": {
            "pattern": "处理超时",
            "recovery": "已完成部分可复用"
        },
        "resource_limit": {
            "pattern": "资源限制",
            "recovery": "部分结果可复用"
        }
    }
    
    def analyze(self, subtask: SubTask) -> Tuple[str, List[Dict]]:
        """分析失败原因并提取可复用部分"""
        if subtask.status == "success":
            return "success", [subtask.actual_output] if subtask.actual_output else []
        
        failure_reason = self._identify_failure_reason(subtask)
        reusable_parts = self._extract_reusable_parts(subtask, failure_reason)
        
        return failure_reason, reusable_parts
    
    def _identify_failure_reason(self, subtask: SubTask) -> str:
        """识别失败原因"""
        if subtask.error_reason:
            for key, pattern in self.FAILURE_PATTERNS.items():
                if pattern["pattern"] in subtask.error_reason:
                    return key
        
        if not subtask.actual_output:
            return "data_incomplete"
        
        if subtask.actual_output.get("quality_score", 1.0) < 0.5:
            return "quality_low"
        
        return "unknown"
    
    def _extract_reusable_parts(self, subtask: SubTask, failure_reason: str) -> List[Dict]:
        """提取可复用部分"""
        reusable = []
        
        if not subtask.actual_output:
            return reusable
        
        data = subtask.actual_output
        
        if failure_reason == "data_incomplete":
            for key, value in data.items():
                if value is not None and value != "":
                    reusable.append({
                        "field": key,
                        "value": value,
                        "source": subtask.task_id,
                        "recovery_type": "partial_field"
                    })
        
        elif failure_reason == "quality_low":
            if "parts" in data:
                for part in data["parts"]:
                    if part.get("quality", 0) > 0.5:
                        reusable.append({
                            "data": part,
                            "source": subtask.task_id,
                            "recovery_type": "high_quality_part"
                        })
        
        elif failure_reason == "logic_error":
            if "valid_sections" in data:
                for section in data["valid_sections"]:
                    reusable.append({
                        "data": section,
                        "source": subtask.task_id,
                        "recovery_type": "valid_section"
                    })
        
        elif failure_reason in ["timeout", "resource_limit"]:
            if "completed_steps" in data:
                for step in data["completed_steps"]:
                    reusable.append({
                        "data": step,
                        "source": subtask.task_id,
                        "recovery_type": "completed_step"
                    })
        
        return reusable


class DataRecoveryEngine:
    """
    数据回收引擎 - 从失败轨迹中回收有价值数据
    
    核心功能：
    1. 收集失败轨迹
    2. 分析可复用部分
    3. 重组为有效数据
    4. 评估回收效率
    """
    
    def __init__(self):
        self.decomposer = SubTaskDecomposer()
        self.analyzer = FailureAnalyzer()
        self.recovered_data = []
        self.recovery_stats = {
            "total_trajectories": 0,
            "failed_trajectories": 0,
            "recovered_items": 0,
            "recovery_rate": 0.0
        }
    
    def process_trajectory(self, task_type: str, input_data: Dict,
                           execute_func) -> TaskTrajectory:
        """处理任务轨迹"""
        trajectory_id = hashlib.md5(
            f"{task_type}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        subtasks = self.decomposer.decompose(task_type, input_data)
        
        for subtask in subtasks:
            try:
                result = execute_func(subtask.input_data)
                subtask.actual_output = result
                subtask.status = "success" if self._is_success(result) else "partial"
            except Exception as e:
                subtask.status = "failed"
                subtask.error_reason = str(e)
            
            failure_reason, reusable = self.analyzer.analyze(subtask)
            subtask.reusable_parts = reusable
        
        success_count = sum(1 for s in subtasks if s.status == "success")
        success_rate = success_count / len(subtasks) if subtasks else 0
        
        all_reusable = []
        for subtask in subtasks:
            all_reusable.extend(subtask.reusable_parts)
        
        failure_analysis = self._analyze_trajectory_failure(subtasks)
        
        trajectory = TaskTrajectory(
            trajectory_id=trajectory_id,
            main_task=task_type,
            subtasks=subtasks,
            final_status="success" if success_rate == 1.0 else "partial" if success_rate > 0 else "failed",
            success_rate=success_rate,
            reusable_data=all_reusable,
            failure_analysis=failure_analysis
        )
        
        self._update_stats(trajectory)
        
        return trajectory
    
    def _is_success(self, result: Dict) -> bool:
        """判断是否成功"""
        if not result:
            return False
        if result.get("error"):
            return False
        if result.get("quality_score", 1.0) < 0.6:
            return False
        return True
    
    def _analyze_trajectory_failure(self, subtasks: List[SubTask]) -> Dict:
        """分析轨迹失败情况"""
        failed_subtasks = [s for s in subtasks if s.status == "failed"]
        partial_subtasks = [s for s in subtasks if s.status == "partial"]
        
        failure_reasons = defaultdict(int)
        for subtask in failed_subtasks:
            reason, _ = self.analyzer.analyze(subtask)
            failure_reasons[reason] += 1
        
        return {
            "failed_count": len(failed_subtasks),
            "partial_count": len(partial_subtasks),
            "failure_reasons": dict(failure_reasons),
            "most_common_failure": max(failure_reasons, key=failure_reasons.get) if failure_reasons else None
        }
    
    def _update_stats(self, trajectory: TaskTrajectory):
        """更新统计"""
        self.recovery_stats["total_trajectories"] += 1
        if trajectory.final_status != "success":
            self.recovery_stats["failed_trajectories"] += 1
        self.recovery_stats["recovered_items"] += len(trajectory.reusable_data)
        self.recovery_stats["recovery_rate"] = (
            self.recovery_stats["recovered_items"] / 
            max(self.recovery_stats["total_trajectories"], 1)
        )
    
    def recover_data(self, trajectories: List[TaskTrajectory]) -> List[Dict]:
        """从多个轨迹回收数据"""
        recovered = []
        
        for trajectory in trajectories:
            for item in trajectory.reusable_data:
                recovered_item = self._reconstruct_item(item, trajectory)
                if recovered_item:
                    recovered.append(recovered_item)
        
        self.recovered_data.extend(recovered)
        return recovered
    
    def _reconstruct_item(self, reusable_part: Dict, trajectory: TaskTrajectory) -> Optional[Dict]:
        """重建数据项"""
        if "data" in reusable_part:
            return {
                **reusable_part["data"],
                "_recovered": True,
                "_source_trajectory": trajectory.trajectory_id,
                "_recovery_type": reusable_part.get("recovery_type", "unknown")
            }
        elif "field" in reusable_part and "value" in reusable_part:
            return {
                reusable_part["field"]: reusable_part["value"],
                "_recovered": True,
                "_source_trajectory": trajectory.trajectory_id,
                "_recovery_type": reusable_part.get("recovery_type", "unknown")
            }
        return None
    
    def get_recovery_report(self) -> Dict:
        """获取回收报告"""
        return {
            "statistics": self.recovery_stats,
            "efficiency": {
                "data_utilization": self.recovery_stats["recovery_rate"],
                "failure_recovery_rate": (
                    self.recovery_stats["recovered_items"] / 
                    max(self.recovery_stats["failed_trajectories"], 1)
                )
            },
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if self.recovery_stats["recovery_rate"] > 1.5:
            recommendations.append("回收效率良好，失败数据利用率高")
        
        if self.recovery_stats["failed_trajectories"] > self.recovery_stats["total_trajectories"] * 0.3:
            recommendations.append("失败率较高，建议优化子任务拆解策略")
        
        if self.recovery_stats["recovered_items"] > 0:
            recommendations.append(f"已回收 {self.recovery_stats['recovered_items']} 条有效数据")
        
        return recommendations


class IterativeOptimizer:
    """
    迭代优化器 - 使用回收数据改进生成
    
    核心功能：
    1. 分析失败模式
    2. 调整生成策略
    3. 验证改进效果
    """
    
    def __init__(self, recovery_engine: DataRecoveryEngine):
        self.recovery_engine = recovery_engine
        self.optimization_history = []
    
    def optimize_generation_params(self, task_type: str) -> Dict:
        """优化生成参数"""
        failure_analysis = self._aggregate_failure_analysis(task_type)
        
        optimizations = {}
        
        if failure_analysis.get("data_incomplete", 0) > 3:
            optimizations["require_fields"] = True
            optimizations["field_validation"] = "strict"
        
        if failure_analysis.get("quality_low", 0) > 3:
            optimizations["quality_threshold"] = 0.7
            optimizations["multi_pass_generation"] = True
        
        if failure_analysis.get("logic_error", 0) > 3:
            optimizations["consistency_check"] = True
            optimizations["cross_validation"] = True
        
        self.optimization_history.append({
            "task_type": task_type,
            "failure_analysis": failure_analysis,
            "optimizations": optimizations,
            "timestamp": datetime.now().isoformat()
        })
        
        return optimizations
    
    def _aggregate_failure_analysis(self, task_type: str) -> Dict:
        """聚合失败分析"""
        failure_counts = defaultdict(int)
        
        for trajectory in self.recovery_engine.recovered_data:
            if isinstance(trajectory, dict) and trajectory.get("_source_trajectory"):
                for reason, count in trajectory.get("failure_analysis", {}).get("failure_reasons", {}).items():
                    failure_counts[reason] += count
        
        return dict(failure_counts)


if __name__ == "__main__":
    print("=" * 60)
    print("失败数据回收机制测试 - TheoremForge")
    print("=" * 60)
    
    engine = DataRecoveryEngine()
    
    def mock_execute(input_data):
        """模拟执行函数"""
        if random.random() < 0.3:
            raise Exception("模拟失败：处理超时")
        
        quality = random.uniform(0.3, 1.0)
        return {
            "result": f"处理完成: {input_data.get('subtask_type', 'unknown')}",
            "quality_score": quality,
            "parts": [
                {"content": "部分1", "quality": quality + 0.1},
                {"content": "部分2", "quality": quality - 0.1}
            ] if quality > 0.5 else []
        }
    
    print("\n[1] 测试任务拆解:")
    decomposer = SubTaskDecomposer()
    subtasks = decomposer.decompose("generate_user_sequence", {"user_id": "u001"})
    print(f"  拆解为 {len(subtasks)} 个子任务:")
    for sub in subtasks:
        print(f"    - {sub.task_type} (难度: {sub.input_data.get('difficulty', '?')})")
    
    print("\n[2] 测试轨迹处理:")
    trajectories = []
    for i in range(5):
        trajectory = engine.process_trajectory(
            "generate_user_sequence",
            {"user_id": f"u00{i}"},
            mock_execute
        )
        trajectories.append(trajectory)
        print(f"  轨迹 {i+1}: {trajectory.final_status} (成功率: {trajectory.success_rate:.0%})")
    
    print("\n[3] 测试数据回收:")
    recovered = engine.recover_data(trajectories)
    print(f"  回收数据: {len(recovered)} 条")
    for item in recovered[:3]:
        print(f"    - {item.get('_recovery_type', 'unknown')}: {str(item)[:50]}...")
    
    print("\n[4] 回收报告:")
    report = engine.get_recovery_report()
    print(f"  总轨迹数: {report['statistics']['total_trajectories']}")
    print(f"  失败轨迹: {report['statistics']['failed_trajectories']}")
    print(f"  回收数据: {report['statistics']['recovered_items']}")
    print(f"  回收效率: {report['efficiency']['data_utilization']:.2f} 条/轨迹")
    
    print("\n[5] 改进建议:")
    for rec in report["recommendations"]:
        print(f"  - {rec}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
