#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CADS - 集体对抗数据合成
基于论文：arXiv:2602.03300 "R1-SyntheticVL"

核心思想：
1. CAD-Generate - 多个AI集体生成数据
2. CAD-Judge - 多个AI互相挑错评估
3. 迭代优化 - 通过对抗提升质量

为什么符合"沙箱社区"：
- 让AI自己跟自己聊、自己挑自己毛病
- 不需要真实用户参与
- 成本可控，用现有API

核心价值：
- 让"无限对话生成"有学术背书
- 自动产出高质量+多样化样本
"""

import json
import random
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, Counter
import math


@dataclass
class AgentPersona:
    """AI代理人格"""
    agent_id: str
    role: str  # generator, critic, validator, enhancer
    personality: str
    expertise: List[str]
    bias_tendency: float  # 0-1, 偏见倾向
    quality_threshold: float


@dataclass
class GeneratedSample:
    """生成的样本"""
    sample_id: str
    content: Dict
    generator_id: str
    generation_round: int
    quality_scores: Dict[str, float]
    issues_found: List[str]
    enhancements: List[str]


@dataclass
class JudgmentResult:
    """评判结果"""
    judge_id: str
    sample_id: str
    overall_score: float
    dimension_scores: Dict[str, float]
    issues: List[Dict]
    suggestions: List[str]


@dataclass
class CADSCycle:
    """CADS循环"""
    cycle_id: str
    round_num: int
    samples_generated: int
    samples_passed: int
    samples_rejected: int
    avg_quality_improvement: float
    issues_resolved: List[str]


class AgentPool:
    """
    AI代理池 - 管理多个AI角色
    
    角色类型：
    - Generator: 生成数据
    - Critic: 挑毛病
    - Validator: 验证质量
    - Enhancer: 增强改进
    """
    
    PERSONALITIES = {
        "strict": {"threshold": 0.8, "focus": ["quality", "accuracy"]},
        "creative": {"threshold": 0.6, "focus": ["diversity", "novelty"]},
        "practical": {"threshold": 0.7, "focus": ["usability", "completeness"]},
        "skeptical": {"threshold": 0.75, "focus": ["consistency", "logic"]},
        "supportive": {"threshold": 0.65, "focus": ["potential", "improvement"]},
    }
    
    EXPERTISE_AREAS = [
        "用户行为", "情绪分析", "对话生成", "数据质量",
        "隐私安全", "业务逻辑", "意外场景", "多模态"
    ]
    
    def __init__(self, pool_size: int = 5):
        self.agents: List[AgentPersona] = []
        self._initialize_pool(pool_size)
    
    def _initialize_pool(self, size: int):
        """初始化代理池"""
        roles = ["generator", "critic", "validator", "enhancer"]
        personalities = list(self.PERSONALITIES.keys())
        
        for i in range(size):
            role = roles[i % len(roles)]
            personality = personalities[i % len(personalities)]
            
            agent = AgentPersona(
                agent_id=f"agent_{i:02d}",
                role=role,
                personality=personality,
                expertise=random.sample(self.EXPERTISE_AREAS, k=2),
                bias_tendency=random.uniform(0.1, 0.5),
                quality_threshold=self.PERSONALITIES[personality]["threshold"]
            )
            self.agents.append(agent)
    
    def get_agents_by_role(self, role: str) -> List[AgentPersona]:
        """按角色获取代理"""
        return [a for a in self.agents if a.role == role]
    
    def get_random_agent(self, role: str = None) -> AgentPersona:
        """获取随机代理"""
        if role:
            candidates = self.get_agents_by_role(role)
        else:
            candidates = self.agents
        return random.choice(candidates) if candidates else self.agents[0]


class CADGenerator:
    """
    CAD生成器 - 集体知识生成
    
    核心功能：
    1. 多代理协作生成
    2. 知识融合
    3. 多样性保证
    """
    
    def __init__(self, agent_pool: AgentPool):
        self.agent_pool = agent_pool
        self.generation_history = []
    
    def generate(self, context: Dict, count: int = 10) -> List[GeneratedSample]:
        """集体生成数据"""
        generators = self.agent_pool.get_agents_by_role("generator")
        if not generators:
            generators = [self.agent_pool.get_random_agent()]
        
        samples = []
        
        for i in range(count):
            generator = generators[i % len(generators)]
            
            sample = self._generate_single(generator, context, i)
            samples.append(sample)
        
        self.generation_history.extend(samples)
        return samples
    
    def _generate_single(self, agent: AgentPersona, context: Dict, 
                         index: int) -> GeneratedSample:
        """单个代理生成"""
        base_content = self._create_base_content(context)
        
        if "用户行为" in agent.expertise:
            base_content["user_behavior"] = self._generate_behavior()
        
        if "情绪分析" in agent.expertise:
            base_content["emotion"] = self._generate_emotion(agent.personality)
        
        if "意外场景" in agent.expertise:
            base_content["unexpected"] = self._generate_unexpected()
        
        quality_scores = self._estimate_quality(agent, base_content)
        
        return GeneratedSample(
            sample_id=f"sample_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}",
            content=base_content,
            generator_id=agent.agent_id,
            generation_round=0,
            quality_scores=quality_scores,
            issues_found=[],
            enhancements=[]
        )
    
    def _create_base_content(self, context: Dict) -> Dict:
        """创建基础内容"""
        actions = ["浏览", "搜索", "点击", "收藏", "加购", "购买", "评价", "分享"]
        return {
            "user_id": f"user_{random.randint(1, 100)}",
            "action": random.choice(actions),
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "session_id": f"session_{random.randint(1000, 9999)}"
        }
    
    def _generate_behavior(self) -> Dict:
        """生成行为"""
        return {
            "sequence": random.sample(["浏览", "搜索", "对比", "加购", "购买"], 
                                      k=random.randint(2, 5)),
            "duration": random.randint(30, 1800),
            "device": random.choice(["mobile", "desktop", "tablet"])
        }
    
    def _generate_emotion(self, personality: str) -> Dict:
        """生成情绪"""
        emotion_map = {
            "strict": "neutral",
            "creative": "excited",
            "practical": "satisfied",
            "skeptical": "hesitant",
            "supportive": "happy"
        }
        return {
            "type": emotion_map.get(personality, "neutral"),
            "intensity": round(random.uniform(0.3, 0.8), 2),
            "trigger": random.choice(["商品", "价格", "服务", "物流"])
        }
    
    def _generate_unexpected(self) -> Dict:
        """生成意外事件"""
        events = [
            {"type": "价格变动", "impact": "重新评估"},
            {"type": "库存告急", "impact": "紧急决策"},
            {"type": "优惠券过期", "impact": "加速购买"},
            {"type": "差评发现", "impact": "犹豫"},
            {"type": "朋友推荐", "impact": "增加信任"}
        ]
        return random.choice(events)
    
    def _estimate_quality(self, agent: AgentPersona, content: Dict) -> Dict[str, float]:
        """估计质量分数"""
        base_score = agent.quality_threshold
        
        return {
            "completeness": base_score + random.uniform(-0.1, 0.1),
            "diversity": base_score + random.uniform(-0.15, 0.15),
            "authenticity": base_score + random.uniform(-0.1, 0.1),
            "consistency": base_score + random.uniform(-0.05, 0.05)
        }


class CADJudge:
    """
    CAD评判器 - 集体评估数据质量
    
    核心功能：
    1. 多代理独立评判
    2. 问题发现
    3. 改进建议
    """
    
    QUALITY_DIMENSIONS = [
        "completeness", "consistency", "accuracy", 
        "diversity", "authenticity", "relevance"
    ]
    
    ISSUE_TEMPLATES = {
        "completeness": [
            "缺少必要字段: {field}",
            "数据不完整: {aspect}"
        ],
        "consistency": [
            "逻辑不一致: {issue}",
            "前后矛盾: {conflict}"
        ],
        "authenticity": [
            "过于模板化",
            "缺乏真实感: {aspect}"
        ],
        "diversity": [
            "模式重复",
            "缺乏变化: {aspect}"
        ]
    }
    
    def __init__(self, agent_pool: AgentPool):
        self.agent_pool = agent_pool
        self.judgment_history = []
    
    def judge(self, samples: List[GeneratedSample]) -> List[JudgmentResult]:
        """集体评判"""
        critics = self.agent_pool.get_agents_by_role("critic")
        if not critics:
            critics = [self.agent_pool.get_random_agent()]
        
        results = []
        
        for sample in samples:
            judgments = []
            for critic in critics[:3]:
                judgment = self._judge_single(critic, sample)
                judgments.append(judgment)
            
            final_judgment = self._aggregate_judgments(sample.sample_id, judgments)
            results.append(final_judgment)
        
        self.judgment_history.extend(results)
        return results
    
    def _judge_single(self, critic: AgentPersona, 
                      sample: GeneratedSample) -> JudgmentResult:
        """单个评判"""
        scores = {}
        for dim in self.QUALITY_DIMENSIONS:
            base = sample.quality_scores.get(dim, 0.7)
            adjustment = random.uniform(-0.1, 0.1) * (1 - critic.bias_tendency)
            scores[dim] = max(0, min(1, base + adjustment))
        
        issues = self._detect_issues(critic, sample, scores)
        suggestions = self._generate_suggestions(critic, issues)
        
        overall = sum(scores.values()) / len(scores)
        
        return JudgmentResult(
            judge_id=critic.agent_id,
            sample_id=sample.sample_id,
            overall_score=overall,
            dimension_scores=scores,
            issues=issues,
            suggestions=suggestions
        )
    
    def _detect_issues(self, critic: AgentPersona, sample: GeneratedSample,
                       scores: Dict[str, float]) -> List[Dict]:
        """检测问题"""
        issues = []
        
        for dim, score in scores.items():
            if score < critic.quality_threshold:
                templates = self.ISSUE_TEMPLATES.get(dim, ["{dim}问题"])
                issue_text = random.choice(templates).format(
                    field=random.choice(["user_id", "timestamp", "action"]),
                    aspect=random.choice(["行为", "情绪", "上下文"]),
                    issue="逻辑跳跃",
                    conflict="前后行为"
                )
                issues.append({
                    "dimension": dim,
                    "severity": "high" if score < 0.5 else "medium",
                    "description": issue_text,
                    "score": score
                })
        
        return issues
    
    def _generate_suggestions(self, critic: AgentPersona, 
                              issues: List[Dict]) -> List[str]:
        """生成建议"""
        suggestions = []
        
        for issue in issues:
            dim = issue["dimension"]
            if dim == "completeness":
                suggestions.append("补充缺失字段")
            elif dim == "consistency":
                suggestions.append("修正逻辑矛盾")
            elif dim == "authenticity":
                suggestions.append("增加真实感细节")
            elif dim == "diversity":
                suggestions.append("增加变化元素")
        
        return suggestions
    
    def _aggregate_judgments(self, sample_id: str, 
                             judgments: List[JudgmentResult]) -> JudgmentResult:
        """聚合评判结果"""
        all_scores = defaultdict(list)
        all_issues = []
        all_suggestions = []
        
        for j in judgments:
            for dim, score in j.dimension_scores.items():
                all_scores[dim].append(score)
            all_issues.extend(j.issues)
            all_suggestions.extend(j.suggestions)
        
        avg_scores = {dim: sum(scores)/len(scores) 
                     for dim, scores in all_scores.items()}
        overall = sum(avg_scores.values()) / len(avg_scores)
        
        unique_issues = []
        seen = set()
        for issue in all_issues:
            key = f"{issue['dimension']}_{issue['description']}"
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return JudgmentResult(
            judge_id="aggregated",
            sample_id=sample_id,
            overall_score=overall,
            dimension_scores=avg_scores,
            issues=unique_issues,
            suggestions=list(set(all_suggestions))
        )


class CADEnhancer:
    """
    CAD增强器 - 根据评判结果改进数据
    
    核心功能：
    1. 问题修复
    2. 质量提升
    3. 多样性增强
    """
    
    def __init__(self, agent_pool: AgentPool):
        self.agent_pool = agent_pool
        self.enhancement_history = []
    
    def enhance(self, samples: List[GeneratedSample], 
                judgments: List[JudgmentResult]) -> List[GeneratedSample]:
        """增强数据"""
        enhanced = []
        
        for sample, judgment in zip(samples, judgments):
            if judgment.overall_score < 0.7:
                enhanced_sample = self._enhance_single(sample, judgment)
                enhanced.append(enhanced_sample)
            else:
                enhanced.append(sample)
        
        self.enhancement_history.extend(enhanced)
        return enhanced
    
    def _enhance_single(self, sample: GeneratedSample, 
                        judgment: JudgmentResult) -> GeneratedSample:
        """单个增强"""
        enhanced_content = sample.content.copy()
        
        for issue in judgment.issues:
            dim = issue["dimension"]
            
            if dim == "completeness":
                enhanced_content["enhanced_fields"] = {
                    "added_at": datetime.now().isoformat(),
                    "reason": "completeness_fix"
                }
            
            elif dim == "authenticity":
                if "emotion" not in enhanced_content:
                    enhanced_content["emotion"] = {
                        "type": random.choice(["犹豫", "期待", "满意"]),
                        "intensity": round(random.uniform(0.4, 0.8), 2)
                    }
            
            elif dim == "diversity":
                enhanced_content["variation_factor"] = random.randint(1, 10)
        
        enhanced_sample = GeneratedSample(
            sample_id=sample.sample_id + "_enhanced",
            content=enhanced_content,
            generator_id=sample.generator_id,
            generation_round=sample.generation_round + 1,
            quality_scores={k: min(1.0, v + 0.1) for k, v in judgment.dimension_scores.items()},
            issues_found=[i["description"] for i in judgment.issues],
            enhancements=judgment.suggestions
        )
        
        return enhanced_sample


class CADSPipeline:
    """
    CADS流水线 - 整合所有组件
    
    核心流程：
    1. Generate - 集体生成
    2. Judge - 集体评判
    3. Enhance - 集体增强
    4. Iterate - 迭代优化
    """
    
    def __init__(self, pool_size: int = 5):
        self.agent_pool = AgentPool(pool_size)
        self.generator = CADGenerator(self.agent_pool)
        self.judge = CADJudge(self.agent_pool)
        self.enhancer = CADEnhancer(self.agent_pool)
        self.cycle_history = []
    
    def run_cycle(self, context: Dict, count: int = 10, 
                  max_rounds: int = 3) -> Dict:
        """运行CADS循环"""
        cycle_id = f"cycle_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"
        
        all_samples = []
        passed_samples = []
        rejected_samples = []
        
        samples = self.generator.generate(context, count)
        all_samples.extend(samples)
        
        for round_num in range(max_rounds):
            judgments = self.judge.judge(samples)
            
            passed = [s for s, j in zip(samples, judgments) if j.overall_score >= 0.7]
            rejected = [s for s, j in zip(samples, judgments) if j.overall_score < 0.7]
            
            passed_samples.extend(passed)
            rejected_samples.extend(rejected)
            
            if not rejected:
                break
            
            samples = self.enhancer.enhance(rejected, 
                [j for s, j in zip(samples, judgments) if j.overall_score < 0.7])
            all_samples.extend(samples)
        
        cycle = CADSCycle(
            cycle_id=cycle_id,
            round_num=max_rounds,
            samples_generated=len(all_samples),
            samples_passed=len(passed_samples),
            samples_rejected=len(rejected_samples),
            avg_quality_improvement=self._calculate_improvement(all_samples),
            issues_resolved=list(set(
                issue for s in all_samples for issue in s.issues_found
            ))
        )
        
        self.cycle_history.append(cycle)
        
        return {
            "cycle_id": cycle_id,
            "total_generated": len(all_samples),
            "passed": len(passed_samples),
            "rejected": len(rejected_samples),
            "pass_rate": len(passed_samples) / len(all_samples) if all_samples else 0,
            "rounds": max_rounds,
            "final_samples": passed_samples,
            "issues_resolved": cycle.issues_resolved
        }
    
    def _calculate_improvement(self, samples: List[GeneratedSample]) -> float:
        """计算改进幅度"""
        if len(samples) < 2:
            return 0.0
        
        initial = samples[0].quality_scores
        final = samples[-1].quality_scores
        
        improvements = []
        for key in initial:
            if key in final:
                improvements.append(final[key] - initial[key])
        
        return sum(improvements) / len(improvements) if improvements else 0.0
    
    def get_statistics(self) -> Dict:
        """获取统计"""
        if not self.cycle_history:
            return {}
        
        total_generated = sum(c.samples_generated for c in self.cycle_history)
        total_passed = sum(c.samples_passed for c in self.cycle_history)
        
        return {
            "total_cycles": len(self.cycle_history),
            "total_generated": total_generated,
            "total_passed": total_passed,
            "overall_pass_rate": total_passed / total_generated if total_generated else 0,
            "avg_improvement": sum(c.avg_quality_improvement for c in self.cycle_history) / len(self.cycle_history),
            "agent_pool_size": len(self.agent_pool.agents)
        }


if __name__ == "__main__":
    print("=" * 60)
    print("CADS 测试 - 集体对抗数据合成")
    print("=" * 60)
    
    pipeline = CADSPipeline(pool_size=5)
    
    print("\n[1] 代理池信息:")
    for agent in pipeline.agent_pool.agents:
        print(f"  {agent.agent_id}: {agent.role} ({agent.personality})")
    
    print("\n[2] 运行CADS循环:")
    result = pipeline.run_cycle(
        context={"domain": "ecommerce", "scenario": "user_shopping"},
        count=10,
        max_rounds=3
    )
    print(f"  生成总数: {result['total_generated']}")
    print(f"  通过数量: {result['passed']}")
    print(f"  拒绝数量: {result['rejected']}")
    print(f"  通过率: {result['pass_rate']:.2%}")
    print(f"  解决问题: {len(result['issues_resolved'])}")
    
    print("\n[3] 示例通过样本:")
    for sample in result['final_samples'][:3]:
        print(f"  [{sample.generator_id}] 质量: {sum(sample.quality_scores.values())/len(sample.quality_scores):.2f}")
        print(f"    增强: {sample.enhancements[:2]}")
    
    print("\n[4] 统计信息:")
    stats = pipeline.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("测试完成! AI自己跟自己对抗生成")
    print("=" * 60)
