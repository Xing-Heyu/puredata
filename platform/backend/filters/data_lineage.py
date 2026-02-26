#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据血缘追溯模块 - 防止被坑，可追溯数据来源

核心功能：
1. 记录数据来源
2. 记录变换过程
3. 记录质量检查
4. 生成血缘链哈希
"""

import hashlib
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter


@dataclass
class LineageRecord:
    """血缘记录"""
    seed_source: str
    transformations: List[str]
    quality_checks: List[str]
    parent_id: Optional[str]
    chain_hash: str
    created_at: str
    version: str


class DataLineage:
    """
    数据血缘追溯器
    
    血缘链结构：
    {
        "seed_source": "knowledge_base|api|template",
        "transformations": ["template_expand", "quality_filter", "dedup"],
        "quality_checks": ["length_check", "language_check", "repetition_check"],
        "parent_id": null | "parent_sample_id",
        "chain_hash": "abc123...",
        "created_at": "2026-02-21T12:00:00",
        "version": "2.0.0"
    }
    """
    
    VERSION = "2.1.0"
    
    TRANSFORMATION_TYPES = {
        "knowledge_base": "知识库定义",
        "api_generation": "API生成",
        "template_expand": "模板扩展",
        "variation": "变体生成",
        "quality_filter": "质量过滤",
        "dedup": "去重处理",
        "calibrated_enhance": "校准增强",
        "anomaly_fix": "异常修复",
    }
    
    QUALITY_CHECK_TYPES = {
        "length_check": "长度检查",
        "language_check": "语言一致性检查",
        "repetition_check": "重复检测",
        "sensitive_check": "敏感信息检测",
        "format_check": "格式检查",
        "quality_score": "质量评分",
    }
    
    @classmethod
    def create_lineage(cls, 
                       seed_source: str,
                       transformations: List[str] = None,
                       quality_checks: List[str] = None,
                       parent_id: str = None,
                       additional_data: Dict = None) -> Dict:
        """创建血缘记录"""
        transformations = transformations or []
        quality_checks = quality_checks or []
        
        chain_data = {
            "seed_source": seed_source,
            "transformations": transformations,
            "quality_checks": quality_checks,
            "parent_id": parent_id,
            "created_at": datetime.now().isoformat(),
            "version": cls.VERSION,
        }
        
        if additional_data:
            chain_data["additional"] = additional_data
        
        chain_hash = cls._compute_chain_hash(chain_data)
        chain_data["chain_hash"] = chain_hash
        
        return chain_data
    
    @classmethod
    def _compute_chain_hash(cls, data: Dict) -> str:
        """计算血缘链哈希"""
        hash_data = {
            "seed_source": data.get("seed_source", ""),
            "transformations": data.get("transformations", []),
            "parent_id": data.get("parent_id", ""),
        }
        
        content = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @classmethod
    def add_transformation(cls, lineage: Dict, transformation: str) -> Dict:
        """添加变换记录"""
        if "transformations" not in lineage:
            lineage["transformations"] = []
        
        lineage["transformations"].append(transformation)
        lineage["chain_hash"] = cls._compute_chain_hash(lineage)
        lineage["updated_at"] = datetime.now().isoformat()
        
        return lineage
    
    @classmethod
    def add_quality_check(cls, lineage: Dict, check: str, passed: bool = True) -> Dict:
        """添加质量检查记录"""
        if "quality_checks" not in lineage:
            lineage["quality_checks"] = []
        
        lineage["quality_checks"].append({
            "check": check,
            "passed": passed,
            "timestamp": datetime.now().isoformat()
        })
        
        return lineage
    
    @classmethod
    def verify_lineage(cls, lineage: Dict) -> bool:
        """验证血缘链完整性"""
        required_fields = ["seed_source", "chain_hash", "created_at", "version"]
        
        for field in required_fields:
            if field not in lineage:
                return False
        
        expected_hash = cls._compute_chain_hash(lineage)
        return lineage.get("chain_hash") == expected_hash
    
    @classmethod
    def get_lineage_report(cls, lineage: Dict) -> str:
        """生成血缘报告"""
        if not lineage:
            return "无血缘信息"
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    数据血缘追溯报告                           ║
╠══════════════════════════════════════════════════════════════╣
║  种子来源: {lineage.get('seed_source', '未知'):<43} ║
║  血缘哈希: {lineage.get('chain_hash', '无'):<43} ║
║  创建时间: {lineage.get('created_at', '未知'):<43} ║
║  版本: {lineage.get('version', '未知'):<47} ║
╠══════════════════════════════════════════════════════════════╣
║  变换过程:                                                    ║
"""
        
        transformations = lineage.get("transformations", [])
        if transformations:
            for t in transformations:
                t_name = cls.TRANSFORMATION_TYPES.get(t, t)
                report += f"║    → {t_name}{' ' * (51 - len(t_name))}║\n"
        else:
            report += "║    无变换记录                                                ║\n"
        
        report += "╠══════════════════════════════════════════════════════════════╣\n"
        report += "║  质量检查:                                                    ║\n"
        
        quality_checks = lineage.get("quality_checks", [])
        if quality_checks:
            for qc in quality_checks:
                if isinstance(qc, dict):
                    check_name = cls.QUALITY_CHECK_TYPES.get(qc.get("check", ""), qc.get("check", ""))
                    passed = "✓" if qc.get("passed", True) else "✗"
                    report += f"║    {passed} {check_name}{' ' * (49 - len(check_name))}║\n"
                else:
                    check_name = cls.QUALITY_CHECK_TYPES.get(qc, qc)
                    report += f"║    ✓ {check_name}{' ' * (49 - len(check_name))}║\n"
        else:
            report += "║    无检查记录                                                ║\n"
        
        report += "╚══════════════════════════════════════════════════════════════╝\n"
        
        return report


class LineageAwareGenerator:
    """
    血缘感知生成器 - 在生成数据时自动添加血缘信息
    """
    
    def __init__(self):
        self.lineage_history = []
    
    def generate_with_lineage(self, 
                              sample: Dict,
                              seed_source: str,
                              transformations: List[str] = None,
                              quality_checks: List[str] = None) -> Dict:
        """生成带血缘信息的数据"""
        lineage = DataLineage.create_lineage(
            seed_source=seed_source,
            transformations=transformations or [],
            quality_checks=quality_checks or [],
            parent_id=sample.get("id")
        )
        
        sample["lineage"] = lineage
        
        self.lineage_history.append({
            "sample_id": sample.get("id"),
            "lineage": lineage
        })
        
        return sample
    
    def batch_generate_with_lineage(self, 
                                    samples: List[Dict],
                                    seed_source: str,
                                    transformations: List[str] = None) -> List[Dict]:
        """批量生成带血缘信息的数据"""
        results = []
        
        for sample in samples:
            result = self.generate_with_lineage(
                sample, 
                seed_source, 
                transformations
            )
            results.append(result)
        
        return results
    
    def get_lineage_stats(self) -> Dict:
        """获取血缘统计"""
        if not self.lineage_history:
            return {}
        
        sources = Counter(l["lineage"]["seed_source"] for l in self.lineage_history)
        
        return {
            "total_samples": len(self.lineage_history),
            "by_source": dict(sources),
            "version": DataLineage.VERSION
        }


data_lineage = DataLineage()
lineage_aware_generator = LineageAwareGenerator()
