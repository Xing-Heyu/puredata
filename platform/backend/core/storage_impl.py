#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心层 - 存储层实现
整合自 storage_layer.py
"""

import sqlite3
import json
import threading
import os
from datetime import datetime
from contextlib import contextmanager

class StorageManager:
    """存储管理器 - SQLite存储"""
    
    _instance = None
    _lock = threading.Lock()
    
    ALLOWED_TABLES = {"key_value_store", "tasks", "users"}
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', 'datagenpro.db'
        )
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS key_value_store (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    status TEXT,
                    progress REAL,
                    result TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE,
                    email TEXT,
                    role TEXT,
                    created_at TEXT
                )
            ''')
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _validate_table(self, table: str):
        """验证表名，防止SQL注入"""
        if table not in self.ALLOWED_TABLES:
            raise ValueError(f"Invalid table name: {table}")
        return table
    
    def get(self, key: str, table: str = "key_value_store") -> any:
        table = self._validate_table(table)
        with self._get_connection() as conn:
            cursor = conn.execute(
                f'SELECT value FROM {table} WHERE key = ?', (key,)
            )
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row['value'])
                except json.JSONDecodeError:
                    return row['value']
            return None
    
    def set(self, key: str, value: any, table: str = "key_value_store"):
        now = datetime.now().isoformat()
        value_str = json.dumps(value) if not isinstance(value, str) else value
        
        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO key_value_store (key, value, created_at, updated_at)
                VALUES (?, ?, COALESCE((SELECT created_at FROM key_value_store WHERE key = ?), ?), ?)
            ''', (key, value_str, key, now, now))
            conn.commit()
    
    def delete(self, key: str, table: str = "key_value_store"):
        table = self._validate_table(table)
        with self._get_connection() as conn:
            conn.execute(f'DELETE FROM {table} WHERE key = ?', (key,))
            conn.commit()
    
    def get_all(self, table: str = "key_value_store") -> dict:
        table = self._validate_table(table)
        with self._get_connection() as conn:
            cursor = conn.execute(f'SELECT key, value FROM {table}')
            result = {}
            for row in cursor:
                try:
                    result[row['key']] = json.loads(row['value'])
                except json.JSONDecodeError:
                    result[row['key']] = row['value']
            return result
    
    def count(self, table: str = "key_value_store") -> int:
        table = self._validate_table(table)
        with self._get_connection() as conn:
            cursor = conn.execute(f'SELECT COUNT(*) as cnt FROM {table}')
            return cursor.fetchone()['cnt']

storage_manager = StorageManager()

__all__ = ["StorageManager", "storage_manager"]
