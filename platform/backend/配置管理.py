#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块 - 兼容层
已整合到 datagenpro/utils/config.py
此文件保留用于向后兼容
"""

from datagenpro.utils.config import Config, config, get_config, is_debug, is_production

__all__ = ["Config", "config", "get_config", "is_debug", "is_production"]
