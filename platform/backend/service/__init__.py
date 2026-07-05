#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务层 - 懒加载入口
业务服务：任务、备份等

使用方式：
    from service import TaskService
"""

__all__ = [
    'TaskService',
    'BackupService',
]

_lazy_modules = {
    'TaskService': ('.task_service', 'TaskService'),
    'BackupService': ('.backup_service', 'BackupService'),
}

def __getattr__(name):
    if name in _lazy_modules:
        module_path, class_name = _lazy_modules[name]
        import importlib
        module = importlib.import_module(module_path, package='service')
        return getattr(module, class_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
