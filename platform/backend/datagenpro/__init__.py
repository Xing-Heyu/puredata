#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataGen Pro - 模块化架构
清晰的模块划分，便于维护和扩展
"""

# 模块导出
from .generators import (
    DataGenerator,
    SequenceGenerator,
    TemplateGenerator
)

from .converters import (
    AIFormatConverter,
    QualityController
)

from .validators import (
    DataValidator,
    AIValidator
)

from .managers import (
    TaskManager,
    TemplateManager,
    FaultToleranceManager
)

from .utils import (
    Config,
    Logger,
    Cache
)

__version__ = "2.1.0"
__all__ = [
    "DataGenerator",
    "SequenceGenerator", 
    "TemplateGenerator",
    "AIFormatConverter",
    "QualityController",
    "DataValidator",
    "AIValidator",
    "TaskManager",
    "TemplateManager",
    "FaultToleranceManager",
    "Config",
    "Logger",
    "Cache"
]
