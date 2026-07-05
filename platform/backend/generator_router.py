#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一生成调度器 - GeneratorRouter
根据 output_type 分发到不同的生成器，并接入统一质量管道
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GenerationResult:
    """生成结果"""
    success: bool
    data: List[Dict] = field(default_factory=list)
    error: str = ""
    metadata: Dict = field(default_factory=dict)
    quality_report: Dict = field(default_factory=dict)


class GeneratorRouter:
    """
    统一生成调度器
    
    工作流程:
    1. 根据 output_type 分发到对应生成器
    2. 接入统一质量管道
    3. 返回验证后的数据
    """
    
    SUPPORTED_TYPES = [
        "text",           # 纯文本
        "knowledge_graph", # 知识图谱三元组
        "event_chain",    # 事件因果链
        "literature",     # 专业文献
        "image",          # 文本+图片
        "audio",          # 文本+音频
        "multimodal"      # 文本+图片+音频
    ]
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self._init_generators()
    
    def _init_generators(self):
        """初始化生成器"""
        self.knowledge_graph_generator = None
        self.event_chain_generator = None
        self.literature_generator = None
        
        # 延迟导入生成器
        try:
            from knowledge_graph_generator import KnowledgeGraphGenerator, LiteratureGenerator
            self.knowledge_graph_generator = KnowledgeGraphGenerator()
            self.literature_generator = LiteratureGenerator()
        except ImportError as e:
            print(f"[GeneratorRouter] 知识图谱/文献生成器导入失败: {e}")
        
        try:
            from event_chain_generator import EventChainGenerator
            self.event_chain_generator = EventChainGenerator()
        except ImportError as e:
            print(f"[GeneratorRouter] 事件链生成器导入失败: {e}")
    
    def generate(self, 
                 output_type: str,
                 domain: str,
                 count: int,
                 task_id: str = "",
                 **kwargs) -> GenerationResult:
        """
        统一生成入口
        
        Args:
            output_type: 输出类型 (text/knowledge_graph/event_chain/literature/image/audio/multimodal)
            domain: 领域
            count: 生成数量
            task_id: 任务ID
            **kwargs: 其他参数 (quality_mode, format_type 等)
        
        Returns:
            GenerationResult: 生成结果
        """
        if output_type not in self.SUPPORTED_TYPES:
            return GenerationResult(
                success=False,
                error=f"不支持的输出类型: {output_type}"
            )
        
        print(f"[GeneratorRouter] 开始生成: output_type={output_type}, domain={domain}, count={count}")
        
        try:
            # 根据类型分发
            if output_type == "knowledge_graph":
                return self._generate_knowledge_graph(domain, count, task_id, **kwargs)
            elif output_type == "event_chain":
                return self._generate_event_chain(domain, count, task_id, **kwargs)
            elif output_type == "literature":
                return self._generate_literature(domain, count, task_id, **kwargs)
            elif output_type == "text":
                return self._generate_text(domain, count, task_id, **kwargs)
            elif output_type in ["image", "audio", "multimodal"]:
                return self._generate_multimodal(output_type, domain, count, task_id, **kwargs)
            else:
                return GenerationResult(success=False, error=f"未实现的输出类型: {output_type}")
        
        except Exception as e:
            print(f"[GeneratorRouter] 生成失败: {e}")
            return GenerationResult(success=False, error=str(e))
    
    def _generate_knowledge_graph(self, domain: str, count: int, task_id: str, **kwargs) -> GenerationResult:
        """生成知识图谱"""
        if not self.knowledge_graph_generator:
            return GenerationResult(success=False, error="知识图谱生成器未初始化")
        
        use_api = kwargs.get("use_api", True)
        data = self.knowledge_graph_generator.generate_triples_batch(domain, count, use_api=use_api)
        
        # 确保数量达标
        while len(data) < count:
            shortage = count - len(data)
            print(f"[GeneratorRouter] 知识图谱数量不足，补充{shortage}条...")
            supplement = self.knowledge_graph_generator.generate_triples_batch(
                domain, shortage, use_api=False
            )
            data.extend(supplement)
        
        data = data[:count]
        
        return GenerationResult(
            success=True,
            data=data,
            metadata={
                "output_type": "knowledge_graph",
                "domain": domain,
                "count": len(data)
            }
        )
    
    def _generate_event_chain(self, domain: str, count: int, task_id: str, **kwargs) -> GenerationResult:
        """生成事件因果链"""
        if not self.event_chain_generator:
            return GenerationResult(success=False, error="事件链生成器未初始化")
        
        use_api = kwargs.get("use_api", True)
        data = self.event_chain_generator.generate_chains_batch(domain, count, use_api=use_api)
        
        # 确保数量达标
        while len(data) < count:
            shortage = count - len(data)
            print(f"[GeneratorRouter] 事件链数量不足，补充{shortage}条...")
            supplement = self.event_chain_generator.generate_chains_batch(
                domain, shortage, use_api=False
            )
            data.extend(supplement)
        
        data = data[:count]
        
        return GenerationResult(
            success=True,
            data=data,
            metadata={
                "output_type": "event_chain",
                "domain": domain,
                "count": len(data)
            }
        )
    
    def _generate_literature(self, domain: str, count: int, task_id: str, **kwargs) -> GenerationResult:
        """生成文献"""
        if not self.literature_generator:
            return GenerationResult(success=False, error="文献生成器未初始化")
        
        length = kwargs.get("length", 2000)
        data = self.literature_generator.generate_literature_batch(domain, count, length=length)
        
        # 确保数量达标
        while len(data) < count:
            shortage = count - len(data)
            print(f"[GeneratorRouter] 文献数量不足，补充{shortage}篇...")
            supplement = self.literature_generator.generate_literature_batch(
                domain, shortage, length=length
            )
            data.extend(supplement)
        
        data = data[:count]
        
        return GenerationResult(
            success=True,
            data=data,
            metadata={
                "output_type": "literature",
                "domain": domain,
                "count": len(data)
            }
        )
    
    def _generate_text(self, domain: str, count: int, task_id: str, **kwargs) -> GenerationResult:
        """生成文本 - 委托给原有函数"""
        try:
            from simple_main import generate_data_clean, generate_data_hybrid, generate_data_noisy
            
            mode = kwargs.get("mode", "hybrid")
            quality_mode = kwargs.get("quality_mode", "standard")
            
            if mode == "clean":
                data = generate_data_clean(domain, count, task_id, quality_mode)
            elif mode == "noisy":
                noise_level = kwargs.get("noise_level", 2)
                advanced_noise = kwargs.get("advanced_noise", None)
                data = generate_data_noisy(domain, count, task_id, noise_level, advanced_noise)
            else:
                data = generate_data_hybrid(domain, count, task_id, 
                                           kwargs.get("noise_level", 2),
                                           kwargs.get("advanced_noise", None))
            
            return GenerationResult(
                success=True,
                data=data,
                metadata={
                    "output_type": "text",
                    "domain": domain,
                    "count": len(data),
                    "mode": mode
                }
            )
        except Exception as e:
            return GenerationResult(success=False, error=f"文本生成失败: {e}")
    
    def _generate_multimodal(self, output_type: str, domain: str, count: int, task_id: str, **kwargs) -> GenerationResult:
        """生成多模态数据"""
        # 先生成文本
        text_result = self._generate_text(domain, count, task_id, **kwargs)
        if not text_result.success:
            return text_result
        
        data = text_result.data
        
        # 添加多模态转换
        if output_type in ["image", "multimodal"]:
            try:
                from multimodal_converter import convert_to_multimodal
                image_style = kwargs.get("image_style", "")
                image_requirement = kwargs.get("image_requirement", "")
                
                loop = asyncio.get_event_loop()
                data = loop.run_until_complete(convert_to_multimodal(
                    data, output_type, image_style, 
                    kwargs.get("voice_id", "zh-CN-XiaoxiaoNeural"),
                    image_requirement
                ))
            except Exception as e:
                print(f"[GeneratorRouter] 多模态转换失败: {e}")
        
        return GenerationResult(
            success=True,
            data=data,
            metadata={
                "output_type": output_type,
                "domain": domain,
                "count": len(data)
            }
        )


def get_generator_router(config: Dict = None) -> GeneratorRouter:
    """获取生成器路由实例"""
    global _generator_router
    if _generator_router is None:
        _generator_router = GeneratorRouter(config)
    return _generator_router


_generator_router = None
