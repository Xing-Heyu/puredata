#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层 - 路径配置
统一管理所有路径常量，确保路径一致性和可维护性

使用方式：
    from core import BACKEND_DIR, OUTPUT_DIR, FRONTEND_DIR
    from core.paths import BACKEND_DIR, OUTPUT_DIR, FRONTEND_DIR
"""

import os

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORM_DIR = os.path.dirname(BACKEND_DIR)
PROJECT_ROOT = os.path.dirname(PLATFORM_DIR)

FRONTEND_DIR = os.path.join(PLATFORM_DIR, 'frontend')
DOCS_DIR = os.path.join(PLATFORM_DIR, 'docs')

OUTPUT_DIR = os.path.join(BACKEND_DIR, 'outputs')
CACHE_DIR = os.path.join(BACKEND_DIR, 'cache')
LOGS_DIR = os.path.join(BACKEND_DIR, 'logs')
DATA_DIR = os.path.join(BACKEND_DIR, 'data')
BACKUPS_DIR = os.path.join(BACKEND_DIR, 'backups')
KEYWORDS_DIR = os.path.join(BACKEND_DIR, 'keywords')
DOMAIN_CONFIGS_DIR = os.path.join(BACKEND_DIR, 'domain_configs')
DOMAIN_TEMPLATES_DIR = os.path.join(BACKEND_DIR, 'domain_templates')
CONFIG_DIR = os.path.join(BACKEND_DIR, 'config')

STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')
IMAGES_DIR = os.path.join(STATIC_DIR, 'images')

USER_DB_FILE = os.path.join(DATA_DIR, 'users.db')
SESSION_FILE = os.path.join(BACKEND_DIR, 'sessions.json')
USER_JSON_FILE = os.path.join(BACKEND_DIR, 'users.json')

DATAGENPRO_DB_FILE = os.path.join(DATA_DIR, 'datagenpro.db')

def ensure_dirs():
    """确保必要的目录存在"""
    dirs_to_create = [
        OUTPUT_DIR, CACHE_DIR, LOGS_DIR, DATA_DIR, BACKUPS_DIR
    ]
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)

ensure_dirs()

def safe_path_join(base_dir: str, user_path: str) -> str:
    """
    安全地连接路径，防止路径遍历攻击
    
    Args:
        base_dir: 基础目录
        user_path: 用户提供的路径
    
    Returns:
        安全的完整路径
    
    Raises:
        ValueError: 如果检测到路径遍历攻击
    """
    base_dir = os.path.normpath(base_dir)
    full_path = os.path.normpath(os.path.join(base_dir, user_path))
    if not full_path.startswith(base_dir + os.sep) and full_path != base_dir:
        raise ValueError(f"Invalid path: path traversal detected - {user_path}")
    return full_path

__all__ = [
    'BACKEND_DIR', 'PLATFORM_DIR', 'PROJECT_ROOT',
    'FRONTEND_DIR', 'DOCS_DIR',
    'OUTPUT_DIR', 'CACHE_DIR', 'LOGS_DIR', 'DATA_DIR', 'BACKUPS_DIR',
    'KEYWORDS_DIR', 'DOMAIN_CONFIGS_DIR', 'DOMAIN_TEMPLATES_DIR', 'CONFIG_DIR',
    'STATIC_DIR', 'IMAGES_DIR',
    'USER_DB_FILE', 'SESSION_FILE', 'USER_JSON_FILE', 'DATAGENPRO_DB_FILE',
    'ensure_dirs', 'safe_path_join'
]
