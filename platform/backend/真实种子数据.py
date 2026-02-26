#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实种子数据机制 - 基于daVinci-Agency论文思想

核心思想：
1. 从真实世界演进过程中提取监督信号
2. 用真实行为日志作为生成基础
3. 保持真实数据的时序特征和因果关系

参考论文：《daVinci-Agency: Unlocking Long-Horizon Agency Data-Efficiently》
核心洞察：PR序列天然包含渐进式任务分解、跨迭代功能一致性、真实改进模式
"""

import json
import random
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import os


@dataclass
class SeedDataConfig:
    """种子数据配置"""
    source_type: str  # log, api, file, manual
    domain: str
    min_samples: int = 100
    max_samples: int = 10000
    quality_threshold: float = 0.7
    diversity_threshold: float = 0.5


@dataclass
class SeedSample:
    """种子样本"""
    sample_id: str
    raw_data: Dict
    processed_data: Dict
    source: str
    timestamp: str
    quality_score: float
    features: Dict
    sequence_context: Optional[List[Dict]] = None


class RealWorldLogParser:
    """
    真实世界日志解析器
    
    支持多种日志格式：
    - Nginx/Apache访问日志
    - 应用行为日志
    - 用户操作日志
    - 交易流水日志
    """
    
    LOG_PATTERNS = {
        "nginx": r'(?P<ip>[\d.]+) - - \[(?P<time>[^\]]+)\] "(?P<method>\w+) (?P<url>[^\s]+) (?P<protocol>[^"]+)" (?P<status>\d+) (?P<size>\d+)',
        "json": None,
        "csv": None,
    }
    
    @classmethod
    def parse_nginx_log(cls, log_line: str) -> Optional[Dict]:
        """解析Nginx日志"""
        import re
        pattern = cls.LOG_PATTERNS["nginx"]
        match = re.match(pattern, log_line)
        if match:
            return match.groupdict()
        return None
    
    @classmethod
    def parse_json_log(cls, log_line: str) -> Optional[Dict]:
        """解析JSON日志"""
        try:
            return json.loads(log_line)
        except (json.JSONDecodeError, TypeError):
            return None
    
    @classmethod
    def auto_detect_and_parse(cls, log_line: str) -> Tuple[Optional[Dict], str]:
        """自动检测并解析日志"""
        log_line = log_line.strip()
        
        if log_line.startswith('{'):
            return cls.parse_json_log(log_line), "json"
        
        if '[' in log_line and ' - - ' in log_line:
            return cls.parse_nginx_log(log_line), "nginx"
        
        if ',' in log_line and log_line.count(',') >= 3:
            parts = log_line.split(',')
            keys = [f"field_{i}" for i in range(len(parts))]
            return dict(zip(keys, parts)), "csv"
        
        return None, "unknown"


class SeedDataManager:
    """
    种子数据管理器
    
    功能：
    1. 导入真实数据作为种子
    2. 清洗和预处理
    3. 质量评估
    4. 特征提取
    5. 序列上下文构建
    """
    
    def __init__(self, config: SeedDataConfig = None):
        self.config = config or SeedDataConfig(
            source_type="file",
            domain="general"
        )
        self.seeds: List[SeedSample] = []
        self.feature_stats = defaultdict(list)
    
    def import_from_file(self, file_path: str, format: str = "auto") -> int:
        """从文件导入种子数据"""
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return 0
        
        imported = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                
                if format == "auto":
                    data, detected_format = RealWorldLogParser.auto_detect_and_parse(line)
                elif format == "json":
                    data = RealWorldLogParser.parse_json_log(line)
                elif format == "nginx":
                    data = RealWorldLogParser.parse_nginx_log(line)
                else:
                    data = {"raw": line}
                
                if data:
                    sample = self._create_seed_sample(data, f"file_{line_num}")
                    if sample.quality_score >= self.config.quality_threshold:
                        self.seeds.append(sample)
                        imported += 1
        
        self._update_feature_stats()
        return imported
    
    def import_from_dict_list(self, data_list: List[Dict]) -> int:
        """从字典列表导入"""
        imported = 0
        for i, data in enumerate(data_list):
            sample = self._create_seed_sample(data, f"dict_{i}")
            if sample.quality_score >= self.config.quality_threshold:
                self.seeds.append(sample)
                imported += 1
        
        self._update_feature_stats()
        return imported
    
    def import_sample_logs(self) -> int:
        """导入示例日志（用于演示）"""
        sample_logs = self._generate_sample_logs()
        return self.import_from_dict_list(sample_logs)
    
    def _generate_sample_logs(self) -> List[Dict]:
        """生成示例日志数据"""
        users = [f"user_{i:03d}" for i in range(1, 51)]
        actions = ["浏览", "搜索", "点击", "收藏", "加入购物车", "下单", "支付", "评价", "分享", "退款"]
        items = [f"item_{i:03d}" for i in range(1, 101)]
        categories = ["电子产品", "服装", "食品", "家居", "美妆", "运动", "图书", "母婴"]
        
        logs = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(500):
            user = random.choice(users)
            action = random.choice(actions)
            item = random.choice(items)
            category = random.choice(categories)
            
            log = {
                "user_id": user,
                "action": action,
                "item_id": item,
                "category": category,
                "timestamp": (base_time + timedelta(minutes=i * 3)).isoformat(),
                "session_id": f"session_{hashlib.md5((user + str(i // 10)).encode()).hexdigest()[:8]}",
                "device": random.choice(["mobile", "desktop", "tablet"]),
                "source": random.choice(["search", "recommend", "direct", "ad"]),
                "price": round(random.uniform(10, 1000), 2) if action in ["下单", "支付"] else None,
                "quantity": random.randint(1, 5) if action in ["下单", "支付"] else None,
            }
            logs.append(log)
        
        return logs
    
    def _create_seed_sample(self, raw_data: Dict, source_id: str) -> SeedSample:
        """创建种子样本"""
        processed_data = self._preprocess(raw_data)
        quality_score = self._calculate_quality(raw_data, processed_data)
        features = self._extract_features(processed_data)
        
        return SeedSample(
            sample_id=hashlib.md5((source_id + str(raw_data)).encode()).hexdigest()[:12],
            raw_data=raw_data,
            processed_data=processed_data,
            source=source_id,
            timestamp=datetime.now().isoformat(),
            quality_score=quality_score,
            features=features
        )
    
    def _preprocess(self, data: Dict) -> Dict:
        """预处理数据"""
        processed = {}
        
        for key, value in data.items():
            if value is None or value == "" or value == "null":
                continue
            
            clean_key = key.lower().replace("-", "_").replace(" ", "_")
            
            if isinstance(value, str):
                value = value.strip()
                if value.isdigit():
                    value = int(value)
                elif value.replace(".", "").isdigit():
                    value = float(value)
            
            processed[clean_key] = value
        
        return processed
    
    def _calculate_quality(self, raw_data: Dict, processed_data: Dict) -> float:
        """计算质量分数"""
        if not raw_data:
            return 0.0
        
        completeness = len(processed_data) / max(len(raw_data), 1)
        
        valid_values = sum(1 for v in processed_data.values() 
                          if v is not None and v != "" and v != "null")
        validity = valid_values / max(len(processed_data), 1)
        
        has_required = any(k in processed_data for k in 
                          ["user_id", "action", "timestamp", "time", "id"])
        
        quality = completeness * 0.3 + validity * 0.4 + (0.3 if has_required else 0)
        
        return min(1.0, quality)
    
    def _extract_features(self, data: Dict) -> Dict:
        """提取特征"""
        features = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                features[f"{key}_length"] = len(value)
                features[f"{key}_word_count"] = len(value.split())
            elif isinstance(value, (int, float)):
                features[f"{key}_numeric"] = value
        
        if "timestamp" in data or "time" in data:
            features["has_timestamp"] = 1
        
        if "user_id" in data or "user" in data:
            features["has_user"] = 1
        
        if "action" in data:
            features["has_action"] = 1
        
        return features
    
    def _update_feature_stats(self):
        """更新特征统计"""
        self.feature_stats = defaultdict(list)
        
        for sample in self.seeds:
            for key, value in sample.features.items():
                if isinstance(value, (int, float)):
                    self.feature_stats[key].append(value)
    
    def get_seeds_by_quality(self, min_quality: float = 0.7) -> List[SeedSample]:
        """按质量筛选种子"""
        return [s for s in self.seeds if s.quality_score >= min_quality]
    
    def get_seeds_by_features(self, feature_filter: Dict) -> List[SeedSample]:
        """按特征筛选种子"""
        result = []
        for sample in self.seeds:
            match = True
            for key, value in feature_filter.items():
                if key not in sample.processed_data or sample.processed_data[key] != value:
                    match = False
                    break
            if match:
                result.append(sample)
        return result
    
    def build_sequences(self, group_by: str = "user_id", 
                        time_field: str = "timestamp") -> List[List[SeedSample]]:
        """构建行为序列"""
        groups = defaultdict(list)
        
        for sample in self.seeds:
            group_key = sample.processed_data.get(group_by, "unknown")
            groups[group_key].append(sample)
        
        sequences = []
        for group_key, samples in groups.items():
            sorted_samples = sorted(samples, 
                                   key=lambda s: s.processed_data.get(time_field, ""))
            sequences.append(sorted_samples)
        
        return sequences
    
    def export_for_training(self, output_format: str = "jsonl") -> List[str]:
        """导出为训练格式"""
        if output_format == "jsonl":
            return [json.dumps(s.processed_data, ensure_ascii=False) for s in self.seeds]
        elif output_format == "json":
            return json.dumps([s.processed_data for s in self.seeds], ensure_ascii=False)
        else:
            return [str(s.processed_data) for s in self.seeds]


class SequenceEvolutionExtractor:
    """
    序列演进提取器 - 基于daVinci-Agency论文
    
    从真实行为序列中提取演进模式：
    1. 渐进式任务分解
    2. 跨迭代一致性
    3. 真实改进模式
    """
    
    @classmethod
    def extract_patterns(cls, sequences: List[List[SeedSample]]) -> Dict:
        """提取演进模式"""
        patterns = {
            "action_transitions": defaultdict(int),
            "time_patterns": [],
            "session_patterns": [],
            "evolution_chains": [],
        }
        
        for sequence in sequences:
            if len(sequence) < 2:
                continue
            
            for i in range(len(sequence) - 1):
                current_action = sequence[i].processed_data.get("action", "unknown")
                next_action = sequence[i + 1].processed_data.get("action", "unknown")
                transition = f"{current_action} -> {next_action}"
                patterns["action_transitions"][transition] += 1
            
            actions = [s.processed_data.get("action", "unknown") for s in sequence]
            if len(actions) >= 3:
                patterns["evolution_chains"].append(actions)
        
        return patterns
    
    @classmethod
    def generate_from_patterns(cls, patterns: Dict, count: int = 100) -> List[Dict]:
        """基于模式生成新序列"""
        transitions = patterns["action_transitions"]
        total_transitions = sum(transitions.values())
        
        if total_transitions == 0:
            return []
        
        transition_probs = {k: v / total_transitions for k, v in transitions.items()}
        
        generated = []
        
        for _ in range(count):
            sequence = []
            
            start_actions = [t.split(" -> ")[0] for t in transition_probs.keys()]
            current_action = random.choice(start_actions)
            sequence.append({"action": current_action, "step": 0})
            
            for step in range(random.randint(3, 10)):
                possible_nexts = [t.split(" -> ")[1] for t in transition_probs.keys() 
                                 if t.startswith(f"{current_action} ->")]
                
                if not possible_nexts:
                    break
                
                current_action = random.choice(possible_nexts)
                sequence.append({"action": current_action, "step": step + 1})
            
            generated.append({
                "sequence": sequence,
                "length": len(sequence),
                "source": "pattern_evolution"
            })
        
        return generated


if __name__ == "__main__":
    print("=" * 60)
    print("真实种子数据机制测试")
    print("=" * 60)
    
    config = SeedDataConfig(
        source_type="sample",
        domain="ecommerce",
        quality_threshold=0.5
    )
    
    manager = SeedDataManager(config)
    
    print("\n[1] 导入示例日志:")
    imported = manager.import_sample_logs()
    print(f"  导入数量: {imported}")
    print(f"  种子总数: {len(manager.seeds)}")
    
    print("\n[2] 质量分布:")
    quality_scores = [s.quality_score for s in manager.seeds]
    print(f"  平均质量: {sum(quality_scores)/len(quality_scores):.2%}")
    print(f"  最高质量: {max(quality_scores):.2%}")
    print(f"  最低质量: {min(quality_scores):.2%}")
    
    print("\n[3] 构建行为序列:")
    sequences = manager.build_sequences(group_by="user_id")
    print(f"  序列数量: {len(sequences)}")
    print(f"  平均长度: {sum(len(s) for s in sequences)/len(sequences):.1f}")
    
    print("\n[4] 提取演进模式:")
    patterns = SequenceEvolutionExtractor.extract_patterns(sequences)
    print(f"  转移模式数: {len(patterns['action_transitions'])}")
    top_transitions = sorted(patterns['action_transitions'].items(), 
                            key=lambda x: x[1], reverse=True)[:5]
    for trans, count in top_transitions:
        print(f"    {trans}: {count}")
    
    print("\n[5] 基于模式生成:")
    generated = SequenceEvolutionExtractor.generate_from_patterns(patterns, count=10)
    print(f"  生成序列数: {len(generated)}")
    for g in generated[:3]:
        actions = [s['action'] for s in g['sequence']]
        print(f"    {' -> '.join(actions)}")
    
    print("\n[6] 导出训练数据:")
    exported = manager.export_for_training("jsonl")
    print(f"  导出行数: {len(exported)}")
    print(f"  示例: {exported[0][:100]}...")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
