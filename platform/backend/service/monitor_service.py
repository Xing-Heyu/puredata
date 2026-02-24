#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务层 - 监控服务
整合自 managers/system_monitor.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from managers.system_monitor import SystemMonitor
    MonitorService = SystemMonitor
    __all__ = ['MonitorService', 'SystemMonitor']
except ImportError:
    import psutil
    from typing import Dict
    from datetime import datetime
    
    class MonitorService:
        """监控服务 - 占位实现"""
        
        @staticmethod
        def get_system_stats() -> Dict:
            return {
                "cpu_percent": psutil.cpu_percent() if 'psutil' in dir() else 0,
                "memory_percent": psutil.virtual_memory().percent if 'psutil' in dir() else 0,
                "disk_percent": psutil.disk_usage('/').percent if 'psutil' in dir() else 0,
                "timestamp": datetime.now().isoformat()
            }
        
        @staticmethod
        def get_process_stats() -> Dict:
            return {
                "pid": os.getpid(),
                "timestamp": datetime.now().isoformat()
            }
    
    SystemMonitor = MonitorService
    __all__ = ['MonitorService', 'SystemMonitor']
