#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务层 - 懒加载入口
业务服务：用户、认证、任务、租户、支付、监控、备份等

使用方式：
    from service import UserService, AuthService, TaskService
"""

__all__ = [
    'UserService', 'AuthService', 'TaskService',
    'TenantService', 'PaymentService', 'MonitorService', 'BackupService',
]

_lazy_modules = {
    'UserService': ('.user_service', 'UserService'),
    'AuthService': ('.auth_service', 'AuthService'),
    'TaskService': ('.task_service', 'TaskService'),
    'TenantService': ('.tenant_service', 'TenantService'),
    'PaymentService': ('.payment_service', 'PaymentService'),
    'MonitorService': ('.monitor_service', 'MonitorService'),
    'BackupService': ('.backup_service', 'BackupService'),
}

def __getattr__(name):
    if name in _lazy_modules:
        module_path, class_name = _lazy_modules[name]
        import importlib
        module = importlib.import_module(module_path, package='service')
        return getattr(module, class_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
