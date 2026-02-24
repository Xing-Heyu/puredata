#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行为序列生成器
支持：转移概率、时间间隔、生命周期
"""

import random
import uuid
from datetime import datetime, timedelta

class SequenceGenerator:
    """用户行为序列生成器"""
    
    BEHAVIOR_CONFIGS = {
        "电商": {
            "behaviors": ["浏览", "搜索", "收藏", "加购", "下单", "支付", "收货", "评价"],
            "transitions": {
                "浏览": {"浏览": 0.3, "搜索": 0.2, "收藏": 0.15, "加购": 0.1, "离开": 0.25},
                "搜索": {"浏览": 0.2, "收藏": 0.2, "加购": 0.15, "离开": 0.45},
                "收藏": {"加购": 0.4, "下单": 0.2, "离开": 0.4},
                "加购": {"下单": 0.5, "离开": 0.5},
                "下单": {"支付": 0.8, "离开": 0.2},
                "支付": {"收货": 0.95, "离开": 0.05},
                "收货": {"评价": 0.6, "离开": 0.4},
                "评价": {"离开": 1.0}
            }
        },
        "医疗": {
            "behaviors": ["挂号", "候诊", "就诊", "检查", "诊断", "开药", "取药", "复诊"],
            "transitions": {
                "挂号": {"候诊": 0.9, "离开": 0.1},
                "候诊": {"就诊": 0.95, "离开": 0.05},
                "就诊": {"检查": 0.4, "诊断": 0.3, "开药": 0.2, "离开": 0.1},
                "检查": {"诊断": 0.8, "离开": 0.2},
                "诊断": {"开药": 0.6, "复诊": 0.3, "离开": 0.1},
                "开药": {"取药": 0.9, "离开": 0.1},
                "取药": {"离开": 0.7, "复诊": 0.3},
                "复诊": {"就诊": 0.8, "离开": 0.2}
            }
        }
    }
    
    def __init__(self):
        pass
    
    def generate(self, domain, user_count, avg_length=10):
        """生成行为序列"""
        if domain not in self.BEHAVIOR_CONFIGS:
            domain = "电商"
        
        config = self.BEHAVIOR_CONFIGS[domain]
        sequences = []
        
        for i in range(user_count):
            user_id = f"user_{i+1:05d}"
            session_id = str(uuid.uuid4())[:8]
            
            user_sequences = self._generate_user_sequence(
                user_id, session_id, config, avg_length
            )
            sequences.extend(user_sequences)
        
        sequences.sort(key=lambda x: x["timestamp"])
        
        for i, seq in enumerate(sequences):
            seq["global_id"] = i + 1
        
        return sequences
    
    def _generate_user_sequence(self, user_id, session_id, config, max_length):
        """生成单个用户序列"""
        behaviors = config["behaviors"]
        transitions = config["transitions"]
        
        sequence = []
        current_behavior = random.choice(behaviors[:3])
        current_time = datetime.now() - timedelta(days=random.randint(1, 30))
        
        step = 0
        while current_behavior != "离开" and step < max_length:
            item = {
                "user_id": user_id,
                "session_id": session_id,
                "sequence_id": step + 1,
                "behavior": current_behavior,
                "timestamp": current_time.isoformat(),
                "domain": list(self.BEHAVIOR_CONFIGS.keys())[0]
            }
            sequence.append(item)
            
            if current_behavior not in transitions:
                break
            
            next_options = transitions[current_behavior]
            current_behavior = random.choices(
                list(next_options.keys()),
                weights=list(next_options.values())
            )[0]
            
            current_time = current_time + timedelta(minutes=random.randint(1, 60))
            step += 1
        
        return sequence
