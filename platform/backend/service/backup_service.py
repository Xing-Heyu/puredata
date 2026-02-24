#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务层 - 备份服务
整合自 managers/backup_manager.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from managers.backup_manager import BackupManager
    BackupService = BackupManager
    __all__ = ['BackupService', 'BackupManager']
except ImportError:
    import shutil
    from typing import Dict, List
    from datetime import datetime
    
    class BackupService:
        """备份服务 - 占位实现"""
        
        def __init__(self, backup_dir: str = "backups"):
            self.backup_dir = backup_dir
            os.makedirs(backup_dir, exist_ok=True)
        
        def create_backup(self, source_path: str, name: str = None) -> Dict:
            name = name or datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, name)
            
            if os.path.isdir(source_path):
                shutil.copytree(source_path, backup_path)
            else:
                shutil.copy2(source_path, backup_path)
            
            return {
                "name": name,
                "path": backup_path,
                "created_at": datetime.now().isoformat()
            }
        
        def list_backups(self) -> List[Dict]:
            backups = []
            for name in os.listdir(self.backup_dir):
                path = os.path.join(self.backup_dir, name)
                backups.append({
                    "name": name,
                    "path": path,
                    "is_dir": os.path.isdir(path)
                })
            return backups
    
    BackupManager = BackupService
    __all__ = ['BackupService', 'BackupManager']
