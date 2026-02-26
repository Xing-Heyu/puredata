#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层 - 配置管理实现
整合自 datagenpro/utils/config.py 和 配置管理.py
"""

import os
import json
from typing import Any, Optional

class Config:
    """配置管理类"""
    
    _instance = None
    _config = {}
    _env_prefix = "DATAGENPRO_"
    _config_file = "config.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._load_config()
        self._load_from_file()
    
    def _load_config(self):
        self._config = {
            "app": {
                "name": "DataGen Pro",
                "version": "2.1.0",
                "debug": self._get_bool("DEBUG", False),
                "host": self._get("HOST", "0.0.0.0"),
                "port": self._get_int("PORT", 8000),
            },
            "security": {
                "secret_key": self._get("SECRET_KEY", "dev-secret-key-change-in-production"),
                "token_expire_hours": self._get_int("TOKEN_EXPIRE_HOURS", 24),
            },
            "database": {
                "url": self._get("DATABASE_URL", "sqlite:///./data/datagenpro.db"),
            },
            "redis": {
                "url": self._get("REDIS_URL", ""),
            },
            "api": {
                "qianwen_api_key": self._get("QIANWEN_API_KEY", ""),
                "qianwen_model": self._get("QIANWEN_MODEL", "qwen-turbo"),
            },
            "generation": {
                "max_batch_size": self._get_int("MAX_BATCH_SIZE", 1000),
                "default_output_dir": self._get("DEFAULT_OUTPUT_DIR", "./outputs"),
                "max_workers": self._get_int("MAX_WORKERS", 4),
                "max_retries": self._get_int("MAX_RETRIES", 3),
            },
            "quota": {
                "free_daily": self._get_int("FREE_DAILY_QUOTA", 100),
                "free_monthly": self._get_int("FREE_MONTHLY_QUOTA", 1000),
            },
        }
    
    def _load_from_file(self):
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._deep_merge(self._config, file_config)
            except Exception:
                pass
    
    def _deep_merge(self, base: dict, override: dict):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _get(self, key: str, default: Any = None) -> Any:
        env_key = f"{self._env_prefix}{key}"
        return os.environ.get(env_key, os.environ.get(key, default))
    
    def _get_int(self, key: str, default: int = 0) -> int:
        value = self._get(key)
        try:
            return int(value) if value else default
        except (ValueError, TypeError):
            return default
    
    def _get_bool(self, key: str, default: bool = False) -> bool:
        value = self._get(key)
        return value.lower() in ("true", "1", "yes", "on") if value else default
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any, persist: bool = False):
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def is_debug(self) -> bool:
        return self.get("app.debug", False)
    
    @property
    def secret_key(self) -> str:
        return self.get("security.secret_key", "dev-secret-key")
    
    @property
    def database_url(self) -> str:
        return self.get("database.url", "sqlite:///./data/datagenpro.db")

config = Config()

def get_config(key: str = None, default: Any = None) -> Any:
    if key is None:
        return config
    return config.get(key, default)

def is_debug() -> bool:
    return config.is_debug()

__all__ = ["Config", "config", "get_config", "is_debug"]
