#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版数据生成器 - 让数据"像人"
包含：情绪建模、意外事件、跨平台行为、时间维度、多轮对话
"""

import random
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

class EmotionType(Enum):
    JOY = "喜悦"
    ANGER = "愤怒"
    SADNESS = "悲伤"
    FEAR = "恐惧"
    SURPRISE = "惊讶"
    DISGUST = "厌恶"
    ANTICIPATION = "期待"
    TRUST = "信任"
    NEUTRAL = "中性"

class EmotionIntensity(Enum):
    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9

@dataclass
class EmotionState:
    emotion_type: EmotionType
    intensity: float
    trigger: str
    duration_minutes: int
    affects_behavior: bool = True

class EmotionModel:
    """
    情绪建模系统 - 模拟真实用户的情绪变化
    
    核心原理：
    1. 情绪有惯性 - 不会突然变化
    2. 情绪有传染性 - 受环境影响
    3. 情绪影响行为 - 决策会受情绪干扰
    """
    
    EMOTION_TRANSITIONS = {
        EmotionType.JOY: [EmotionType.TRUST, EmotionType.ANTICIPATION, EmotionType.NEUTRAL],
        EmotionType.ANGER: [EmotionType.DISGUST, EmotionType.SADNESS, EmotionType.NEUTRAL],
        EmotionType.SADNESS: [EmotionType.FEAR, EmotionType.NEUTRAL, EmotionType.ANTICIPATION],
        EmotionType.FEAR: [EmotionType.ANGER, EmotionType.SADNESS, EmotionType.NEUTRAL],
        EmotionType.SURPRISE: [EmotionType.JOY, EmotionType.FEAR, EmotionType.ANGER],
        EmotionType.DISGUST: [EmotionType.ANGER, EmotionType.NEUTRAL],
        EmotionType.ANTICIPATION: [EmotionType.JOY, EmotionType.FEAR, EmotionType.NEUTRAL],
        EmotionType.TRUST: [EmotionType.JOY, EmotionType.NEUTRAL],
        EmotionType.NEUTRAL: [e for e in EmotionType if e != EmotionType.NEUTRAL],
    }
    
    EMOTION_TRIGGERS = {
        EmotionType.JOY: [
            "收到优惠券", "商品降价", "好评反馈", "朋友推荐", "节日促销",
            "新品上架", "会员升级", "积分奖励", "抽奖中奖", "客服好评"
        ],
        EmotionType.ANGER: [
            "商品缺货", "物流延迟", "客服敷衍", "价格欺诈", "虚假宣传",
            "退换货困难", "账户异常", "支付失败", "系统崩溃", "隐私泄露"
        ],
        EmotionType.SADNESS: [
            "商品下架", "喜欢的店铺关闭", "会员过期", "积分清零", "促销错过",
            "退款失败", "账号被封", "评价被删", "收藏清空", "历史丢失"
        ],
        EmotionType.FEAR: [
            "支付风险提示", "账户安全警告", "隐私政策变更", "数据泄露新闻",
            "诈骗提醒", "价格暴涨", "库存告急", "限时倒计时", "竞争激烈"
        ],
        EmotionType.SURPRISE: [
            "意外折扣", "神秘礼包", "隐藏功能", "系统升级", "界面改版",
            "新功能上线", "意外推荐", "彩蛋发现", "VIP特权", "惊喜快递"
        ],
        EmotionType.DISGUST: [
            "差评商品", "虚假评论", "刷单行为", "低俗广告", "过度营销",
            "捆绑销售", "隐藏费用", "诱导消费", "质量造假", "服务态度差"
        ],
        EmotionType.ANTICIPATION: [
            "新品预告", "促销预告", "限时秒杀", "预售开启", "会员日活动",
            "节日大促", "版本更新", "功能上线", "活动倒计时", "开箱期待"
        ],
        EmotionType.TRUST: [
            "品牌认证", "官方保障", "正品承诺", "售后承诺", "用户评价",
            "朋友推荐", "专家背书", "媒体报道", "资质展示", "历史记录"
        ],
    }
    
    BEHAVIOR_MODIFIERS = {
        EmotionType.JOY: {
            "purchase_probability": 1.5,
            "browse_time": 1.2,
            "share_probability": 1.8,
            "review_probability": 1.5,
            "price_sensitivity": 0.7,
        },
        EmotionType.ANGER: {
            "purchase_probability": 0.3,
            "browse_time": 0.5,
            "share_probability": 0.2,
            "review_probability": 2.0,
            "price_sensitivity": 1.5,
        },
        EmotionType.SADNESS: {
            "purchase_probability": 0.6,
            "browse_time": 1.5,
            "share_probability": 0.5,
            "review_probability": 0.8,
            "price_sensitivity": 1.2,
        },
        EmotionType.FEAR: {
            "purchase_probability": 0.4,
            "browse_time": 0.8,
            "share_probability": 0.3,
            "review_probability": 0.5,
            "price_sensitivity": 2.0,
        },
        EmotionType.SURPRISE: {
            "purchase_probability": 1.3,
            "browse_time": 1.4,
            "share_probability": 1.6,
            "review_probability": 1.2,
            "price_sensitivity": 0.8,
        },
        EmotionType.ANTICIPATION: {
            "purchase_probability": 1.2,
            "browse_time": 1.6,
            "share_probability": 1.3,
            "review_probability": 0.9,
            "price_sensitivity": 0.9,
        },
        EmotionType.TRUST: {
            "purchase_probability": 1.4,
            "browse_time": 1.1,
            "share_probability": 1.5,
            "review_probability": 1.3,
            "price_sensitivity": 0.8,
        },
        EmotionType.DISGUST: {
            "purchase_probability": 0.2,
            "browse_time": 0.3,
            "share_probability": 0.1,
            "review_probability": 1.8,
            "price_sensitivity": 1.8,
        },
        EmotionType.NEUTRAL: {
            "purchase_probability": 1.0,
            "browse_time": 1.0,
            "share_probability": 1.0,
            "review_probability": 1.0,
            "price_sensitivity": 1.0,
        },
    }
    
    def __init__(self, personality_seed: int = None):
        if personality_seed:
            random.seed(personality_seed)
        
        self.current_emotion = EmotionType.NEUTRAL
        self.emotion_intensity = 0.5
        self.emotion_history: List[EmotionState] = []
        self.emotion_duration = 0
        
        self.personality = {
            "emotional_stability": random.uniform(0.3, 0.9),
            "positive_bias": random.uniform(0.3, 0.7),
            "reactivity": random.uniform(0.3, 0.8),
        }
    
    def update_emotion(self, external_trigger: str = None, time_passed: int = 1) -> EmotionState:
        """
        更新情绪状态
        
        Args:
            external_trigger: 外部触发事件
            time_passed: 经过的分钟数
        
        Returns:
            新的情绪状态
        """
        self.emotion_duration += time_passed
        
        decay_factor = self.personality["emotional_stability"]
        if self.emotion_duration > 30:
            self.emotion_intensity *= (decay_factor ** (time_passed / 10))
        
        if external_trigger and random.random() < self.personality["reactivity"]:
            new_emotion = self._get_emotion_from_trigger(external_trigger)
            if new_emotion:
                self.current_emotion = new_emotion
                self.emotion_intensity = random.uniform(0.5, 0.9)
                self.emotion_duration = 0
        
        if self.emotion_intensity < 0.2 or random.random() < 0.1:
            possible_transitions = self.EMOTION_TRANSITIONS.get(self.current_emotion, [EmotionType.NEUTRAL])
            
            if random.random() < self.personality["positive_bias"]:
                positive_emotions = [EmotionType.JOY, EmotionType.TRUST, EmotionType.ANTICIPATION]
                possible_transitions = [e for e in possible_transitions if e in positive_emotions] or possible_transitions
            
            self.current_emotion = random.choice(possible_transitions)
            self.emotion_intensity = random.uniform(0.3, 0.6)
            self.emotion_duration = 0
        
        state = EmotionState(
            emotion_type=self.current_emotion,
            intensity=self.emotion_intensity,
            trigger=external_trigger or "自然过渡",
            duration_minutes=self.emotion_duration,
            affects_behavior=self.emotion_intensity > 0.3
        )
        
        self.emotion_history.append(state)
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]
        
        return state
    
    def _get_emotion_from_trigger(self, trigger: str) -> Optional[EmotionType]:
        """从触发事件推断情绪"""
        for emotion, triggers in self.EMOTION_TRIGGERS.items():
            if any(t in trigger for t in triggers):
                return emotion
        return None
    
    def get_behavior_modifier(self) -> Dict[str, float]:
        """获取当前情绪对行为的影响系数"""
        base_modifiers = self.BEHAVIOR_MODIFIERS.get(self.current_emotion, {}).copy()
        
        intensity_factor = self.emotion_intensity
        for key in base_modifiers:
            if base_modifiers[key] > 1:
                base_modifiers[key] = 1 + (base_modifiers[key] - 1) * intensity_factor
            else:
                base_modifiers[key] = 1 - (1 - base_modifiers[key]) * intensity_factor
        
        return base_modifiers
    
    def get_emotion_description(self) -> str:
        """获取情绪描述"""
        intensity_desc = ""
        if self.emotion_intensity < 0.3:
            intensity_desc = "轻微"
        elif self.emotion_intensity < 0.6:
            intensity_desc = "中等"
        else:
            intensity_desc = "强烈"
        
        return f"{intensity_desc}{self.current_emotion.value}"


class UnexpectedEvent:
    """
    意外事件生成器 - 让数据有"意外性"
    
    真实用户行为不是线性的，会有各种意外打断
    """
    
    EVENT_TYPES = {
        "中断类": [
            {"event": "接到电话", "behavior_change": "暂停浏览", "duration": "5-30分钟"},
            {"event": "消息通知", "behavior_change": "切换应用", "duration": "1-10分钟"},
            {"event": "电量不足", "behavior_change": "快速决策或放弃", "duration": "即时"},
            {"event": "网络波动", "behavior_change": "等待或刷新", "duration": "10秒-5分钟"},
            {"event": "有人打扰", "behavior_change": "离开或分心", "duration": "不定"},
        ],
        "干扰类": [
            {"event": "弹窗广告", "behavior_change": "关闭或误点", "duration": "即时"},
            {"event": "推荐干扰", "behavior_change": "浏览推荐内容", "duration": "1-5分钟"},
            {"event": "价格变动", "behavior_change": "重新评估", "duration": "即时"},
            {"event": "库存变化", "behavior_change": "紧急决策", "duration": "即时"},
            {"event": "优惠券过期", "behavior_change": "放弃或加速", "duration": "即时"},
        ],
        "意外类": [
            {"event": "发现更好选择", "behavior_change": "比较或切换", "duration": "5-20分钟"},
            {"event": "看到差评", "behavior_change": "犹豫或放弃", "duration": "即时"},
            {"event": "朋友推荐", "behavior_change": "查看推荐", "duration": "3-15分钟"},
            {"event": "限时秒杀", "behavior_change": "紧急购买", "duration": "即时"},
            {"event": "系统故障", "behavior_change": "重试或放弃", "duration": "1-10分钟"},
        ],
        "情绪类": [
            {"event": "突然不想买了", "behavior_change": "放弃购物车", "duration": "即时"},
            {"event": "冲动消费", "behavior_change": "快速下单", "duration": "即时"},
            {"event": "纠结犹豫", "behavior_change": "反复比较", "duration": "10-60分钟"},
            {"event": "后悔下单", "behavior_change": "取消订单", "duration": "即时"},
            {"event": "分享冲动", "behavior_change": "转发分享", "duration": "1-5分钟"},
        ],
    }
    
    INTERRUPTION_PROBABILITY = {
        "morning": 0.15,
        "noon": 0.25,
        "afternoon": 0.20,
        "evening": 0.30,
        "night": 0.10,
    }
    
    @classmethod
    def generate_event(cls, time_context: str = "afternoon") -> Optional[Dict]:
        """
        生成意外事件
        
        Args:
            time_context: 时间上下文 (morning/noon/afternoon/evening/night)
        
        Returns:
            意外事件字典，或None
        """
        base_prob = cls.INTERRUPTION_PROBABILITY.get(time_context, 0.20)
        
        if random.random() > base_prob:
            return None
        
        event_category = random.choice(list(cls.EVENT_TYPES.keys()))
        event = random.choice(cls.EVENT_TYPES[event_category]).copy()
        event["category"] = event_category
        event["timestamp"] = datetime.now().isoformat()
        
        return event
    
    @classmethod
    def apply_event_to_sequence(cls, sequence: List[Dict], event: Dict) -> List[Dict]:
        """
        将意外事件应用到行为序列中
        
        Args:
            sequence: 原始行为序列
            event: 意外事件
        
        Returns:
            修改后的行为序列
        """
        if not event:
            return sequence
        
        insert_position = random.randint(1, max(1, len(sequence) - 1))
        
        event_action = {
            "action": f"[意外] {event['event']}",
            "behavior_change": event["behavior_change"],
            "duration": event["duration"],
            "event_category": event["category"],
            "is_unexpected": True,
        }
        
        modified_sequence = sequence[:insert_position] + [event_action] + sequence[insert_position:]
        
        if event["behavior_change"] in ["放弃购物车", "取消订单", "放弃或加速"]:
            for i in range(insert_position + 1, len(modified_sequence)):
                if "购买" in modified_sequence[i].get("action", ""):
                    modified_sequence[i]["cancelled"] = True
                    modified_sequence[i]["cancel_reason"] = event["event"]
        
        return modified_sequence


class CrossPlatformBehavior:
    """
    跨平台行为模拟 - 真实用户会在多个平台间切换
    
    场景：用户在淘宝看商品，去小红书搜评价，回淘宝下单
    """
    
    PLATFORMS = {
        "电商": {
            "name": "电商平台",
            "actions": ["浏览商品", "加入购物车", "下单", "查看订单", "评价商品"],
            "typical_duration": "5-30分钟",
        },
        "社交": {
            "name": "社交平台",
            "actions": ["发动态", "评论", "点赞", "私信", "分享"],
            "typical_duration": "3-20分钟",
        },
        "内容": {
            "name": "内容平台",
            "actions": ["看视频", "读文章", "搜索内容", "收藏", "关注"],
            "typical_duration": "10-60分钟",
        },
        "搜索": {
            "name": "搜索引擎",
            "actions": ["搜索关键词", "点击结果", "查看详情", "返回修改"],
            "typical_duration": "1-10分钟",
        },
        "支付": {
            "name": "支付平台",
            "actions": ["转账", "付款", "查余额", "理财", "红包"],
            "typical_duration": "1-5分钟",
        },
    }
    
    CROSS_PLATFORM_PATTERNS = [
        {
            "name": "比价模式",
            "sequence": ["电商", "搜索", "电商"],
            "description": "在电商平台看商品，去搜索引擎比价，回电商下单",
            "probability": 0.3,
        },
        {
            "name": "种草模式",
            "sequence": ["内容", "电商", "社交"],
            "description": "在内容平台看到推荐，去电商购买，在社交平台分享",
            "probability": 0.25,
        },
        {
            "name": "评价模式",
            "sequence": ["电商", "内容", "社交", "电商"],
            "description": "看中商品，去内容平台搜评价，问朋友意见，回来下单",
            "probability": 0.2,
        },
        {
            "name": "冲动模式",
            "sequence": ["社交", "电商"],
            "description": "朋友推荐或看到分享，直接去电商购买",
            "probability": 0.15,
        },
        {
            "name": "研究模式",
            "sequence": ["搜索", "内容", "社交", "电商", "搜索"],
            "description": "深度研究后购买，可能多次反复",
            "probability": 0.1,
        },
    ]
    
    @classmethod
    def generate_cross_platform_sequence(cls, primary_platform: str = "电商") -> List[Dict]:
        """
        生成跨平台行为序列
        
        Args:
            primary_platform: 主要平台类型
        
        Returns:
            跨平台行为序列
        """
        pattern = random.choices(
            cls.CROSS_PLATFORM_PATTERNS,
            weights=[p["probability"] for p in cls.CROSS_PLATFORM_PATTERNS]
        )[0]
        
        sequence = []
        start_time = datetime.now()
        
        for i, platform_type in enumerate(pattern["sequence"]):
            platform = cls.PLATFORMS[platform_type]
            
            actions_count = random.randint(2, 5)
            actions = random.choices(platform["actions"], k=actions_count)
            
            for action in actions:
                sequence.append({
                    "platform": platform["name"],
                    "platform_type": platform_type,
                    "action": action,
                    "timestamp": (start_time + timedelta(minutes=i * 10 + random.randint(0, 5))).isoformat(),
                    "pattern": pattern["name"],
                })
        
        return sequence
    
    @classmethod
    def get_platform_transition_probability(cls, from_platform: str, to_platform: str) -> float:
        """获取平台间转移概率"""
        transitions = {
            ("电商", "内容"): 0.3,
            ("电商", "社交"): 0.2,
            ("电商", "搜索"): 0.25,
            ("内容", "电商"): 0.4,
            ("社交", "电商"): 0.35,
            ("搜索", "电商"): 0.3,
        }
        return transitions.get((from_platform, to_platform), 0.1)


class UserLifecycle:
    """
    用户生命周期建模 - 让数据"动起来"
    
    阶段：新手 → 活跃 → 稳定 → 沉默 → 流失/回流
    """
    
    STAGES = {
        "新手期": {
            "duration_days": (1, 7),
            "characteristics": {
                "exploration_rate": 0.8,
                "purchase_rate": 0.1,
                "feature_discovery": 0.9,
                "error_rate": 0.3,
            },
            "behaviors": ["注册", "浏览首页", "查看分类", "搜索商品", "查看帮助"],
        },
        "活跃期": {
            "duration_days": (7, 30),
            "characteristics": {
                "exploration_rate": 0.6,
                "purchase_rate": 0.4,
                "feature_discovery": 0.5,
                "error_rate": 0.1,
            },
            "behaviors": ["频繁浏览", "加入购物车", "下单购买", "评价商品", "分享推荐"],
        },
        "稳定期": {
            "duration_days": (30, 180),
            "characteristics": {
                "exploration_rate": 0.3,
                "purchase_rate": 0.6,
                "feature_discovery": 0.2,
                "error_rate": 0.05,
            },
            "behaviors": ["重复购买", "会员活动", "积分兑换", "专属优惠", "稳定消费"],
        },
        "沉默期": {
            "duration_days": (7, 30),
            "characteristics": {
                "exploration_rate": 0.1,
                "purchase_rate": 0.05,
                "feature_discovery": 0.05,
                "error_rate": 0.1,
            },
            "behaviors": ["偶尔登录", "只看不买", "忽略推送", "浏览历史", "收藏不买"],
        },
        "流失期": {
            "duration_days": (30, float('inf')),
            "characteristics": {
                "exploration_rate": 0.02,
                "purchase_rate": 0.01,
                "feature_discovery": 0.01,
                "error_rate": 0.2,
            },
            "behaviors": ["长时间不登录", "卸载应用", "取消关注", "忽略所有通知"],
        },
        "回流期": {
            "duration_days": (1, 14),
            "characteristics": {
                "exploration_rate": 0.5,
                "purchase_rate": 0.3,
                "feature_discovery": 0.6,
                "error_rate": 0.15,
            },
            "behaviors": ["重新登录", "查看新功能", "优惠吸引", "朋友邀请", "活动参与"],
        },
    }
    
    TRANSITION_MATRIX = {
        "新手期": {"活跃期": 0.7, "沉默期": 0.2, "流失期": 0.1},
        "活跃期": {"稳定期": 0.6, "沉默期": 0.3, "活跃期": 0.1},
        "稳定期": {"稳定期": 0.7, "沉默期": 0.25, "活跃期": 0.05},
        "沉默期": {"流失期": 0.5, "回流期": 0.2, "稳定期": 0.3},
        "流失期": {"回流期": 0.1, "流失期": 0.9},
        "回流期": {"活跃期": 0.4, "稳定期": 0.3, "流失期": 0.3},
    }
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id or f"user_{random.randint(10000, 99999)}"
        self.current_stage = "新手期"
        self.days_in_stage = 0
        self.total_days = 0
        self.stage_history = []
    
    def advance_day(self) -> Dict:
        """推进一天，返回当天状态"""
        self.days_in_stage += 1
        self.total_days += 1
        
        stage_config = self.STAGES[self.current_stage]
        min_days, max_days = stage_config["duration_days"]
        
        if self.days_in_stage >= min_days:
            transition_probs = self.TRANSITION_MATRIX.get(self.current_stage, {})
            if transition_probs:
                rand = random.random()
                cumulative = 0
                for next_stage, prob in transition_probs.items():
                    cumulative += prob
                    if rand < cumulative:
                        if next_stage != self.current_stage:
                            self.stage_history.append({
                                "from": self.current_stage,
                                "to": next_stage,
                                "day": self.total_days,
                            })
                            self.current_stage = next_stage
                            self.days_in_stage = 0
                        break
        
        return {
            "user_id": self.user_id,
            "day": self.total_days,
            "stage": self.current_stage,
            "days_in_stage": self.days_in_stage,
            "characteristics": stage_config["characteristics"],
        }
    
    def generate_daily_behaviors(self) -> List[Dict]:
        """生成当天行为"""
        stage_config = self.STAGES[self.current_stage]
        characteristics = stage_config["characteristics"]
        
        behaviors = []
        
        login_prob = 0.9 if self.current_stage in ["新手期", "活跃期"] else 0.3
        if random.random() < login_prob:
            behaviors.append({
                "action": "登录",
                "stage": self.current_stage,
                "day": self.total_days,
            })
            
            behavior_count = int(5 * characteristics["exploration_rate"] + 
                               3 * characteristics["purchase_rate"])
            
            for _ in range(random.randint(1, max(1, behavior_count))):
                action = random.choice(stage_config["behaviors"])
                behaviors.append({
                    "action": action,
                    "stage": self.current_stage,
                    "day": self.total_days,
                })
        
        return behaviors


class SeasonalPattern:
    """
    季节性模式 - 模拟节假日、促销季等周期性变化
    """
    
    HOLIDAYS = {
        "元旦": {"date": "01-01", "impact": 1.5, "categories": ["礼品", "食品"]},
        "春节": {"date": "01-22", "impact": 3.0, "categories": ["年货", "礼品", "服装"]},
        "情人节": {"date": "02-14", "impact": 2.0, "categories": ["礼品", "鲜花", "珠宝"]},
        "妇女节": {"date": "03-08", "impact": 1.5, "categories": ["美妆", "服装", "礼品"]},
        "五一": {"date": "05-01", "impact": 2.0, "categories": ["旅游", "家电", "服装"]},
        "618": {"date": "06-18", "impact": 3.0, "categories": ["数码", "家电", "全品类"]},
        "七夕": {"date": "08-22", "impact": 1.8, "categories": ["礼品", "鲜花", "珠宝"]},
        "中秋": {"date": "09-29", "impact": 1.5, "categories": ["月饼", "礼品", "食品"]},
        "国庆": {"date": "10-01", "impact": 2.5, "categories": ["旅游", "家电", "服装"]},
        "双11": {"date": "11-11", "impact": 4.0, "categories": ["全品类"]},
        "双12": {"date": "12-12", "impact": 2.5, "categories": ["全品类"]},
        "圣诞": {"date": "12-25", "impact": 1.5, "categories": ["礼品", "食品", "服装"]},
    }
    
    WEEKLY_PATTERN = {
        0: {"name": "周一", "activity": 0.7, "purchase": 0.6},
        1: {"name": "周二", "activity": 0.8, "purchase": 0.7},
        2: {"name": "周三", "activity": 0.85, "purchase": 0.75},
        3: {"name": "周四", "activity": 0.9, "purchase": 0.8},
        4: {"name": "周五", "activity": 1.0, "purchase": 0.9},
        5: {"name": "周六", "activity": 1.2, "purchase": 1.1},
        6: {"name": "周日", "activity": 1.3, "purchase": 1.2},
    }
    
    HOURLY_PATTERN = {
        range(0, 6): {"activity": 0.1, "purchase": 0.05},
        range(6, 9): {"activity": 0.5, "purchase": 0.3},
        range(9, 12): {"activity": 0.8, "purchase": 0.6},
        range(12, 14): {"activity": 1.0, "purchase": 0.7},
        range(14, 18): {"activity": 0.9, "purchase": 0.8},
        range(18, 21): {"activity": 1.2, "purchase": 1.0},
        range(21, 24): {"activity": 1.1, "purchase": 0.9},
    }
    
    @classmethod
    def get_seasonal_modifier(cls, date: datetime = None) -> Dict:
        """获取季节性影响系数"""
        if date is None:
            date = datetime.now()
        
        modifiers = {
            "activity": 1.0,
            "purchase": 1.0,
            "categories": [],
            "events": [],
        }
        
        date_str = date.strftime("%m-%d")
        for holiday, config in cls.HOLIDAYS.items():
            if date_str == config["date"]:
                modifiers["activity"] *= config["impact"]
                modifiers["purchase"] *= config["impact"]
                modifiers["categories"] = config["categories"]
                modifiers["events"].append(holiday)
        
        weekday = date.weekday()
        week_config = cls.WEEKLY_PATTERN[weekday]
        modifiers["activity"] *= week_config["activity"]
        modifiers["purchase"] *= week_config["purchase"]
        
        hour = date.hour
        for hour_range, config in cls.HOURLY_PATTERN.items():
            if hour in hour_range:
                modifiers["activity"] *= config["activity"]
                modifiers["purchase"] *= config["purchase"]
                break
        
        return modifiers


class MultiTurnDialogue:
    """
    多轮对话生成器 - 让数据"聊起来"
    
    特点：
    1. 话题转换自然
    2. 有追问和澄清
    3. 有情绪变化
    4. 有意外话题
    """
    
    DIALOGUE_PATTERNS = {
        "客服咨询": {
            "turns": (3, 8),
            "flow": [
                {"role": "user", "intent": "提问", "emotion": "neutral"},
                {"role": "assistant", "intent": "确认问题", "emotion": "neutral"},
                {"role": "user", "intent": "补充信息", "emotion": "neutral"},
                {"role": "assistant", "intent": "提供方案", "emotion": "helpful"},
                {"role": "user", "intent": "追问", "emotion": "curious"},
                {"role": "assistant", "intent": "详细解答", "emotion": "patient"},
                {"role": "user", "intent": "确认", "emotion": "satisfied"},
                {"role": "assistant", "intent": "结束语", "emotion": "friendly"},
            ],
        },
        "产品推荐": {
            "turns": (5, 12),
            "flow": [
                {"role": "user", "intent": "需求描述", "emotion": "neutral"},
                {"role": "assistant", "intent": "需求确认", "emotion": "attentive"},
                {"role": "user", "intent": "补充偏好", "emotion": "expectant"},
                {"role": "assistant", "intent": "推荐产品", "emotion": "confident"},
                {"role": "user", "intent": "询问细节", "emotion": "interested"},
                {"role": "assistant", "intent": "详细说明", "emotion": "helpful"},
                {"role": "user", "intent": "比较询问", "emotion": "hesitant"},
                {"role": "assistant", "intent": "对比分析", "emotion": "objective"},
                {"role": "user", "intent": "价格咨询", "emotion": "practical"},
                {"role": "assistant", "intent": "优惠介绍", "emotion": "persuasive"},
            ],
        },
        "问题解决": {
            "turns": (4, 10),
            "flow": [
                {"role": "user", "intent": "问题描述", "emotion": "frustrated"},
                {"role": "assistant", "intent": "共情", "emotion": "empathetic"},
                {"role": "user", "intent": "详细说明", "emotion": "anxious"},
                {"role": "assistant", "intent": "分析原因", "emotion": "analytical"},
                {"role": "user", "intent": "确认理解", "emotion": "hopeful"},
                {"role": "assistant", "intent": "提供方案", "emotion": "confident"},
                {"role": "user", "intent": "执行反馈", "emotion": "relieved"},
                {"role": "assistant", "intent": "确认解决", "emotion": "satisfied"},
            ],
        },
    }
    
    TOPIC_TRANSITIONS = {
        "产品功能": ["使用方法", "注意事项", "常见问题", "进阶技巧"],
        "价格": ["优惠活动", "会员权益", "分期付款", "竞品对比"],
        "售后": ["退换政策", "保修服务", "维修流程", "投诉渠道"],
        "物流": ["发货时间", "配送方式", "物流查询", "签收注意"],
    }
    
    EMOTION_TRANSITIONS = {
        "neutral": ["curious", "interested", "expectant"],
        "curious": ["interested", "hesitant", "satisfied"],
        "interested": ["excited", "hesitant", "practical"],
        "hesitant": ["convinced", "skeptical", "neutral"],
        "frustrated": ["hopeful", "relieved", "angry"],
        "satisfied": ["grateful", "loyal", "neutral"],
    }
    
    @classmethod
    def generate_dialogue(cls, pattern_name: str = None, min_turns: int = None) -> List[Dict]:
        """生成多轮对话"""
        if pattern_name is None:
            pattern_name = random.choice(list(cls.DIALOGUE_PATTERNS.keys()))
        
        pattern = cls.DIALOGUE_PATTERNS[pattern_name]
        flow = pattern["flow"]
        
        turns = min_turns or random.randint(*pattern["turns"])
        
        dialogue = []
        current_emotion = "neutral"
        current_topic = None
        
        for i in range(min(len(flow), turns)):
            turn = flow[i % len(flow)].copy()
            
            if i > 0 and random.random() < 0.3:
                possible_emotions = cls.EMOTION_TRANSITIONS.get(current_emotion, ["neutral"])
                turn["emotion"] = random.choice(possible_emotions)
            
            current_emotion = turn["emotion"]
            
            if turn["intent"] in cls.TOPIC_TRANSITIONS:
                current_topic = turn["intent"]
                turn["possible_next_topics"] = cls.TOPIC_TRANSITIONS[current_topic]
            
            turn["turn_number"] = i + 1
            dialogue.append(turn)
        
        while len(dialogue) < turns:
            last_turn = dialogue[-1]
            new_turn = {
                "role": "user" if last_turn["role"] == "assistant" else "assistant",
                "intent": random.choice(["追问", "补充", "确认", "感谢"]),
                "emotion": random.choice(cls.EMOTION_TRANSITIONS.get(last_turn["emotion"], ["neutral"])),
                "turn_number": len(dialogue) + 1,
            }
            dialogue.append(new_turn)
        
        return dialogue


class EnhancedDataGenerator:
    """
    增强版数据生成器 - 整合所有增强模块
    """
    
    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
        
        self.emotion_model = EmotionModel(seed)
        self.user_lifecycle = UserLifecycle()
    
    def generate_enhanced_sequence(self, domain: str = "电商", days: int = 1) -> Dict:
        """生成增强版用户行为序列"""
        result = {
            "user_id": self.user_lifecycle.user_id,
            "domain": domain,
            "sequences": [],
            "metadata": {
                "total_days": days,
                "emotion_changes": [],
                "lifecycle_stages": [],
                "unexpected_events": [],
                "cross_platform_jumps": 0,
            },
        }
        
        for day in range(days):
            lifecycle_state = self.user_lifecycle.advance_day()
            result["metadata"]["lifecycle_stages"].append({
                "day": day + 1,
                "stage": lifecycle_state["stage"],
            })
            
            daily_behaviors = self.user_lifecycle.generate_daily_behaviors()
            
            seasonal = SeasonalPattern.get_seasonal_modifier(
                datetime.now() + timedelta(days=day)
            )
            
            for behavior in daily_behaviors:
                emotion_state = self.emotion_model.update_emotion(
                    external_trigger=random.choice(["浏览商品", "收到推荐", "看到优惠", None])
                )
                
                behavior["emotion"] = {
                    "type": emotion_state.emotion_type.value,
                    "intensity": emotion_state.intensity,
                    "description": self.emotion_model.get_emotion_description(),
                }
                
                behavior_modifiers = self.emotion_model.get_behavior_modifier()
                behavior["modifiers"] = behavior_modifiers
                
                behavior["seasonal_impact"] = seasonal
                
                unexpected = UnexpectedEvent.generate_event("afternoon")
                if unexpected:
                    result["metadata"]["unexpected_events"].append({
                        "day": day + 1,
                        "event": unexpected,
                    })
            
            if random.random() < 0.3:
                cross_platform = CrossPlatformBehavior.generate_cross_platform_sequence()
                daily_behaviors.extend(cross_platform)
                result["metadata"]["cross_platform_jumps"] += 1
            
            result["sequences"].extend(daily_behaviors)
        
        return result
    
    def generate_dialogue_dataset(self, count: int = 10, min_turns: int = 5) -> List[Dict]:
        """生成对话数据集"""
        dialogues = []
        
        for i in range(count):
            pattern = random.choice(list(MultiTurnDialogue.DIALOGUE_PATTERNS.keys()))
            dialogue = MultiTurnDialogue.generate_dialogue(pattern, min_turns)
            
            dialogues.append({
                "id": f"dialogue_{i+1}",
                "pattern": pattern,
                "turns": len(dialogue),
                "dialogue": dialogue,
            })
        
        return dialogues


class MultimodalGenerator:
    """
    多模态数据生成器 - 支持文本+图片+音频+视频+代码+表格
    
    模态类型：
    1. 文本 - 对话、评论、描述
    2. 图片 - 商品图、截图、用户上传
    3. 音频 - 语音消息、客服录音
    4. 视频 - 短视频、直播片段、教程
    5. 代码 - 代码片段、配置文件
    6. 表格 - 数据表、报表、清单
    """
    
    MODAL_TYPES = {
        "text": {
            "formats": ["plain", "markdown", "html"],
            "max_length": 10000,
            "use_cases": ["对话", "评论", "描述", "标题", "标签"],
        },
        "image": {
            "formats": ["jpg", "png", "webp", "gif"],
            "resolutions": ["thumbnail", "medium", "hd", "4k"],
            "use_cases": ["商品图", "截图", "头像", "证件照", "海报"],
        },
        "audio": {
            "formats": ["mp3", "wav", "aac", "ogg"],
            "durations": ["short", "medium", "long"],
            "use_cases": ["语音消息", "客服录音", "背景音乐", "播客"],
        },
        "video": {
            "formats": ["mp4", "webm", "mov"],
            "durations": ["clip", "short", "medium", "long"],
            "use_cases": ["短视频", "直播片段", "教程", "广告"],
        },
        "code": {
            "formats": ["json", "python", "javascript", "sql", "yaml"],
            "use_cases": ["配置", "脚本", "查询", "接口", "模板"],
        },
        "table": {
            "formats": ["csv", "xlsx", "html", "markdown"],
            "use_cases": ["数据表", "报表", "清单", "对比表"],
        },
    }
    
    IMAGE_TEMPLATES = {
        "商品图": {
            "elements": ["主体商品", "背景", "标签", "水印"],
            "styles": ["简约", "高端", "活泼", "专业"],
            "typical_size": "800x800",
        },
        "截图": {
            "elements": ["界面", "光标", "高亮", "标注"],
            "styles": ["清晰", "模糊", "标注", "裁剪"],
            "typical_size": "1920x1080",
        },
        "头像": {
            "elements": ["人物", "背景", "边框", "装饰"],
            "styles": ["真实", "卡通", "简约", "艺术"],
            "typical_size": "200x200",
        },
    }
    
    AUDIO_SCENARIOS = {
        "语音消息": {
            "duration_range": (3, 60),
            "sample_rate": 16000,
            "noise_level": "low",
            "speaker": "user",
        },
        "客服录音": {
            "duration_range": (30, 600),
            "sample_rate": 8000,
            "noise_level": "medium",
            "speaker": "agent",
        },
        "背景音乐": {
            "duration_range": (60, 300),
            "sample_rate": 44100,
            "noise_level": "none",
            "speaker": "system",
        },
    }
    
    VIDEO_SCENARIOS = {
        "短视频": {
            "duration_range": (15, 60),
            "resolution": "1080p",
            "fps": 30,
            "content": ["产品展示", "使用教程", "开箱", "评测"],
        },
        "直播片段": {
            "duration_range": (30, 300),
            "resolution": "720p",
            "fps": 25,
            "content": ["互动问答", "产品介绍", "抽奖", "促销"],
        },
        "教程": {
            "duration_range": (60, 1800),
            "resolution": "1080p",
            "fps": 30,
            "content": ["操作演示", "功能讲解", "问题解决", "技巧分享"],
        },
    }
    
    CODE_TEMPLATES = {
        "json": {
            "template": {"key": "value", "items": [], "config": {}},
            "use_cases": ["配置文件", "API响应", "数据交换"],
        },
        "python": {
            "template": "def function_name(params):\n    # TODO: implement\n    pass",
            "use_cases": ["数据处理", "自动化脚本", "API调用"],
        },
        "sql": {
            "template": "SELECT * FROM table WHERE condition = 'value';",
            "use_cases": ["数据查询", "报表生成", "数据分析"],
        },
        "javascript": {
            "template": "const data = await fetch(url).then(r => r.json());",
            "use_cases": ["前端交互", "API调用", "数据处理"],
        },
    }
    
    TABLE_TEMPLATES = {
        "数据表": {
            "columns": ["ID", "名称", "数量", "价格", "状态"],
            "rows_range": (5, 100),
        },
        "报表": {
            "columns": ["日期", "指标", "数值", "环比", "同比"],
            "rows_range": (7, 365),
        },
        "清单": {
            "columns": ["序号", "项目", "数量", "备注"],
            "rows_range": (3, 50),
        },
    }
    
    @classmethod
    def generate_multimodal_content(cls, modality: str, scenario: str = None) -> Dict:
        """生成多模态内容描述"""
        if modality not in cls.MODAL_TYPES:
            return {"error": f"不支持的模态类型: {modality}"}
        
        config = cls.MODAL_TYPES[modality]
        result = {
            "modality": modality,
            "format": random.choice(config["formats"]),
            "use_case": random.choice(config["use_cases"]),
            "metadata": {},
        }
        
        if modality == "image":
            template = cls.IMAGE_TEMPLATES.get(scenario or "商品图")
            result["metadata"] = {
                "resolution": template["typical_size"],
                "style": random.choice(template["styles"]),
                "elements": random.sample(template["elements"], min(2, len(template["elements"]))),
                "file_size_kb": random.randint(50, 500),
            }
        
        elif modality == "audio":
            audio_config = cls.AUDIO_SCENARIOS.get(scenario or "语音消息")
            result["metadata"] = {
                "duration_seconds": random.randint(*audio_config["duration_range"]),
                "sample_rate": audio_config["sample_rate"],
                "noise_level": audio_config["noise_level"],
                "speaker": audio_config["speaker"],
                "transcription": "[语音转文字内容]",
            }
        
        elif modality == "video":
            video_config = cls.VIDEO_SCENARIOS.get(scenario or "短视频")
            result["metadata"] = {
                "duration_seconds": random.randint(*video_config["duration_range"]),
                "resolution": video_config["resolution"],
                "fps": video_config["fps"],
                "content_type": random.choice(video_config["content"]),
                "file_size_mb": random.randint(5, 100),
            }
        
        elif modality == "code":
            code_template = cls.CODE_TEMPLATES.get(result["format"], cls.CODE_TEMPLATES["json"])
            result["metadata"] = {
                "lines": random.randint(5, 100),
                "use_case": random.choice(code_template["use_cases"]),
                "template": code_template["template"],
            }
        
        elif modality == "table":
            table_template = cls.TABLE_TEMPLATES.get(scenario or "数据表")
            result["metadata"] = {
                "columns": table_template["columns"],
                "rows": random.randint(*table_template["rows_range"]),
                "has_header": True,
                "has_total": random.random() > 0.5,
            }
        
        return result
    
    @classmethod
    def generate_multimodal_sequence(cls, sequence_length: int = 5) -> List[Dict]:
        """生成多模态内容序列"""
        sequence = []
        
        modalities = list(cls.MODAL_TYPES.keys())
        weights = [0.5, 0.2, 0.1, 0.1, 0.05, 0.05]
        
        for i in range(sequence_length):
            modality = random.choices(modalities, weights=weights)[0]
            content = cls.generate_multimodal_content(modality)
            content["sequence_index"] = i + 1
            content["timestamp"] = (datetime.now() + timedelta(minutes=i * 5)).isoformat()
            sequence.append(content)
        
        return sequence
    
    @classmethod
    def generate_cross_modal_reference(cls) -> Dict:
        """生成跨模态引用关系"""
        references = []
        
        ref_types = [
            ("text", "image", "描述图片内容"),
            ("image", "text", "图片中的文字"),
            ("audio", "text", "语音转文字"),
            ("video", "image", "视频截图"),
            ("code", "text", "代码注释"),
            ("table", "image", "表格图表化"),
        ]
        
        for from_mod, to_mod, relation in random.sample(ref_types, min(3, len(ref_types))):
            references.append({
                "from_modality": from_mod,
                "to_modality": to_mod,
                "relation": relation,
                "confidence": round(random.uniform(0.7, 0.99), 2),
            })
        
        return {
            "reference_count": len(references),
            "references": references,
            "cross_modal_type": random.choice(["parallel", "sequential", "embedded"]),
        }


class MultimodalDialogueEnhancer:
    """
    多模态对话增强器 - 为对话添加多模态元素
    """
    
    @classmethod
    def enhance_dialogue(cls, dialogue: List[Dict]) -> List[Dict]:
        """为对话添加多模态元素"""
        enhanced = []
        
        for turn in dialogue:
            enhanced_turn = turn.copy()
            
            if turn["role"] == "user":
                if random.random() < 0.3:
                    enhanced_turn["attachment"] = MultimodalGenerator.generate_multimodal_content(
                        random.choice(["image", "audio"])
                    )
                
                if random.random() < 0.2:
                    enhanced_turn["emotion_indicator"] = {
                        "type": random.choice(["emoji", "sticker", "voice_tone"]),
                        "value": random.choice(["😊", "👍", "❓", "😢", "😠"]),
                    }
            
            else:
                if random.random() < 0.4:
                    enhanced_turn["attachment"] = MultimodalGenerator.generate_multimodal_content(
                        random.choice(["image", "table", "code"])
                    )
                
                if random.random() < 0.3:
                    enhanced_turn["quick_actions"] = random.sample(
                        ["查看详情", "立即购买", "联系客服", "查看订单", "评价"],
                        random.randint(1, 3)
                    )
            
            enhanced.append(enhanced_turn)
        
        return enhanced


if __name__ == "__main__":
    print("=" * 60)
    print("增强版数据生成器测试")
    print("=" * 60)
    
    generator = EnhancedDataGenerator(seed=42)
    
    print("\n[1] 情绪建模测试:")
    for i in range(5):
        state = generator.emotion_model.update_emotion(
            external_trigger=random.choice(["收到优惠券", "商品缺货", None])
        )
        print(f"  第{i+1}次: {generator.emotion_model.get_emotion_description()}")
    
    print("\n[2] 意外事件测试:")
    for i in range(3):
        event = UnexpectedEvent.generate_event("afternoon")
        if event:
            print(f"  事件: {event['event']} -> {event['behavior_change']}")
    
    print("\n[3] 跨平台行为测试:")
    sequence = CrossPlatformBehavior.generate_cross_platform_sequence()
    print(f"  生成 {len(sequence)} 个跨平台行为")
    for s in sequence[:3]:
        print(f"    [{s['platform_type']}] {s['action']}")
    
    print("\n[4] 用户生命周期测试:")
    for day in range(10):
        state = generator.user_lifecycle.advance_day()
        if state["stage"] != generator.user_lifecycle.stage_history[-1]["from"] if generator.user_lifecycle.stage_history else True:
            print(f"  Day {state['day']}: {state['stage']}")
    
    print("\n[5] 多轮对话测试:")
    dialogue = MultiTurnDialogue.generate_dialogue("客服咨询", 5)
    for turn in dialogue:
        print(f"  [{turn['role']}] {turn['intent']} ({turn['emotion']})")
    
    print("\n[6] 多模态内容测试:")
    for modality in ["image", "audio", "video", "code", "table"]:
        content = MultimodalGenerator.generate_multimodal_content(modality)
        print(f"  [{modality}] 格式: {content['format']}, 用途: {content['use_case']}")
    
    print("\n[7] 多模态对话增强测试:")
    enhanced = MultimodalDialogueEnhancer.enhance_dialogue(dialogue)
    for turn in enhanced:
        attachment = turn.get("attachment", {})
        if attachment:
            print(f"  [{turn['role']}] 附件: {attachment.get('modality')} - {attachment.get('use_case')}")
    
    print("\n[8] 跨模态引用测试:")
    cross_ref = MultimodalGenerator.generate_cross_modal_reference()
    print(f"  引用数量: {cross_ref['reference_count']}")
    for ref in cross_ref['references']:
        print(f"    {ref['from_modality']} -> {ref['to_modality']}: {ref['relation']}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
