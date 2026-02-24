#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataGen Pro - 配置管理模块（整合版）
环境变量和配置文件管理

整合自：
- 配置管理.py（完整功能）
- 原有config.py

功能：
- 环境变量支持
- 嵌套键访问（如 "app.debug"）
- 敏感信息脱敏
- 文件持久化
"""

import os
import json
from pathlib import Path
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
                "version": "1.0.0",
                "debug": self._get_bool("DEBUG", False),
                "host": self._get("HOST", "0.0.0.0"),
                "port": self._get_int("PORT", 8000),
            },
            "security": {
                "secret_key": self._get("SECRET_KEY", "dev-secret-key-change-in-production"),
                "token_expire_hours": self._get_int("TOKEN_EXPIRE_HOURS", 24),
                "password_min_length": self._get_int("PASSWORD_MIN_LENGTH", 6),
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
                "api_timeout": self._get_int("API_TIMEOUT", 30),
            },
            "generation": {
                "max_batch_size": self._get_int("MAX_BATCH_SIZE", 1000),
                "default_output_dir": self._get("DEFAULT_OUTPUT_DIR", "./outputs"),
                "max_workers": self._get_int("MAX_WORKERS", 4),
                "max_retries": self._get_int("MAX_RETRIES", 3),
                "checkpoint_interval": self._get_int("CHECKPOINT_INTERVAL", 10),
                "default_quality": self._get("DEFAULT_QUALITY", "normal"),
            },
            "quota": {
                "free_daily": self._get_int("FREE_DAILY_QUOTA", 100),
                "free_monthly": self._get_int("FREE_MONTHLY_QUOTA", 1000),
                "vip_daily": self._get_int("VIP_DAILY_QUOTA", 1000),
                "vip_monthly": self._get_int("VIP_MONTHLY_QUOTA", 10000),
            },
            "logging": {
                "level": self._get("LOG_LEVEL", "INFO"),
                "file": self._get("LOG_FILE", "logs/datagenpro.log"),
            },
        }
    
    def _load_from_file(self):
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._deep_merge(self._config, file_config)
            except Exception as e:
                print(f"[Config] 加载配置文件失败: {e}")
    
    def _save_to_file(self):
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Config] 保存配置文件失败: {e}")
    
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
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def _get_bool(self, key: str, default: bool = False) -> bool:
        value = self._get(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")
    
    def _get_float(self, key: str, default: float = 0.0) -> float:
        value = self._get(key)
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
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
        
        if persist:
            self._save_to_file()
    
    def get_all(self) -> dict:
        return self._config.copy()
    
    def is_debug(self) -> bool:
        return self.get("app.debug", False)
    
    def is_production(self) -> bool:
        return not self.is_debug()
    
    @property
    def app_name(self) -> str:
        return self.get("app.name", "DataGen Pro")
    
    @property
    def version(self) -> str:
        return self.get("app.version", "1.0.0")
    
    @property
    def secret_key(self) -> str:
        return self.get("security.secret_key", "dev-secret-key")
    
    @property
    def database_url(self) -> str:
        return self.get("database.url", "sqlite:///./data/datagenpro.db")
    
    @property
    def redis_url(self) -> Optional[str]:
        return self.get("redis.url") or None
    
    @property
    def qianwen_api_key(self) -> Optional[str]:
        return self.get("api.qianwen_api_key") or None
    
    @property
    def max_batch_size(self) -> int:
        return self.get("generation.max_batch_size", 1000)
    
    @property
    def output_dir(self) -> str:
        return self.get("generation.default_output_dir", "./outputs")
    
    @property
    def max_workers(self) -> int:
        return self.get("generation.max_workers", 4)
    
    @property
    def max_retries(self) -> int:
        return self.get("generation.max_retries", 3)
    
    @property
    def checkpoint_interval(self) -> int:
        return self.get("generation.checkpoint_interval", 10)
    
    @property
    def default_quality(self) -> str:
        return self.get("generation.default_quality", "normal")
    
    def to_json(self) -> str:
        safe_config = self._config.copy()
        if safe_config.get("api", {}).get("qianwen_api_key"):
            safe_config["api"]["qianwen_api_key"] = "***"
        if safe_config.get("security", {}).get("secret_key"):
            safe_config["security"]["secret_key"] = "***"
        return json.dumps(safe_config, indent=2, ensure_ascii=False)
    
    def save(self):
        self._save_to_file()
    
    def reload(self):
        self._load_config()
        self._load_from_file()

config = Config()

def get_config(key: str = None, default: Any = None) -> Any:
    if key is None:
        return config
    return config.get(key, default)

def is_debug() -> bool:
    return config.is_debug()

def is_production() -> bool:
    return config.is_production()

__all__ = ["Config", "config", "get_config", "is_debug", "is_production"]
