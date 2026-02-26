#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据备份模块 - 自动备份和恢复

功能：
1. 定期自动备份
2. 手动备份
3. 数据恢复
4. 备份清理
"""

import os
import json
import shutil
import zipfile
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import hashlib


@dataclass
class BackupInfo:
    """备份信息"""
    id: str
    filename: str
    created_at: str
    size_bytes: int
    type: str  # auto, manual
    description: str


class BackupManager:
    """
    备份管理器
    
    备份内容：
    - 用户数据
    - 生成历史
    - 配置文件
    - 知识库
    """
    
    def __init__(self, backup_dir: str = None, max_backups: int = 30):
        self.backup_dir = backup_dir or os.path.join(
            os.path.dirname(__file__), '..', 'backups'
        )
        self.max_backups = max_backups
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        
        os.makedirs(self.backup_dir, exist_ok=True)
        self._running = False
        self._backup_thread = None
    
    def create_backup(self, description: str = "", backup_type: str = "manual") -> BackupInfo:
        """创建备份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        filename = f"backup_{backup_id}_{timestamp}.zip"
        filepath = os.path.join(self.backup_dir, filename)
        
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists(self.data_dir):
                for root, dirs, files in os.walk(self.data_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(self.data_dir))
                        zf.write(file_path, arcname)
            
            if os.path.exists(self.outputs_dir):
                for root, dirs, files in os.walk(self.outputs_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(self.outputs_dir))
                        zf.write(file_path, arcname)
            
            if os.path.exists(self.config_dir):
                for root, dirs, files in os.walk(self.config_dir):
                    for file in files:
                        if file.endswith('.py') or file.endswith('.json'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(self.config_dir))
                            zf.write(file_path, arcname)
            
            manifest = {
                "id": backup_id,
                "created_at": datetime.now().isoformat(),
                "type": backup_type,
                "description": description,
                "version": "2.1.0",
            }
            zf.writestr('manifest.json', json.dumps(manifest, indent=2))
        
        size_bytes = os.path.getsize(filepath)
        
        return BackupInfo(
            id=backup_id,
            filename=filename,
            created_at=datetime.now().isoformat(),
            size_bytes=size_bytes,
            type=backup_type,
            description=description
        )
    
    def restore_backup(self, backup_id: str) -> bool:
        """恢复备份"""
        backup_file = self._find_backup_file(backup_id)
        if not backup_file:
            return False
        
        try:
            with zipfile.ZipFile(backup_file, 'r') as zf:
                zf.extractall(os.path.dirname(self.data_dir))
            return True
        except Exception as e:
            print(f"[Backup] Restore failed: {e}")
            return False
    
    def list_backups(self) -> List[BackupInfo]:
        """列出所有备份"""
        backups = []
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('backup_') and filename.endswith('.zip'):
                filepath = os.path.join(self.backup_dir, filename)
                
                try:
                    with zipfile.ZipFile(filepath, 'r') as zf:
                        if 'manifest.json' in zf.namelist():
                            manifest = json.loads(zf.read('manifest.json'))
                        else:
                            manifest = {}
                except (zipfile.BadZipFile, json.JSONDecodeError, KeyError):
                    manifest = {}
                
                backups.append(BackupInfo(
                    id=manifest.get('id', filename.split('_')[1]),
                    filename=filename,
                    created_at=manifest.get('created_at', ''),
                    size_bytes=os.path.getsize(filepath),
                    type=manifest.get('type', 'unknown'),
                    description=manifest.get('description', '')
                ))
        
        return sorted(backups, key=lambda x: x.created_at, reverse=True)
    
    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        backup_file = self._find_backup_file(backup_id)
        if backup_file:
            os.remove(backup_file)
            return True
        return False
    
    def cleanup_old_backups(self):
        """清理旧备份"""
        backups = self.list_backups()
        
        auto_backups = [b for b in backups if b.type == 'auto']
        manual_backups = [b for b in backups if b.type == 'manual']
        
        while len(auto_backups) > self.max_backups // 2:
            old_backup = auto_backups.pop()
            self.delete_backup(old_backup.id)
        
        while len(manual_backups) > self.max_backups // 2:
            old_backup = manual_backups.pop()
            self.delete_backup(old_backup.id)
    
    def start_auto_backup(self, interval_hours: int = 24):
        """启动自动备份"""
        if self._running:
            return
        
        self._running = True
        self._backup_thread = threading.Thread(
            target=self._auto_backup_loop,
            args=(interval_hours,),
            daemon=True
        )
        self._backup_thread.start()
    
    def stop_auto_backup(self):
        """停止自动备份"""
        self._running = False
    
    def _auto_backup_loop(self, interval_hours: int):
        """自动备份循环"""
        while self._running:
            try:
                self.create_backup(
                    description="自动备份",
                    backup_type="auto"
                )
                self.cleanup_old_backups()
            except Exception as e:
                print(f"[Backup] Auto backup failed: {e}")
            
            time.sleep(interval_hours * 3600)
    
    def _find_backup_file(self, backup_id: str) -> Optional[str]:
        """查找备份文件"""
        for filename in os.listdir(self.backup_dir):
            if backup_id in filename:
                return os.path.join(self.backup_dir, filename)
        return None
    
    def get_backup_stats(self) -> Dict:
        """获取备份统计"""
        backups = self.list_backups()
        total_size = sum(b.size_bytes for b in backups)
        
        return {
            "total_backups": len(backups),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "auto_backups": len([b for b in backups if b.type == 'auto']),
            "manual_backups": len([b for b in backups if b.type == 'manual']),
            "latest_backup": backups[0].created_at if backups else None,
        }


import time
backup_manager = BackupManager()
