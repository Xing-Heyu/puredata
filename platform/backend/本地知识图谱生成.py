#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地知识图谱+任务合成 - 基于REDSearcher论文

核心思想：
1. 本地知识图谱 - 完全离线，不依赖外部API
2. 双约束任务合成 - 难度和多样性可控
3. 工具增强模拟 - 增加意外性，模拟真实用户
4. 零成本数据生成 - 完全自产，无需API调用

论文来源：REDSearcher (arXiv:2602.14234)
核心洞察：本地模拟环境可以生成高质量训练数据，完全脱离真实网络
"""

import json
import random
import hashlib
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import math
import urllib.request
import urllib.parse
import urllib.error
import ssl
import re


@dataclass
class KnowledgeNode:
    """知识节点"""
    node_id: str
    node_type: str  # entity, action, attribute, relation
    name: str
    attributes: Dict[str, Any]
    connections: List[str]


@dataclass
class KnowledgeEdge:
    """知识边"""
    edge_id: str
    source_id: str
    target_id: str
    relation: str
    weight: float
    constraints: Dict[str, Any]


@dataclass
class TaskTemplate:
    """任务模板"""
    template_id: str
    task_type: str
    difficulty_range: Tuple[int, int]
    required_entities: List[str]
    required_actions: List[str]
    constraints: Dict[str, Any]
    generation_hints: List[str]


@dataclass
class SynthesizedTask:
    """合成的任务"""
    task_id: str
    task_type: str
    difficulty: int
    entities: List[Dict]
    actions: List[Dict]
    constraints: Dict[str, Any]
    expected_trajectory: List[Dict]
    tool_requirements: List[str]
    complexity_score: float


class LocalKnowledgeGraph:
    """
    本地知识图谱 - 完全离线运行
    
    功能：
    1. 存储实体、动作、属性、关系
    2. 支持路径查询
    3. 支持约束推理
    4. 完全离线，零API成本
    """
    
    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, KnowledgeEdge] = {}
        self.type_index: Dict[str, Set[str]] = defaultdict(set)
        
        self._initialize_default_knowledge()
    
    def _initialize_default_knowledge(self):
        """初始化默认知识"""
        entities = [
            {"id": "user", "type": "entity", "name": "用户", "attrs": {"age_range": "18-65", "device": ["mobile", "desktop", "tablet"]}},
            {"id": "product", "type": "entity", "name": "商品", "attrs": {"category": ["电子产品", "服装", "食品", "家居"], "price_range": "10-10000"}},
            {"id": "order", "type": "entity", "name": "订单", "attrs": {"status": ["pending", "paid", "shipped", "delivered", "cancelled"]}},
            {"id": "payment", "type": "entity", "name": "支付", "attrs": {"method": ["alipay", "wechat", "card", "cash"]}},
            {"id": "review", "type": "entity", "name": "评价", "attrs": {"rating": "1-5", "sentiment": ["positive", "neutral", "negative"]}},
            {"id": "coupon", "type": "entity", "name": "优惠券", "attrs": {"type": ["discount", "cash", "free_shipping"]}},
            {"id": "cart", "type": "entity", "name": "购物车", "attrs": {"capacity": "1-50"}},
            {"id": "address", "type": "entity", "name": "地址", "attrs": {"type": ["home", "work", "other"]}},
        ]
        
        actions = [
            {"id": "browse", "type": "action", "name": "浏览", "attrs": {"duration": "1-300s", "depth": "1-5"}},
            {"id": "search", "type": "action", "name": "搜索", "attrs": {"query_type": ["keyword", "category", "brand"]}},
            {"id": "click", "type": "action", "name": "点击", "attrs": {"target": ["product", "ad", "recommendation"]}},
            {"id": "add_to_cart", "type": "action", "name": "加入购物车", "attrs": {"quantity": "1-10"}},
            {"id": "remove_from_cart", "type": "action", "name": "移出购物车", "attrs": {}},
            {"id": "checkout", "type": "action", "name": "结算", "attrs": {}},
            {"id": "pay", "type": "action", "name": "支付", "attrs": {}},
            {"id": "cancel", "type": "action", "name": "取消", "attrs": {}},
            {"id": "refund", "type": "action", "name": "退款", "attrs": {}},
            {"id": "review_action", "type": "action", "name": "评价", "attrs": {}},
            {"id": "share", "type": "action", "name": "分享", "attrs": {"platform": ["wechat", "weibo", "qq"]}},
            {"id": "favorite", "type": "action", "name": "收藏", "attrs": {}},
            {"id": "compare", "type": "action", "name": "对比", "attrs": {"compare_count": "2-5"}},
            {"id": "consult", "type": "action", "name": "咨询客服", "attrs": {"topic": ["product", "logistics", "payment", "refund"]}},
        ]
        
        attributes = [
            {"id": "price", "type": "attribute", "name": "价格", "attrs": {"range": "0-100000"}},
            {"id": "quality", "type": "attribute", "name": "质量", "attrs": {"level": ["high", "medium", "low"]}},
            {"id": "brand", "type": "attribute", "name": "品牌", "attrs": {}},
            {"id": "stock", "type": "attribute", "name": "库存", "attrs": {"range": "0-10000"}},
            {"id": "rating", "type": "attribute", "name": "评分", "attrs": {"range": "1-5"}},
        ]
        
        relations = [
            {"source": "user", "target": "product", "relation": "浏览", "weight": 1.0},
            {"source": "user", "target": "product", "relation": "购买", "weight": 0.8},
            {"source": "user", "target": "product", "relation": "收藏", "weight": 0.6},
            {"source": "user", "target": "cart", "relation": "管理", "weight": 0.9},
            {"source": "product", "target": "order", "relation": "属于", "weight": 1.0},
            {"source": "order", "target": "payment", "relation": "支付", "weight": 1.0},
            {"source": "order", "target": "review", "relation": "评价", "weight": 0.5},
            {"source": "user", "target": "coupon", "relation": "使用", "weight": 0.7},
            {"source": "browse", "target": "search", "relation": "前置", "weight": 0.6},
            {"source": "search", "target": "click", "relation": "导致", "weight": 0.8},
            {"source": "click", "target": "add_to_cart", "relation": "转化", "weight": 0.5},
            {"source": "add_to_cart", "target": "checkout", "relation": "推进", "weight": 0.7},
            {"source": "checkout", "target": "pay", "relation": "完成", "weight": 0.9},
        ]
        
        for entity in entities:
            self.add_node(KnowledgeNode(
                node_id=entity["id"],
                node_type=entity["type"],
                name=entity["name"],
                attributes=entity["attrs"],
                connections=[]
            ))
        
        for action in actions:
            self.add_node(KnowledgeNode(
                node_id=action["id"],
                node_type=action["type"],
                name=action["name"],
                attributes=action["attrs"],
                connections=[]
            ))
        
        for attr in attributes:
            self.add_node(KnowledgeNode(
                node_id=attr["id"],
                node_type=attr["type"],
                name=attr["name"],
                attributes=attr["attrs"],
                connections=[]
            ))
        
        for i, rel in enumerate(relations):
            self.add_edge(KnowledgeEdge(
                edge_id=f"edge_{i}",
                source_id=rel["source"],
                target_id=rel["target"],
                relation=rel["relation"],
                weight=rel["weight"],
                constraints={}
            ))
    
    def add_node(self, node: KnowledgeNode):
        """添加节点"""
        self.nodes[node.node_id] = node
        self.type_index[node.node_type].add(node.node_id)
    
    def add_edge(self, edge: KnowledgeEdge):
        """添加边"""
        self.edges[edge.edge_id] = edge
        if edge.source_id in self.nodes:
            self.nodes[edge.source_id].connections.append(edge.edge_id)
    
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """获取节点"""
        return self.nodes.get(node_id)
    
    def get_nodes_by_type(self, node_type: str) -> List[KnowledgeNode]:
        """按类型获取节点"""
        return [self.nodes[nid] for nid in self.type_index.get(node_type, set())]
    
    def get_neighbors(self, node_id: str, relation: str = None) -> List[KnowledgeNode]:
        """获取邻居节点"""
        node = self.nodes.get(node_id)
        if not node:
            return []
        
        neighbors = []
        for edge_id in node.connections:
            edge = self.edges.get(edge_id)
            if edge and (relation is None or edge.relation == relation):
                neighbor = self.nodes.get(edge.target_id)
                if neighbor:
                    neighbors.append(neighbor)
        
        return neighbors
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 5) -> List[List[str]]:
        """查找路径"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return []
        
        paths = []
        queue = [(start_id, [start_id])]
        visited = set()
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            if current == end_id:
                paths.append(path)
                continue
            
            if current in visited:
                continue
            visited.add(current)
            
            for neighbor in self.get_neighbors(current):
                if neighbor.node_id not in path:
                    queue.append((neighbor.node_id, path + [neighbor.node_id]))
        
        return paths
    
    def get_random_entity(self, entity_type: str = None) -> Optional[KnowledgeNode]:
        """获取随机实体"""
        if entity_type:
            nodes = list(self.type_index.get(entity_type, set()))
        else:
            nodes = list(self.type_index.get("entity", set()))
        
        if nodes:
            return self.nodes[random.choice(nodes)]
        return None
    
    def get_random_action(self) -> Optional[KnowledgeNode]:
        """获取随机动作"""
        actions = list(self.type_index.get("action", set()))
        if actions:
            return self.nodes[random.choice(actions)]
        return None


class DualConstraintTaskSynthesizer:
    """
    双约束任务合成器 - 基于REDSearcher论文
    
    核心功能：
    1. 难度约束 - 控制任务复杂度
    2. 多样性约束 - 保证数据多样性
    3. 工具增强 - 模拟需要工具的任务
    """
    
    DIFFICULTY_LEVELS = {
        1: {"name": "简单", "steps": "1-3", "entities": "1-2", "actions": "1-2"},
        2: {"name": "较简单", "steps": "3-5", "entities": "2-3", "actions": "2-3"},
        3: {"name": "中等", "steps": "5-8", "entities": "3-4", "actions": "3-5"},
        4: {"name": "较复杂", "steps": "8-12", "entities": "4-5", "actions": "5-8"},
        5: {"name": "复杂", "steps": "12-20", "entities": "5+", "actions": "8+"},
    }
    
    TASK_TYPES = {
        "simple_browse": {"difficulty": 1, "description": "简单浏览任务"},
        "search_and_view": {"difficulty": 2, "description": "搜索查看任务"},
        "add_to_cart": {"difficulty": 2, "description": "加购任务"},
        "complete_purchase": {"difficulty": 3, "description": "完整购买任务"},
        "compare_products": {"difficulty": 3, "description": "商品对比任务"},
        "consult_and_buy": {"difficulty": 4, "description": "咨询后购买任务"},
        "complex_shopping": {"difficulty": 5, "description": "复杂购物任务"},
        "return_refund": {"difficulty": 3, "description": "退换货任务"},
        "multi_session": {"difficulty": 4, "description": "多会话任务"},
        "cross_platform": {"difficulty": 5, "description": "跨平台任务"},
    }
    
    def __init__(self, knowledge_graph: LocalKnowledgeGraph):
        self.kg = knowledge_graph
        self.synthesis_history = []
    
    def synthesize(self, difficulty: int = None, task_type: str = None,
                   diversity_constraint: Dict = None) -> SynthesizedTask:
        """合成任务"""
        if difficulty is None:
            difficulty = random.randint(1, 5)
        
        if task_type is None:
            valid_types = [t for t, info in self.TASK_TYPES.items() 
                          if info["difficulty"] <= difficulty]
            task_type = random.choice(valid_types) if valid_types else "simple_browse"
        
        entities = self._select_entities(difficulty, diversity_constraint)
        actions = self._select_actions(difficulty, entities, diversity_constraint)
        constraints = self._generate_constraints(difficulty, entities, actions)
        trajectory = self._generate_trajectory(entities, actions, constraints)
        tools = self._determine_tool_requirements(actions)
        complexity = self._calculate_complexity(entities, actions, constraints)
        
        task = SynthesizedTask(
            task_id=f"task_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
            task_type=task_type,
            difficulty=difficulty,
            entities=entities,
            actions=actions,
            constraints=constraints,
            expected_trajectory=trajectory,
            tool_requirements=tools,
            complexity_score=complexity
        )
        
        self.synthesis_history.append(task)
        return task
    
    def _select_entities(self, difficulty: int, diversity_constraint: Dict) -> List[Dict]:
        """选择实体"""
        entity_count = min(difficulty + 1, 5)
        entities = []
        
        used_types = set()
        for _ in range(entity_count):
            entity = self.kg.get_random_entity("entity")
            if entity:
                entity_data = {
                    "id": entity.node_id,
                    "name": entity.name,
                    "type": entity.node_type,
                    "attributes": self._sample_attributes(entity.attributes)
                }
                entities.append(entity_data)
                used_types.add(entity.node_id)
        
        return entities
    
    def _select_actions(self, difficulty: int, entities: List[Dict],
                        diversity_constraint: Dict) -> List[Dict]:
        """选择动作"""
        action_count = min(difficulty * 2, 10)
        actions = []
        
        for _ in range(action_count):
            action = self.kg.get_random_action()
            if action:
                action_data = {
                    "id": action.node_id,
                    "name": action.name,
                    "attributes": self._sample_attributes(action.attributes)
                }
                actions.append(action_data)
        
        return actions
    
    def _sample_attributes(self, attributes: Dict) -> Dict:
        """采样属性值"""
        result = {}
        for key, value in attributes.items():
            if isinstance(value, list):
                result[key] = random.choice(value)
            elif isinstance(value, str) and "-" in value:
                parts = value.split("-")
                if len(parts) == 2:
                    try:
                        start = int(''.join(filter(str.isdigit, parts[0])))
                        end = int(''.join(filter(str.isdigit, parts[1])))
                        if start > 0 and end > start:
                            result[key] = random.randint(start, end)
                        else:
                            result[key] = value
                    except (ValueError, IndexError):
                        result[key] = value
                else:
                    result[key] = value
            else:
                result[key] = value
        return result
    
    def _generate_constraints(self, difficulty: int, entities: List[Dict],
                              actions: List[Dict]) -> Dict:
        """生成约束"""
        return {
            "max_steps": difficulty * 3 + 5,
            "time_limit": difficulty * 60,
            "must_include_entities": [e["id"] for e in entities[:difficulty]],
            "must_include_actions": [a["id"] for a in actions[:difficulty]],
            "forbidden_patterns": [] if difficulty < 4 else ["direct_purchase"],
            "quality_threshold": 0.5 + difficulty * 0.1
        }
    
    def _generate_trajectory(self, entities: List[Dict], actions: List[Dict],
                             constraints: Dict) -> List[Dict]:
        """生成预期轨迹"""
        trajectory = []
        
        user_entity = next((e for e in entities if e["id"] == "user"), entities[0] if entities else None)
        
        if not user_entity:
            return trajectory
        
        step_count = min(constraints.get("max_steps", 10), len(actions) + 2)
        
        for i in range(step_count):
            if i < len(actions):
                action = actions[i]
            else:
                action = random.choice(actions) if actions else {"name": "浏览"}
            
            step = {
                "step": i + 1,
                "actor": user_entity.get("id", "user"),
                "action": action.get("name", "浏览"),
                "target": random.choice(entities).get("id", "product") if entities else "product",
                "timestamp_offset": i * random.randint(10, 60)
            }
            trajectory.append(step)
        
        return trajectory
    
    def _determine_tool_requirements(self, actions: List[Dict]) -> List[str]:
        """确定工具需求"""
        tools = []
        
        action_tools = {
            "搜索": ["search_engine"],
            "对比": ["comparison_tool"],
            "支付": ["payment_gateway"],
            "咨询客服": ["chat_system"],
            "分享": ["social_platform"],
        }
        
        for action in actions:
            action_name = action.get("name", "")
            for key, required_tools in action_tools.items():
                if key in action_name:
                    tools.extend(required_tools)
        
        return list(set(tools))
    
    def _calculate_complexity(self, entities: List[Dict], actions: List[Dict],
                              constraints: Dict) -> float:
        """计算复杂度分数"""
        entity_factor = len(entities) * 0.1
        action_factor = len(actions) * 0.15
        constraint_factor = len(constraints.get("forbidden_patterns", [])) * 0.2
        tool_factor = len(self._determine_tool_requirements(actions)) * 0.1
        
        return min(1.0, entity_factor + action_factor + constraint_factor + tool_factor)
    
    def batch_synthesize(self, count: int, difficulty_distribution: Dict = None) -> List[SynthesizedTask]:
        """批量合成任务"""
        if difficulty_distribution is None:
            difficulty_distribution = {1: 0.2, 2: 0.3, 3: 0.25, 4: 0.15, 5: 0.1}
        
        tasks = []
        for _ in range(count):
            rand = random.random()
            cumulative = 0
            difficulty = 3
            
            for diff, prob in difficulty_distribution.items():
                cumulative += prob
                if rand < cumulative:
                    difficulty = diff
                    break
            
            task = self.synthesize(difficulty=difficulty)
            tasks.append(task)
        
        return tasks


class ToolAugmentedSimulator:
    """
    工具增强模拟器 - 模拟需要工具的任务执行
    
    核心功能：
    1. 模拟工具调用
    2. 增加意外性
    3. 生成真实感轨迹
    """
    
    SIMULATED_TOOLS = {
        "search_engine": {
            "success_rate": 0.95,
            "latency_range": (0.1, 2.0),
            "failure_modes": ["no_results", "timeout", "irrelevant_results"]
        },
        "comparison_tool": {
            "success_rate": 0.9,
            "latency_range": (0.5, 3.0),
            "failure_modes": ["incompatible_items", "insufficient_data"]
        },
        "payment_gateway": {
            "success_rate": 0.98,
            "latency_range": (1.0, 5.0),
            "failure_modes": ["insufficient_balance", "network_error", "card_declined"]
        },
        "chat_system": {
            "success_rate": 0.99,
            "latency_range": (0.5, 10.0),
            "failure_modes": ["agent_unavailable", "queue_full"]
        },
        "social_platform": {
            "success_rate": 0.95,
            "latency_range": (0.2, 2.0),
            "failure_modes": ["auth_expired", "rate_limited"]
        }
    }
    
    def __init__(self):
        self.simulation_history = []
    
    def simulate_task_execution(self, task: SynthesizedTask) -> Dict:
        """模拟任务执行"""
        result = {
            "task_id": task.task_id,
            "execution_steps": [],
            "tool_calls": [],
            "unexpected_events": [],
            "final_status": "success",
            "execution_time": 0
        }
        
        total_time = 0
        
        for step in task.expected_trajectory:
            step_result = self._simulate_step(step, task.tool_requirements)
            result["execution_steps"].append(step_result)
            total_time += step_result.get("duration", 0)
            
            if step_result.get("tool_call"):
                result["tool_calls"].append(step_result["tool_call"])
            
            if step_result.get("unexpected"):
                result["unexpected_events"].append(step_result["unexpected"])
            
            if step_result.get("status") == "failed":
                result["final_status"] = "partial"
        
        result["execution_time"] = total_time
        self.simulation_history.append(result)
        
        return result
    
    def _simulate_step(self, step: Dict, required_tools: List[str]) -> Dict:
        """模拟单步执行"""
        step_result = {
            "step": step,
            "status": "success",
            "duration": random.uniform(0.1, 1.0),
            "tool_call": None,
            "unexpected": None
        }
        
        action = step.get("action", "")
        
        for tool_id in required_tools:
            tool_config = self.SIMULATED_TOOLS.get(tool_id, {})
            
            if any(keyword in action for keyword in ["搜索", "查找", "检索"]):
                if tool_id == "search_engine":
                    step_result["tool_call"] = self._simulate_tool_call(tool_id, tool_config)
                    step_result["duration"] += step_result["tool_call"].get("latency", 0)
            
            elif any(keyword in action for keyword in ["支付", "付款"]):
                if tool_id == "payment_gateway":
                    step_result["tool_call"] = self._simulate_tool_call(tool_id, tool_config)
                    step_result["duration"] += step_result["tool_call"].get("latency", 0)
            
            elif any(keyword in action for keyword in ["咨询", "客服"]):
                if tool_id == "chat_system":
                    step_result["tool_call"] = self._simulate_tool_call(tool_id, tool_config)
                    step_result["duration"] += step_result["tool_call"].get("latency", 0)
        
        if random.random() < 0.1:
            step_result["unexpected"] = self._generate_unexpected_event(step)
        
        return step_result
    
    def _simulate_tool_call(self, tool_id: str, config: Dict) -> Dict:
        """模拟工具调用"""
        success_rate = config.get("success_rate", 0.9)
        latency_range = config.get("latency_range", (0.5, 2.0))
        failure_modes = config.get("failure_modes", ["unknown_error"])
        
        is_success = random.random() < success_rate
        latency = random.uniform(*latency_range)
        
        return {
            "tool": tool_id,
            "status": "success" if is_success else "failed",
            "latency": latency,
            "error": random.choice(failure_modes) if not is_success else None,
            "response": self._generate_tool_response(tool_id, is_success)
        }
    
    def _generate_tool_response(self, tool_id: str, success: bool) -> Dict:
        """生成工具响应"""
        if success:
            responses = {
                "search_engine": {"results_count": random.randint(1, 100)},
                "comparison_tool": {"comparison_matrix": "generated"},
                "payment_gateway": {"transaction_id": f"txn_{random.randint(10000, 99999)}"},
                "chat_system": {"agent_id": f"agent_{random.randint(1, 10)}", "queue_position": 0},
                "social_platform": {"share_id": f"share_{random.randint(1000, 9999)}"}
            }
            return responses.get(tool_id, {"status": "ok"})
        else:
            return {"error": "tool_call_failed"}
    
    def _generate_unexpected_event(self, step: Dict) -> Dict:
        """生成意外事件"""
        events = [
            {"type": "interruption", "description": "用户被电话打断", "delay": random.randint(30, 300)},
            {"type": "distraction", "description": "用户分心浏览其他页面", "delay": random.randint(10, 60)},
            {"type": "hesitation", "description": "用户犹豫不决", "delay": random.randint(60, 300)},
            {"type": "price_change", "description": "商品价格变动", "impact": "reconsider"},
            {"type": "stock_change", "description": "库存变化", "impact": "urgent_decision"},
            {"type": "coupon_expire", "description": "优惠券即将过期", "impact": "hurry"},
        ]
        
        return random.choice(events)


class ZeroCostDataGenerator:
    """
    零成本数据生成器 - 整合所有组件
    
    核心功能：
    1. 完全离线运行
    2. 知识图谱驱动
    3. 工具增强模拟
    4. 零API成本
    """
    
    def __init__(self):
        self.kg = LocalKnowledgeGraph()
        self.synthesizer = DualConstraintTaskSynthesizer(self.kg)
        self.simulator = ToolAugmentedSimulator()
        self.generation_stats = {
            "total_tasks": 0,
            "total_steps": 0,
            "unexpected_events": 0,
            "api_calls_saved": 0
        }
    
    def generate(self, count: int = 100, difficulty_distribution: Dict = None) -> Dict:
        """生成数据"""
        tasks = self.synthesizer.batch_synthesize(count, difficulty_distribution)
        
        results = []
        for task in tasks:
            execution = self.simulator.simulate_task_execution(task)
            results.append({
                "task": {
                    "id": task.task_id,
                    "type": task.task_type,
                    "difficulty": task.difficulty,
                    "complexity": task.complexity_score
                },
                "execution": execution,
                "data": self._extract_data(task, execution)
            })
            
            self.generation_stats["total_tasks"] += 1
            self.generation_stats["total_steps"] += len(execution["execution_steps"])
            self.generation_stats["unexpected_events"] += len(execution["unexpected_events"])
            self.generation_stats["api_calls_saved"] += len(execution["tool_calls"])
        
        return {
            "data": results,
            "stats": self.generation_stats,
            "cost_saved": self._calculate_cost_saved()
        }
    
    def _extract_data(self, task: SynthesizedTask, execution: Dict) -> List[Dict]:
        """提取生成数据"""
        data = []
        
        for step in execution["execution_steps"]:
            record = {
                "user_id": f"user_{random.randint(1, 100)}",
                "action": step["step"].get("action", "unknown"),
                "target": step["step"].get("target", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "duration": step.get("duration", 0),
                "unexpected": step.get("unexpected"),
                "tool_used": step.get("tool_call", {}).get("tool") if step.get("tool_call") else None,
                "task_type": task.task_type,
                "difficulty": task.difficulty
            }
            data.append(record)
        
        return data
    
    def _calculate_cost_saved(self) -> Dict:
        """计算节省的成本"""
        api_calls = self.generation_stats["api_calls_saved"]
        avg_cost_per_call = 0.008
        
        return {
            "api_calls_equivalent": api_calls,
            "cost_saved_yuan": api_calls * avg_cost_per_call,
            "cost_saved_usd": api_calls * avg_cost_per_call / 7.2
        }
    
    def get_knowledge_stats(self) -> Dict:
        """获取知识图谱统计"""
        return {
            "total_nodes": len(self.kg.nodes),
            "total_edges": len(self.kg.edges),
            "node_types": {t: len(ids) for t, ids in self.kg.type_index.items()},
            "avg_connections": sum(len(n.connections) for n in self.kg.nodes.values()) / max(len(self.kg.nodes), 1)
        }


class KGRepoSearch:
    """
    联网搜索开源可商用知识图谱库 - 可选功能
    
    优先联网搜索，搜索失败则使用内置推荐列表。
    不影响核心离线生成功能。
    """
    
    # 内置：已知的开源可商用知识图谱库（许可证均为 Apache 2.0 / MIT / BSD 等宽松协议）
    BUILTIN_KG_REPOS = [
        {
            "name": "Neo4j Community Edition",
            "url": "https://github.com/neo4j/neo4j",
            "license": "GPLv3 (Community), 商用需企业版",
            "language": "Java",
            "description": "最流行的图数据库，Cypher查询语言，社区版可免费用于非GPL项目",
            "stars": "13k+",
            "commercial_friendly": "conditional"
        },
        {
            "name": "JanusGraph",
            "url": "https://github.com/JanusGraph/janusgraph",
            "license": "Apache 2.0",
            "language": "Java",
            "description": "Linux基金会下的分布式图数据库，支持HBase/Cassandra/BerkeleyDB后端",
            "stars": "5k+",
            "commercial_friendly": True
        },
        {
            "name": "ArangoDB",
            "url": "https://github.com/arangodb/arangodb",
            "license": "Apache 2.0 (Community)",
            "language": "C++",
            "description": "多模型数据库（图+文档+键值），AQL查询语言",
            "stars": "14k+",
            "commercial_friendly": True
        },
        {
            "name": "Dgraph",
            "url": "https://github.com/dgraph-io/dgraph",
            "license": "Apache 2.0",
            "language": "Go",
            "description": "原生GraphQL图数据库，分布式、高性能、支持ACID事务",
            "stars": "20k+",
            "commercial_friendly": True
        },
        {
            "name": "NebulaGraph",
            "url": "https://github.com/vesoft-inc/nebula",
            "license": "Apache 2.0",
            "language": "C++",
            "description": "国产开源的分布式图数据库，高性能、水平扩展，支持openCypher",
            "stars": "10k+",
            "commercial_friendly": True
        },
        {
            "name": "Apache TinkerPop / Gremlin",
            "url": "https://github.com/apache/tinkerpop",
            "license": "Apache 2.0",
            "language": "Java",
            "description": "图计算框架标准，Gremlin图遍历语言，生态广泛",
            "stars": "2k+",
            "commercial_friendly": True
        },
        {
            "name": "NetworkX",
            "url": "https://github.com/networkx/networkx",
            "license": "BSD-3-Clause",
            "language": "Python",
            "description": "Python图分析库，轻量级，适合研究和原型开发",
            "stars": "15k+",
            "commercial_friendly": True
        },
        {
            "name": "PyTorch Geometric (PyG)",
            "url": "https://github.com/pyg-team/pytorch_geometric",
            "license": "MIT",
            "language": "Python",
            "description": "图神经网络框架，基于PyTorch，适合GNN研究和应用",
            "stars": "22k+",
            "commercial_friendly": True
        },
        {
            "name": "igraph",
            "url": "https://github.com/igraph/igraph",
            "license": "GPLv2",
            "language": "C / R / Python",
            "description": "高效的图分析库，支持大规模网络分析",
            "stars": "1k+",
            "commercial_friendly": "conditional"
        },
        {
            "name": "OrientDB",
            "url": "https://github.com/orientechnologies/orientdb",
            "license": "Apache 2.0",
            "language": "Java",
            "description": "多模型数据库，图+文档，支持SQL扩展语法",
            "stars": "4k+",
            "commercial_friendly": True
        },
    ]
    
    @staticmethod
    def _try_web_search(query: str, timeout: float = 3.0) -> Optional[str]:
        """
        尝试联网搜索（使用 DuckDuckGo Lite，无需API key）
        失败返回 None，不影响主流程
        """
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}"
            
            # 忽略 SSL 验证问题（内网环境兼容）
            ctx = ssl.create_default_context()
            
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                return html
        except Exception:
            return None
    
    @staticmethod
    def _parse_duckduckgo_results(html: str, max_results: int = 10) -> List[Dict]:
        """解析 DuckDuckGo Lite 搜索结果"""
        results = []
        
        # 提取链接和标题
        link_pattern = re.compile(
            r'<a[^>]*class="result-link"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            re.DOTALL
        )
        snippet_pattern = re.compile(
            r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>',
            re.DOTALL
        )
        
        links = link_pattern.findall(html)
        snippets = snippet_pattern.findall(html)
        
        for i, (href, title) in enumerate(links[:max_results]):
            title_clean = re.sub(r'<[^>]+>', '', title).strip()
            snippet_clean = ""
            if i < len(snippets):
                snippet_clean = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            
            results.append({
                "title": title_clean,
                "url": href,
                "snippet": snippet_clean[:300]
            })
        
        return results
    
    @classmethod
    def search_kg_libraries(cls, use_web: bool = True, timeout: float = 3.0) -> Dict:
        """
        搜索开源可商用的知识图谱库
        
        Args:
            use_web: 是否尝试联网搜索
            timeout: 联网超时秒数
        
        Returns:
            {"web_results": [...], "builtin_results": [...], "source": "web"|"builtin"}
        """
        result = {
            "web_results": [],
            "builtin_results": cls.BUILTIN_KG_REPOS,
            "source": "builtin"
        }
        
        if use_web:
            queries = [
                "open source knowledge graph database commercial Apache license",
                "开源知识图谱 图数据库 可商用 Apache",
            ]
            
            all_web = []
            for query in queries:
                html = cls._try_web_search(query, timeout=timeout)
                if html:
                    parsed = cls._parse_duckduckgo_results(html, max_results=5)
                    all_web.extend(parsed)
            
            if all_web:
                # 去重
                seen = set()
                unique = []
                for item in all_web:
                    if item["url"] not in seen:
                        seen.add(item["url"])
                        unique.append(item)
                
                result["web_results"] = unique
                result["source"] = "web"
        
        return result
    
    @classmethod
    def recommend(cls, use_web: bool = True) -> List[Dict]:
        """
        推荐最适合商用的知识图谱库
        联网获取的排在前面，内置列表作为补充
        """
        search_result = cls.search_kg_libraries(use_web=use_web)
        
        recommendations = []
        
        # 联网结果
        if search_result["web_results"]:
            for item in search_result["web_results"]:
                recommendations.append({
                    "name": item["title"],
                    "url": item["url"],
                    "description": item["snippet"],
                    "source": "web",
                    "commercial_friendly": "需自行验证许可证"
                })
        
        # 内置推荐
        for repo in search_result["builtin_results"]:
            repo["source"] = "builtin"
            recommendations.append(repo)
        
        return recommendations
    
    @classmethod
    def print_recommendations(cls, use_web: bool = True):
        """打印推荐列表"""
        print("\n" + "=" * 60)
        print("开源可商用知识图谱库推荐")
        print("=" * 60)
        
        recs = cls.recommend(use_web=use_web)
        
        web_count = sum(1 for r in recs if r.get("source") == "web")
        builtin_count = sum(1 for r in recs if r.get("source") == "builtin")
        
        print(f"\n  联网搜索: {web_count} 条 | 内置推荐: {builtin_count} 条\n")
        
        for i, repo in enumerate(recs, 1):
            source_tag = "[网]" if repo.get("source") == "web" else "[内置]"
            name = repo.get("name", "未知")
            license_info = repo.get("license", "")
            desc = repo.get("description", "")
            url = repo.get("url", "")
            lang = repo.get("language", "")
            
            print(f"  {i}. {source_tag} {name}")
            if lang:
                print(f"     语言: {lang}")
            if license_info:
                print(f"     许可证: {license_info}")
            if desc:
                print(f"     简介: {desc}")
            if url:
                print(f"     链接: {url}")
            print()
        
        print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("本地知识图谱+任务合成测试 - REDSearcher")
    print("=" * 60)
    
    generator = ZeroCostDataGenerator()
    
    print("\n[1] 知识图谱统计:")
    kg_stats = generator.get_knowledge_stats()
    print(f"  节点总数: {kg_stats['total_nodes']}")
    print(f"  边总数: {kg_stats['total_edges']}")
    print(f"  节点类型: {kg_stats['node_types']}")
    
    print("\n[2] 任务合成测试:")
    task = generator.synthesizer.synthesize(difficulty=3)
    print(f"  任务ID: {task.task_id}")
    print(f"  任务类型: {task.task_type}")
    print(f"  难度: {task.difficulty}")
    print(f"  实体数: {len(task.entities)}")
    print(f"  动作数: {len(task.actions)}")
    print(f"  复杂度: {task.complexity_score:.2f}")
    print(f"  工具需求: {task.tool_requirements}")
    
    print("\n[3] 批量生成测试:")
    result = generator.generate(count=10)
    print(f"  生成任务: {result['stats']['total_tasks']}")
    print(f"  总步骤: {result['stats']['total_steps']}")
    print(f"  意外事件: {result['stats']['unexpected_events']}")
    print(f"  工具调用: {result['stats']['api_calls_saved']}")
    
    print("\n[4] 成本节省:")
    cost = result['cost_saved']
    print(f"  等效API调用: {cost['api_calls_equivalent']}")
    print(f"  节省成本: ¥{cost['cost_saved_yuan']:.4f}")
    
    print("\n[5] 示例数据:")
    for item in result['data'][0]['data'][:3]:
        unexpected = item.get('unexpected') or {}
        unexpected_type = unexpected.get('type', '无') if isinstance(unexpected, dict) else '无'
        print(f"  [{item['action']}] -> {item['target']} (意外: {unexpected_type})")
    
    print("\n[6] 联网搜索开源知识图谱库（可选）:")
    try:
        KGRepoSearch.print_recommendations(use_web=True)
    except Exception as e:
        print(f"  联网搜索跳过 ({e})，使用内置推荐:")
        KGRepoSearch.print_recommendations(use_web=False)
    
    print("\n" + "=" * 60)
    print("测试完成! 完全离线，零API成本")
    print("=" * 60)
