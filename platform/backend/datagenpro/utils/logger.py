#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataGen Pro - 结构化日志系统

此文件为兼容层，实际实现已迁移到 core/logger_impl.py
保持向后兼容，新代码建议直接从 core.logger_impl 导入

迁移说明：
    # 旧代码（仍然有效）
    from datagenpro.utils.logger import StructuredLogger, get_logger
    
    # 新代码（推荐）
    from core.logger_impl import StructuredLogger, get_logger, setup_logging
"""

from core.logger_impl import (
    StructuredLogger,
    StructuredFormatter,
    ColoredFormatter,
    logger,
    get_logger,
    setup_logging,
    log_execution,
    LOG_DIR
)

__all__ = [
    "StructuredLogger",
    "StructuredFormatter",
    "ColoredFormatter", 
    "logger",
    "get_logger",
    "setup_logging",
    "log_execution",
    "LOG_DIR"
]
