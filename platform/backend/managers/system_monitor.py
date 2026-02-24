#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控模块 - 实时监控系统状态

监控指标：
1. 系统资源（CPU、内存、磁盘）
2. 生成任务状态
3. API调用统计
4. 错误率和告警
"""

import os
import time
import psutil
import threading
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import deque


@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_tasks: int
    requests_per_minute: int
    error_rate: float
    avg_response_time: float


@dataclass
class Alert:
    """告警"""
    id: str
    level: str  # info, warning, error, critical
    message: str
    timestamp: str
    resolved: bool = False
    resolved_at: str = None


class SystemMonitor:
    """
    系统监控器
    
    监控项：
    - CPU使用率
    - 内存使用率
    - 磁盘使用率
    - 活跃任务数
    - 请求速率
    - 错误率
    """
    
    ALERT_THRESHOLDS = {
        "cpu_high": {"threshold": 80, "level": "warning"},
        "cpu_critical": {"threshold": 95, "level": "critical"},
        "memory_high": {"threshold": 80, "level": "warning"},
        "memory_critical": {"threshold": 95, "level": "critical"},
        "disk_high": {"threshold": 80, "level": "warning"},
        "disk_critical": {"threshold": 95, "level": "critical"},
        "error_rate_high": {"threshold": 0.1, "level": "warning"},
        "error_rate_critical": {"threshold": 0.3, "level": "critical"},
    }
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.alerts: List[Alert] = []
        self.request_times: deque = deque(maxlen=100)
        self.error_count = 0
        self.total_requests = 0
        self._lock = threading.Lock()
        self._running = False
        self._monitor_thread = None
    
    def start_monitoring(self, interval: int = 60):
        """启动监控"""
        if self._running:
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def _monitor_loop(self, interval: int):
        """监控循环"""
        while self._running:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                self._check_alerts(metrics)
            except Exception as e:
                print(f"[Monitor] Error: {e}")
            
            time.sleep(interval)
    
    def collect_metrics(self, active_tasks: int = 0) -> SystemMetrics:
        """收集系统指标"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        with self._lock:
            error_rate = self.error_count / max(self.total_requests, 1)
            avg_response_time = (
                sum(self.request_times) / len(self.request_times)
                if self.request_times else 0
            )
            requests_per_minute = len([t for t in self.request_times if t > 0])
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            active_tasks=active_tasks,
            requests_per_minute=requests_per_minute,
            error_rate=error_rate,
            avg_response_time=avg_response_time
        )
    
    def record_request(self, response_time: float, is_error: bool = False):
        """记录请求"""
        with self._lock:
            self.request_times.append(response_time)
            self.total_requests += 1
            if is_error:
                self.error_count += 1
    
    def _check_alerts(self, metrics: SystemMetrics):
        """检查告警"""
        if metrics.cpu_percent > self.ALERT_THRESHOLDS["cpu_critical"]["threshold"]:
            self._create_alert(
                "critical",
                f"CPU使用率过高: {metrics.cpu_percent:.1f}%"
            )
        elif metrics.cpu_percent > self.ALERT_THRESHOLDS["cpu_high"]["threshold"]:
            self._create_alert(
                "warning",
                f"CPU使用率较高: {metrics.cpu_percent:.1f}%"
            )
        
        if metrics.memory_percent > self.ALERT_THRESHOLDS["memory_critical"]["threshold"]:
            self._create_alert(
                "critical",
                f"内存使用率过高: {metrics.memory_percent:.1f}%"
            )
        elif metrics.memory_percent > self.ALERT_THRESHOLDS["memory_high"]["threshold"]:
            self._create_alert(
                "warning",
                f"内存使用率较高: {metrics.memory_percent:.1f}%"
            )
        
        if metrics.disk_percent > self.ALERT_THRESHOLDS["disk_critical"]["threshold"]:
            self._create_alert(
                "critical",
                f"磁盘使用率过高: {metrics.disk_percent:.1f}%"
            )
        elif metrics.disk_percent > self.ALERT_THRESHOLDS["disk_high"]["threshold"]:
            self._create_alert(
                "warning",
                f"磁盘使用率较高: {metrics.disk_percent:.1f}%"
            )
    
    def _create_alert(self, level: str, message: str):
        """创建告警"""
        alert = Alert(
            id=f"{int(time.time() * 1000)}",
            level=level,
            message=message,
            timestamp=datetime.now().isoformat()
        )
        self.alerts.append(alert)
        
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def resolve_alert(self, alert_id: str):
        """解决告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now().isoformat()
                break
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        if self.metrics_history:
            latest = self.metrics_history[-1]
        else:
            latest = self.collect_metrics()
        
        unresolved_alerts = [a for a in self.alerts if not a.resolved]
        
        return {
            "status": "healthy" if not unresolved_alerts else "warning",
            "metrics": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "disk_percent": latest.disk_percent,
                "active_tasks": latest.active_tasks,
                "requests_per_minute": latest.requests_per_minute,
                "error_rate": latest.error_rate,
                "avg_response_time": latest.avg_response_time,
            },
            "alerts": {
                "total": len(self.alerts),
                "unresolved": len(unresolved_alerts),
                "critical": len([a for a in unresolved_alerts if a.level == "critical"]),
                "warning": len([a for a in unresolved_alerts if a.level == "warning"]),
            },
            "uptime": len(self.metrics_history),
            "timestamp": latest.timestamp,
        }
    
    def get_metrics_history(self, count: int = 100) -> List[Dict]:
        """获取历史指标"""
        history = list(self.metrics_history)[-count:]
        return [
            {
                "timestamp": m.timestamp,
                "cpu_percent": m.cpu_percent,
                "memory_percent": m.memory_percent,
                "disk_percent": m.disk_percent,
            }
            for m in history
        ]
    
    def get_alerts(self, unresolved_only: bool = True) -> List[Dict]:
        """获取告警列表"""
        alerts = self.alerts
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]
        
        return [
            {
                "id": a.id,
                "level": a.level,
                "message": a.message,
                "timestamp": a.timestamp,
                "resolved": a.resolved,
            }
            for a in alerts[-50:]
        ]


system_monitor = SystemMonitor()
